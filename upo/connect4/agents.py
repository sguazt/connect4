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
    def __init__(self, index):
        self.idx = index
        self.name = 'Agent #' + str(index)

    def get_action(self, game_state):
        """
        The Agent will receive a GameState object and must return an action
        representing the column of the board where to put the token.
        """
        utils.raise_undefined_method()

    def get_index(self):
        return self.idx

    def set_name(self, name):
        self.name = name

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
        self.action = None

    def set_action(self, c):
        self.action = c

    def get_action(self, game_state):
        return self.action;

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


class FirstFitLeftComputerAgent(ComputerAgent):
    """
    A not-very-smart computer-controlled agent that chooses the first available
    valid leftmost column.
    """
    def get_action(self, game_state):
        legals = game_state.get_legal_actions()
        if len(legals) == 0:
            return None
        return min(legals)


################################################################################


class RandomComputerAgent(ComputerAgent):
    """
    A not-very-smart computer-controlled agent that chooses its actions at
    random.
    """
    def get_action(self, game_state):
        legals = game_state.get_legal_actions()
        if len(legals) == 0:
            return None
        return random.choice(legals)


################################################################################


def basic_evaluation_function(game_state, agent, **context):
    """
    This simple evaluation functions evaluates a node (i.e., a game state) by
    only considering if its a terminal node or not, and, in case of a terminal
    node, if it represents a win or a lose situation.

    It returns:
    - 1 if the given state is a win situation for the given agent,
    - -1 if the given state is a lose situation for the given agent, or
    - 0 if the given state is a tie situation or if it isn't a terminal state.

    The argument context is not used.
    """
    agent_index = agent.get_index()
    if game_state.is_final():
        if game_state.is_winner(agent_index):
            return 1.0
        if game_state.is_tie():
            return 0.0
        return -1.0
    return 0.0


def improved_evaluation_function(game_state, agent, **context):
    """
    This simple evaluation functions improves the basic one by adding some
    randomness when choosing among non final states.
    In some cases this evaluation function behaves better than the basic one
    since it can block opponents' threats by a random move.

    It returns:
    - 1 if the given state is a win situation for the given agent,
    - -1 if the given state is a lose situation for the given agent, or
    - 0 if the given state is a tie situation,
    - a random number uniformly chosen in [0,1) if the given state isn't a
      terminal state.

    The argument context is not used.
    """
    agent_index = agent.get_index()
    if game_state.is_final():
        if game_state.is_winner(agent_index):
            return 1.0
        if game_state.is_tie():
            return 0.0
        return -1.0
    return random.random() # Pick a value in [0,1) at random


# Define the default evaluation function to use in case it is not specified
#default_evaluation_function = basic_evaluation_function
default_evaluation_function = improved_evaluation_function


################################################################################


