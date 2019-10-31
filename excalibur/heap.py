"""
if index starts from 0
left is 2i+1
right is 2i+2

parent is (i-1)//2



index from 1
left child is 2i
right child is 2i+1
i parent is i//2

"""
from typing import TypeVar
import sys


T = TypeVar('T')


class MaxHeap:
    def __init__(self, arr_of_obj, key_func=lambda x: x):
        self.get_key = key_func
        self.arr = []
        for obj in arr_of_obj:
            self.insert(obj)

    def swap_element(self, idx_from, idx_to):
        temp = self.arr[idx_to]
        self.arr[idx_to] = self.arr[idx_from]
        self.arr[idx_from] = temp

    def insert(self, obj):
        self.arr.append(obj)
        current_index = len(self.arr) - 1
        parent_index = (current_index - 1) // 2

        # if insertion element is smaller than parent, then bubble up until it doesn't or hit the root
        while current_index > 0 and self.get_key(self.arr[parent_index]) < self.get_key(self.arr[current_index]):
            self.swap_element(current_index, parent_index)
            current_index = parent_index
            parent_index = (current_index - 1) // 2

    def __get_two_children(self, current_idx):
        left_child_idx = 2 * current_idx + 1
        right_child_idx = 2 * current_idx + 2

        left_child = self.get_key(self.arr[left_child_idx]) if left_child_idx < len(self.arr) - 1 else -1
        right_child = self.get_key(self.arr[right_child_idx]) if right_child_idx < len(self.arr) - 1 else -1
        return left_child_idx, right_child_idx, left_child, right_child

    def rebalance_tree(self):
        current_idx = 0
        left_child_idx, right_child_idx, left_child, right_child = self.__get_two_children(current_idx)

        while current_idx < len(self.arr) - 1 and self.get_key(self.arr[current_idx]) < max(
                left_child, right_child):
            idx_to_swap = left_child_idx if self.get_key(self.arr[left_child_idx]) > self.get_key(self.arr[right_child_idx]) else right_child_idx
            self.swap_element(current_idx, idx_to_swap)
            current_idx = idx_to_swap

            left_child_idx, right_child_idx, left_child, right_child = self.__get_two_children(current_idx)

    def pop_element(self):
        res = None

        if len(self.arr) > 0:
            # swap root with last leaf, and pops the leaf
            self.swap_element(0, len(self.arr) - 1)
            res = self.arr.pop()
            # now heap root is not max value in the arr, so need to rebalance the tree
            self.rebalance_tree()

        if res is not None:
            return res
        else:
            sys.stderr.write("No more element to pop\n")
            return None

    def ppformat(self):
        res = []
        temp = []
        for idx in range(len(self.arr)):
            if idx % 2 == 1:
                # a new level is encountered
                res.append(temp)
                temp = []
            temp.append(self.arr[idx])
        res.append(temp)
        return res

    def pprint(self):
        res = self.ppformat()
        print('Heap Content:')
        for arr in res:
            print(arr)
