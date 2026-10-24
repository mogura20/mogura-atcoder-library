# Source: https://github.com/mogura20/mogura-atcoder-library/blob/3c3652ff152a79f54e88806b9a261df05b2aa4bc/examples/segment_tree_queries.py
"""点代入・点加算・区間取得。入力仕様はMoguraSegTreeのクラス直下。

python3 -m examples.segment_tree_queries < input.txt
MODEをmin/sum/gcd/maxへ変えるだけで取得方法を選べる。
"""

from mogura.segtree import MoguraSegTree


def main():
    mode = input().strip()
    n, q = map(int, input().split())
    values = list(map(int, input().split()))
    seg = MoguraSegTree(values, mode=mode)
    for _ in range(q):
        kind, x, y = map(int, input().split())
        if kind == 0:
            seg.set(x, y)
        elif kind == 1:
            seg.add(x, y)
        else:
            print(seg.query(x, y))


if __name__ == "__main__":
    main()