class MinimaxComputerAgent(ComputerAgent):
    """
    A computer-controlled agent that chooses its action according to the
    minimax algorithm.

    The minimax algorithm evaluates the game tree until the given depth.
    Note that the depth is expressed in terms of plies (i.e., a sequence of
    actions where each agent plays its turn).

    See:
    - S. Russell and P. Norvig, "Artificial Intelligence: A Modern Approach," 3rd Edition, Prentice Hall, 2010.
    """
    def __init__(self, index, depth=float('+inf'), eval_func=default_evaluation_function):
        ComputerAgent.__init__(self, index)
        self.depth = depth
        self.evaluation_function = eval_func

    def get_depth(self):
        return self.depth

    def get_action(self, game_state):
        #print('MINIMAX-DECISION>> Agent: ', self.get_index(), ', Board: \n', game_state.get_board())#XXX
        action = None
        if game_state.get_board().is_empty() and (game_state.get_board().width() % 2) != 0:
            # When the board is empty and has an odd number of columns,
            # it is better to push a token in the middle
            action = game_state.get_board().width()//2
        else:
            (value, action) = self.make_minimax_decision(game_state, self.get_index(), 0, True)
        #print("MINIMAX-DECISION>> Final action: ", action)#XXX
        return action

    def make_minimax_decision(self, game_state, agent_index, depth, first=False):
        #print('  '*(depth+1) + 'Making MINIMAX-DECISION(',agent_index,',',depth,') ')#XXX
        next_agent_index = 0
        if first:
            next_agent_index = agent_index
        else:
            next_agent_index = (agent_index+1) % game_state.num_agents()
        if next_agent_index == self.get_index():
            return self.make_max_decision(game_state, next_agent_index, depth+1)
        else:
            return self.make_min_decision(game_state, next_agent_index, depth+1)

    def make_min_decision(self, game_state, agent_index, depth):
        #print('  '*(depth+1) + 'Making MIN-DECISION(',agent_index,',',depth,') ')#XXX
        if self.cutoff_test(game_state, depth):
            #print('  '*(depth+1) + '[cutoff] Returning MIN-VALUE(',agent_index,',',depth,'): ', self.evaluation_function(game_state, self, depth=depth), ' (', None, ')')#XXX
            return (self.evaluation_function(game_state, self, depth=depth), None)
        min_value = float('+inf')
        min_action = None
        for action in game_state.get_legal_actions():
            #print('  '*(depth+1) + 'MIN-DECISION Action: ', action)#XXX
            successor_game_state = game_state.generate_successor(agent_index, action)
            (successor_value,successor_action) = self.make_minimax_decision(successor_game_state, agent_index, depth)
            if successor_value < min_value:
                min_value = successor_value
                min_action = action
        #print('  '*(depth+1) + 'Returning MIN-VALUE(',agent_index,',',depth,'): ', min_value, ' (', min_action, ')')#XXX
        return (min_value, min_action)

    def make_max_decision(self, game_state, agent_index, depth):
        #print('  '*(depth+1) + 'Making MAX-DECISION(',agent_index,',',depth,') ')#XXX
        if self.cutoff_test(game_state, depth):
            #print('  '*(depth+1) + '[cutoff] Returning MAX-VALUE(',agent_index,',',depth,'): ', self.evaluation_function(game_state, self, depth=depth), ' (', None, ')')#XXX
            return (self.evaluation_function(game_state, self, depth=depth), None)
        max_value = float('-inf')
        max_action = None
        for action in game_state.get_legal_actions():
            #print('  '*(depth+1) + 'MAX-DECISION Action: ', action)#XXX
            successor_game_state = game_state.generate_successor(agent_index, action)
            (successor_value,successor_action) = self.make_minimax_decision(successor_game_state, agent_index, depth)
            if successor_value > max_value:
                max_value = successor_value
                max_action = action
        #print('  '*(depth+1) + 'Returning MAX-VALUE(',agent_index,',',depth,'): ', max_value, ' (', max_action, ')')#XXX
        return (max_value, max_action)

    def cutoff_test(self, game_state, depth):
        """
        Checks if the maximum tree depth has been reached or if the current
        node of the game tree is a terminal node.
        """
        #if depth == self.depth*game_state.num_agents() or game_state.is_final():
        if depth == self.depth or game_state.is_final():
            return True
        return False


################################################################################


