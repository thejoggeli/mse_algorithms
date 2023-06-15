import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import networkx as nx

class Node:
    def __init__(self, index, name):
        self.index = index
        self.name = name
        self.edges = [] # all edges connected to this node
        self.edges_in = [] # only edges pointing towards node
        self.edges_out = [] # only edges pointing away from node
        self.relatives = [] # all neighbours
        self.parents = [] # only neighbours from incoming edges (arrow pointing towards node)
        self.children = [] # only neighbours from outgoing edges (arrow pointing away from node)

        # used for dijkstra
        self.pi = None 
        self.d = None

    def add_edge(self, edge):
        self.edges.append(edge)
        if(edge.node_from == self): 
            self.edges_out.append(edge)
            if(edge.node_to not in self.children):
                self.children.append(edge.node_to)
        if(edge.node_to == self):
            self.edges_in.append(edge)
            if(edge.node_from not in self.parents):
                self.parents.append(edge.node_from)
        if(edge.node_from != self and edge.node_from not in self.relatives):
            self.relatives.append(edge.node_from)
        if(edge.node_to != self and edge.node_to not in self.relatives):
            self.relatives.append(edge.node_to)        

    def __str__(self):
        return f"Node(index={self.index}, name={self.name})"

class Edge:
    def __init__(self, node_from, node_to, weight):
        self.node_from = node_from
        self.node_to = node_to
        self.weight = weight
        self.name = Edge.to_name(node_from.name, node_to.name)
    def __str__(self):
        return f"Edge(from={self.node_from.name}, to={self.node_to.name}, weight={self.weight})"
    @staticmethod
    def to_name(n1, n2):
        return f"{n1};{n2}"

class Graph:
    def __init__(self):
        self.matrix = None # weight matrix
        self.nodes = []
        self.edges = []
        self.name_to_node = {}
        self.name_to_edge = {}
        self.verbose = False

    def get_node(self, name):
        return self.name_to_node[name]
    
    def get_edge(self, n1, n2):
        name = Edge.to_name(n1, n2)
        return self.name_to_edge[name]

    def add_node(self, name):
        if(name in self.name_to_node):
            return
        node = Node(len(self.nodes), name)
        self.nodes.append(node)
        self.name_to_node[name] = node
        if(self.verbose):
            print(f"node added: {node}")

    def add_edge(self, from_node, to_node, weight=1, bi=False):
        n1 = self.name_to_node[from_node]
        n2 = self.name_to_node[to_node]
        edge = Edge(n1, n2, weight)
        assert edge.name not in self.name_to_edge
        self.edges.append(edge)
        self.name_to_edge[edge.name] = edge
        n1.add_edge(edge)
        n2.add_edge(edge)
        if(self.verbose):
            print(f"edge added: {edge}")
        if(bi):
            edge = Edge(n2, n1, weight)
            assert edge.name not in self.name_to_edge
            self.edges.append(edge)
            self.name_to_edge[edge.name] = edge
            n1.add_edge(edge)
            n2.add_edge(edge)
            if(self.verbose):
                print(f"edge added: {edge}")

    def build_matrix(self):
        n = len(self.nodes)
        matrix = np.full((n,n), np.nan, dtype=float)
        for edge in self.edges:
            i_from = edge.node_from.index
            i_to = edge.node_to.index
            matrix[i_from, i_to] = edge.weight
        self.matrix = matrix

    def from_matrix(self, node_names:list, weight_matrix):
        weight_matrix = np.array(weight_matrix, dtype=float)
        n = len(node_names)
        assert n == weight_matrix.shape[0]
        assert n == weight_matrix.shape[1]
        # create nodes
        for i in range(n):
            for j in range(n):
                weight = weight_matrix[i,j]
                if(not np.isnan(weight)):
                    name_from = node_names[i]
                    name_to = node_names[j]
                    self.add_node(name_from)
                    self.add_node(name_to)
        # create edges
        for i in range(n):
            for j in range(n):
                weight = weight_matrix[i,j]
                if(not np.isnan(weight)):
                    name_from = node_names[i]
                    name_to = node_names[j]
                    self.add_edge(name_from, name_to, weight)
        # build weight matrix
        self.build_matrix()

    def draw(self, size=None, path=None):
        if(size is not None):
            plt.rcParams['figure.figsize'] = size
        
        G = nx.DiGraph()

        nodes = []
        for node in self.nodes:
            nodes.append(node.name)

        edges = []
        for edge in self.edges:
            n1 = edge.node_from.name
            n2 = edge.node_to.name
            weight = edge.weight
            edges.append((n1, n2, weight))
            
        G.add_nodes_from(nodes)
        G.add_weighted_edges_from(edges)
           
        edge_labels = {e: str(G.get_edge_data(*e)["weight"]) for e in G.edges}

        layout = nx.planar_layout(G)

        fig, ax = plt.subplots()
        nx.draw(G, ax=ax, with_labels=True, font_weight='bold', pos=layout, node_color="lightblue")
        if(path is not None):    
            path_edges = []
            for i in range(len(path)-1):
                n1 = path[i]
                n2 = path[i+1]
                path_edges.append((n1.name, n2.name))
            nx.draw_networkx_edges(G, ax=ax, pos=layout, edgelist=path_edges, edge_color="red", width=2)
        nx.draw_networkx_edge_labels(G, ax=ax, pos=layout, edge_labels=edge_labels, font_size=10)
        plt.show()

    def dijkstra(self, source, target, verbose=False):
        path = []

        for node in self.nodes:
            node.d = float("inf")
            node.pi = None

        source_node = self.name_to_node[source]
        source_node.d = 0.0
        
        Q = [node for node in self.nodes]

        def extract_min(Q):
            min_node = None
            min_d = float("inf")
            for node in Q:
                if(node.d < min_d):
                    min_d = node.d
                    min_node = node
            return min_node

        def print_nodes():
            for node in self.nodes:
                pi = node.pi.name if node.pi is not None else "None"
                print(f"{node}, d={node.d}, pi={pi}")

        it = 1
        while len(Q) > 0:
            u = extract_min(Q)
            Q.remove(u)

            for v in u.children:
                if(v not in Q):
                    continue
                alt = u.d + self.matrix[u.index, v.index]
                if alt < v.d:
                    v.d = alt
                    v.pi = u

            if(verbose):
                print(f"after iteration #{it}")
                print(f"u: {u}")
                print_nodes()

            it += 1


        S = []
        u = self.name_to_node[target]
        if u.pi is not None or u == source_node:
            while u is not None:
                S.append(u)
                u = u.pi

        return list(reversed(S))