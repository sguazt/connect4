# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
#
# Copyright 2015 Marco Guazzone (marco.guazzone@gmail.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class Stack:
    """
    A LIFO container data structure.
    """
    def __init__(self):
        self.data = []

    def push(self, x):
        self.data.append(x)

    def pop(self):
        return self.data.pop()

    def top(self):
        return self.data[-1]


class Matrix:
    """
    A 2-dimensional array of objects backed by a list of lists.
    Data is accessed via matrix[x][y] where (r,c) denotes the rth row and cth
    column of the matrix.
    """
    def __init__(self, nrows, ncols, value=None):
        """
        Constructs a (nrows x ncols) matrix filled by the given value.
        """
        self.nr = nrows
        self.nc = nc
        self.data = [[value for c in range(ncols)] for y in range(nrows)]

    def __getitem__(self, i):
        return self.data[i]

    def __setitem__(self, r, x):
        self.data[r] = x

    def __str__(self):
        out = [[str(self.data[r][c])[0] for c in range(self.nc)] for r in range(self.nr)]
        out.reverse()
        return '\n'.join([''.join(x) for x in out])

    def __eq__(self, other):
        if other == None:
            return False
        return self.data == other.data

    def __hash__(self):
        # return hash(str(self))
        base = 1
        h = 0
        for l in self.data:
            for i in l:
                if i:
                    h += base
                base *= 2
        return hash(h)

    def num_rows(self):
        return self.nr

    def num_columns(self):
        return self.nc

    def size(self):
        return self.nr*self.nc

    def copy(self):
        m = Matrix(self.nr, self.nc)
        m.data = [c[:] for c in self.data]
        return m

    def deep_copy(self):
        return self.copy()

    def shallow_copy(self):
        m = Matrix(self.nr, self.nc)
        m.data = self.data
        return m

    def count(self, value):
        return sum([x.count(value) for x in self.data])


class Grid:
    """
    A 2-dimensional array of objects backed by a list of lists.
    Data is accessed via grid[x][y] where (x,y) are positions on the game board
    with x horizontal, y vertical and the origin (0,0) in the bottom left
    corner.

    The __str__ method constructs an output that is oriented like a game board.
    """
    def __init__(self, width, height, init_value):
        self.w = width
        self.h = height
        self.data = [[init_value for y in range(height)] for x in range(width)]

    def __getitem__(self, i):
        return self.data[i]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __str__(self):
        out = [[str(self.data[x][y]) for y in range(self.height())] for x in range(self.width())]
        #out.reverse()
        return '\n'.join([' '.join(x) for x in out])

    def __eq__(self, other):
        if other == None:
            return False
        return self.data == other.data

    def __hash__(self):
        # return hash(str(self))
        base = 1
        h = 0
        for l in self.data:
            for i in l:
                if i:
                    h += base
                base *= 2
        return hash(h)

    def height(self):
        return self.h

    def width(self):
        return self.w

    def size(self):
        return self.w*self.h

    def copy(self):
        g = Grid(self.w, self.h)
        g.data = [x[:] for x in self.data]
        return g

    def deep_copy(self):
        return self.copy()

    def shallow_copy(self):
        g = Grid(self.w, self.h)
        g.data = self.data
        return g

    def count(self, value):
        return sum([x.count(value) for x in self.data])

    def get_cells(self, value):
        """
        Returns a list of the grid positions containing the given value.
        """
        lst = []
        for x in range(self.w):
            for y in range(self.h):
                if self[x][y] == value:
                    lst.append((x,y))
        return lst
