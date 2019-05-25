#UTILITY CLASSES AND METHOD FOR GRAPH

import string


class Vertice:
    def __init__(self, name, neighbors=None):
        if not neighbors:
            neighbors = []
        self.neighbors = neighbors
        self.name = name

    def add_neighbor(self, nei):
        self.neighbors.append(nei)


class Graph:
    def __init__(self, vertices = []):
        self.vertices = vertices

    def get_name_from_vertices_arr(self) -> None:
        res = []
        for vert in self.vertices:
            res.append(vert.name)
        return res

    def generate_graph(self) -> dict:
        graph = {}
        for vert in self.vertices:
            neighbors = vert.neighbors
            if vert.name not in graph:
                graph[vert.name] = []
            for nei in neighbors:
                graph[vert.name].append(nei.name)
        return graph

    def get_edges(self) -> [(Vertice, Vertice)]:
        self.edges = []
        for vert in self.vertices:
            neighbors = vert.neighbors
            for nei in neighbors:
                self.edges.append((vert, nei))

        return self.edges

    def get_edges_only_name(self) -> [(str,str)]:

        edge_name_only = []
        for edge_pair in self.edges:
            ver_from, ver_to = edge_pair
            edge_name_only.append((ver_from.name, ver_to.name))

        return edge_name_only

    def reverse_all_edges(self):
        new_edges = []
        for ver_from, ver_to in self.edges:
            new_edges.append((ver_to, ver_from))
        return new_edges

    def set_new_vertices_direction(self, new_edges):
        for ver_from, ver_to in new_edges:
            ver_from.add_neighbor(ver_to)

    def reset_all_vertices_direction(self):
        for ver in self.vertices:
            ver.neighbors = []

    def reverse_graph(self):
        # 1. generate edges first
        self.get_edges()
        # 2. clear all neighbors for all vertices
        self.reset_all_vertices_direction()
        # 3. reverse all edge in edges
        new_edges = self.reverse_all_edges()
        # 4. adds neighbors back according to all edges
        self.set_new_vertices_direction(new_edges)
        # 5. regenerate all edges
        self.get_edges()


def init_graph(size=26):
    res = []
    for char in string.ascii_lowercase[:size]:
        res.append(Vertice(name = char))
    return res


