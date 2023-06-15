import MyAlgUtils
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

class PathPoint:
    def __init__(self, step, index, name, desc, value):
        self.step = step
        self.index = index
        self.name = name
        self.desc = desc
        self.value = value

    def __str__(self):
        return str({
            "step": self.step,
            "index": self.index,
            "name": self.name,
            "desc": self.desc,
            "value": self.value,   
        })

class OptimizGrid:

    def __init__(self, dtype=np.int64):
        self.grid = []
        self.dtype = dtype
        self.dirs = None
        self.x_names = None
        self.y_names = None
        self.i2n_x = None
        self.i2n_y = None
        self.n2i_x = None
        self.n2i_y = None
        self.allow_diagonal(False)

    def allow_diagonal(self, allow):
        if(allow):
            self.dirs = [
                ( 0, -1, "left"),
                (+1, -1, "down-left"),
                (+1,  0, "down"), 
                (+1, +1, "down-right"), 
                ( 0, +1, "right"),
                (-1, +1, "up-right"),
                (-1  ,0, "up"),
                (-1, -1, "up-left"),
            ]
        else:
            self.dirs = [
                ( 0, -1, "left"),
                (+1,  0, "down"),  
                ( 0, +1, "right"),
                (-1  ,0, "up"),
            ]

    def build_from_text(self, txt):
        self.grid = MyAlgUtils.table_to_np(txt, dtype=self.dtype)
        self.set_index_names(
            x=np.arange(0, self.grid.shape[0]),
            y=np.arange(0, self.grid.shape[1]),
        )

    def set_index_names(self, x, y):
        self.i2n_x = x
        self.i2n_y = y
        self.n2i_x = {x[i]: i for i in range(len(x))}
        self.n2i_y = {y[i]: i for i in range(len(y))}

    def name_to_index(self, x, y):
        return (self.n2i_x[x], self.n2i_y[y])
    
    def index_to_name(self, x, y):
        return (self.i2n_x[x], self.i2n_y[y])

    def local_search(self, start=(0,0)):

        grid = self.grid
        step = 0
        x = start[0]
        y = start[1]
        val = grid[x,y]
        dirs = self.dirs
        
        path = [PathPoint(
            step=step,
            index=(x, y),
            name=self.index_to_name(x, y),
            desc="start",
            value=val,   
        )]

        while True:
            step += 1
            best_found = False
            best_val = val
            best_x = None
            best_y = None
            best_name = None
            for dir in dirs:

                # test if position is inside space boundaries
                xn = x+dir[0]
                yn = y+dir[1]
                if(xn < 0 or xn >= grid.shape[0] or yn < 0 or yn >= grid.shape[1]):
                    continue

                # test if value is better than previous best value
                if(grid[xn,yn] < best_val):
                    best_x = xn
                    best_y = yn
                    best_found = True
                    best_val = grid[xn,yn]
                    best_name = dir[2]

            # stop if no better value was found in all directions
            if(not best_found):
                break

            # store current step
            x = best_x
            y = best_y
            val = best_val
            path.append(PathPoint(
                step=step,
                index=(x, y),
                name=self.index_to_name(x, y),
                desc=best_name,
                value=val,   
            ))

        return path
    
    def tabu_search(self, start=(0,0)):
        return []

    def draw(self, path=None):

        fig, ax = plt.subplots()

        vmin = np.amin(self.grid)
        vmax = np.amax(self.grid)
        vr = vmax-vmin

        ax.imshow(self.grid, cmap="Blues", vmin=vmin-vr*0.1, vmax=vmax+vr*0.1)
        ax.set_xticks(np.arange(0, self.grid.shape[0]), self.i2n_x, fontsize=9)
        ax.set_yticks(np.arange(0, self.grid.shape[1]), self.i2n_y, fontsize=9)

        if(path is not None):
            m = np.full_like(self.grid, np.nan, dtype=float)
            v = np.linspace(0.7, 0.3, len(path))
            for i, p in enumerate(path):
                m[p.index[0], p.index[1]] = v[i]
            ax.imshow(m, cmap="Reds", vmin=0, vmax=1)


        for (j,i),label in np.ndenumerate(self.grid):
            ax.text(i,j,label,ha='center',va='center', color="black", fontsize=9)

        plt.show()