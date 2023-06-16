import MyAlgUtils
import MyGraph
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

class TSP:
    def __init__(self):
        self.graph : MyGraph.Graph = None
        self.matrix = None

    def from_text(self, node_names, txt:str):
        txt = txt.replace("-", "nan")
        matrix = MyAlgUtils.table_to_np(txt, dtype=float)
        self.from_matrix(node_names, matrix)

    def from_matrix(self, node_names, matrix):
        self.graph = MyGraph.Graph()
        self.graph.from_matrix(node_names, matrix)
        self.compile()

    def compile(self):
        self.graph.build_matrix()

    def get_matrix(self):
        return self.graph.matrix

    def compute_cost(self, tour):
        c = 0
        for i in range(1, len(tour)):
            n1 = self.index_to_name(tour[i-1])
            n2 = self.index_to_name(tour[i]) 
            edge = self.graph.get_edge(n1, n2)
            c += edge.weight
        return c
    
    def name_to_index(self, name):
        if(type(name) is list or type(name) == tuple):
            indices = []
            for i in range(len(name)):
                indices[i].append(self.graph.get_node(name[i]).index)
            return indices
        return self.graph.get_node(name).index
    
    def index_to_name(self, index):
        if(type(index) is list or type(index) is np.ndarray or type(index) == tuple):
            names = []
            for i in range(len(index)):
                names.append(self.graph.nodes[index[i]].name)
            return names
        return self.graph.nodes[index].name
    
    def tour_to_pairs(self, tour):
        pairs = []
        for i in range(0, len(tour)-1):
            a = tour[i]
            b = tour[i+1]
            pair = (a, b)
            pairs.append(pair)
        return pairs

    def print_tour(self, tour):
        matrix = self.get_matrix()
        tour = np.array(tour)
        pairs = self.tour_to_pairs(tour)
        cost = 0
        print(f"tour (index) -> {tour}")
        print(f"tour (names) -> {self.index_to_name(tour)}")
        for pair in pairs:
            a = self.index_to_name(pair[0])
            b = self.index_to_name(pair[1])
            u = pair[0]
            v = pair[1]
            c = matrix[pair[0],pair[1]]
            print(f"index({u} -> {v}) | name({a} -> {b}) | cost is {c}")
            cost += c
        print(f"total cost is {cost}")
    
    def find_nearest(self, idx, mat):
        vec = mat[idx,:].reshape(mat.shape[0])
        return np.where(vec==np.min(vec[~np.isnan(vec)]))[0]
    
    def distance(self, a, b):
        return self.get_matrix[a,b]
                
    def search_nearest(self, start, complete, mat=None):
        tour = [start]
        M = np.copy(self.get_matrix() if mat is None else mat)
        M[:,start] = np.nan
        curr = start
        while np.count_nonzero(~np.isnan(M)) > 0:
            curr = self.find_nearest(curr, mat=M)[0]
            tour.append(curr)
            M[:,curr] = np.nan
        if(complete):
            tour.append(start)
        return tour
    
    def search_pilot(self, start, complete, mat=None):
        
        M = np.copy(self.get_matrix() if mat is None else mat)
        M[:,start] = 0

        index = {i: True for i in range(M.shape[0])}
        tour = [start]
        index.pop(start)
        keys = list(index.keys())

        while len(keys) > 0:
            
            cost = self.compute_cost(tour)
            print(f"current tour: i={tour}, n={self.index_to_name(tour)}, cost={cost}")
            
            print(f"looking for best point out of {keys}")

            c_min = None
            c_best = None
            for s in keys:
                t = self.search_nearest(start=s, complete=False, mat=M)
                if(complete):
                    t.append(start)
                c = self.compute_cost(t)
                print(f"s={s}, i={t}, n={self.index_to_name(t)}, c={c}")
                if(c_min is None or c < c_min):
                    c_min = c
                    c_best = s
            
            print(f"best is s={s}")
            
            tour.append(c_best)
            index.pop(c_best)
            M[:,c_best] = 0
            
            keys = list(index.keys())
        
        if(complete):
            tour.append(start)

        return tour
    
    def exhaustive_tours(self, index, start, k, complete):

        index.pop(start)
        tours = []

        def ex(k, index, t):
            k -= 1
            if(k >= 0 and len(index.keys()) > 0):
                for i in index.keys():
                    ic = index.copy()
                    ic.pop(i)
                    tc = t.copy()
                    tc.append(i)
                    ex(k, ic, tc)
            else:
                tc = t.copy()
                if(complete):
                    tc.append(start)
                tours.append(tc)
        
        ex(k, index, [start])

        return tours
        

    def exhaustive_search(self, start, k, complete, mat=None):

        if(mat is None):
            mat = self.get_matrix()

        index = {}
        index = {i: True for i in range(mat.shape[0])}
        tours = self.exhaustive_tours(index, start, k, complete=complete)

        print(f"searching through {len(tours)} tours")

        min_cost = None
        min_idx = None
        for i, tour in enumerate(tours):
            c = self.compute_cost(tour)
            if(min_cost is None or c < min_cost):
                min_idx = i
                min_cost = c

        return tours[min_idx]
