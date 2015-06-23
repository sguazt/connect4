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


import argparse
import enum
import inspect
import random
import upo.connect4.agents
import upo.connect4.game
import upo.connect4.ui
import upo.utils


class GameDifficulty(enum.IntEnum):
    """
    Enumeration for predefined difficulty levels.
    """
    very_easy = 1
    easy = 2
    medium = 3
    hard = 4
    very_hard = 5
    no_hope = -1 # Actually, this leads to the full exploration of the game tree (may take a huge amount of time)

    def __str__(self):
        return self.name

    @classmethod
    def default_difficulty(cls):
        return cls.easy

    @classmethod
    def str2int(cls, s):
        ls = s.lower()
        if ls == 'veryeasy':
            return cls.very_easy
        if ls == 'easy':
            return cls.easy
        if ls == 'medium':
            return cls.medium
        if ls == 'hard':
            return cls.hard
        if ls == 'veryhard':
            return cls.very_hard
        if ls == 'nohope':
            return cls.no_hope
        if s.isdigit():
            return int(s)
        return cls.default_difficulty()


class AgentFactory:
    ids = ['alphabeta', 'custom', 'expectimax', 'firstfitleft', 'human', 'minimax', 'random']

    def make_agent(self, agent_id, agent_index, args):
        #if agent_id not in self.ids:
        #    raise Exception('Unknown agent identifier "' + agent_id + '"')
        if agent_id == 'alphabeta':
            return upo.connect4.agents.AlphaBetaMinimaxComputerAgent(agent_index, args['depth'])
        if agent_id == 'custom':
            klass = upo.utils.import_lib(args['class'])
            if len(inspect.signature(klass.__init__).parameters) <= 2:
                return klass(agent_index)
            return klass(agent_index, **args)
        if agent_id == 'firstfitleft':
            return upo.connect4.agents.FirstFitLeftComputerAgent(agent_index)
        if agent_id == 'expectimax':
            return upo.connect4.agents.ExpectimaxComputerAgent(agent_index, args['depth'])
        if agent_id == 'human':
            return upo.connect4.agents.HumanAgent(agent_index)
        if agent_id == 'minimax':
            return upo.connect4.agents.MinimaxComputerAgent(agent_index, args['depth'])
        if agent_id == 'random':
            return upo.connect4.agents.RandomComputerAgent(agent_index)

    @classmethod
    def get_available_agents(cls):
        return cls.ids


def parse_options():
    parser = argparse.ArgumentParser(description="UPO :: Connect 4 game")

    parser.add_argument('-a', '--agent', action='append', dest='agents',
                        choices=AgentFactory.get_available_agents(),
                        help='The type of a player agent.', default=[])
    #parser.add_argument('--agentclass', action='append', dest='agent_classes', type=str,
    #                    help='The fully qualified class name of the custom agent (e.g., upo.connect4.agents.MyAgent); only used when the agent type is "custom" (see option "--agent").', default=[])
    parser.add_argument('--agentargs', action='append', dest='agent_args', type=str, nargs="*",
                        help='The arguments to pass to the associated "custom" agent.'
                            +'Specify as many parameters you need in the form of a space-separated sequence of "key=value" elements; for instance, "--agentargs key1=value1 key2=value2 ... keyN=valueN".'
                            +'The following keys are available:'
                            +'"class": the value is the fully qualified class name of the custom agent (e.g., upo.connect4.agents.MyAgent);'
                            +'"depth": the maximum depth in the game tree where stopping the search (same as "--difficulty" option, but specific for a given agent);'
                            +'"evalfunc": the fully qualified function name of the evaluation function to use for evaluating nodes of the game tree.'
                            +'There must be at least one parameter whose key is "class"'
                            +'Only used when the agent type is "custom" (see option "--agent").'
                            +'Repeat this option for each "custom" agent.', default=[])
    parser.add_argument('-d', '--difficulty', dest='difficulty', type=str,
                        help='The level of difficulty of the game (valid only for intelligent computer agents.', default=str(GameDifficulty.default_difficulty))
    parser.add_argument('--fps', dest='fps', type=int,
                        help='Number of frames per second.', default=30)
    parser.add_argument('-g', '--geometry', dest='geometry', type=int, nargs=2,
                        help='A pair of two numbers specifying the width and height (in pixels) of the whole window.', default=[640, 480])
    parser.add_argument('-l', '--layout', dest='layout', type=int, nargs=2,
                        help='A pair of two numbers specifying the width and height (in number of tiles) of the game board.', default=[7, 6])
    parser.add_argument('--timeout', dest='timeout', type=int,
                        help='Number of seconds to wait for a player\'s move before timing out. Setting it to zero disables the timeout', default=0)
    parser.add_argument('--verbose', '-v', action='count',
                        help='Increase output verbosity', default=0)

    args = parser.parse_args()

    # We need at least two agents
    while len(args.agents) <= 1:
        args.agents.append('random')

    # Check arguments consistency
    if args.agents.count('custom') != len(args.agent_args):
        parser.error('Agent arguments not found for "custom" agent')
    if args.fps <= 0:
        parser.error('Frame rate must be a positive number')
    if any(args.geometry) <= 0:
        parser.error('Window geometry must be a pair of positive numbers')
    if any(args.layout) <= 0:
        parser.error('Board layout must be a pair of positive numbers')
    if args.timeout < 0:
        parser.error('Timeout value must be a nonnegative number')

    return args


if __name__ == '__main__':
    args = parse_options()
    #print('Command-line Arguments: ', args)
    #rng_state = ...
    #random.setstate(rng_state)
    #rng_state = random.getstate()
    #print "Random State: ", rng_state
    agent_factory = AgentFactory()
    agents = []
    agent_idx = 0
    for agent_type in args.agents:
        xargs = {}
        #xargs['depth'] = GameDifficulty.str2int(args.difficulty)
        xargs['depth'] = args.difficulty
        if agent_type == 'custom':
            agent_args = args.agent_args.pop(0)
            for arg in agent_args:
                (key, value) = arg.split('=', 1) # Retrieves the key and the value
                xargs[key.lower()] = value
            if 'class' not in xargs:
                raise Exception('Class name not specified for custom agent')
        xargs['depth'] = int(GameDifficulty.str2int(xargs['depth']))*len(args.agents)
        agent = agent_factory.make_agent(agent_type, agent_idx, xargs)
        agent.set_verbosity_level(args.verbose)
        agents.append(agent)
        agent_idx += 1
    game = upo.connect4.game.Game(agents, args.layout)
    game.set_verbosity_level(args.verbose)
    ui = upo.connect4.ui.PyGameUI(game, args.geometry, args.fps, args.timeout)
    ui.show()
