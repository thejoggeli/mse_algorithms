import numpy as np
import matplotlib
import matplotlib.pyplot as plt

class BinaryTree:
    def __init__(self):
        self.root = None
        self.depth = 0
        self.next_idx = 1

    def get_next_idx(self):
        idx = self.next_idx
        self.next_idx += 1
        return idx

    def build(self, values:list):
        
        values = values.copy()

        idx = self.get_next_idx()
        root = BinaryTreeNode(idx, parent=None, val=values.pop(0))

        nodes = [root]

        while len(values) > 0:

            parent = nodes.pop(0)

            val = values.pop(0)
            if(val is not None):
                idx = self.get_next_idx()
                parent.left = BinaryTreeNode(idx, parent=parent, val=val)
                nodes.append(parent.left)

            if(len(values) == 0):
                break

            val = values.pop(0)
            if(val is not None):
                self.get_next_idx()
                parent.right = BinaryTreeNode(idx, parent=parent, val=val)
                nodes.append(parent.right)

        self.root = root

        self.recompute_depth()

    def find_depth(self):
        depth = [0]
        def fd_inner(node, depth):
            depth[0] = max(node.depth, depth[0])
            if(node.left is not None):
                fd_inner(node.left, depth)
            if(node.right is not None):
                fd_inner(node.right, depth)
        fd_inner(self.root, depth)
        self.depth = depth[0]

    def plot(self, ax, root=None):

        if(root is None):
            root = self.root

        depth = self.depth
        levels = [[] for i in range(depth)]
        def gen_levels(node):
            if(node is None):
                return
            level = node.depth-1
            levels[level].append(node)
            gen_levels(node.left)
            gen_levels(node.right)
        gen_levels(root)

        width = depth**2
        height = (depth+1)

        for i, level in enumerate(levels):

            w = width/2

            for j, node in enumerate(levels[i]):
                x = node.pos[0]*w
                y = (node.pos[1]+1)
                label = str(node.val)
                ax.text(x, y, label, ha="center", va="center", backgroundcolor="white")

                if(node.parent is not None):
                    px = node.parent.pos[0]*w
                    py = (node.parent.pos[1]+1)
                    ax.plot([x, px], [y, py], color="gray")

        ax.set_xlim(-width*1.1/2, width*1.1/2)
        ax.set_ylim(height-0.5, 0.5)

        ax.set_yticks(np.arange(1, depth+1))
        ax.set_xticks([])

        ax.grid(True)


    def draw(self, root=None):
        fig, ax = plt.subplots()
        self.plot(ax, root)
        plt.show()
    
    def transplant(self, u, v):
        if(u.parent is None):
            self.root = v
        elif(u == u.parent.left):
            u.parent.left = v
        else:
            u.parent.right = v
        if(v is not None):
            v.parent = u.parent

    def insert(self, val):

        idx = self.get_next_idx()
        z = BinaryTreeNode(idx, None, val)
        y = None
        x = self.root
        while x is not None:
            y = x
            if z.val < x.val:
                x = x.left
            else:
                x = x.right
        z.parent = y
        if y is None:
            self.root = z
        elif z.val < y.val:
            y.left = z
        else:
            y.right = z
        self.recompute_depth()

        return z
                           
    def delete(self, z):
        if(z.left is None):
            self.transplant(z, z.right)
        elif(z.right is None):
            self.transplant(z, z.left)
        else:
            y = self.minimum(z.right)
            if(y.parent != z):
                self.transplant(y, y.right)
                y.right = z.right
                y.right.parent = y
            self.transplant(z, y)
            y.left = z.left
            y.left.parent = y
            
        self.recompute_depth()

    def minimum(self, root=None):

        if(root is None):
            root = self.root

        result = [None]
        def min_inner(node):
            if(result[0] is None or node.val < result[0].val):
                result[0] = node
            if(node.left is not None):
                min_inner(node.left)
            if(node.right is not None):
                min_inner(node.right)
        min_inner(root)
        
        return result[0]

    def maximum(self, root=None):

        if(root is None):
            root = self.root

        result = [None]
        def max_inner(node):
            if(result[0] is None or node.val > result[0].val):
                result[0] = node
            if(node.left is not None):
                max_inner(node.left)
            if(node.right is not None):
                max_inner(node.right)
        max_inner(root)
        
        return result[0]

    def find(self, value):

        def find_inner(node):
            if(node.val == value):
                return node
            if(node.left is not None):
                r = find_inner(node.left)
                if(r is not None):
                    return r
            if(node.right is not None):
                r = find_inner(node.right)
                if(r is not None):
                    return r
            return None
        
        result = find_inner(self.root)
        
        return result
    
    def recompute_depth(self):

        def cd_inner(node, depth, pos):

            node.depth = depth
            node.pos = pos
            
            if(node.left is not None):
                pos_left = (pos[0]-1.0/(2**depth), pos[1]+1)
                cd_inner(node.left, depth+1, pos_left)
            
            if(node.right is not None):
                pos_right = (pos[0]+1.0/(2**depth), pos[1]+1)
                cd_inner(node.right, depth+1, pos_right)
        
        cd_inner(self.root, depth=1, pos=(0,0))
        
        self.find_depth()

class BinaryTreeNode:
    def __init__(self, idx, parent, val):
        self.idx = idx
        self.depth = None
        self.parent = parent
        self.left = None
        self.right = None
        self.val = val
        self.pos = None

    def __str__(self):
        return f"idx={self.idx}, depth={self.depth}, val={self.val}"