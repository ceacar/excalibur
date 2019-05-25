import string

class Vertice:
    def __init__(self, name, neighbors=None):
        if not neighbors:
            neighbors = []
        self.neighbors = neighbors
        self.name = name

    def add_neighbor(self, nei):
        self.neighbors.append(nei)



def init_graph(size=26):
    res = []
    for char in string.ascii_lowercase[:size]:
        res.append(Vertice(name = char))
    return res


def get_name_from_vertices_arr(graph_arr: [Vertice]) -> None:
    res = []
    for vert in graph_arr:
        res.append(vert.name)
    return res
