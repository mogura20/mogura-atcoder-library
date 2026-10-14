# Source: https://github.com/mogura20/mogura-atcoder-library/blob/92672adf53b8e2d9409cc822a203867ca24ae4bc/examples/desktop_recipes.py
"""mogura: Desktop/atcoderから追加した機能の最小使用例。

python3 -m examples.desktop_recipesで実行。全て0始まり・区間は半開。
"""

from mogura.weighted_dsu import MoguraWeightedDSU
from mogura.graph_extra import mogura_bellman_ford, mogura_zero_one_bfs
from mogura.mst import mogura_kruskal
from mogura.matching import MoguraBipartiteMatching
from mogura.dp import mogura_lis, mogura_lcs, mogura_interval_dp, mogura_grid_path_count
from mogura.range_utils import MoguraPrefixSum2D
from mogura.math_extra import MoguraOsaK, mogura_team_sizes
from mogura.geometry import mogura_segments_intersect
from mogura.trie import MoguraTrie
from mogura.rolling_hash import MoguraRollingHash


def main():
    uf = MoguraWeightedDSU(3)
    assert uf.merge(0,1,3) and uf.merge(1,2,-1)
    assert uf.diff(0,2) == 2 and not uf.merge(0,2,9)
    assert mogura_zero_one_bfs([[(1,0)],[]],0)[0] == [0,0]
    assert mogura_bellman_ford(3,[(0,1,2),(1,2,-3)],0)[0] == [0,2,-1]
    assert mogura_kruskal(3,[(0,1,2),(1,2,1),(0,2,5)])[0] == 3
    matching = MoguraBipartiteMatching(2,2)
    matching.add_edge(0,0)
    matching.add_edge(0,1)
    matching.add_edge(1,0)
    assert matching.maximum_matching() == 2
    values = [3,1,2,4]
    length, indices = mogura_lis(values)
    assert length == 3 and [values[i] for i in indices] == [1,2,4]
    assert mogura_lcs('abc','ac') == (2,['a','c'])
    prefix = [0,10,30,60]
    assert mogura_interval_dp(3,lambda l,m,r: prefix[r]-prefix[l])[0][3] == 90
    assert mogura_grid_path_count(['..','..']) == 2
    assert MoguraPrefixSum2D([[1,2],[3,4]]).sum(0,1,2,2) == 6
    assert MoguraOsaK(100).factorize(100) == {2:2,5:2}
    assert list(mogura_team_sizes(4,2)) == [(1,3),(2,2)]
    assert mogura_segments_intersect((0,0),(2,2),(0,2),(2,0))
    trie = MoguraTrie()
    for word in ('ab','ac','ab'):
        trie.insert(word)
    assert trie.pair_lcp_sum() == 4
    hashed = MoguraRollingHash('abcabc')
    assert hashed.same(0,3,hashed,3,6)
    print('mogura desktop recipes: OK')


if __name__ == '__main__':
    main()
