from excalibur.heap import *
import unittest
import random
import copy

class TestHeap(unittest.TestCase):
    def test_heap(self):
        input_nums = [3,7,9,1,5]
        mh = MaxHeap(input_nums)
        res = []
        for i in range(len(mh.arr)):
            res.append(mh.pop_element())

        assert res == [9,7,5,3,1]

    def test_heap_large_number(self):
        test_size = 100
        input_nums = []
        for i in range(test_size):
            input_nums.append(random.randint(0, test_size))

        expected_arr = copy.deepcopy(input_nums)
        expected_arr.sort(reverse = True)
        res = []
        mh = MaxHeap(input_nums)
        for i in range(len(mh.arr)):
            res.append(mh.pop_element())

        assert res == expected_arr

    def test_heap(self):
        input_nums = [{"a":3},{"b":7},{"c":9},{"d":1},{"e":5}]
        mh = MaxHeap(input_nums, key_func = lambda x: next(iter(x.values())) )
        res = []
        for i in range(len(mh.arr)):
            res.append(mh.pop_element())

        expected_result = [
            {"c":9},
            {"b":7},
            {"e":5},
            {"a":3},
            {"d":1},
        ]
        assert res == expected_result


