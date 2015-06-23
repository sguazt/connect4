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


import copy
import upo.containers


class GridBoard:
    """
    Represents a board for the Connect 4 game using a grid-like data structure.

    From the user point of view a board is a WxH grid with width W and height H.
    Each cell of the grid has a coordinate (x,y), where x grows from left to
    right (starting from 0 until W-1) and y grows from bottom to up (starting from 0 until H-1).
    For instance, a 7x6 board can be depicted as follows:
        (0,0)         (6,0)
        |-|-|-|-|-|-|-|
        | | | | | | | |
        |-|-|-|-|-|-|-|
        | | | | | | | |
        |-|-|-|-|-|-|-|
        | | | | | | | |
        |-|-|-|-|-|-|-|
        | | | | | | | |
        |-|-|-|-|-|-|-|
        | | | | | | | |
        |-|-|-|-|-|-|-|
        | | | | | | | |
        |-|-|-|-|-|-|-|
        (0,5)         (6,5)
    """

    INVALID_TOKEN = None

    def __init__(self, width, height):
        self.data = upo.containers.Grid(width, height, self.INVALID_TOKEN)

    def copy(self):
        """
        Creates an deep copy of this board.
        """
        b = Board(self.w, self.h)
        b.data = self.data.copy()
        return b

    def deep_copy(self):
        """
        Creates an deep copy of this board.
        Same as the copy method.
        """
        return self.copy()

    def shallow_copy(self):
        """
        Creates a shallow (alias) copy of this board.
        """
        b = Board(self.w, self.h)
        b.data = self.data
        return b

    def can_push_token(self, column):
        """
        Tells if a token can be pushed down to the given column.
        """
        if self.data[column][0] == self.INVALID_TOKEN:
            return True
        return False

    def push_token(self, token, column):
        """
        Push the given token down to the given column, if possible.
        Returns the row where the token has been pushed, or None, otherwise.
        """
        row = self.to_impl_row(self.get_column_empty_row(column))
        if row != -1:
            self.data[column][row] = token
        return self.to_user_row(row)

    def pop_token(self, column):
        """
        Pop the token on top of the given column, if possible.
        Returns the popped token (if present), or INVALID_TOKEN, otherwise.
        """
        token = self.INVALID_TOKEN
        row = self.to_impl_row(self.get_column_empty_row(column))
        if row != -1:
            token = self.data[column][row]
            self.data[column][row] = self.INVALID_TOKEN
        return token

    def get_token(self, column, row):
        """
        Returns the token stored in (column,row) position of the board.
        """
        return self.data[column][self.to_impl_row(row)]

    def has_token(self, column, row):
        """
        Tells if the (column,row) position of the board contains a valid token.
        """
        return self.data[column][self.to_impl_row(row)] != self.INVALID_TOKEN

    def get_column_empty_row(self, column):
        """
        Returns the deepest row in the given column that can store a token, if
        any; otherwise, returns -1.
        """
        for y in range(self.data.height()-1, -1, -1):
            if self.data[column][y] == self.INVALID_TOKEN:
                return self.to_user_row(y)
        return -1

    def width(self):
        """
        Returns the width of the board.
        """
        return self.data.width()

    def height(self):
        """
        Returns the height of the board.
        """
        return self.data.height()

    def num_column_tokens(self, column):
        """
        Get the number of tokens pushed in the given column.
        """
        return self.data.height() - self.to_impl_row(self.get_column_empty_row(column)) + 1

    def is_column_full(self, column):
        """
        Tells if the given column is full of tokens.
        """
        return self.data[column][0] != self.INVALID_TOKEN

    def is_full(self):
        """
        Tells if this board is full of tokens.
        """
        for c in range(self.data.width()):
            if not self.is_column_full(c):
                return False
        return True

    def is_column_empty(self, column):
        """
        Tells if the given column is empty.
        """
        return self.data[column].count(self.INVALID_TOKEN) == self.height()

    def is_empty(self):
        """
        Tells if this board has no token
        """
        for c in range(self.data.width()):
            if not self.is_column_empty(c):
                return False
        return True

    def clear(self):
        """
        Clears the whole board.
        """
        self.data = upo.containers.Grid(self.data.width(), self.data.height(), self.INVALID_TOKEN)

    def __str__(self):
        """
        Creates a string representation of this board.
        """
        # Compute
        w = -1
        for x in range(self.width()):
            for y in range(self.height()):
                if self.data[x][y] != None:
                    w = max(w, len(str(self.data[x][y])))
                else:
                    w = max(w, 4)
        out = [['{:>{width}}'.format(str(self.data[x][y]), width=w) for x in range(self.width())] for y in range(self.height())]
        #for x in out:
        #    print('Inspect: ', x)
        #    print('Reverse: ', x.reverse())
        return '\n'.join([' '.join(x) for x in out])

    def to_user_row(self, impl_row):
        """
        Transforms the given row from internal representation to user
        representation.
        """
        if impl_row < 0:
            return -1
        return impl_row

    def to_impl_row(self, user_row):
        """
        Transforms the given row from user representation to internal
        representation.
        """
        if user_row < 0:
            return -1
        return user_row


