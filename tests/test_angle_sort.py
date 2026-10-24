"""偏角ソートを分数による独立な順序付けと比較する。"""

import random
import unittest
from fractions import Fraction

from mogura.angle_sort import mogura_angle_sort


def diamond_position(x, y):
    """L1単位円の周上位置を0..4の有理数で表す。浮動小数点不要。"""
    if x > 0 and y >= 0:
        return Fraction(y, x + y)
    if y > 0 and x <= 0:
        return 1 + Fraction(-x, -x + y)
    if x < 0 and y <= 0:
        return 2 + Fraction(-y, -x - y)
    return 3 + Fraction(x, x - y)


class MoguraAngleSortTests(unittest.TestCase):
    def test_axes_and_directions(self):
        points = [(0, -1), (-1, -1), (-1, 0), (-1, 1),
                  (0, 1), (1, 1), (1, 0), (1, -1)]
        expected = [(1, 0), (1, 1), (0, 1), (-1, 1),
                    (-1, 0), (-1, -1), (0, -1), (1, -1)]
        self.assertEqual(mogura_angle_sort(points), expected)
        self.assertEqual(mogura_angle_sort(points, clockwise=True), [expected[0]] + expected[:0:-1])
        self.assertEqual(mogura_angle_sort(points, start=(0, 1)), expected[2:] + expected[:2])
        self.assertEqual(mogura_angle_sort([]), [])

    def test_same_ray_distance_and_zero(self):
        points = [(2, 2), (1, 1), (-2, -2), (-1, -1), (0, 0), (0, 0)]
        self.assertEqual(mogura_angle_sort(points), points)
        self.assertEqual(mogura_angle_sort(points, tie="near"),
                         [(1, 1), (2, 2), (-1, -1), (-2, -2), (0, 0), (0, 0)])
        self.assertEqual(mogura_angle_sort(points, tie="far"), points)
        self.assertEqual(mogura_angle_sort(points, zero="first"), [(0, 0), (0, 0)] + points[:4])
        with self.assertRaises(ValueError):
            mogura_angle_sort(points, zero="error")

    def test_random_against_fraction_oracle(self):
        rng = random.Random(20261024)
        for _ in range(200):
            origin = (rng.randrange(-4, 5), rng.randrange(-4, 5))
            start = rng.choice([(1, 0), (0, 1), (-1, 0), (0, -1), (2, 3), (-3, 2)])
            clockwise = bool(rng.randrange(2))
            points = [(rng.randrange(-7, 8), rng.randrange(-7, 8)) for _ in range(50)]
            points += [origin, origin]
            centers = [p for p in points if p == origin]
            others = [p for p in points if p != origin]
            for tie in ("stable", "near", "far"):
                for zero in ("first", "last"):
                    def reference(point):
                        x, y = point[0] - origin[0], point[1] - origin[1]
                        u = start[0] * x + start[1] * y
                        v = start[0] * y - start[1] * x
                        if clockwise:
                            v = -v
                        distance = 0 if tie == "stable" else x*x + y*y
                        if tie == "far":
                            distance = -distance
                        return diamond_position(u, v), distance
                    ordered = sorted(others, key=reference)
                    expected = centers + ordered if zero == "first" else ordered + centers
                    self.assertEqual(mogura_angle_sort(points, origin=origin, start=start,
                                                       clockwise=clockwise, tie=tie, zero=zero), expected)

    def test_payload_and_key_once(self):
        records = [{"id": "far", "xy": (2, 2)}, {"id": "near", "xy": (1, 1)},
                   {"id": "zero1", "xy": (0, 0)}, {"id": "zero2", "xy": (0, 0)}]
        calls = []
        def key(record):
            calls.append(record["id"])
            return record["xy"]
        result = mogura_angle_sort(iter(records), key=key)
        self.assertEqual(calls, [r["id"] for r in records])
        self.assertTrue(all(a is b for a, b in zip(result, records)))
        self.assertEqual([r["id"] for r in mogura_angle_sort(records, key=lambda r: r["xy"], tie="near")],
                         ["near", "far", "zero1", "zero2"])
        duplicate = [{"id": 0, "xy": (1, 0)}, {"id": 1, "xy": (1, 0)}]
        self.assertEqual(mogura_angle_sort(duplicate, key=lambda r: r["xy"], tie="far"), duplicate)

    def test_huge_integers_and_almost_equal_angles(self):
        n = 10**1000
        # 外積が1しか違わない方向でも、丸めずに厳密な順序で返す。
        a, b = (n + 1, n), (n, n - 1)
        self.assertEqual(mogura_angle_sort([a, b]), [b, a])
        self.assertEqual(mogura_angle_sort([a, b], clockwise=True), [a, b])
        shifted = [(x + n, y - n) for x, y in [a, b]]
        self.assertEqual(mogura_angle_sort(shifted, origin=(n, -n)), [shifted[1], shifted[0]])
        self.assertEqual(mogura_angle_sort([a, b], start=(n, 0)), [b, a])

    def test_invalid_input(self):
        for kwargs in ({"start": (0, 0)}, {"tie": "unknown"}, {"zero": "unknown"}):
            with self.assertRaises(ValueError):
                mogura_angle_sort([], **kwargs)
        for points, kwargs in (([(1.0, 2)], {}), ([(1, 2)], {"origin": (0.0, 0)}),
                               ([(1, 2)], {"start": (1, 0.0)})):
            with self.assertRaises(TypeError):
                mogura_angle_sort(points, **kwargs)
