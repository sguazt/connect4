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
import random
import upo.connect4.agents
import upo.connect4.game
import upo.connect4.ui


class GameDifficulty(enum.IntEnum):
    """
    Enumeration for predefined difficulty levels.
    """
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
    ids = ['alphabeta', 'expectimax', 'firstfit', 'human', 'minimax', 'random']

    def make_agent(self, agent_id, agent_index, args):
        #if agent_id not in self.ids:
        #    raise Exception('Unknown agent identifier "' + agent_id + '"')
        if agent_id == 'alphabeta':
            return upo.connect4.agents.AlphaBetaMinimaxComputerAgent(agent_index, GameDifficulty.str2int(args.difficulty))
        if agent_id == 'firstfit':
            return upo.connect4.agents.FirstFitComputerAgent(agent_index)
        if agent_id == 'expectimax':
            return upo.connect4.agents.ExpectimaxComputerAgent(agent_index, GameDifficulty.str2int(args.difficulty))
        if agent_id == 'human':
            return upo.connect4.agents.HumanAgent(agent_index)
        if agent_id == 'minimax':
            return upo.connect4.agents.MinimaxComputerAgent(agent_index, GameDifficulty.str2int(args.difficulty))
        if agent_id == 'random':
            return upo.connect4.agents.RandomComputerAgent(agent_index)

    @classmethod
    def get_available_agents(cls):
        return cls.ids


def parse_options():
    parser = argparse.ArgumentParser(description="UPO :: Connect 4 game")

    parser.add_argument('-a', '--agent', action='append', dest='agents',
                        choices=AgentFactory.get_available_agents(),
                        help='A player agent', default=[])
    parser.add_argument('--fps', dest='fps', type=int,
                        help='Number of frames per second', default=30)
    parser.add_argument('-g', '--geometry', dest='geometry', type=int, nargs=2,
                        help='A pair of two numbers specifying the width and height (in pixels) of the whole window', default=[640, 480])
    parser.add_argument('-l', '--layout', dest='layout', type=int, nargs=2,
                        help='A pair of two numbers specifying the width and height (in number of tiles) of the game board', default=[7, 6])
    parser.add_argument('-d', '--difficulty', dest='difficulty', type=str,
                        help='The level of difficulty of the game (valid only for intelligent computer agents', default=str(GameDifficulty.default_difficulty))

    args = parser.parse_args()

    # We need at least two agents
    while len(args.agents) <= 1:
        args.agents.append('random')

    return args


if __name__ == '__main__':
    args = parse_options()
    #print('Command-line Arguments: ', args)
    #rng_state = ...
    #random.setstate(rng_state)
    rng_state = random.getstate()
    #print "Random State: ", rng_state
    agent_factory = AgentFactory()
    agents = []
    agent_idx = 0
    for agent in args.agents:
        agents.append(agent_factory.make_agent(agent, agent_idx, args))
        agent_idx += 1
    #agents = [upo.connect4.agents.RandomComputerAgent(0),
    #          upo.connect4.agents.RandomComputerAgent(1)]
    game = upo.connect4.game.Game(agents, args.layout)
    ui = upo.connect4.ui.PyGameUI(game, args.geometry, args.fps)
    ui.show()
