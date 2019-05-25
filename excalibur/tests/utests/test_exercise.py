import unittest
import excalibur
from excalibur.exercise import *


class TestExercise(unittest.TestCase):
    def setUp(self):
        self.vertices = init_graph(size=3)
        self.graph = Graph(self.vertices)
        a,b,c = self.vertices
        a.add_neighbor(b)
        b.add_neighbor(c)
        c.add_neighbor(b)
        a.add_neighbor(c)
        self.graph.get_edges()


    def test_init_graph(self):
        assert self.vertices[0].name == 'a'
        assert self.vertices[1].name == 'b'
        assert self.vertices[2].name == 'c'

    def test_get_name_from_vertices_arr(self):
        assert self.graph.get_name_from_vertices_arr() == ['a','b','c']

    def test_generate_graph(self):
        """
        a->b->c->b
        |-----^
        should have
        """
        expected_graph = {
            "a":["b", "c"],
            "b":["c"],
            "c":["b"],
        }

        assert self.graph.generate_graph() == expected_graph

    def test_get_edges_only_name(self):
        edges_name_only = self.graph.get_edges_only_name()
        assert sorted(edges_name_only) == sorted([
            ("a","b"),
            ("b","c"),
            ("a","c"),
            ("c","b"),
        ])

    def test_reverse_all_edges(self):
        self.graph.reverse_graph()
        edges_name_only = self.graph.get_edges_only_name()
        assert sorted(edges_name_only) == sorted([
            ("b","a"),
            ("c","b"),
            ("c","a"),
            ("b","c"),
        ])