################################################################################


class StackBoard:
    """
    Represents a board for the Connect 4 game using a stack-like data structure.

    From the user point of view a board is a WxH grid with width W and height H.
    Each cell of the grid has a coordinate (x,y), where x grows from left to
    right (starting from 0 until W-1) and y grows from bottom to up (starting from 0 until H-1).
    For instance, a 7x6 board can be depicted as follows:
        (0,0)         (6,0)
        |-|-|-|-|-|-|-|
        | | | | | | | |
        |-|-|-|-|-|-|-|
        | | | | | | | |
        |-|-|-|-|-|-|-|
        | | | | | | | |
        |-|-|-|-|-|-|-|
        | | | | | | | |
        |-|-|-|-|-|-|-|
        | | | | | | | |
        |-|-|-|-|-|-|-|
        | | | | | | | |
        |-|-|-|-|-|-|-|
        (0,5)         (6,5)
    """

    INVALID_TOKEN = None

    def __init__(self, width, height):
        #self.data = [[]]*width
        self.data = [[] for i in range(width)]
        self.w = width
        self.h = height

    def copy(self):
        """
        Creates an deep copy of this board.
        """
        b = Board(self.w, self.h)
        b.data = [x[:] for x in self.data]
        return b

    def deep_copy(self):
        """
        Creates an deep copy of this board.
        Same as the copy method.
        """
        return self.copy()

    def shallow_copy(self):
        """
        Creates a shallow (alias) copy of this board.
        """
        b = Board(self.w, self.h)
        b.data = self.data
        return b

    def can_push_token(self, column):
        """
        Tells if a token can be pushed down to the given column.
        """
        if len(self.data[column]) < self.h:
            return True
        return False

    def push_token(self, token, column):
        """
        Push the given token down to the given column, if possible.
        Returns the row where the token has been pushed, on success; otherwise,
        returns -1.
        """
        row = len(self.data[column])
        if row >= self.h:
            return -1
        self.data[column].append(token)
        return self.to_user_row(row)

    def pop_token(self, column):
        """
        Pop the token on top of the given column, if possible.
        Returns the token stored on the top of the column, if present;
        otherwise, returns INVALID_TOKEN.
        """
        if len(self.data[column]) == 0:
            return self.INVALID_TOKEN
        return self.data[column].pop()

    def get_token(self, column, row):
        """
        Returns the token stored in (column,row) position of the board, if
        present; otherwise, returns INVALID_TOKEN.
        """
        impl_row = self.to_impl_row(row)
        if impl_row >= len(self.data[column]):
            return self.INVALID_TOKEN
        return self.data[column][impl_row]

    def has_token(self, column, row):
        """
        Tells if the (column,row) position of the board contains a valid token.
        """
        impl_row = self.to_impl_row(row)
        if impl_row < len(self.data[column]):
            return True
        return False

    def get_column_empty_row(self, column):
        """
        Returns the first row of the given column where it is possible to store
        a token, if any; otherwise, returns -1.
        """
        row = len(self.data[column])
        if row >= self.h:
            return -1
        return self.to_user_row(row)

    def width(self):
        """
        Returns the width of the board.
        """
        return self.w

    def height(self):
        """
        Returns the height of the board.
        """
        return self.h

    def num_column_tokens(self, column):
        """
        Get the number of tokens pushed in the given column.
        """
        return len(self.data[column])

    def is_column_full(self, column):
        """
        Tells if the given column is full of tokens.
        """
        return len(self.data[column]) == self.h

    def is_full(self):
        """
        Tells if this board is full of tokens.
        """
        for c in range(self.w):
            if not self.is_column_full(c):
                return False
        return True

    def is_column_empty(self, column):
        """
        Tells if the given column is empty.
        """
        return len(self.data[column]) == 0

    def is_empty(self):
        """
        Tells if this board has no token
        """
        for c in range(self.w):
            if not self.is_column_empty(c):
                return False
        return True

    def clear(self):
        """
        Clears the whole board.
        """
        #self.data = [[]]*self.w
        self.data = [[] for i in range(self.w)]

    def __str__(self):
        """
        Creates a string representation of this board.
        """
        #return str(self.data)
        w = -1
        for x in range(self.w):
            for y in range(self.h):
                elem_len = 1
                if self.has_token(x, y):
                    elem_len = len(str(self.get_token(x, y)))
                w = max(w, elem_len)
        out = [['{:>{width}}'.format(str(self.get_token(x,y) if self.has_token(x,y) else ' '), width=w) for x in range(self.w)] for y in range(self.h)]
        s = ''
        for x in out:
            s += '\n['
            s += ' '.join(x)
            s += ']'
        #s =  '\n['.join([' '.join(x)+']' for x in out])
        s += '\n-' + '--'*w*self.w
        s += '\n ' + ' '.join(['{:>{width}}'.format(x, width=w) for x in range(self.w)]) + '\n'
        return s


    def to_user_row(self, impl_row):
        """
        Transforms the given row from internal representation to user
        representation.
        """
        if impl_row < 0:
            return -1
        return self.h-impl_row-1

    def to_impl_row(self, user_row):
        """
        Transforms the given row from user representation to internal
        representation.
        """
        if user_row < 0:
            return -1
        return self.h-user_row-1


