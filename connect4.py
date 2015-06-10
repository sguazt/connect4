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
import random
import upo.connect4.agents
import upo.connect4.game
import upo.connect4.ui



class AgentFactory:
    EASY_LEVEL = 2
    MEDIUM_LEVEL = 3
    HARD_LEVEL = 4
    NOHOPE_LEVEL = -1
    DEFAULT_DEPTH = EASY_LEVEL

    def __init__(self):
        self.ids = ['alphabeta', 'expectimax', 'firstfit', 'human', 'minimax', 'random']

    def get_available_agents(self):
        return self.ids

    def make_agent(self, agent_id, agent_index, *args):
        #if agent_id not in self.ids:
        #    raise Exception('Unknown agent identifier "' + agent_id + '"')
        if agent_id == 'alphabeta':
            return upo.connect4.agents.AlphaBetaMinimaxComputerAgent(agent_index, self.DEFAULT_DEPTH)
        if agent_id == 'firstfit':
            return upo.connect4.agents.FirstFitComputerAgent(agent_index)
        if agent_id == 'expectimax':
            return upo.connect4.agents.ExpectimaxComputerAgent(agent_index, self.DEFAULT_DEPTH)
        if agent_id == 'human':
            return upo.connect4.agents.HumanAgent(agent_index)
        if agent_id == 'minimax':
            return upo.connect4.agents.MinimaxComputerAgent(agent_index, self.DEFAULT_DEPTH)
        if agent_id == 'random':
            return upo.connect4.agents.RandomComputerAgent(agent_index)

def parse_options():
    parser = argparse.ArgumentParser(description="UPO :: Connect 4 game")

    parser.add_argument('-a', '--agent', action='append', dest='agents',
                        choices=AgentFactory().get_available_agents(),
                        help='A player agent', default=[])
    parser.add_argument('--fps', dest='fps', type=int,
                        help='Number of frames per second', default=30)
    parser.add_argument('-g', '--geometry', dest='geometry', type=int, nargs=2,
                        help='A pair of two numbers specifying the width and height (in pixels) of the whole window', default=[640, 480])
    parser.add_argument('-l', '--layout', dest='layout', type=int, nargs=2,
                        help='A pair of two numbers specifying the width and height (in number of tiles) of the game board', default=[7, 6])

    args = parser.parse_args()

    # We need at least two agents
    while len(args.agents) <= 1:
        args.agents.append('random')

    return args


if __name__ == '__main__':
    args = parse_options()
    #print 'Command-line Arguments: ', args
    #rng_state = ...
    #random.setstate(rng_state)
    rng_state = random.getstate()
    #print "Random State: ", rng_state
    agent_factory = AgentFactory()
    agents = []
    agent_idx = 0
    for agent in args.agents:
        agents.append(agent_factory.make_agent(agent, agent_idx))
        agent_idx += 1
    #agents = [upo.connect4.agents.RandomComputerAgent(0),
    #          upo.connect4.agents.RandomComputerAgent(1)]
    game = upo.connect4.game.Game(agents, args.layout)
    ui = upo.connect4.ui.PyGameUI(game, args.geometry, args.fps)
    ui.show()
