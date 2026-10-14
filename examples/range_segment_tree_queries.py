"""区間加算・区間代入・区間取得。入力仕様はMoguraRangeSegTreeのクラス直下。

python3 -m examples.range_segment_tree_queries < input.txt
MODEをsum/min/maxへ変えて使用する。区間は0始まりの[L,R)。
"""

from mogura.lazy_segtree import MoguraRangeSegTree


def main():
    mode = input().strip()
    n, q = map(int, input().split())
    values = list(map(int, input().split()))
    seg = MoguraRangeSegTree(values, mode=mode)
    for _ in range(q):
        query = list(map(int, input().split()))
        kind, left, right = query[:3]
        if kind == 0:
            seg.range_add(left, right, query[3])
        elif kind == 1:
            seg.range_assign(left, right, query[3])
        else:
            print(seg.query(left, right))


if __name__ == "__main__":
    main()
