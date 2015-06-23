# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
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
import upo.connect4.agents
import upo.utils


class FirstFitRightComputerAgent(upo.connect4.agents.ComputerAgent):
    """
    A not-very-smart computer-controlled agent that chooses the first available
    valid rightmost column.
    """
    def get_action(self, game_state):
        """
        Returns the next move (i.e., a column) to play, if any; otherwise, returns None.
        """
        #TODO: put here your implementation
        upo.utils.raise_undefined_method()


################################################################################


class EnhancedRandomComputerAngent(upo.connect4.agents.ComputerAgent):
    """
    A smart computer-controlled agent that chooses its actions at
    random.
    """
    def get_action(self, game_state):
        """
        Returns the next move (i.e., a column) to play, if any; otherwise, returns None.
        """
        #TODO: put here your implementation
        upo.utils.raise_undefined_method()


################################################################################


class AlphaBetaMinimaxComputerAgent(upo.connect4.agents.AlphaBetaMinimaxComputerAgent):
    """
    A computer agent that makes decision according to the depth-limited minimax
    strategy with alpha-beta pruning.

    This is essentially a proxy class for the upo.connect4.agents.AlphaBetaMinimaxComputerAgent
    that is used for parsing input arguments.
    """
    def __init__(self, index, **kwargs):
        depth = float('+inf')
        eval_func = upo.connect4.agents.basic_evaluation_function
        if 'depth' in kwargs:
            depth = kwargs['depth']
        if 'evalfunc' in kwargs:
            eval_func = upo.utils.import_lib(kwargs['evalfunc'])
        upo.connect4.agents.AlphaBetaMinimaxComputerAgent.__init__(self, index, depth, eval_func)


################################################################################


def better_evaluation_function(game_state, agent, **context):
    """
    The purpose of this evaluation function is to improve the default one, by
    exploiting some state information.

    Parameters
    - game_state: an instance of the 'upo.connect4.game.GameState' class
      representing the game state (a node of the game tree) to be evaluated.
    - agent: an instance of the 'upo.connect4.agents.Agent' class
      representing the decision making agent (i.e., the agent that must make
      a decision about the next move to play).
    - context: additional information that can be used to evaluate this state;
      the following information are available:
    - context['depth']: the current depth of the node that is to be evaluated.

    Return Value
    This function should return a positive value if this game state is
    advantageous for the given agent and a negative value if it is not.
    """
    agent_index = agent.get_index()
    depth = 0
    if 'depth' in context:
        depth = context['depth']//game_state.num_agents()

    score = 0.0
    
    #TODO: put here your implementation
    upo.utils.raise_undefined_method()

    print("Agent: ", agent_index, ", State: ", game_state, ", Depth: ", depth, " =>  Score: ", score) #XXX

    return score
