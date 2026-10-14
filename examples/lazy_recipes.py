# Source: https://github.com/mogura20/mogura-atcoder-library/blob/92672adf53b8e2d9409cc822a203867ca24ae4bc/examples/lazy_recipes.py
"""mogura: 遅延セグメント木の設定例。必要な設定だけコピーして使う。

python3 -m examples.lazy_recipesで結果を確認できる。
各設定で、単位元への更新が単位元のままになるよう区間長を保持する。
"""

from mogura.lazy_segtree import MoguraLazySegTree


def mogura_range_add_sum(values):
    """区間加算・区間和。値=(和,長さ)、作用=加算量。"""
    return MoguraLazySegTree(
        [(value, 1) for value in values],
        op=lambda a, b: (a[0] + b[0], a[1] + b[1]),
        identity=(0, 0),
        mapping=lambda delta, node: (node[0] + delta * node[1], node[1]),
        composition=lambda new, old: new + old,
        identity_action=0,
    )


def mogura_range_assign_sum(values):
    """区間代入・区間和。作用=Noneは更新なし、整数は代入する値。

    0の代入も有効。Noneを0やif actionへ置き換えると誤動作する。
    """
    return MoguraLazySegTree(
        [(value, 1) for value in values],
        op=lambda a, b: (a[0] + b[0], a[1] + b[1]),
        identity=(0, 0),
        mapping=lambda value, node: node if value is None else (value * node[1], node[1]),
        composition=lambda new, old: old if new is None else new,
        identity_action=None,
    )


def mogura_range_affine_sum(values, mod=998244353):
    """区間一次変換 x→a*x+b と区間和mod。作用=(a,b)。

    composition(new,old)はnew(old(x))。順序を逆にしないこと。
    apply(l,r,(1,b))は加算、(0,b)は代入、(a,0)は乗算。
    """
    if mod < 1:
        raise ValueError("modは正で指定してください")
    return MoguraLazySegTree(
        [(value % mod, 1) for value in values],
        op=lambda a, b: ((a[0] + b[0]) % mod, a[1] + b[1]),
        identity=(0, 0),
        mapping=lambda action, node: ((action[0] * node[0] + action[1] * node[1]) % mod, node[1]),
        composition=lambda new, old: (new[0] * old[0] % mod, (new[0] * old[1] + new[1]) % mod),
        identity_action=(1, 0),
    )


if __name__ == "__main__":
    seg = mogura_range_add_sum([1, 2, 3, 4])
    seg.apply(1, 3, 10)
    assert seg.prod(0, 4)[0] == 30
    assign = mogura_range_assign_sum([1, 2, 3])
    assign.apply(0, 2, 0)
    assert assign.all_prod()[0] == 3
    affine = mogura_range_affine_sum([1, 2, 3])
    affine.apply(0, 3, (2, 1))
    assert affine.all_prod()[0] == 15
    print("mogura lazy recipes: OK")