class AlphaBetaMinimaxComputerAgent(ComputerAgent):
    """
    A computer-controlled agent that chooses its action according to the
    minimax algorithm with alpha-beta pruning.

    The minimax algorithm evaluates the game tree until the given depth.
    Note that the depth is expressed in terms of plies (i.e., a sequence of
    actions where each agent plays its turn).
    The alpha-beta pruning technique lets you speed-up the search along the
    game tree by pruning useless evaluations of subtrees.

    See:
    - S. Russell and P. Norvig, "Artificial Intelligence: A Modern Approach," 3rd Edition, Prentice Hall, 2010.
    """
    def __init__(self, index, depth=float('+inf'), eval_func=default_evaluation_function):
        ComputerAgent.__init__(self, index)
        self.depth = depth
        self.evaluation_function = eval_func

    def get_depth(self):
        return self.depth

    def get_action(self, game_state):
        #print('ALPHA-BETA-MINIMAX-DECISION>> Agent: ', self.get_index(), ', Board: \n', game_state.get_board()) #XXX
        action = None
        if game_state.get_board().is_empty() and (game_state.get_board().width() % 2) != 0:
            # When the board is empty and has an odd number of columns,
            # it is better to push a token in the middle
            action = game_state.get_board().width()//2
        else:
            (value, action) = self.make_minimax_decision(game_state, self.get_index(), float('-inf'), float('+inf'), 0, True)
        #print("ALPHA-BETA-MINIMAX-DECISION>> Final action: ", action) #XXX
        return action

    def make_minimax_decision(self, game_state, agent_index, alpha, beta, depth, first=False):
        #print('  '*(depth+1) + 'Making ALPHA-BETA-MINIMAX-DECISION(agent=',agent_index,',depth=',depth,',alpha=', alpha, ',beta=', beta, ')') #XXX
        next_agent_index = 0
        if first:
            next_agent_index = agent_index
        else:
            next_agent_index = (agent_index+1) % game_state.num_agents()
        if next_agent_index == self.get_index():
            return self.make_max_decision(game_state, next_agent_index, alpha, beta, depth+1)
        else:
            return self.make_min_decision(game_state, next_agent_index, alpha, beta, depth+1)

    def make_min_decision(self, game_state, agent_index, alpha, beta, depth):
        #print('  '*(depth+1) + 'Making MIN-DECISION(',game_state,',agent=',agent_index,',depth=',depth,',alpha=',alpha,',beta=',beta,') ') #XXX
        if self.cutoff_test(game_state, depth):
            #print('  '*(depth+1) + '[cutoff] Returning MIN-VALUE(agent=',agent_index,',depth=',depth,',alpha=',alpha,',beta=',beta,'): ', self.evaluation_function(game_state, self, depth=depth), ' (', None, ')') #XXX
            return (self.evaluation_function(game_state, self, depth=depth), None)
        min_value = float('+inf')
        min_action = None
        for action in game_state.get_legal_actions():
            #print('  '*(depth+1) + 'MIN-DECISION Action: ', action)
            successor_game_state = game_state.generate_successor(agent_index, action)
            (successor_value,successor_action) = self.make_minimax_decision(successor_game_state, agent_index, alpha, beta, depth)
            if successor_value < min_value:
                min_value = successor_value
                min_action = action
            if min_value <= alpha:
                break
            beta = min(beta, min_value)
        #print('  '*(depth+1) + 'Returning MIN-VALUE(agent=',agent_index,',depth=',depth,',alpha=',alpha,',beta=',beta,'): ', min_value, ' (', min_action, ')') #XXX
        return (min_value, min_action)

    def make_max_decision(self, game_state, agent_index, alpha, beta, depth):
        #print('  '*(depth+1) + 'Making MAX-DECISION(',game_state,',agent=',agent_index,',depth=',depth,',alpha=',alpha,',beta=',beta,') ') #XXX
        if self.cutoff_test(game_state, depth):
            #print('  '*(depth+1) + '[cutoff] Returning MAX-VALUE(agent=',agent_index,',depth=',depth,',alpha=',alpha,',beta=',beta,'): ', self.evaluation_function(game_state, self, depth=depth), ' (', None, ')') #XXX
            return (self.evaluation_function(game_state, self, depth=depth), None)
        max_value = float('-inf')
        max_action = None
        for action in game_state.get_legal_actions():
            #print('  '*(depth+1) + 'MAX-DECISION Action: ', action) #XXX
            successor_game_state = game_state.generate_successor(agent_index, action)
            (successor_value,successor_action) = self.make_minimax_decision(successor_game_state, agent_index, alpha, beta, depth)
            if successor_value > max_value:
                max_value = successor_value
                max_action = action
            if max_value >= beta:
                break
            alpha = max(alpha, max_value)
        #print('  '*(depth+1) + 'Returning MAX-VALUE(agent=',agent_index,',depth=',depth,',alpha=',alpha,',beta=',beta,'): ', max_value, ' (', max_action, ')') #XXX
        return (max_value, max_action)

    def cutoff_test(self, game_state, depth):
        """
        Checks if the maximum tree depth has been reached or if the current
        node of the game tree is a terminal node.
        """
        if depth == self.depth or game_state.is_final():
            return True
        return False


################################################################################