################################################################################


class Board(StackBoard):
    """
    Represents a board for the Connect 4 game.

    From the user point of view a board is a WxH grid with width W and height H.
    Each cell of the grid has a coordinate (x,y), where x grows from left to
    right (starting from 0 until W-1) and y grows from bottom to up (starting from 0 until H-1).
    For instance, a 7x6 board can be depicted as follows:
        (0,0)         (6,0)
        |-|-|-|-|-|-|-|
        | | | | | | | |
        |-|-|-|-|-|-|-|
        | | | | | | | |
        |-|-|-|-|-|-|-|
        | | | | | | | |
        |-|-|-|-|-|-|-|
        | | | | | | | |
        |-|-|-|-|-|-|-|
        | | | | | | | |
        |-|-|-|-|-|-|-|
        | | | | | | | |
        |-|-|-|-|-|-|-|
        (0,5)         (6,5)
    """
    pass


################################################################################


class GameState:
    """
    A GameState specifies the full game state, including the board, agent
    configurations and score changes.

    GameStates are used by the Game object to capture the actual state of the
    game and can be used by agents to reason about the game.

    Much of the information in a GameState is stored in a GameStateData object.
    """

    def __init__(self, layout, num_agents):
        self.board = Board(layout[0], layout[1])
        self.nagents = num_agents
        #self.cur_agent = None

    def get_board(self):
        """
        Returns the current game board.
        """
        return self.board

    def get_layout(self):
        """
        Returns the layout of the game board as a tuple (width, height).
        """
        return (self.board.width(), self.board.height())

    def num_agents(self):
        """
        Returns the number of agents in the game.
        """
        return self.nagents

    def is_legal_action(self, action):
        """
        Tells if in the current state it is valid to perform the given action.
        """
        return self.board.can_push_token(action)

    def get_legal_actions(self):
        """
        Returns the legal actions for the current state.
        """
        #if self.is_final():
        #    return []

        actions = []
        for x in range(self.board.width()):
            if self.is_legal_action(x):
                actions.append(x)
        return actions

    def generate_successor(self, agent_index, action):
        """
        Generate a new GameState instance resulting from applying the given
        action in the current state.
        """
        # Check that a successor exists
        if self.is_final():
            raise Exception('Cannot generate a successor of a terminal state.')
        if not self.is_legal_action(action):
            raise Exception('Cannot generate a successor of a state from an illegal action.')

        #new_state = copy.deepcopy(self)
        new_state = GameState(self.get_layout(), self.nagents)
        new_state.board = self.board.deep_copy()
        new_state.nagents = self.nagents
        new_state.make_move(agent_index, action)

        return new_state

    def make_move(self, agent_index, action):
        """
        Applies the given action in the current state.
        """
        self.board.push_token(agent_index, action)
        #self.cur_agent = agent_index

    def unmake_move(self, action):
        """
        Undo the given action in the current state.
        """
        self.board.pop_token(action)

    #def get_current_agent(self):
    #    return self.cur_agent

    def get_winner_positions(self):
        """
        Returns a list of (column,row) pairs representing the winning positions,
        if any; otherwise, returns an empty list
        """
        pos = []
        for x in range(self.board.width()):
            #for y in range(self.board.height()):
            for y in range(self.board.get_column_empty_row(x)+1, self.board.height()):
                #if not self.board.has_token(x, y):
                #    continue
                token = self.board.get_token(x, y)
                if x < (self.board.width()-3):
                    # check horizontal '-' pattern
                    if (self.board.get_token(x+1, y) == token and
                        self.board.get_token(x+2, y) == token and
                        self.board.get_token(x+3, y) == token):
                        pos = [(x,y), (x+1,y), (x+2,y), (x+3,y)]
                        # check for more than 4 tokens
                        for xx in range(x+4, self.board.width()):
                            if self.board.get_token(xx, y) != token:
                                break
                            pos.append((xx,y))
                        for xx in range(x-1, -1, -1):
                            if self.board.get_token(xx, y) != token:
                                break
                            pos.append((xx,y))
                        break;
                    # check right diagonal '/' pattern
                    if (y >= 3 and
                        self.board.get_token(x+1, y-1) == token and
                        self.board.get_token(x+2, y-2) == token and
                        self.board.get_token(x+3, y-3) == token):
                        pos = [(x,y), (x+1,y-1), (x+2,y-2), (x+3,y-3)]
                        # check for more than 4 tokens
                        k0 = 4
                        k1 = min(self.board.width()-(x+4), (y-3)) + k0
                        for k in range(k0, k1):
                            (xx, yy) = (x+k, y-k)
                            if self.board.get_token(xx, yy) != token:
                                break
                            pos.append((xx,yy))
                        k0 = min(x, self.board.height()-y)-1
                        k1 = -1
                        for k in range(k0, k1, -1):
                            (xx, yy) = (x-k, y+k)
                            if self.board.get_token(xx, yy) != token:
                                break
                            pos.append((xx,yy))
                        break;
                    ## check left diagonal '\' pattern
                    if (y < (self.board.height()-3) and
                        self.board.get_token(x+1, y+1) == token and
                        self.board.get_token(x+2, y+2) == token and
                        self.board.get_token(x+3, y+3) == token):
                        pos = [(x,y), (x+1,y+1), (x+2,y+2), (x+3,y+3)]
                        # check for more than 4 tokens
                        #nk = min(self.board.width()-(x+3), self.board.height()-(y+3))-1
                        #for k in range(nk):
                        #    (xx, yy) = (x+k, y+k)
                        #    if self.board.get_token(xx, yy) != token:
                        #        break
                        #    pos.append((xx,yy))
                        #nk = min(x, y)-1
                        #for k in range(nk, -1, -1):
                        #    (xx, yy) = (x-k, y-k)
                        #    if self.board.get_token(xx, yy) != token:
                        #        break
                        #    pos.append((xx,yy))
                        k0 = 4
                        k1 = min(self.board.width()-(x+4), self.board.height()-(y+4)) + k0
                        for k in range(k0, k1):
                            (xx, yy) = (x+k, y+k)
                            if self.board.get_token(xx, yy) != token:
                                break
                            pos.append((xx,yy))
                        k0 = min(x, y)-1
                        k1 = -1
                        for k in range(k0, k1, -1):
                            (xx, yy) = (x-k, y-k)
                            if self.board.get_token(xx, yy) != token:
                                break
                            pos.append((xx,yy))
                        break;
                # check vertical pattern
                if (y < (self.board.height()-3) and
                    self.board.get_token(x, y+1) == token and
                    self.board.get_token(x, y+2) == token and
                    self.board.get_token(x, y+3) == token):
                    pos = [(x,y), (x,y+1), (x,y+2), (x,y+3)]
                    # check for more than 4 tokens
                    for yy in range(y+4, self.board.height()):
                        if self.board.get_token(x, yy) != token:
                            break
                        pos.append((x,yy))
                    for yy in range(y-1, -1, -1):
                        if self.board.get_token(x, yy) != token:
                            break
                        pos.append((x,yy))
                    break;
                # check right diagonal '/' pattern
                if (x >= 3 and
                    y < (self.board.height()-3) and
                    self.board.get_token(x-1, y+1) == token and
                    self.board.get_token(x-2, y+2) == token and
                    self.board.get_token(x-3, y+3) == token):
                    pos = [(x,y), (x-1,y+1), (x-2,y+2), (x-3,y+3)]
                    # check for more than 4 tokens
                    k0 = 4
                    k1 = min((x-3), self.board.height()-(y+4)) + k0
                    for k in range(k0, k1):
                        (xx, yy) = (x-k, y+k)
                        if self.board.get_token(xx, yy) != token:
                            break
                        pos.append((xx,yy))
                    k0 = min(self.board.width()-x, y)-1
                    k1 = -1
                    for k in range(k0, k1, -1):
                        (xx, yy) = (x+k, y-k)
                        if self.board.get_token(xx, yy) != token:
                            break
                        pos.append((xx,yy))
                    break;
            if len(pos) > 0:
                break
        return pos

    def can_win(self):
        """
        Tells if in the current state it is possible to win (irrespective of who
        actually wins).
        Note, if current state represents a winning situation the method returns
        True as well.
        """
        # Checks from the top of the board (and left-to-right) if there is
        # enough space to form a pattern or at least 4 tokens of the same
        # colors.
        # Note, to do this check it is sufficient to start from the top of each
        # column, pick the first available token in the column, and check for
        # one of the possible token patterns.
        for x in range(self.board.width()):
            # Starts at the top of the column
            y = 0
            # Picks the first available token
            ytok = min(self.board.get_column_empty_row(x)+1, self.board.height()-1)
            token = self.board.get_token(x, ytok)
            # Checks for token patterns
            if x < (self.board.width()-3):
                # check horizontal '-' pattern
                if (self.board.get_token(x+1, y) in [token, self.board.INVALID_TOKEN] and
                    self.board.get_token(x+2, y) in [token, self.board.INVALID_TOKEN] and
                    self.board.get_token(x+3, y) in [token, self.board.INVALID_TOKEN]):
                    return True
                ## check right diagonal '/' pattern
                #if (y >= 3 and
                #    self.board.get_token(x+1, y-1) in [token, self.board.INVALID_TOKEN] and
                #    self.board.get_token(x+2, y-2) in [token, self.board.INVALID_TOKEN] and
                #    self.board.get_token(x+3, y-3) in [token, self.board.INVALID_TOKEN]):
                #    return True
                # check left diagonal '\' pattern
                if (y < (self.board.height()-3) and
                    self.board.get_token(x+1, y+1) in [token, self.board.INVALID_TOKEN] and
                    self.board.get_token(x+2, y+2) in [token, self.board.INVALID_TOKEN] and
                    self.board.get_token(x+3, y+3) in [token, self.board.INVALID_TOKEN]):
                    return True
            # check vertical pattern
            if (y < (self.board.height()-3) and
                self.board.get_token(x, y+1) in [token, self.board.INVALID_TOKEN] and
                self.board.get_token(x, y+2) in [token, self.board.INVALID_TOKEN] and
                self.board.get_token(x, y+3) in [token, self.board.INVALID_TOKEN]):
                return True
            # check right diagonal '/' pattern
            if x >= 3 and y < (self.board.height()-3):
                # check horizontal '-' pattern
                if (self.board.get_token(x-1, y+1) in [token, self.board.INVALID_TOKEN] and
                    self.board.get_token(x-2, y+2) in [token, self.board.INVALID_TOKEN] and
                    self.board.get_token(x-3, y+3) in [token, self.board.INVALID_TOKEN]):
                    return True
        return False

    def is_win(self):
        """
        Tells if the current state is a winning situation.
        """
        #return len(self.get_winner_positions()) > 0
        for x in range(self.board.width()):
            #for y in range(self.board.height()):
            for y in range(self.board.get_column_empty_row(x)+1, self.board.height()):
                token = self.board.get_token(x, y)
                if x < (self.board.width()-3):
                    # check horizontal '-' pattern
                    if (self.board.get_token(x+1, y) == token and
                        self.board.get_token(x+2, y) == token and
                        self.board.get_token(x+3, y) == token):
                        return True
                    ## check right diagonal '/' pattern
                    #if (y >= 3 and
                    #    self.board.get_token(x+1, y-1) == token and
                    #    self.board.get_token(x+2, y-2) == token and
                    #    self.board.get_token(x+3, y-3) == token):
                    #    return True
                    ## check left diagonal '\' pattern
                    if (y < (self.board.height()-3) and
                        self.board.get_token(x+1, y+1) == token and
                        self.board.get_token(x+2, y+2) == token and
                        self.board.get_token(x+3, y+3) == token):
                        return True
                # check vertical pattern
                if (y < (self.board.height()-3) and
                    self.board.get_token(x, y+1) == token and
                    self.board.get_token(x, y+2) == token and
                    self.board.get_token(x, y+3) == token):
                    return True
                # check left diagonal '\' pattern
                if x >= 3:
                    if (y < (self.board.height()-3) and
                        self.board.get_token(x-1, y+1) == token and
                        self.board.get_token(x-2, y+2) == token and
                        self.board.get_token(x-3, y+3) == token):
                        return True
        return False


    def is_tie(self):
        """
        Tells if the current state is a tie situation (i.e., a situation with no
        winner).
        """
        #return self.is_final() and not self.is_win()
        return not self.can_win()

    def is_final(self):
        """
        Tells if the current game state is a final state, that is:
        - if there are at least 4 consecutive tokens belonging to the same
          player, or
        - if the board is full, or
        - if the space left cannot contain a winner combination.
        """
        #return self.board.is_full() or self.is_win() or not self.can_win()
        return self.board.is_full() or self.is_win() or self.is_tie()

    def is_winner(self, agent_index):
        """
        Tells if the given agent is the winner.
        """
        win_pos = self.get_winner_positions()
        # Make sure this is a winning situation
        if len(win_pos) > 0:
            # Check if the winning token belongs to the given agent
            (x,y) = win_pos[0]
            if self.board.get_token(x, y) == agent_index:
                return True
        return False

    def get_winner(self):
        """
        Returns the identifier of the winner agent, if the current state
        represents a win situation; None, otherwise.
        """
        win_pos = self.get_winner_positions()
        # Make sure this is a winning situation
        if len(win_pos) > 0:
            # Check if the winning token belongs to the given agent
            (x,y) = win_pos[0]
            return self.board.get_token(x, y)
        return None

    def __str__(self):
        """
        Returns a string representation of this state.
        """
        return str(self.board)


