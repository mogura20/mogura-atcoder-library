"""mogura: 固定シードのランダム差分テスト。外部依存なし。

実行: python3 -m unittest discover -s tests -v
"""

import math
import random
import subprocess
import sys
import unittest
from pathlib import Path

from mogura.basic import mogura_bisect_int, mogura_compress, mogura_prefix_sum
from mogura.dsu import MoguraDSU
from mogura.fenwick import MoguraFenwickTree
from mogura.graph import mogura_bfs, mogura_dijkstra, mogura_restore_path, mogura_scc, mogura_toposort
from mogura.lca import MoguraLCA
from mogura.number_theory import MoguraComb, mogura_extgcd, mogura_factorize, mogura_sieve
from mogura.segtree import MoguraSegTree
from mogura.string import mogura_manacher, mogura_z_algorithm
from examples.lazy_recipes import mogura_range_add_sum, mogura_range_assign_sum, mogura_range_affine_sum
from tools.bundle import MODULES, mogura_bundle


class MoguraTests(unittest.TestCase):
    def setUp(self):
        self.rng = random.Random(20261014)

    def test_basic(self):
        self.assertEqual(mogura_compress([]), ([], [], {}))
        for _ in range(100):
            values = [self.rng.randrange(-10, 11) for _ in range(30)]
            encoded, ordered, rank = mogura_compress(iter(values))
            self.assertEqual([ordered[i] for i in encoded], values)
            self.assertEqual(rank, {x: i for i, x in enumerate(sorted(set(values)))})
            prefix = mogura_prefix_sum(values)
            for left in range(31):
                for right in range(left, 31):
                    self.assertEqual(prefix[right] - prefix[left], sum(values[left:right]))
        for n in range(50):
            for boundary in range(n + 1):
                self.assertEqual(mogura_bisect_int(-1, n, lambda x: x < boundary), boundary-1)
                self.assertEqual(mogura_bisect_int(n, -1, lambda x: x >= boundary), boundary)

    def test_dsu(self):
        self.assertEqual(MoguraDSU(0).groups(), [])
        for n in range(1, 20):
            uf = MoguraDSU(n)
            labels = list(range(n))
            for _ in range(100):
                a, b = self.rng.randrange(n), self.rng.randrange(n)
                old, new = labels[b], labels[a]
                labels = [new if label == old else label for label in labels]
                root = uf.merge(a, b)
                self.assertEqual(root, uf.leader(a))
                self.assertEqual(uf.component_count, len(set(labels)))
                for vertex in range(n):
                    self.assertEqual(uf.size(vertex), labels.count(labels[vertex]))
                    self.assertEqual(uf.same(a, vertex), labels[a] == labels[vertex])
            self.assertEqual({frozenset(group) for group in uf.groups()},
                             {frozenset(i for i in range(n) if labels[i] == label) for label in set(labels)})

    def test_dsu_unite_and_component_summaries(self):
        empty = MoguraDSU(0)
        self.assertEqual(empty.roots(), [])
        self.assertEqual(empty.group_sizes(), [])
        for n in range(1, 25):
            uf = MoguraDSU(n)
            labels = list(range(n))
            self.assertFalse(uf.unite(0, 0))
            for _ in range(100):
                a, b = self.rng.randrange(n), self.rng.randrange(n)
                was_separate = labels[a] != labels[b]
                if self.rng.randrange(2):
                    result = uf.unite(a, b)
                    self.assertIs(result, was_separate)
                else:
                    result = uf.merge(a, b)
                    self.assertEqual(result, uf.leader(a))
                old, new = labels[b], labels[a]
                labels = [new if label == old else label for label in labels]
                roots, sizes = uf.roots(), uf.group_sizes()
                self.assertEqual(roots, sorted(roots))
                self.assertEqual(len(roots), len(set(labels)))
                self.assertEqual(len(roots), uf.component_count)
                self.assertEqual(sizes, [uf.size(root) for root in roots])
                self.assertEqual(sorted(sizes), sorted(labels.count(label) for label in set(labels)))
                self.assertEqual(sum(sizes), n)
                self.assertEqual(set(roots), {uf.leader(v) for v in range(n)})
        # 代表0でも成功はTrue。代表番号は成分内の最小とは限らない。
        uf = MoguraDSU(3)
        self.assertTrue(uf.unite(0, 1))
        self.assertEqual(uf.leader(1), 0)
        saved_roots, saved_sizes = uf.roots(), uf.group_sizes()
        uf.merge(0, 2)
        self.assertEqual(saved_roots, [0, 2])
        self.assertEqual(saved_sizes, [2, 1])
        other = MoguraDSU(3)
        other.merge(2, 0)
        self.assertEqual(other.leader(0), 2)

    def test_fenwick(self):
        for n in range(31):
            values = [self.rng.randrange(-10, 11) for _ in range(n)]
            bit = MoguraFenwickTree(values)
            for _ in range(100):
                if n and self.rng.randrange(2):
                    index, delta = self.rng.randrange(n), self.rng.randrange(-10, 11)
                    values[index] += delta
                    bit.add(index, delta)
                left = self.rng.randrange(n + 1)
                right = self.rng.randrange(left, n + 1)
                self.assertEqual(bit.sum(left, right), sum(values[left:right]))
            values = [self.rng.randrange(5) for _ in range(n)]
            bit = MoguraFenwickTree(values)
            for target in range(-1, sum(values) + 2):
                expected = 0 if target <= 0 else next((i for i in range(n) if sum(values[:i+1]) >= target), n)
                self.assertEqual(bit.lower_bound(target), expected)
        self.assertEqual(MoguraFenwickTree(5).sum(0, 5), 0)

    def test_segtree(self):
        for n in range(31):
            values = [self.rng.randrange(10) for _ in range(n)]
            seg = MoguraSegTree(values, lambda a, b: a+b, 0)
            for _ in range(100):
                if n and self.rng.randrange(2):
                    index, value = self.rng.randrange(n), self.rng.randrange(10)
                    values[index] = value
                    seg.set(index, value)
                    self.assertEqual(seg.get(index), value)
                left = self.rng.randrange(n+1)
                right = self.rng.randrange(left, n+1)
                self.assertEqual(seg.prod(left, right), sum(values[left:right]))
                self.assertEqual(seg.all_prod(), sum(values))
                limit = self.rng.randrange(30)
                expected = left
                while expected < n and sum(values[left:expected+1]) <= limit:
                    expected += 1
                self.assertEqual(seg.max_right(left, lambda total: total <= limit), expected)
        # 非可換の演算で左右の順序を確認。
        seg = MoguraSegTree(list('abcdefghijk'), lambda a, b: a+b, '')
        for left in range(12):
            for right in range(left, 12):
                self.assertEqual(seg.prod(left, right), 'abcdefghijk'[left:right])

    def test_lazy_add_assign(self):
        for factory in (mogura_range_add_sum, mogura_range_assign_sum):
            for n in range(21):
                values = [self.rng.randrange(-5, 6) for _ in range(n)]
                seg = factory(values)
                for _ in range(150):
                    left = self.rng.randrange(n+1)
                    right = self.rng.randrange(left, n+1)
                    action = self.rng.randrange(-5, 6)
                    if self.rng.randrange(3):
                        seg.apply(left, right, action)
                        for i in range(left, right):
                            values[i] = values[i]+action if factory is mogura_range_add_sum else action
                    else:
                        self.assertEqual(seg.prod(left, right), (sum(values[left:right]), right-left))
                    if n and self.rng.randrange(5) == 0:
                        index = self.rng.randrange(n)
                        values[index] = action
                        seg.set(index, (action, 1))
                        self.assertEqual(seg.get(index), (action, 1))
                    self.assertEqual(seg.all_prod(), (sum(values), n))

    def test_lazy_affine_composition(self):
        mod = 101
        for n in range(21):
            values = [self.rng.randrange(mod) for _ in range(n)]
            seg = mogura_range_affine_sum(values, mod)
            for _ in range(200):
                left = self.rng.randrange(n+1)
                right = self.rng.randrange(left, n+1)
                a, b = self.rng.randrange(5), self.rng.randrange(10)
                seg.apply(left, right, (a, b))
                for i in range(left, right):
                    values[i] = (a*values[i]+b) % mod
                query_left = self.rng.randrange(n+1)
                query_right = self.rng.randrange(query_left, n+1)
                self.assertEqual(seg.prod(query_left, query_right),
                                 (sum(values[query_left:query_right]) % mod, query_right-query_left))
                self.assertEqual(seg.all_prod(), (sum(values) % mod, n))

    def test_shortest_paths(self):
        for n in range(1, 12):
            for _ in range(30):
                graph = [[] for _ in range(n)]
                matrix = [[float('inf')] * n for _ in range(n)]
                for u in range(n):
                    matrix[u][u] = 0
                    for v in range(n):
                        if self.rng.randrange(4) == 0:
                            weight = self.rng.randrange(10)
                            graph[u].append((v, weight))
                            matrix[u][v] = min(matrix[u][v], weight)
                for k in range(n):
                    for i in range(n):
                        for j in range(n):
                            matrix[i][j] = min(matrix[i][j], matrix[i][k]+matrix[k][j])
                sources = self.rng.sample(range(n), self.rng.randrange(1, n+1))
                dist, parent = mogura_dijkstra(graph, sources)
                self.assertEqual(dist, [min(matrix[s][v] for s in sources) for v in range(n)])
                for target in range(n):
                    if dist[target] != float('inf'):
                        path = mogura_restore_path(parent, target)
                        self.assertIn(path[0], sources)
                        for u, v in zip(path, path[1:]):
                            self.assertTrue(any(to == v and dist[u]+weight == dist[v] for to, weight in graph[u]))
                plain = [[v for v, _ in edges] for edges in graph]
                unit = [[(v, 1) for v in edges] for edges in plain]
                bfs_dist, _ = mogura_bfs(plain, sources)
                expected, _ = mogura_dijkstra(unit, sources)
                self.assertEqual(bfs_dist, [-1 if x == float('inf') else x for x in expected])
        self.assertEqual(mogura_bfs([], []), ([], []))
        self.assertEqual(mogura_dijkstra([], []), ([], []))
        self.assertEqual(mogura_bfs([[1], []], 0)[0], [0, 1])
        self.assertEqual(mogura_dijkstra([[(1, 2)], []], 0)[0], [0, 2])
        with self.assertRaises(ValueError):
            mogura_dijkstra([[(0, -1)]], 0)

    def test_scc_and_toposort(self):
        for n in range(16):
            for _ in range(40):
                graph = [[v for v in range(n) if self.rng.randrange(5) == 0] for _ in range(n)]
                reach = []
                for start in range(n):
                    dist, _ = mogura_bfs(graph, start)
                    reach.append([x != -1 for x in dist])
                groups, ids = mogura_scc(graph)
                self.assertEqual(sorted(v for group in groups for v in group), list(range(n)))
                for u in range(n):
                    self.assertIn(u, groups[ids[u]])
                    for v in range(n):
                        self.assertEqual(ids[u] == ids[v], reach[u][v] and reach[v][u])
                    for v in graph[u]:
                        self.assertLessEqual(ids[u], ids[v])
                has_cycle = any(len(group) > 1 for group in groups) or any(u in graph[u] for u in range(n))
                order = mogura_toposort(graph)
                if has_cycle:
                    self.assertIsNone(order)
                else:
                    self.assertEqual(sorted(order), list(range(n)))
                    position = {v: i for i, v in enumerate(order)}
                    for u in range(n):
                        for v in graph[u]:
                            self.assertLess(position[u], position[v])
        # 鎖状グラフでもPythonの再帰上限に依存しない。
        chain = [[v+1] for v in range(9999)] + [[]]
        self.assertEqual(len(mogura_scc(chain)[0]), 10000)

    def test_lca(self):
        for n in range(1, 60):
            graph = [[] for _ in range(n)]
            for v in range(1, n):
                p = self.rng.randrange(v)
                graph[v].append(p)
                graph[p].append(v)
            root = self.rng.randrange(n)
            tree = MoguraLCA(graph, root)
            _, parent = mogura_bfs(graph, root)
            for _ in range(100):
                a, b = self.rng.randrange(n), self.rng.randrange(n)
                ancestors = set()
                current = a
                while current != -1:
                    ancestors.add(current)
                    current = parent[current]
                current = b
                while current not in ancestors:
                    current = parent[current]
                self.assertEqual(tree.lca(a, b), current)
                dist, _ = mogura_bfs(graph, a)
                self.assertEqual(tree.distance(a, b), dist[b])
                steps = self.rng.randrange(n+2)
                current = a
                for _ in range(steps):
                    if current != -1:
                        current = parent[current]
                self.assertEqual(tree.ancestor(a, steps), current)
        chain = [[1]] + [[v-1, v+1] for v in range(1, 9999)] + [[9998]]
        self.assertEqual(MoguraLCA(chain).distance(0, 9999), 9999)
        with self.assertRaises(ValueError):
            MoguraLCA([])
        with self.assertRaises(ValueError):
            MoguraLCA([[], []])

    def test_math(self):
        for limit in range(100):
            expected = [n for n in range(2, limit+1) if all(n % d for d in range(2, math.isqrt(n)+1))]
            self.assertEqual(mogura_sieve(limit), expected)
        for n in range(1, 1000):
            factors = mogura_factorize(n)
            self.assertEqual(math.prod(prime ** exponent for prime, exponent in factors.items()), n)
            for prime in factors:
                self.assertTrue(all(prime % d for d in range(2, math.isqrt(prime)+1)))
        for a in range(-20, 21):
            for b in range(-20, 21):
                gcd, x, y = mogura_extgcd(a, b)
                self.assertEqual(gcd, math.gcd(a, b))
                self.assertEqual(a*x+b*y, gcd)
        for mod in (2, 7, 101, 998244353, 1000000007):
            limit = min(50, mod-1)
            comb = MoguraComb(limit, mod)
            for n in range(limit+1):
                for r in range(n+1):
                    self.assertEqual(comb.ncr(n, r), math.comb(n, r) % mod)
                    self.assertEqual(comb.npr(n, r), math.factorial(n)//math.factorial(n-r) % mod)
            self.assertEqual(comb.ncr(3, -1), 0)
            with self.assertRaises(ValueError):
                comb.ncr(limit+1, 0)

    def test_strings(self):
        for n in range(60):
            for _ in range(30):
                text = ''.join(self.rng.choice('abc') for _ in range(n))
                expected = []
                for i in range(n):
                    length = 0
                    while i+length < n and text[length] == text[i+length]:
                        length += 1
                    expected.append(length)
                self.assertEqual(mogura_z_algorithm(text), expected)
                odd, even = mogura_manacher(text)
                for i in range(n):
                    radius = 1
                    while i-radius >= 0 and i+radius < n and text[i-radius] == text[i+radius]:
                        radius += 1
                    self.assertEqual(odd[i], radius)
                    radius = 0
                    while i-radius-1 >= 0 and i+radius < n and text[i-radius-1] == text[i+radius]:
                        radius += 1
                    self.assertEqual(even[i], radius)

    def test_bundle(self):
        code = mogura_bundle(MODULES, source_ref='a'*40)
        namespace = {}
        exec(compile(code, '<bundle>', 'exec'), namespace)
        self.assertTrue(namespace['MoguraDSU'](1).same(0, 0))
        root = Path(__file__).resolve().parents[1]
        main = (root/'examples/shortest_path.py').read_text(encoding='utf-8')
        code = mogura_bundle(['graph'], main)
        process = subprocess.run([sys.executable, '-c', code], input='4 4 0 3\n0 1 2\n1 3 3\n0 2 1\n2 3 8\n', text=True, capture_output=True)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(process.stdout, '5\n0 1 3\n')
        for bad in ('import mogura.graph\n', 'from mogura.dsu import MoguraDSU as DSU\n',
                    'from mogura.dsu import *\n', 'from mogura.graph import mogura_bfs\n',
                    'from mogura.dsu import MoguraDSU; x=1\n',
                    'def f():\n    from mogura.dsu import MoguraDSU\n'):
            with self.assertRaises(ValueError):
                mogura_bundle(['dsu'], bad)


if __name__ == '__main__':
    unittest.main()