class ExpectimaxComputerAgent(ComputerAgent):
    """
    A computer-controlled agent that chooses its action according to the
    expectimax algorithm.

    The expectimax algorithm evaluates the game tree until the given depth.
    Note that the depth is expressed in terms of plies (i.e., a sequence of
    actions where each agent plays its turn).

    See:
    - S. Russell and P. Norvig, "Artificial Intelligence: A Modern Approach," 3rd Edition, Prentice Hall, 2010.
    """
    def __init__(self, index, depth=float('+inf'), eval_func=default_evaluation_function):
        ComputerAgent.__init__(self, index)
        self.depth = depth
        self.evaluation_function = eval_func

    def get_depth(self):
        return self.depth

    def get_action(self, game_state):
        #print('EXPECTIMAX-DECISION>> Agent: ', self.get_index(), ', Board: \n', game_state.get_board())#XXX
        action = None
        if game_state.get_board().is_empty() and (game_state.get_board().width() % 2) != 0:
            # When the board is empty and has an odd number of columns,
            # it is better to push a token in the middle
            action = game_state.get_board().width()//2
        else:
            (value, action) = self.make_expectimax_decision(game_state, self.get_index(), 0, True)
        #print("EXPECTIMAX-DECISION>> Final action: ", action)#XXX
        return action

    def make_expectimax_decision(self, game_state, agent_index, depth, first=False):
        #print('  '*(depth+1) + 'Making EXPECTIMAX-DECISION(agent=',agent_index,',depth=',depth,') ')#XXX
        next_agent_index = 0
        if first:
            next_agent_index = agent_index
        else:
            next_agent_index = (agent_index+1) % game_state.num_agents()
        if next_agent_index == self.get_index():
            return self.make_max_decision(game_state, next_agent_index, depth+1)
        else:
            return self.make_exp_decision(game_state, next_agent_index, depth+1)

    def make_exp_decision(self, game_state, agent_index, depth):
        #print('  '*(depth+1) + 'Making EXP-DECISION(agent=',agent_index,',depth=',depth,') ')#XXX
        if self.cutoff_test(game_state, depth):
            #print('  '*(depth+1) + '[cutoff] Returning EXP-VALUE(agent=',agent_index,',depth=',depth,'): ', self.evaluation_function(game_state, self, depth=depth), ' (', None, ')')#XXX
            return (self.evaluation_function(game_state, self, depth=depth), None)
        exp_value = 0
        exp_action = None
        for action in game_state.get_legal_actions():
            #print('  '*(depth+1) + 'EXP-DECISION Action: ', action)
            successor_game_state = game_state.generate_successor(agent_index, action)
            (successor_value,successor_action) = self.make_expectimax_decision(successor_game_state, agent_index, depth)
            exp_value += successor_value
        exp_value /= float(len(game_state.get_legal_actions()))
        #print('  '*(depth+1) + 'Returning EXP-VALUE(agent=',agent_index,',depth=',depth,'): ', exp_value, ' (', exp_action, ')')#XXX
        return (exp_value, exp_action)

    def make_max_decision(self, game_state, agent_index, depth):
        #print('  '*(depth+1) + 'Making MAX-DECISION(agent=',agent_index,',',depth,') ')#XXX
        if self.cutoff_test(game_state, depth):
            #print('  '*(depth+1) + '[cutoff] Returning MAX-VALUE(agent=',agent_index,',depth=',depth,'): ', self.evaluation_function(game_state, self, depth=depth), ' (', None, ')')#XXX
            return (self.evaluation_function(game_state, self, depth=depth), None)
        max_value = float('-inf')
        max_action = None
        for action in game_state.get_legal_actions():
            #print('  '*(depth+1) + 'MAX-DECISION Action: ', action)#XXX
            successor_game_state = game_state.generate_successor(agent_index, action)
            (successor_value,successor_action) = self.make_expectimax_decision(successor_game_state, agent_index, depth)
            if successor_value > max_value:
                max_value = successor_value
                max_action = action
        #print('  '*(depth+1) + 'Returning MAX-VALUE(agent=',agent_index,',depth=',depth,'): ', max_value, ' (', max_action, ')')#XXX
        return (max_value, max_action)

    def cutoff_test(self, game_state, depth):
        """
        Checks if the maximum tree depth has been reached or if the current
        node of the game tree is a terminal node.
        """
        if depth == self.depth or game_state.is_final():
            return True
        return False


