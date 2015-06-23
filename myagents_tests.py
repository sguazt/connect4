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


import upo.connect4.agents
import upo.connect4.game
import myagents


def do_test_evalfunc():
    """
        board(7x6) = [             ] (row 0)
                     [             ] (row 1)
                     [             ] (row 2)
                     [             ] (row 3)
                     [      1      ] (row 4)
                     [      0   0  ] (row 5)
                     ---------------
             column:  0 1 2 3 4 5 6
        board[column,row] -> token (a integer number >= 0, denoting the agent
        who pushed to token)
    """
    layout = (7, 6)
    num_agents = 2
    depth = 2*num_agents
    verbose = 2
    
    game_state = upo.connect4.game.GameState(layout, num_agents)
    game_state.set_verbosity_level(verbose)

    #[TODO]: Change the content of the board to setup a specific game state
    
    # Fill 1st column
    # Fill 2nd column
    game_state.make_move(1, 1)
    # Fill 3rd column
    #game_state.make_move(0, 2)
    #game_state.make_move(1, 2)
    # Fill 4th column
    game_state.make_move(0, 3)
    game_state.make_move(1, 3)
    # Fill 5th column
    #game_state.make_move(0, 4)
    # Fill 6th column
    game_state.make_move(0, 5)
    # Fill 7th column
    
    #[/TODO]

    # Setup first player (RED agent)
    red_agent = upo.connect4.agents.AlphaBetaMinimaxComputerAgent(0, depth)
    #red_agent.set_verbosity_level(verbose) # Uncomment if you need to know what RED agent is doing
    # Setup second player (YELLOW agent)
    yellow_agent = upo.connect4.agents.AlphaBetaMinimaxComputerAgent(1, depth, myagents.better_evaluation_function)
    yellow_agent.set_verbosity_level(verbose)

    print('Current State: ', game_state)
    yellow_action = yellow_agent.get_action(game_state)
    print('YELLOW moves: ', yellow_action)
    game_state.make_move(yellow_agent.get_index(), yellow_action)
    print('New State: ', game_state)


if __name__ == '__main__':
    do_test_evalfunc()
