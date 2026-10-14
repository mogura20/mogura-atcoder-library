"""mogura: 移行したアルゴリズムを小規模の全探索・独立計算と比較する。"""

import itertools
import math
import random
import re
import unittest
from pathlib import Path
from io import StringIO
from fractions import Fraction
from functools import lru_cache

from mogura.weighted_dsu import MoguraWeightedDSU
from mogura.graph import mogura_dijkstra, mogura_bfs
from mogura.graph_extra import mogura_zero_one_bfs, mogura_bellman_ford, mogura_floyd_warshall, mogura_dfs_orders
from mogura.mst import mogura_kruskal, mogura_prim
from mogura.matching import MoguraBipartiteMatching, MoguraHopcroftKarp
from mogura.interactive import MoguraInteractiveIO
from mogura.dp import (mogura_lis, mogura_lcs, mogura_hamiltonian_cost, mogura_interval_dp,
                       mogura_grid_path_count, mogura_tree_independent_set, mogura_expected_steps)
from mogura.range_utils import MoguraPrefixSum2D, mogura_subarrays_sum_leq, mogura_true_runs
from mogura.math_extra import MoguraOsaK, mogura_divisors, mogura_ceil_div, mogura_base_digits, mogura_team_sizes
from mogura.number_theory import mogura_factorize
from mogura.geometry import (mogura_cross, mogura_dot, mogura_distance_squared,
                             mogura_segments_intersect, mogura_rotate_point, mogura_transpose, mogura_rotate_grid)
from mogura.string import mogura_run_length, mogura_z_search
from mogura.trie import MoguraTrie
from mogura.rolling_hash import MoguraRollingHash
from mogura.enumeration import mogura_states, mogura_distinct_permutations
from mogura.heuristic import mogura_anneal, mogura_beam_search
from tools.bundle import mogura_bundle
from examples.heuristic_recipes import mogura_permutation_beam


