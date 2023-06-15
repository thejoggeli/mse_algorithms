import numpy as np
import matplotlib
import matplotlib.pyplot as plt

class SplitNode:
    def __init__(self, depth, parent, L, pos):
        self.is_leaf = False
        self.depth = depth
        self.parent = parent
        self.left = None
        self.right = None
        self.L = L
        self.pos = pos

    def __str__(self):
        s = f"depth={self.depth}, L={self.L}"
        return s
    
class LeafNode:
    def __init__(self, depth, parent, P, pos):
        self.is_leaf = True
        self.depth = depth
        self.parent = parent
        self.P = P
        self.pos = pos

    def __str__(self):
        s = f"depth={self.depth}, P={self.P}"
        return s

class Point:

    def __init__(self, index, x, y):
        self.index = index
        self.number = index+1
        self.x = x
        self.y = y

    def __getitem__(self, key):
        if(key == "x"):
            return self.x
        if(key == "y"):
            return self.y
        raise KeyError()
    
    def __str__(self):
        return f"Point(index={self.index}, number={self.number}, x={self.x}, y={self.y})"

class KDTree:

    def __init__(self):
        self.points = []
        self.root = None
        self.depth = 0

    def find_depth(self):
        self.depth = 0
        def fd_inner(node):
            if(node.is_leaf):
                self.depth = max(node.depth, self.depth)
            else:
                fd_inner(node.left)
                fd_inner(node.right)
        fd_inner(self.root)

    def add_point(self, x, y):
        index = len(self.points)
        p = Point(index, x, y)
        self.points.append(p)

    def build(self, split_between=True):
        
        def build_kd(P, depth, parent, pos):

            if(len(P) == 1):
                return LeafNode(depth, parent, P[0], pos)
            if(depth%2 == 0):
                key = "y"
            else:
                key = "x"
            P = sorted(P, key=lambda P: P[key])
            if(len(P)%2 == 0):
                s = len(P)//2
            else:
                s = len(P)//2+1
            if(split_between):
                L = (P[s-1][key] + P[s][key]) * 0.5 # lines between points
            else:
                L = P[s-1][key] # lines on points
            P1 = P[:s]
            P2 = P[s:]
            v = SplitNode(depth, parent, L, pos)
            v.left = build_kd(P1, depth+1, v, pos=(pos[0]-1.0/(2**depth), pos[1]+1))
            v.right = build_kd(P2, depth+1, v, pos=(pos[0]+1.0/(2**depth), pos[1]+1))
            return v
        
        self.root = build_kd(self.points, depth=1, parent=None, pos=(0,0))

        self.find_depth()

    def print(self):
        def print_tree(node):
            if(node is None):
                return
            print(node)
            if(not node.is_leaf):
                print_tree(node.left)
                print_tree(node.right)
        print_tree(self.root)

    def draw_split(self):
        fig, ax = plt.subplots()

        xv = [point.x for point in self.points]
        yv = [point.y for point in self.points]

        x_min = np.amin(xv)-2
        x_max = np.amax(xv)+2
        y_min = np.amin(yv)-2
        y_max = np.amax(yv)+2

        colors = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple"]

        def draw_split_inner(node, x_min, y_min, x_max, y_max):
            if(node is None or node.is_leaf):
                return
            if(node.depth%2 == 1):
                ax.plot([node.L, node.L], [y_min, y_max], color="gray")
                draw_split_inner(node.left,  x_min, y_min, node.L, y_max)
                draw_split_inner(node.right, node.L, y_min, x_max, y_max)
            else:
                ax.plot([x_min, x_max], [node.L, node.L], color="gray")
                draw_split_inner(node.left,  x_min, y_min, x_max, node.L)
                draw_split_inner(node.right, x_min, node.L, x_max, y_max)

        draw_split_inner(self.root, x_min, y_min, x_max, y_max)

        cmap = matplotlib.colormaps['hsv']
        colors = cmap(np.linspace(0, 1.0, len(self.points), endpoint=False))

        for j, point in enumerate(self.points):
            label = str(point.number)
            ax.scatter(point.x, point.y, label=label, color=colors[j])
            ax.text(xv[j]+0.4, yv[j]+0.4, label)

        ax.plot([x_min, x_max], [y_min, y_min], color="gray")
        ax.plot([x_min, x_max], [y_max, y_max], color="gray")
        ax.plot([x_min, x_min], [y_min, y_max], color="gray")
        ax.plot([x_max, x_max], [y_min, y_max], color="gray")

        ax.set_xlim(x_min-3, x_max+3)
        ax.set_ylim(y_min-3, y_max+3)

        ax.grid(True)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        # ax.legend()

        plt.show()
    
    def draw_tree(self):

        levels = [[] for i in range(self.depth)]

        def gen_levels(node):
            if(node is None):
                return
            level = node.depth-1
            levels[level].append(node)
            if(not node.is_leaf):
                gen_levels(node.left)
                gen_levels(node.right)

        gen_levels(self.root)

        fig, ax = plt.subplots()

        width = self.depth**2
        height = (self.depth+1)

        for i, level in enumerate(levels):

            w = width/2

            for j, node in enumerate(levels[i]):
                x = node.pos[0]*w
                y = (node.pos[1]+1)
                if(node.is_leaf):
                    label = str(node.P.number) + "\n" + str((node.P.x, node.P.y))
                    ax.text(x, y, label, ha="center", va="center", color="red", backgroundcolor="white", fontsize=8)
                else:
                    if(node.depth%2 == 0):
                        key = "y"
                    else:
                        key = "x"
                    label = f"{key}({node.L})"
                    ax.text(x, y, label, ha="center", va="center", backgroundcolor="white")

                if(node.parent is not None):
                    px = node.parent.pos[0]*w
                    py = (node.parent.pos[1]+1)
                    ax.plot([x, px], [y, py], color="gray")

            # print(len(level))

        ax.set_xlim(-width*1.1/2, width*1.1/2)
        ax.set_ylim(height-0.5, 0.5)

        ax.set_yticks(np.arange(1, self.depth+1))
        ax.set_xticks([])

        ax.grid(True)

        plt.show()