################################################################################


class Game:
    """
    Provides the logic to play to the Connect 4 game.

    Note, to play this game, the following requirements need to be satisfied:
    - the board layout must be 4x4 or larger (the standard game uses a 7x6 board
      layout),
    - the number of agents must be 2 or greater.
    """
    def __init__(self, agents, layout):
        if layout[0] < 4 or layout[1] < 4:
            raise Exception('Board must be at least 4x4 large.')
        if len(agents) < 2:
            raise Exception('The game needs at least two agents to play.')
        self.agents = agents
        self.state = GameState(layout, len(agents))
        self.start_agent_idx = agents[0].get_index()
        self.cur_agent_idx = self.start_agent_idx

    def reset(self):
        """
        Resets the game to the initial state.
        """
        self.state = GameState(self.get_layout(), self.num_agents())
        self.cur_agent_idx = self.start_agent_idx

    def get_state(self):
        """
        Gets the current game state.
        """
        return self.state

    def get_layout(self):
        """
        Gets the board layout.
        """
        return self.state.get_layout()

    def get_starting_agent(self):
        """
        Gets the agent who starts playing.
        """
        return self.agents[self.start_agent_idx]

    def get_current_agent(self):
        """
        Gets the currently playing agent.
        """
        return self.agents[self.cur_agent_idx]

    def get_agents(self):
        """
        Gets the agents playing the current game.
        """
        return self.agents

    def num_agents(self):
        """
        Returns the number of agents playing the current game.
        """
        return len(self.agents)

    def get_agent(self, agent_index):
        """
        Gets the agent identified by the given agent index.
        """
        return self.agents[agent_index]

    def make_move(self):
        """
        Advances the game by making the move for the current agent and passing
        the turn to the next agent.
        Returns the action.

        Note, if you call get_current_agent before and after a call to
        make_move, the returned agent is in general different because make_move
        passes the turn to the next agent.
        """
        agent = self.get_current_agent()
        column = agent.get_action(self.state)
        if column != None:
            print('Agent ', agent.get_index(), ' placed a token in column: ', column)
            self.state.make_move(agent.get_index(), column)
        self.cur_agent_idx = (self.cur_agent_idx+1) % len(self.agents)
        return column

    def is_over(self):
        """
        Tells if the game is over.
        """
        return self.state.is_final()