class MoguraDesktopTests(unittest.TestCase):
    def setUp(self):
        self.rng = random.Random(20261015)

    def test_weighted_dsu_against_constraint_graph(self):
        n = 20
        uf = MoguraWeightedDSU(n)
        graph = [[] for _ in range(n)]
        for _ in range(500):
            a,b,delta = self.rng.randrange(n), self.rng.randrange(n), self.rng.randrange(-10,11)
            potentials = {a:0}
            queue = [a]
            for u in queue:
                for v,w in graph[u]:
                    if v not in potentials:
                        potentials[v] = potentials[u]+w
                        queue.append(v)
            expected = b not in potentials or potentials[b] == delta
            self.assertEqual(uf.merge(a,b,delta), expected)
            if expected:
                graph[a].append((b,delta))
                graph[b].append((a,-delta))
            for v in potentials:
                self.assertEqual(uf.diff(a,v), potentials[v])
            if not expected:
                self.assertNotEqual(uf.diff(a,b), delta)
        self.assertIsNone(MoguraWeightedDSU(2).diff(0,1))

    def test_dfs_against_recursive_order(self):
        for n in range(15):
            graph = [[v for v in range(n) if self.rng.randrange(5)==0] for _ in range(n)]
            pre,post,parent = [],[],[-1]*n
            seen = set()
            def visit(u):
                seen.add(u)
                pre.append(u)
                for v in graph[u]:
                    if v not in seen:
                        parent[v] = u
                        visit(v)
                post.append(u)
            for u in range(n):
                if u not in seen:
                    visit(u)
            self.assertEqual(mogura_dfs_orders(graph), (pre,post,parent))
        self.assertEqual(mogura_dfs_orders([[1],[],[]],0)[0], [0,1])

    def test_zero_one_bfs(self):
        for n in range(1,30):
            for _ in range(20):
                graph = [[(v,self.rng.randrange(2)) for v in range(n) if self.rng.randrange(5)==0] for _ in range(n)]
                sources = self.rng.sample(range(n),self.rng.randrange(n+1))
                self.assertEqual(mogura_zero_one_bfs(graph,sources)[0],mogura_dijkstra(graph,sources)[0])
        self.assertEqual(mogura_zero_one_bfs([],[]),([],[]))
        with self.assertRaises(ValueError):
            mogura_zero_one_bfs([[(0,2)]],0)

    def test_negative_shortest_paths(self):
        # 重みw=非負基礎値+potential[v]-potential[u]なら負辺があっても負閉路なし。
        for n in range(1,12):
            for _ in range(30):
                potential = [self.rng.randrange(-10,11) for _ in range(n)]
                edges,base_graph = [],[[] for _ in range(n)]
                for u in range(n):
                    for v in range(n):
                        if self.rng.randrange(4)==0:
                            base = self.rng.randrange(8)
                            base_graph[u].append((v,base))
                            edges.append((u,v,base+potential[v]-potential[u]))
                all_dist = mogura_floyd_warshall(n,edges)
                for start in range(n):
                    reference,_ = mogura_dijkstra(base_graph,start)
                    expected = [d+potential[v]-potential[start] for v,d in enumerate(reference)]
                    dist,_ = mogura_bellman_ford(n,edges,start)
                    self.assertEqual(dist,expected)
                    self.assertEqual(all_dist[start],expected)
        edges = [(0,1,2),(1,2,-2),(2,1,1),(2,3,4),(4,4,-1)]
        expected = [0,-math.inf,-math.inf,-math.inf,math.inf]
        self.assertEqual(mogura_bellman_ford(5,edges,0)[0],expected)
        all_dist = mogura_floyd_warshall(5,edges)
        self.assertEqual(all_dist[0],expected)
        self.assertEqual(all_dist[4],[math.inf]*4+[-math.inf])
        self.assertEqual(mogura_floyd_warshall(2,[(0,1,3)],False),[[0,3],[3,0]])
        self.assertEqual(mogura_floyd_warshall(0,[]),[])

    def test_mst_against_spanning_tree_enumeration(self):
        for n in range(1,6):
            for _ in range(30):
                edges = [(u,v,self.rng.randrange(-5,10)) for u in range(n) for v in range(u+1,n)
                         if v==u+1 or self.rng.randrange(2)]
                graph = [[] for _ in range(n)]
                for u,v,w in edges:
                    graph[u].append((v,w)); graph[v].append((u,w))
                optimum = math.inf
                for chosen in itertools.combinations(edges,n-1):
                    adjacent = [[] for _ in range(n)]
                    for u,v,_ in chosen:
                        adjacent[u].append(v); adjacent[v].append(u)
                    if all(d!=-1 for d in mogura_bfs(adjacent,0)[0]):
                        optimum = min(optimum,sum(w for _,_,w in chosen))
                before = edges[:]
                for result in (mogura_kruskal(n,edges),mogura_prim(graph)):
                    self.assertEqual(result[0],optimum)
                    self.assertEqual(len(result[1]),n-1)
                    self.assertEqual(result[2],1)
                self.assertEqual(edges,before)
        self.assertEqual(mogura_kruskal(4,[(0,1,2)]),(2,[(0,1,2)],3))
        self.assertEqual(mogura_prim([[(1,2)],[(0,2)],[],[]])[2],3)

    def test_matching_against_enumeration(self):
        for left_size in range(6):
            for right_size in range(6):
                for _ in range(20):
                    matching = MoguraBipartiteMatching(left_size,right_size)
                    hk = MoguraHopcroftKarp(left_size,right_size)
                    graph = [[] for _ in range(left_size)]
                    def brute(left,used):
                        if left==left_size:
                            return 0
                        return max([brute(left+1,used)]+[1+brute(left+1,used|{right}) for right in graph[left] if right not in used])
                    candidates = list(itertools.product(range(left_size),range(right_size)))
                    self.rng.shuffle(candidates)
                    for left,right in candidates[:len(candidates)//2]:
                        graph[left].append(right)
                        matching.add_edge(left,right)
                        hk.add_edge(left,right)
                        self.assertEqual(matching.maximum_matching(),brute(0,set()))
                        self.assertEqual(hk.maximum_matching(),brute(0,set()))
                    self.assertEqual(matching.maximum_matching(),brute(0,set()))
                    self.assertEqual(hk.maximum_matching(),brute(0,set()))
                    pairs = matching.pairs()
                    self.assertEqual(len({right for _,right in pairs}),len(pairs))
                    for left,right in pairs:
                        self.assertIn(right,graph[left])

    def test_lis_and_lcs(self):
        for n in range(9):
            for _ in range(30):
                values = [self.rng.randrange(5) for _ in range(n)]
                for strict in (True,False):
                    length,indices = mogura_lis(values,strict)
                    expected = 0
                    for mask in range(1<<n):
                        chosen = [values[i] for i in range(n) if mask>>i&1]
                        if all(a<b if strict else a<=b for a,b in zip(chosen,chosen[1:])):
                            expected = max(expected,len(chosen))
                    self.assertEqual(length,expected)
                    self.assertEqual(indices,sorted(indices))
                    chosen = [values[i] for i in indices]
                    self.assertEqual(len(chosen),length)
                    self.assertTrue(all(a<b if strict else a<=b for a,b in zip(chosen,chosen[1:])))
                right = [self.rng.randrange(5) for _ in range(n)]
                subsequences = {tuple(values[i] for i in range(n) if mask>>i&1) for mask in range(1<<n)}
                right_subseqs = {tuple(right[i] for i in range(n) if mask>>i&1) for mask in range(1<<n)}
                length,subseq = mogura_lcs(values,right)
                self.assertEqual(length,max(map(len,subsequences & right_subseqs)))
                self.assertIn(tuple(subseq),subsequences & right_subseqs)

    def test_hamiltonian_and_interval_dp(self):
        self.assertEqual(mogura_hamiltonian_cost([]),0)
        for n in range(1,7):
            cost = [[self.rng.randrange(-3,10) if self.rng.randrange(5) else math.inf for _ in range(n)] for _ in range(n)]
            for cycle in (False,True):
                for start in (None,0,n-1):
                    reference = math.inf
                    fixed_start = 0 if cycle and start is None else start
                    for permutation in itertools.permutations(range(n)):
                        if fixed_start is not None and permutation[0]!=fixed_start:
                            continue
                        value = sum(cost[a][b] for a,b in zip(permutation,permutation[1:]))
                        if cycle and n>1:
                            value += cost[permutation[-1]][permutation[0]]
                        reference = min(reference,value)
                    self.assertEqual(mogura_hamiltonian_cost(cost,start,cycle),reference)
        for n in range(8):
            values = tuple(self.rng.randrange(1,10) for _ in range(n))
            @lru_cache(None)
            def brute(groups):
                if len(groups)<=1:
                    return 0
                return min(groups[i]+groups[i+1]+brute(groups[:i]+(groups[i]+groups[i+1],)+groups[i+2:]) for i in range(len(groups)-1))
            table = mogura_interval_dp(n,lambda l,m,r: sum(values[l:r]))
            self.assertEqual(table[0][n],brute(values))

    def test_grid_and_tree_dp(self):
        for h in range(1,6):
            for w in range(1,6):
                grid = [''.join(self.rng.choice('..#') for _ in range(w)) for _ in range(h)]
                def brute(r,c):
                    if r>=h or c>=w or grid[r][c]=='#':
                        return 0
                    if (r,c)==(h-1,w-1):
                        return 1
                    return brute(r+1,c)+brute(r,c+1)
                self.assertEqual(mogura_grid_path_count(grid,mod=None),brute(0,0))
        self.assertEqual(mogura_grid_path_count([]),0)
        for n in range(1,11):
            graph = [[] for _ in range(n)]
            edges = []
            for v in range(1,n):
                u = self.rng.randrange(v)
                graph[u].append(v); graph[v].append(u); edges.append((u,v))
            weights = [self.rng.randrange(-5,10) for _ in range(n)]
            reference = max(sum(weights[v] for v in range(n) if mask>>v&1) for mask in range(1<<n)
                            if all(not(mask>>u&1 and mask>>v&1) for u,v in edges))
            value,chosen = mogura_tree_independent_set(graph,weights,self.rng.randrange(n))
            self.assertEqual(value,reference)
            self.assertEqual(sum(weights[v] for v in chosen),value)
            self.assertTrue(all(not(u in chosen and v in chosen) for u,v in edges))

    def test_expectation(self):
        for goal in range(20):
            @lru_cache(None)
            def exact(position):
                if position>=goal:
                    return Fraction(0)
                return 1+sum(exact(position+d)*Fraction(1,6) for d in range(1,7))
            self.assertAlmostEqual(mogura_expected_steps(goal,[(d,1/6) for d in range(1,7)]),float(exact(0)))
        with self.assertRaises(ValueError):
            mogura_expected_steps(3,[(0,1)])

    def test_range_utils(self):
        for n in range(30):
            values = [self.rng.randrange(6) for _ in range(n)]
            for limit in range(-1,12):
                lengths = [r-l for l in range(n) for r in range(l+1,n+1) if sum(values[l:r])<=limit]
                self.assertEqual(mogura_subarrays_sum_leq(values,limit),(len(lengths),max(lengths,default=0)))
            runs = mogura_true_runs(values,lambda x:x%2==0)
            self.assertEqual([i for l,r in runs for i in range(l,r)], [i for i,x in enumerate(values) if x%2==0])
        for h in range(6):
            for w in range(6):
                grid = [[self.rng.randrange(-5,6) for _ in range(w)] for _ in range(h)]
                prefix = MoguraPrefixSum2D(grid)
                for top in range(h+1):
                    for bottom in range(top,h+1):
                        for left in range(prefix.width+1):
                            for right in range(left,prefix.width+1):
                                self.assertEqual(prefix.sum(top,left,bottom,right),sum(sum(row[left:right]) for row in grid[top:bottom]))

    def test_math_and_enumeration(self):
        osa = MoguraOsaK(1000)
        for number in range(1,1001):
            self.assertEqual(osa.factorize(number),mogura_factorize(number))
            self.assertEqual(math.prod(osa.factor_list(number)),number)
            self.assertEqual(mogura_divisors(number),[d for d in range(1,number+1) if number%d==0])
        for a in range(-20,21):
            for b in range(-10,11):
                if b:
                    self.assertEqual(mogura_ceil_div(a,b),math.ceil(Fraction(a,b)))
        for number in range(100):
            for base in range(2,12):
                reconstructed = 0
                for digit in mogura_base_digits(number,base):
                    reconstructed = reconstructed*base+digit
                self.assertEqual(reconstructed,number)
        for total in range(8):
            for teams in range(5):
                all_sizes = [size for size in itertools.product(range(1,total+1),repeat=teams) if sum(size)==total]
                self.assertEqual(sorted(mogura_team_sizes(total,teams,True)),sorted(all_sizes))
                self.assertEqual(list(mogura_team_sizes(total,teams)),sorted({tuple(sorted(size)) for size in all_sizes}))
        self.assertEqual(list(mogura_states(3,3)),list(itertools.product(range(3),repeat=3)))
        for values in ([],[1],[1,1,2,2],list('abca')):
            self.assertEqual(list(mogura_distinct_permutations(values)),sorted(set(itertools.permutations(values))))

    def test_geometry_against_exact_parameter_solution(self):
        def point_on(point,a,b):
            return (b[0]-a[0])*(point[1]-a[1])==(b[1]-a[1])*(point[0]-a[0]) and all(min(a[k],b[k])<=point[k]<=max(a[k],b[k]) for k in (0,1))
        def reference(a,b,c,d):
            u = (b[0]-a[0],b[1]-a[1]); v = (d[0]-c[0],d[1]-c[1]); w = (c[0]-a[0],c[1]-a[1])
            cross = lambda x,y: x[0]*y[1]-x[1]*y[0]
            denominator = cross(u,v)
            if denominator==0:
                return point_on(a,c,d) or point_on(b,c,d) or point_on(c,a,b) or point_on(d,a,b)
            t,s = Fraction(cross(w,v),denominator),Fraction(cross(w,u),denominator)
            return 0<=t<=1 and 0<=s<=1
        for _ in range(3000):
            points = [(self.rng.randrange(-3,4),self.rng.randrange(-3,4)) for _ in range(4)]
            self.assertEqual(mogura_segments_intersect(*points),reference(*points))
        self.assertFalse(mogura_segments_intersect((0,0),(0,0),(1,1),(1,1)))
        self.assertEqual(mogura_cross((0,0),(1,0),(0,1)),1)
        self.assertEqual(mogura_dot((0,0),(1,2),(3,4)),11)
        self.assertEqual(mogura_distance_squared((1,2),(4,6)),25)
        x,y = mogura_rotate_point((2,1),90,center=(1,1))
        self.assertAlmostEqual(x,1); self.assertAlmostEqual(y,2)
        matrix = [[1,2,3],[4,5,6]]
        self.assertEqual(mogura_transpose(matrix),[[1,4],[2,5],[3,6]])
        self.assertEqual(mogura_rotate_grid(matrix),[[4,1],[5,2],[6,3]])
        self.assertEqual(mogura_rotate_grid(matrix,4),matrix)

    def test_string_additions(self):
        for _ in range(100):
            text = ''.join(self.rng.choice('ab$') for _ in range(self.rng.randrange(20)))
            pattern = ''.join(self.rng.choice('ab$') for _ in range(self.rng.randrange(5)))
            self.assertEqual(mogura_z_search(text,pattern),[i for i in range(len(text)+1) if text.startswith(pattern,i)])
            runs = mogura_run_length(text)
            self.assertEqual(''.join(value*count for value,count in runs),text)
            trie = MoguraTrie()
            words = [''.join(self.rng.choice('ab') for _ in range(self.rng.randrange(7))) for _ in range(20)]
            for word in words:
                trie.insert(word)
            for word in words+['z']:
                self.assertEqual(trie.count(word),words.count(word))
                self.assertEqual(trie.count_prefix(word),sum(s.startswith(word) for s in words))
            total = 0
            for a,b in itertools.combinations(words,2):
                for x,y in zip(a,b):
                    if x!=y:
                        break
                    total += 1
            self.assertEqual(trie.pair_lcp_sum(),total)
            hashed = MoguraRollingHash(text)
            for left in range(len(text)+1):
                for right in range(left,len(text)+1):
                    other = MoguraRollingHash(text[left:right])
                    self.assertEqual(hashed.get(left,right),other.get(0,right-left))
                    self.assertTrue(hashed.same(left,right,other,0,right-left))

    def test_heuristic_invariants(self):
        initial = [0]
        def propose(state,rng):
            return [state[0]+rng.choice([-1,1])]
        args = (initial,lambda state: -(state[0]-4)**2,propose,list)
        first = mogura_anneal(*args,iterations=200,seed=7)
        second = mogura_anneal(*args,iterations=200,seed=7)
        self.assertEqual(first,second)
        self.assertEqual(initial,[0])
        self.assertEqual(first[1],-(first[0][0]-4)**2)
        self.assertGreaterEqual(first[1],-16)
        self.assertEqual(mogura_anneal(*args,iterations=0)[0],[0])
        self.assertEqual(mogura_anneal(*args,time_limit=0)[2]['iterations'],0)
        for n in range(7):
            state,value,_ = mogura_permutation_beam(n,width=10000)
            self.assertEqual(sorted(state),list(range(n)))
            self.assertEqual(value,-max(0,n-1))
        # 短い枝に完成解があっても深い枝のより良い完成解を探索する。
        children = {'start':['done1','middle'],'middle':['done2']}
        result = mogura_beam_search('start',lambda s:children.get(s,[]),lambda s:0,
                                    lambda s:s.startswith('done'),final_score=lambda s:int(s[-1]),max_depth=3)
        self.assertEqual(result[:2],('done2',2))
        self.assertEqual(mogura_beam_search(0,lambda s:[],lambda s:0,lambda s:False)[:2],(None,None))

    def test_bundle_dependencies_and_examples(self):
        code = mogura_bundle(['mst'],'from mogura.mst import mogura_kruskal\nassert mogura_kruskal(2,[(0,1,3)])[0]==3\n')
        self.assertNotIn('from mogura.',code)
        exec(compile(code,'<bundle>','exec'),{})

    def test_interactive_real_and_mock(self):
        output = StringIO()
        io = MoguraInteractiveIO(input_stream=StringIO('1\n'),output_stream=output)
        self.assertEqual(io.ask(2),'1')
        io.answer(3)
        self.assertEqual(output.getvalue(),'? 2\n! 3\n')
        with self.assertRaises(EOFError):
            io.ask(4)
        output = StringIO()
        io = MoguraInteractiveIO(mock_query=lambda i:'0111'[i],output_stream=output)
        self.assertEqual(io.ask(1),'1')
        io.answer(0)
        self.assertEqual(io.query_count,1)
        self.assertEqual(io.last_answer,(0,))
        self.assertEqual(output.getvalue(),'')

    def test_hopcroft_karp_long_augmenting_path(self):
        n = 3000
        hk = MoguraHopcroftKarp(n,n)
        for i in range(n-1):
            hk.add_edge(i,i)
            hk.add_edge(i,i+1)
        hk.add_edge(n-1,0)
        self.assertEqual(hk.maximum_matching(),n)
        self.assertEqual(len(set(hk.match_right)),n)

    def test_documentation_examples(self):
        root = Path(__file__).resolve().parents[1]
        for filename in ('docs/usage.md','docs/python_notes.md'):
            source = (root/filename).read_text(encoding='utf-8')
            for index,code in enumerate(re.findall(r'```python\n(.*?)```',source,re.S)):
                with self.subTest(file=filename,example=index):
                    exec(compile(code,filename,'exec'),{})


if __name__ == '__main__':
    unittest.main()
