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


import pathlib
import random
import upo.connect4.agents
import upo.connect4.game
import upo.utils


verbosity = 2


def make_schedule(players):
    indices = list(range(len(players)))
    random.shuffle(indices)
    schedule = []
    for i in range(len(players)//2):
        schedule.append([players[indices[0]], players[indices[1]]])
        indices.pop(0)
        indices.pop(0)
    return schedule


def play_schedule(schedule):
    winners = []
    for match in schedule:
        if verbosity > 1:
            print('\n\nMatch ', match[0], ' vs. ', match[1])

        evalfunc1 = upo.utils.import_lib(match[0])
        evalfunc2 = upo.utils.import_lib(match[1])

        nrun = 4
        depth = 4
        match_winners = []
        match_stats = {match[0]: {'win_count': 0, 'nmoves': 0, 'nstates': 0, 'timings': 0},
                       match[1]: {'win_count': 0, 'nmoves': 0, 'nstates': 0, 'timings': 0}}
        for r in range(nrun):
            agents = []
            red_agent = yellow_agent = None
            if r < (nrun//2):
                red_agent = upo.connect4.agents.AlphaBetaMinimaxComputerAgent(0, depth, evalfunc1)
                red_agent.set_name(match[0])
                yellow_agent = upo.connect4.agents.AlphaBetaMinimaxComputerAgent(1, depth, evalfunc2)
                yellow_agent.set_name(match[1])
            else:
                red_agent = upo.connect4.agents.AlphaBetaMinimaxComputerAgent(0, depth, evalfunc2)
                red_agent.set_name(match[1])
                yellow_agent = upo.connect4.agents.AlphaBetaMinimaxComputerAgent(1, depth, evalfunc1)
                yellow_agent.set_name(match[0])
            agents = [red_agent, yellow_agent]

            if verbosity > 1:
                print('Run #', r, ' -> RED: ', red_agent.get_name(), ', YELLOW: ', yellow_agent.get_name())

            game = upo.connect4.game.Game(agents, (7,6))
            while not game.is_over():
                game.make_move()
            match_stats[red_agent.get_name()]['nmoves'] += game.get_stats().get_tot_num_moves(red_agent.get_index())
            match_stats[red_agent.get_name()]['nstates'] += game.get_stats().get_tot_expanded_states(red_agent.get_index())
            match_stats[red_agent.get_name()]['timings'] += game.get_stats().get_tot_elapsed_time(red_agent.get_index())
            match_stats[yellow_agent.get_name()]['nmoves'] += game.get_stats().get_tot_num_moves(yellow_agent.get_index())
            match_stats[yellow_agent.get_name()]['nstates'] += game.get_stats().get_tot_expanded_states(yellow_agent.get_index())
            match_stats[yellow_agent.get_name()]['timings'] += game.get_stats().get_tot_elapsed_time(yellow_agent.get_index())
            if game.get_state().is_win():
                winning_cells = game.get_state().get_winner_positions()
                winning_agent = game.get_agent(game.get_state().get_winner())
                if verbosity > 1:
                    print('-> Run ', r, ' is won by ' + winning_agent.get_name() + '!')
                match_stats[winning_agent.get_name()]['win_count'] += 1
            else:
                if verbosity > 1:
                    print('-> Run #', r, ' ended with a tie!')
            if verbosity > 1:
                print('Statitics:')
                print('* ', red_agent.get_name(), ':')
                print('  - Number of moves: ', game.get_stats().get_tot_num_moves(red_agent.get_index())) 
                print('  - Elapsed time: ', game.get_stats().get_tot_elapsed_time(red_agent.get_index())) 
                print('  - Number of expanded states: ', game.get_stats().get_tot_expanded_states(red_agent.get_index())) 
                print('* ', yellow_agent.get_name(), ':')
                print('  - Number of moves: ', game.get_stats().get_tot_num_moves(yellow_agent.get_index())) 
                print('  - Elapsed time: ', game.get_stats().get_tot_elapsed_time(yellow_agent.get_index())) 
                print('  - Number of expanded states: ', game.get_stats().get_tot_expanded_states(yellow_agent.get_index())) 
        if match_stats[match[0]]['win_count'] > match_stats[match[1]]['win_count']:
            match_winners.append(match[0])
        elif match_stats[match[1]]['win_count'] > match_stats[match[0]]['win_count']:
            match_winners.append(match[1])
        else:
            if match_stats[match[0]]['nmoves'] < match_stats[match[1]]['nmoves']:
                match_winners.append(match[0])
            elif match_stats[match[1]]['nmoves'] < match_stats[match[0]]['nmoves']:
                match_winners.append(match[1])
            else:
                if match_stats[match[0]]['nstates'] < match_stats[match[1]]['nstates']:
                    match_winners.append(match[0])
                elif match_stats[match[1]]['nstates'] < match_stats[match[0]]['nstates']:
                    match_winners.append(match[1])
                else:
                    if match_stats[match[0]]['timings'] < match_stats[match[1]]['timings']:
                        match_winners.append(match[0])
                    elif match_stats[match[1]]['timings'] < match_stats[match[0]]['timings']:
                        match_winners.append(match[1])
                    else:
                        match_winners.append(match[0])
                        match_winners.append(match[1])

        if verbosity > 1:
            if len(match_winners) > 1:
                print('\n\n-> Match ', match[0], ' vs. ', match[1], ' ended with a draw!')
            else:
                print('\n\n-> Match ', match[0], ' vs. ', match[1], ' is won by ', match_winners[0], '!')

        for w in match_winners:
            winners.append(w)

    return winners


def main():

    # Retrieve the script names containing agents' implementation
    path = pathlib.Path('./tournament')
    module_prefix = 'tournament.'
    modules = []
    for f in path.glob('*.py'):
        if f.name != '__init__.py':
            modules.append(module_prefix + f.stem + '.better_evaluation_function')
    #print('Modules: ', modules)

    # Check for bad modules and throw them away
    safe_modules = []
    for m in modules:
        try:
            upo.utils.import_lib(m)
            safe_modules.append(m)
        except:
            print('Agent: ', m, ' cannot be loaded')

    if verbosity > 0:
        print('Agents: ', safe_modules)

    random.seed(5489) # Just fix the seed to make executions reproducible

    #schedule = make_schedule(safe_modules)

    #if verbosity > 0:
    #    print('Schedule #', i, ': ', schedule)

    #winners = play_schedule(schedule)
    #if verbosity > 0:
    #    print('-> Schedule #', i, ' Winners: ', winners)

    i = 0
    winners = safe_modules
    old_winners_len = 0
    while len(winners) > 1 and old_winners_len != len(winners):
        i += 1
        if verbosity > 0:
            print('\n\n')
        schedule = make_schedule(winners)
        if verbosity > 0:
            print('Schedule #', i, ': ', schedule)
        old_winners_len = len(winners)
        winners = play_schedule(schedule)
        if verbosity > 0:
            print('-> Schedule #', i, ' Winners: ', winners)
        if len(winners) > 1 and (len(winners) % 2) != 0:
            tie_agents = []
            tie_agent_idx = random.choice(range(len(winners)))
            tie_agents.append(winners[tie_agent_idx])
            winners.pop(tie_agent_idx)
            tie_agent_idx = random.choice(range(len(winners)))
            tie_agents.append(winners[tie_agent_idx])
            winners.pop(tie_agent_idx)
            tie_schedule = make_schedule(tie_agents)
            if verbosity > 0:
                print('Tie-breaker Schedule #', i, ': ', tie_schedule)
            tie_winners = play_schedule(tie_schedule)
            if verbosity > 0:
                print('-> Tie-breaker Schedule #', i, ' Winners: ', tie_winners)
            if len(tie_winners) > 1:
                # OK just choose one at random
                tie_winners = [random.choice(tie_winners)]
                if verbosity > 0:
                    print('-> Unable to tie-broken current schedule. Random winner is: ', tie_winners)
            winners.append(tie_winners[0])

    print('-> The final winner is: ', winners)

    # Play a match with instructor's agent
    if verbosity > 0:
        print("\nLet's play against the instructor...")
    instructor_evalfunc = 'myagents_instructor.better_evaluation_function'
    masters = []
    for winner in winners:
        i += 1
        schedule = make_schedule([winner, instructor_evalfunc])
        if verbosity > 0:
            print('Schedule #', i, ': ', schedule)
        tmp_winners = play_schedule(schedule)
        if verbosity > 0:
            print('-> Schedule #', i, ' Winners: ', tmp_winners)

        if winner in tmp_winners:
            masters.append(winner)

    if len(masters) > 0:
        for master in masters:
            print('-> Congratulations!! ', master, ' is a master of Connect 4')
    else:
        print('-> Nobody is able to beat the instructor!')


if __name__ == '__main__':
    import sys
    sys.stdout.flush()
    main()
