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


import random
import upo.utils


class Agent:
    """
    Base class for player agents.
    A derived class must define a get_action method.
    """
    def __init__(self, index, name=None):
        self.idx = index
        if name != None:
            self.name = name
        else:
            self.name = 'Agent #' + str(index)

    def get_action(self, game_state):
        """
        The Agent will receive a GameState object and must return an action
        representing the column of the board where to put the token.
        """
        utils.raise_undefined_method()

    def get_index(self):
        return self.idx

    def get_name(self):
        return self.name

    def is_interactive(self):
        return False


################################################################################


class HumanAgent(Agent):
    """
    An agent controlled by human.
    """
    def __init__(self, index):
        Agent.__init__(self, index)

    #def get_action(self, game_state):
    #    pass;

    def is_interactive(self):
        return True


################################################################################


class ComputerAgent(Agent):
    """
    Base class for computer-controlled agents.
    """
    def __init__(self, index):
        Agent.__init__(self, index)


################################################################################


class FirstFitComputerAgent(ComputerAgent):
    """
    A not-very-smart computer-controlled agent that chooses the first available
    valid column.
    """
    def get_action(self, game_state):
        legals = game_state.get_legal_actions()
        return min(legals);


################################################################################


class RandomComputerAgent(ComputerAgent):
    """
    A not-very-smart computer-controlled agent that chooses its actions at
    random.
    """
    def get_action(self, game_state):
        legals = game_state.get_legal_actions()
        return random.choice(legals);


################################################################################


def default_evaluation_function(game_state, agent_index):
    if game_state.is_final():
        if game_state.is_winner(agent_index):
            return 1.0
        if game_state.is_tie():
            return 0.0
        return -1.0
    return 0.0

class MinimaxComputerAgent(ComputerAgent):
    """
    A computer-controlled agent that chooses its action according to the
    minimax algorithm.

    The minimax algorithm evaluates the game tree until the given depth.
    Note that the depth is expressed in terms of plies (i.e., a sequence of
    actions where each agent plays its turn).
    """
    def __init__(self, index, depth):
        ComputerAgent.__init__(self, index)
        self.depth = depth
        self.evaluation_function = default_evaluation_function

    def get_depth(self):
        return self.depth

    def get_action(self, game_state):
        #print 'Agent: ', self.get_index(), ', Board: \n', game_state.get_board()
        (value, action) = self.make_minimax_decision(game_state, self.get_index(), 0)
        return action

    def make_minimax_decision(self, game_state, agent_index, depth):
        if depth == self.depth:
            return (self.evaluation_function(game_state, agent_index), None)
        next_agent_index = (agent_index+1) % game_state.num_agents()
        if next_agent_index == self.get_index():
            return self.make_max_decision(game_state, next_agent_index, depth)
        else:
            return self.make_min_decision(game_state, next_agent_index, depth)

    def make_min_decision(self, game_state, agent_index, depth):
        if game_state.is_final():
            #print 'MIN-VALUE(',agent_index,',',depth,'): ', self.evaluation_function(game_state, agent_index), ' (', None, ')'
            return (self.evaluation_function(game_state, agent_index), None)
        min_value = float('+inf')
        min_action = None
        for action in game_state.get_legal_actions():
            successor_game_state = game_state.generate_successor(agent_index, action)
            (successor_value,successor_action) = self.make_minimax_decision(successor_game_state, agent_index, depth+1)
            if successor_value < min_value:
                min_value = successor_value
                min_action = action
        #print 'MIN-VALUE(',agent_index,',',depth,'): ', min_value, ' (', min_action, ')'
        return (min_value, min_action)

    def make_max_decision(self, game_state, agent_index, depth):
        if game_state.is_final():
            #print 'MAX-VALUE(',agent_index,',',depth,'): ', self.evaluation_function(game_state, agent_index), ' (', None, ')'
            return (self.evaluation_function(game_state, agent_index), None)
        max_value = float('-inf')
        max_action = None
        for action in game_state.get_legal_actions():
            successor_game_state = game_state.generate_successor(agent_index, action)
            (successor_value,successor_action) = self.make_minimax_decision(successor_game_state, agent_index, depth+1)
            if successor_value > max_value:
                max_value = successor_value
                max_action = action
        #print 'MAX-VALUE(',agent_index,',',depth,'): ', max_value, ' (', max_action, ')'
        return (max_value, max_action)

