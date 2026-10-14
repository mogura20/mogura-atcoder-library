"""名前で選ぶ点更新・区間更新を、通常の配列とランダム比較する。"""

import math
import random
import unittest

from mogura.segtree import MoguraSegTree
from mogura.lazy_segtree import MoguraRangeSegTree


class MoguraSegmentModes(unittest.TestCase):
    def test_point_modes(self):
        rng = random.Random(20261015)
        reducers = {
            "min": lambda a: min(a, default=math.inf),
            "max": lambda a: max(a, default=-math.inf),
            "sum": sum,
            "gcd": lambda a: math.gcd(*a),
        }
        for mode, reduce in reducers.items():
            for n in range(25):
                values = [rng.randrange(-20, 21) for _ in range(n)]
                seg = MoguraSegTree(values, mode=mode)
                for _ in range(150):
                    if n:
                        index, change = rng.randrange(n), rng.randrange(-20, 21)
                        if rng.randrange(2):
                            values[index] = change
                            seg.set(index, change)
                        else:
                            values[index] += change
                            seg.add(index, change)
                        self.assertEqual(seg.get(index), values[index])
                    left = rng.randrange(n + 1)
                    right = rng.randrange(left, n + 1)
                    self.assertEqual(seg.query(left, right), reduce(values[left:right]))
                    self.assertEqual(seg.all_query(), reduce(values))
        self.assertEqual(MoguraSegTree([4, 2, 7]).query(0, 3), 2)
        # 1要素の負数でもGCDは非負。
        self.assertEqual(MoguraSegTree([-6], mode="gcd").all_query(), 6)
        with self.assertRaises(ValueError):
            MoguraSegTree([1], mode="unknown")

    def test_mixed_range_operations(self):
        rng = random.Random(241015)
        for mode, reduce in (("sum", sum), ("min", lambda a: min(a, default=math.inf)),
                             ("max", lambda a: max(a, default=-math.inf))):
            for n in range(30):
                values = [rng.randrange(-10, 11) for _ in range(n)]
                seg = MoguraRangeSegTree(values, mode=mode)
                for _ in range(200):
                    left = rng.randrange(n + 1)
                    right = rng.randrange(left, n + 1)
                    change = rng.randrange(-10, 11)
                    kind = rng.randrange(5)
                    if kind == 0:
                        seg.range_add(left, right, change)
                        for i in range(left, right):
                            values[i] += change
                    elif kind == 1:
                        seg.range_assign(left, right, change)
                        for i in range(left, right):
                            values[i] = change
                    elif n and kind == 2:
                        index = rng.randrange(n)
                        seg.set(index, change)
                        values[index] = change
                    elif n and kind == 3:
                        index = rng.randrange(n)
                        seg.add(index, change)
                        values[index] += change
                    self.assertEqual(seg.query(left, right), reduce(values[left:right]))
                    self.assertEqual(seg.all_query(), reduce(values))
                    if n:
                        index = rng.randrange(n)
                        self.assertEqual(seg.get(index), values[index])
        with self.assertRaises(ValueError):
            MoguraRangeSegTree([1], mode="gcd")

    def test_assignment_overrides_and_zero_assignment(self):
        for mode, expected in (("sum", 3), ("min", -2), ("max", 7)):
            seg = MoguraRangeSegTree([1, 2, 3, 4], mode=mode)
            seg.range_add(0, 4, 10)
            seg.range_assign(0, 4, 0)
            seg.range_add(1, 4, -2)
            seg.range_assign(2, 3, 7)
            self.assertEqual([seg.get(i) for i in range(4)], [0, -2, 7, -2])
            self.assertEqual(seg.all_query(), expected)
