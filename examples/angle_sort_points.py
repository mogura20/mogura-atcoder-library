# Source: https://github.com/mogura20/mogura-atcoder-library/blob/3c3652ff152a79f54e88806b9a261df05b2aa4bc/examples/angle_sort_points.py
"""偏角ソートの実行例。Nと、N行の整数座標x yを読み込む。

python3 -m examples.angle_sort_points < input.txt
正のx軸から反時計回り。同方向は入力順、原点は末尾。
"""

from mogura.angle_sort import mogura_angle_sort


def main():
    n = int(input())
    points = [tuple(map(int, input().split())) for _ in range(n)]
    for x, y in mogura_angle_sort(points):
        print(x, y)


if __name__ == "__main__":
    main()
