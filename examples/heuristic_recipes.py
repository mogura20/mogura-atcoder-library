# Source: https://github.com/mogura20/mogura-atcoder-library/blob/9bfcc0557ab1f6feec0911de8c6cf5bd26c11a41/examples/heuristic_recipes.py
"""mogura: 焼きなまし/ビームサーチの最小動作例。問題固有の部分を差し替える。

python3 -m examples.heuristic_recipes。探索中に標準出力を使わず、結果だけ表示。
"""

from mogura.heuristic import mogura_anneal, mogura_beam_search


def mogura_permutation_score(sequence):
    """例の評価関数: 隣接差が小さいほど高い。実際の問題の評価へ変更する。"""
    return -sum(abs(a-b) for a,b in zip(sequence, sequence[1:]))


def mogura_swap_candidate(sequence, rng):
    """合法な近傍を返す。0/1要素ならそのまま返す。"""
    if len(sequence) < 2:
        return sequence
    result = list(sequence)
    a,b = rng.sample(range(len(result)), 2)
    result[a],result[b] = result[b],result[a]
    return tuple(result)


def mogura_permutation_beam(n, width=100):
    """部分列を伸ばす例。訪問集合と末尾が等しければ将来の選択も等しい。"""
    def expand(sequence):
        used = set(sequence)
        for value in range(n):
            if value not in used:
                yield sequence + (value,)

    return mogura_beam_search(
        (), expand, mogura_permutation_score, lambda state: len(state) == n,
        key=lambda state: (frozenset(state), state[-1] if state else -1),
        width=width, max_depth=n,
    )


if __name__ == '__main__':
    initial = (0, 3, 1, 4, 2)
    best, value, stats = mogura_anneal(initial, mogura_permutation_score, mogura_swap_candidate,
                                      copy_state=lambda state: state, iterations=1000, seed=0)
    print('anneal:', best, value, stats)
    print('beam:', mogura_permutation_beam(5))
