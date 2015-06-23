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
        #upo.utils.raise_undefined_method()
        
        legals = game_state.get_legal_actions()
        if len(legals) == 0:
            return None
        return max(legals)


################################################################################


class EnhancedRandomComputerAgent(upo.connect4.agents.ComputerAgent):
    """
    A smart computer-controlled agent that chooses its actions at
    random.
    """
    def get_action(self, game_state):
        """
        Returns the next move (i.e., a column) to play, if any; otherwise, returns None.
        """
        #TODO: put here your implementation
        #upo.utils.raise_undefined_method()
        
        # Retrieves the list of al possible valid actions that can be performed
        # in the given game state
        legals = game_state.get_legal_actions()
        if len(legals) == 0:
            return None
        blocking_actions = []
        for action in legals:
            for agent_index in range(game_state.num_agents()):
                next_state = game_state.generate_successor(agent_index, action)
                if next_state.is_win():
                    # This action leads to a state where either this agent is a
                    # winner or is a loser.
                    # In case of a winning action, chooses it immediately.
                    # In case of a losing action, before choosing it to prevent
                    # an another agent to win, check if there is some other
                    # action that will lead to a win for this agent
                    if agent_index == self.get_index():
                        return action
                    blocking_actions.append(action)
        if len(blocking_actions) > 0:
            # Avoid that another agent wins in the next move
            # NOTE: if there are more than 1 actions, there is no way to block
            #       all of them.
            #       So choose one of them at random
            return random.choice(blocking_actions)
        # Randomly chooses an action among the legal ones
        return random.choice(legals)


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


def score4_evaluation_function(game_state, agent, **context):
    """
    This evaluation function comes from Score4 project:
    https://github.com/ttsiodras/Score4

    "Speaking of the scoreBoard function, I tried various forms to evaluate the
     board. I ended up on a simple policy: measuring how many chips of the same
     color exist, in spans of 4 going in any direction. I do this over each of
     the board's cells, and then aggregate this in a table keeping the
     aggregates from -4 to 4:

     -4 means that the cell is a part of 4 cells that contain 4 yellow chips
     -3 means that the cell is a part of 4 cells that contain 3 yellow chips
     ...
     3 means that the cell is a part of 4 cells that contain 3 orange chips
     4 means that the cell is a part of 4 cells that contain 4 orange chips 

     If 4 is found, the board is a win for the Orange player, and the function
     returns orangeWins (i.e. 1000000). If -4 is found, the board is a win for
     the Yellow player, and the function returns yellowWins (i.e. -1000000).
     Otherwise, scaling factors are applied, so that the more '3'-cells found,
     the more positive the board's score. Correspondingly, the more '-3' found,
     the more negative the board's score."
    """
    agent_index = agent.get_index()

    counters = [0] * 9

    board = game_state.get_board()
    # Horizontal spans
    for r in range(board.height()):
        score = 0
        for k in range(3):
            if board.has_token(k, r):
                if board.get_token(k, r) == agent_index:
                    score += 1
                else:
                    score -= 1
        for c in range(3, board.width()):
            if board.has_token(c, r):
                if board.get_token(c, r) == agent_index:
                    score += 1
                else:
                    score -= 1
            counters[int(score) + 4] += 1
            if board.has_token(c-3, r):
                if board.get_token(c-3, r) == agent_index:
                    score -= 1
                else:
                    score += 1

    # Vertical spans
    for c in range(board.width()):
        score = 0
        for k in range(3):
            if board.has_token(c, k):
                if board.get_token(c, k) == agent_index:
                    score += 1
                else:
                    score -= 1
        for r in range(3, board.height()):
            if board.has_token(c, r):
                if board.get_token(c, r) == agent_index:
                    score += 1
                else:
                    score -= 1
            counters[score + 4] += 1
            if board.has_token(c, r-3):
                if board.get_token(c, r-3) == agent_index:
                    score -= 1
                else:
                    score += 1

    # Down-right (and up-left) diagonals
    for r in range(board.height()-3):
        for c in range(board.width()-3):
            score = 0
            for k in range(4):
                rr = r + k
                cc = c + k
                if board.has_token(cc, rr):
                    if board.get_token(cc, rr) == agent_index:
                        score += 1
                    else:
                        score -= 1
            counters[score + 4] += 1

    # up-right (and down-left) diagonals
    for r in range(3,board.height()):
        for c in range(board.width()-3):
            score = 0
            for k in range(4):
                rr = r - k
                cc = c + k
                if board.has_token(cc, rr):
                    if board.get_token(cc, rr) == agent_index:
                        score += 1
                    else:
                        score -= 1
            counters[score + 4] += 1

    max_score = 1000000
    score = 0.0

    if counters[0] != 0:
        score = -max_score
    elif counters[8] != 0:
        score = max_score
    else:
        score = (counters[5] + 2*counters[6] + 5*counters[7] - counters[3] - 2*counters[2] - 5*counters[1])

    score /= max_score

    print("Agent: ", agent_index, ", State: ", game_state, ", Counter: ", counters, " =>  Score: ", score)

    return score


################################################################################


def gnome_all_adjacent_empty(board, c, r):
    for k in range(-1, 2):
        for l in range(-1, 2):
            if k == 0 and l == 0:
                continue
            if ((r + k) >= 0 and
                (r + k) < board.height() and
                (c + l) >= 0 and
                (c + l) < board.width()
                and board.has_token(r + k, c + l)):
                return False

    return True

def gnome_count_3_in_a_row(game_state, token):
    board = game_state.get_board()
    count = 0
    for c in range(board.width()):
        for r in range(board.height()):
            if not board.has_token(c, r):
                break
            if gnome_all_adjacent_empty(board, c, r):
                continue;
            game_state.make_move(token, c)
            if game_state.is_win():
                count += 1
            game_state.unmake_move(c)
    return count


def gnome_evaluation_function(game_state, agent, **context):
    """
    This function is the one found in the Gnome 4-in-a-row game:
    https://github.com/GNOME/four-in-a-row
    """
    agent_index = agent.get_index()

    board = game_state.get_board()

    count = gnome_count_3_in_a_row(game_state, agent_index) - gnome_count_3_in_a_row(game_state, (agent_index+1) % game_state.num_agents())

    score = random.randrange(1, 49) if count == 0 else count*100

    print("Agent: ", agent_index, ", State: ", game_state, " =>  Score: ", score)

    return score

################################################################################


def jc4_calculate_score(aiScore, moreMoves):
    moveScore = 4 - moreMoves
    if aiScore == 0:
        return 0
    if aiScore == 1:
        return 1*moveScore
    if aiScore == 2:
        return 10*moveScore
    if aiScore == 3:
        return 100*moveScore
    return 1000

def jc4_evaluation_function(game_state, agent, **context):
    """
    This evaluation function comes from the JC4 game:
    http://sourceforge.net/projects/jc4/
    """

    agent_index = agent.get_index()

    board = game_state.get_board()

    aiScore=1
    score=0
    blanks = 0
    k=0
    moreMoves=0
    for i in range(board.height()-1, -1, -1):
        for j in range(board.width()):

            if not board.has_token(j, i) or board.get_token(j, i) != agent_index:
                continue

            if j <= 3:
                for k in range(1, 4):
                    if not board.has_token(j+k, i):
                        blanks += 1
                    elif board.get_token(j+k, i) == agent_index:
                        aiScore += 1
                    else:
                        aiScore = 0
                        blanks = 0
                        break

                moreMoves = 0;
                if blanks > 0:
                    for c in range(1, 4):
                        column = j+c
                        for m in range(i, board.heigth()):
                            if board.has_token(column, m):
                                break
                            else:
                                moreMoves += 1

                if moreMoves != 0:
                    score += jc4_calculate_score(aiScore, moreMoves)
                aiScore = 1
                blanks = 0

            if i >= 3:
                for k in range(1, 4):
                    if board.get_token(j, i-k) == agent_index:
                        aiScore += 1
                    elif board.get_token(j, i-k) != agent_index:
                        aiScore=0
                        break
                moreMoves = 0

                if aiScore > 0:
                    column = j
                    for m in range(i-k+1, i):
                        if board.has_token(column, m):
                            break
                        else:
                            moreMoves += 1
                if moreMoves!=0:
                    score += jc4_calculate_score(aiScore, moreMoves)
                aiScore = 1
                blanks = 0

            if j >= 3:
                for k in range(1, 4):
                    if not board.has_token(j-k, i):
                        blanks += 1
                    elif board.get_token(j-k, i) == agent_index:
                        aiScore += 1
                    else:
                        aiScore = 0
                        blanks = 0
                        break
                moreMoves = 0
                if blanks > 0:
                    for c in range(1, 4):
                        column = j- c
                        for m in range(i, board.height()):
                            if board.has_token(column, m):
                                break
                            else:
                                moreMoves += 1

                if moreMoves != 0:
                    score += jc4_calculate_score(aiScore, moreMoves)
                aiScore = 1
                blanks = 0

            if j <= 3 and i >= 3:
                for k in range(1, 4):
                    if not board.has_token(j+k, i-k):
                        blanks += 1
                    if board.get_token(j+k, i-k) == agent_index:
                        aiScore += 1
                    else:
                        aiScore = 0
                        blanks = 0
                        break
                moreMoves = 0
                if blanks > 0:
                    for c in range(1, 4):
                        column = j+c
                        row = i-c
                        for m in range(row, board.height()):
                            if not board.has_token(column, m):
                                moreMoves += 1
                            elif board.get_token(column, m) != agent_index:
                                break
                    if moreMoves != 0:
                        score += jc4_calculate_score(aiScore, moreMoves)
                    aiScore = 1
                    blanks = 0
            if i >= 3 and j >= 3:
                for k in range(1, 4):
                    if not board.has_token(j-k, i-k):
                        blanks += 1
                    elif board.get_token(j-k, i-k) == agent_index:
                        aiScore += 1
                    else:
                        aiScore = 0
                        blanks = 0
                        break
                moreMoves = 0
                if blanks > 0:
                    for c in range(1, 4):
                        column = j-c
                        row = i-c
                        for m in range(row, board.height()):
                            if not board.has_token(column, m):
                                moreMoves += 1
                            elif board.get_token(column, m) != agent_index:
                                break
                    if moreMoves != 0:
                        score += jc4_calculate_score(aiScore, moreMoves)
                    aiScore = 1
                    blanks = 0
        return score;


################################################################################


def lookahead_evaluation_function(game_state, agent, **context):
    """
    This function tries to improve the basic evaluation function by
    using a 1 step look-ahead to see what happens in the next move.
    """
    agent_index = agent.get_index()

    depth = 0
    if 'depth' in context:
        depth = context['depth']//game_state.num_agents()

    max_score = 100.0*game_state.get_board().width()*game_state.get_board().height()

    if game_state.is_final():
        if game_state.is_winner(agent_index):
            score = max_score
        elif game_state.is_tie():
            score = 0.0
        else:
            score = -max_score
    else:
        my_win_weight = 0.5
        your_win_weight = -1.0

        final_actions = 0
        winning_actions = 0
        losing_actions = 0
        for c in game_state.get_legal_actions():
            for a in range(game_state.num_agents()):
                game_state.make_move(a, c)
                if game_state.is_final():
                    final_actions += 1
                    if game_state.is_win():
                        if game_state.is_winner(agent_index):
                            winning_actions += 1
                        else:
                            losing_actions += 1
                game_state.unmake_move(c)
        if final_actions > 0:
            #score = (winning_actions-losing_actions)/final_actions
            score = (my_win_weigth*winning_actions+your_win_weight*losing_actions)/max_score
        else:
            #score = 0.0
            score = random.random() # Pick a value in [0,1) at random
        score /= (depth if depth > 0 else 1)
    return score


################################################################################


#def score_cell(board, x, y, token):
#    if board.has_token(x, y):
#        if board.get_token(x, y) == token:
#            return 1.0
#        return -1.0
#    return 0.0
#
#def count_blocked_threats_old(game_state, agent_index, threat_len):
#    board = game_state.get_board()
#
#    count = 0
#    for c in range(board.width()):
#        for r in range(board.get_column_empty_row(c)+1, board.height()):
#            # check horizontal '-' pattern
#            if c < (board.width()-threat_len+1):
#                token_sum = 0
#                for k in range(threat_len):
#                    if board.has_token(c+k, r):
#                        token_sum += board.get_token(c+k, r)
#                for other_agent_index in range(game_state.num_agents()):
#                    if other_agent_index != agent_index and token_sum == ((threat_len-1)*other_agent_index+agent_index):
#                        count += 1
#            # check vertical '|' pattern
#            if r < (board.height()-threat_len+1):
#                token_sum = 0
#                for k in range(threat_len):
#                    if board.has_token(c, r+k):
#                        token_sum += board.get_token(c, r+k)
#                for other_agent_index in range(game_state.num_agents()):
#                    if other_agent_index != agent_index and token_sum == ((threat_len-1)*other_agent_index+agent_index):
#                        count += 1
#            # check left diagonal '\' pattern
#            if (c < (board.width()-threat_len+1) and
#                r < (board.height()-threat_len+1)):
#                token_sum = 0
#                for k in range(threat_len):
#                    if board.has_token(c+k, r+k):
#                        token_sum += board.get_token(c+k, r+k)
#                for other_agent_index in range(game_state.num_agents()):
#                    if other_agent_index != agent_index and token_sum == ((threat_len-1)*other_agent_index+agent_index):
#                        count += 1
#            # check right diagonal '/' pattern
#            if (c >= 3 and
#                r < (board.height()-threat_len+1)):
#                token_sum = 0
#                for k in range(threat_len):
#                    if board.has_token(c-k, r+k):
#                        token_sum += board.get_token(c-k, r+k)
#                for other_agent_index in range(game_state.num_agents()):
#                    if other_agent_index != agent_index and token_sum == ((threat_len-1)*other_agent_index+agent_index):
#                        count += 1
#
#    return count
#
#def count_win_opportunities_old(game_state, agent_index):
#    board = game_state.get_board()
#
#    count = 0
#    for c in range(board.width()):
#        for r in range(board.get_column_empty_row(c), board.height()):
#            # check horizontal '-' pattern
#            if c < (board.width()-3):
#                token_sum = 0
#                for k in range(4):
#                    if board.has_token(c+k, r):
#                        token_sum += board.get_token(c+k, r)
#                if token_sum == 3*agent_index:
#                    count += 1
#            # check vertical '|' pattern
#            if r < (board.height()-3):
#                token_sum = 0
#                for k in range(4):
#                    if board.has_token(c, r+k):
#                        token_sum += board.get_token(c, r+k)
#                if token_sum == 3*agent_index:
#                    count += 1
#            # check left diagonal '\' pattern
#            if (c < (board.width()-3) and
#                r < (board.height()-3)):
#                token_sum = 0
#                for k in range(4):
#                    if board.has_token(c+k, r+k):
#                        token_sum += board.get_token(c+k, r+k)
#                if token_sum == 3*agent_index:
#                    count += 1
#            # check right diagonal '/' pattern
#            if (c >= 3 and
#                r < (board.height()-3)):
#                token_sum = 0
#                for k in range(4):
#                    if board.has_token(c-k, r+k):
#                        token_sum += board.get_token(c-k, r+k)
#                if token_sum == 3*agent_index:
#                    count += 1
#    return count
#
#def score_lookahead(game_state, current_agent_index, lookahead, max_score):
#    if lookahead == 0:
#        return 0.0
#
#    score = 0.0
#    found_final = False
#    for x in range(game_state.get_board().width()):
#        for other_agent_index in range(game_state.num_agents()):
#            if other_agent_index == current_agent_index:
#                continue
#            game_state.make_move(other_agent_index, x)
#            if game_state.is_final():
#                if game_state.is_win():
#                    score += max_score if other_agent_index == current_agent_index else -max_score
#                    found_final = True
#            else:
#                score += score_lookahead(game_state, current_agent_index, lookahead-1, max_score)
#            game_state.unmake_move(x)
#            if found_final:
#                break
#        if found_final:
#            break
#    print("Lookahead ", (2-lookahead+1), " => Score: ", score)
#    return score


def count_blocked_threats(game_state, agent_index, threat_len):
    threat_patterns =  {2: [0b0011,0b0101,0b0110,0b1010,0b1100,0b1001], # threats of length 2
                        3: [0b0111,0b1011,0b1101,0b1110]}; # threats of length 3

    if threat_len not in threat_patterns:
        raise Exception('Unknown threat length')

    board = game_state.get_board()

    expected_num_blanks = 4-threat_len-1 # e.g., threat_len==3 -> expected_num_blanks = 1 (i.e, exactly one blank expected)
    #min_pattern_val = 2**threat_len-1 # e.g., threat_len==3 -> min value is 0b0111 == 2^3-1
    other_agents = [x for x in range(game_state.num_agents())]
    other_agents.pop(agent_index)
    count = 0
    for c in range(board.width()):
        r0 = max(board.get_column_empty_row(c)-expected_num_blanks+1, 0)
        for r in range(r0, board.height()):
            #cur_patterns = []
            # check horizontal '-' pattern
            if (c < (board.width()-3) and
                all([(r >= board.get_column_empty_row(c+k)) for k in range(1,4)])):
                for other_agent_index in other_agents:
                    cur_pattern = 0
                    num_blanks = 0
                    valid_pattern = True
                    for k in range(4):
                        if board.has_token(c+k, r):
                            cur_pattern <<= 1
                            if board.get_token(c+k, r) == other_agent_index:
                                cur_pattern |= 1
                            elif board.get_token(c+k, r) != agent_index:
                                # Invalid pattern
                                valid_pattern = False
                                break
                        else:
                            cur_pattern <<= 1
                            num_blanks += 1
                    if valid_pattern and num_blanks == expected_num_blanks and cur_pattern in threat_patterns[threat_len]:
                        #print("Found horizontal threat of len ", threat_len, " at (", (c,r), ") - num blanks: ", num_blanks, " - pattern: ", cur_pattern)
                        count += 1
            # check vertical '|' pattern
            if r < (board.height()-3):
                for other_agent_index in other_agents:
                    cur_pattern = 0
                    num_blanks = 0
                    valid_pattern = True
                    for k in range(4):
                        if board.has_token(c, r+k):
                            cur_pattern <<= 1
                            if board.get_token(c, r+k) == other_agent_index:
                                cur_pattern |= 1
                            elif board.get_token(c, r+k) != agent_index:
                                # Invalid pattern
                                valid_pattern = False
                                break
                        else:
                            cur_pattern <<= 1
                            num_blanks += 1
                    if valid_pattern and num_blanks == expected_num_blanks and cur_pattern in threat_patterns[threat_len]:
                        #print("Found vertical threat of len ", threat_len, " at (", (c,r), ") - num blanks: ", num_blanks, " - pattern: ", cur_pattern)
                        count += 1
            # check left diagonal '\' pattern
            if (c < (board.width()-3) and
                r < (board.height()-3) and
                all([((r+k) >= board.get_column_empty_row(c+k)) for k in range(1,4)])):
                for other_agent_index in other_agents:
                    cur_pattern = 0
                    num_blanks = 0
                    valid_pattern = True
                    for k in range(4):
                        if board.has_token(c+k, r+k):
                            cur_pattern <<= 1
                            if board.get_token(c+k, r+k) == other_agent_index:
                                cur_pattern |= 1
                            elif board.get_token(c+k, r+k) != agent_index:
                                # Invalid pattern
                                valid_pattern = False
                                break
                        else:
                            cur_pattern <<= 1
                            num_blanks += 1
                    if valid_pattern and num_blanks == expected_num_blanks and cur_pattern in threat_patterns[threat_len]:
                        #print("Found left diagonal '\\' threat of len ", threat_len, " at (", (c,r), ") - num blanks: ", num_blanks, " - pattern: ", cur_pattern)
                        count += 1
            # check right diagonal '/' pattern
            if (c >= 3 and
                r < (board.height()-3) and
                all([((r+k) >= board.get_column_empty_row(c-k)) for k in range(1,4)])):
                for other_agent_index in other_agents:
                    cur_pattern = 0
                    num_blanks = 0
                    valid_pattern = True
                    for k in range(4):
                        if board.has_token(c-k, r+k):
                            cur_pattern <<= 1
                            if board.get_token(c-k, r+k) == other_agent_index:
                                cur_pattern |= 1
                            elif board.get_token(c-k, r+k) != agent_index:
                                # Invalid pattern
                                valid_pattern = False
                                break
                        else:
                            cur_pattern <<= 1
                            num_blanks += 1
                    if valid_pattern and num_blanks == expected_num_blanks and cur_pattern in threat_patterns[threat_len]:
                        #print("Found right diagonal '/' threat of len ", threat_len, " at (", (c,r), ") - num blanks: ", num_blanks, " - pattern: ", cur_pattern)
                        count += 1
            ## check found patterns against threat patterns
            #for threat_pattern in threat_patterns[threat_len]:
            #    for cur_pattern in cur_patterns:
            #        if cur_pattern == threat_pattern:
            #            count += 1
    return count

def count_winning_opportunities(game_state, agent_index, pattern_len):
    winning_patterns =  {2: [0b0011,0b0101,0b0110,0b1010,0b1100,0b1001], # patterns of length 2
                         3: [0b0111,0b1011,0b1101,0b1110]}; # patterns of length 3

    if pattern_len not in winning_patterns:
        raise Exception('Unknown pattern length')

    board = game_state.get_board()

    expected_num_blanks = 4-pattern_len
    min_pattern_val = 2**pattern_len-1 # e.g., pattern_len==3 -> min value is 0b0111 == 2^3-1
    count = 0
    for c in range(board.width()):
        r0 = max(board.get_column_empty_row(c)-expected_num_blanks, 0)
        for r in range(r0, board.height()):
            #cur_patterns = []
            # check horizontal '-' pattern
            if (c < (board.width()-3) and
                all([(r >= board.get_column_empty_row(c+k)) for k in range(1,4)])):
                cur_pattern = 0
                num_blanks = 0
                valid_pattern = True
                for k in range(4):
                    if board.has_token(c+k, r):
                        cur_pattern <<= 1
                        if board.get_token(c+k, r) == agent_index:
                            cur_pattern |= 1
                        else:
                            # Invalid pattern
                            valid_pattern = False
                            break
                    else:
                        cur_pattern <<= 1
                        num_blanks += 1
                if valid_pattern and num_blanks == expected_num_blanks and cur_pattern in winning_patterns[pattern_len]:
                    #print("Found horizontal winning opportunity of len ", pattern_len, " at (", (c,r), ") - num blanks: ", num_blanks, " - pattern: ", cur_pattern, ' - agent: ', agent_index)
                    count += 1
            # check vertical '|' pattern
            if r < (board.height()-3):
                cur_pattern = 0
                num_blanks = 0
                valid_pattern = True
                for k in range(4):
                    if board.has_token(c, r+k):
                        cur_pattern <<= 1
                        if board.get_token(c, r+k) == agent_index:
                            cur_pattern |= 1
                        else:
                            # Invalid pattern
                            valid_pattern = False
                            break
                    else:
                        cur_pattern <<= 1
                        num_blanks += 1
                if valid_pattern and num_blanks == expected_num_blanks and cur_pattern in winning_patterns[pattern_len]:
                    #print("Found vertical winning opportunity of len ", pattern_len, " at (", (c,r), ") - num blanks: ", num_blanks, " - pattern: ", cur_pattern, ' - agent: ', agent_index)
                    count += 1
            # check left diagonal '\' pattern
            if (c < (board.width()-3) and
                r < (board.height()-3) and
                all([((r+k) >= board.get_column_empty_row(c+k)) for k in range(1,4)])):
                cur_pattern = 0
                num_blanks = 0
                valid_pattern = True
                for k in range(4):
                    if board.has_token(c+k, r+k):
                        cur_pattern <<= 1
                        if board.get_token(c+k, r+k) == agent_index:
                            cur_pattern |= 1
                        else:
                            # Invalid pattern
                            valid_pattern = False
                            break
                    else:
                        cur_pattern <<= 1
                        num_blanks += 1
                if valid_pattern and num_blanks == expected_num_blanks and cur_pattern in winning_patterns[pattern_len]:
                    #print("Found left diagonal '\\' winning opportunity of len ", pattern_len, " at (", (c,r), ") - num blanks: ", num_blanks, " - pattern: ", cur_pattern, ' - agent: ', agent_index)
                    count += 1
            # check right diagonal '/' pattern
            if (c >= 3 and
                r < (board.height()-3) and
                all([((r+k) >= board.get_column_empty_row(c-k)) for k in range(1,4)])):
                cur_pattern = 0
                num_blanks = 0
                valid_pattern = True
                for k in range(4):
                    if board.has_token(c-k, r+k):
                        cur_pattern <<= 1
                        if board.get_token(c-k, r+k) == agent_index:
                            cur_pattern |= 1
                        else:
                            # Invalid pattern
                            valid_pattern = False
                            break
                    else:
                        cur_pattern <<= 1
                        num_blanks += 1
                if valid_pattern and num_blanks == expected_num_blanks and cur_pattern in winning_patterns[pattern_len]:
                    #print("Found right diagonal '/' winning opportunity of len ", pattern_len, " at (", (c,r), ") - num blanks: ", num_blanks, " - pattern: ", cur_pattern, ' - agent: ', agent_index)
                    count += 1

    return count

def token_patterns_evaluation_function(game_state, agent, **context):
    agent_index = agent.get_index()
    depth = 0
    if 'depth' in context:
        depth = context['depth']//game_state.num_agents()

    board = game_state.get_board()

    score = 0.0

    #max_score = float(board.height()*board.width()) # not realistic but OK
    #found_final = False
    #for x in range(board.width()):
    #    for y in range(board.get_column_empty_row(x)+1, board.height()):
    #        cell_score = score_cell(board, x, y, agent_index)
    #
    #        # check horizontal '-' pattern
    #        local_score = cell_score
    #        if x < (board.width()-1):
    #            local_score += score_cell(board, x+1, y, agent_index)
    #        if x < (board.width()-2):
    #            local_score += score_cell(board, x+2, y, agent_index)
    #        if x < (board.width()-3):
    #            local_score += score_cell(board, x+3, y, agent_index)
    #        if abs(local_score) >= 4:
    #            score = max_score if local_score > 0 else -max_score
    #            found_final = True
    #            break
    #        score += local_score
    #
    #        # check right diagonal '/' pattern
    #        local_score = cell_score
    #        if x > 0 and y > 0:
    #            local_score += score_cell(board, x-1, y-1, agent_index)
    #        if x > 1 and y > 1:
    #            local_score += score_cell(board, x-2, y-2, agent_index)
    #        if x > 2 and y > 2:
    #            local_score += score_cell(board, x-3, y-3, agent_index)
    #        if abs(local_score) >= 4:
    #            score = max_score if local_score > 0 else -max_score
    #            found_final = True
    #            break
    #
    #        # check left diagonal '\' pattern
    #        local_score = cell_score
    #        if x < (board.width()-1) and y < (board.height()-1):
    #            local_score += score_cell(board, x+1, y+1, agent_index)
    #        if x < (board.width()-2) and y < (board.height()-2):
    #            local_score += score_cell(board, x+2, y+2, agent_index)
    #        if x < (board.width()-3) and y < (board.height()-3):
    #            local_score += score_cell(board, x+3, y+3, agent_index)
    #        if abs(local_score) >= 4:
    #            score = max_score if local_score > 0 else -max_score
    #            found_final = True
    #            break
    #
    #        # check vertical '|' pattern
    #        local_score = cell_score
    #        if y < (board.height()-1):
    #            local_score += score_cell(board, x, y+1, agent_index)
    #        if y < (board.height()-2):
    #            local_score += score_cell(board, x, y+2, agent_index)
    #        if y < (board.height()-3):
    #            local_score += score_cell(board, x, y+3, agent_index)
    #        if abs(local_score) >= 4:
    #            score = max_score if local_score > 0 else -max_score
    #            found_final = True
    #            break
    #
    #    if found_final:
    #        break

    ## check horizontal '-' pattern
    #found_final = False
    #for x in range(0, board.width(), 4):
    #    #for y in range(board.get_column_empty_row(x)+1, board.height()):
    #    for y in range(board.height()):
    #        cell_score = score_cell(board, x, y, agent_index)
    #        local_score = cell_score
    #        if x < (board.width()-1):
    #            local_score += score_cell(board, x+1, y, agent_index)
    #        if x < (board.width()-2):
    #            local_score += score_cell(board, x+2, y, agent_index)
    #        if x < (board.width()-3):
    #            local_score += score_cell(board, x+3, y, agent_index)
    #        print("Horizontal pattern -> Local Score: ", local_score)
    #        if abs(local_score) >= 4:
    #            score = max_score if local_score > 0 else -max_score
    #            found_final = True
    #            break
    #        score += local_score
    #    if found_final:
    #        break
    #print("Horizontal pattern -> Score: ", score)

    ## check right diagonal '/' pattern
    #if not found_final:
    #    for x in range(board.width()):
    #        #for y in range(board.get_column_empty_row(x)+1, board.height()):
    #        for y in range(board.height()):
    #            cell_score = score_cell(board, x, y, agent_index)
    #            local_score = cell_score
    #            if x > 0 and y < (board.height()-1):
    #                local_score += score_cell(board, x-1, y+1, agent_index)
    #            if x > 1 and y < (board.height()-2):
    #                local_score += score_cell(board, x-2, y+2, agent_index)
    #            if x > 2 and y < (board.height()-3):
    #                local_score += score_cell(board, x-3, y+3, agent_index)
    #            if abs(local_score) >= 4:
    #                score = max_score if local_score > 0 else -max_score
    #                found_final = True
    #                break
    #        score += local_score
    #        if found_final:
    #            break
    #print("Right diagonal pattern -> Score: ", score)

    ## check left diagonal '\' pattern
    #if not found_final:
    #    for x in range(board.width()):
    #        #for y in range(board.get_column_empty_row(x)+1, board.height()):
    #        for y in range(board.height()):
    #            cell_score = score_cell(board, x, y, agent_index)
    #            local_score = cell_score
    #            if x < (board.width()-1) and y < (board.height()-1):
    #                local_score += score_cell(board, x+1, y+1, agent_index)
    #            if x < (board.width()-2) and y < (board.height()-2):
    #                local_score += score_cell(board, x+2, y+2, agent_index)
    #            if x < (board.width()-3) and y < (board.height()-3):
    #                local_score += score_cell(board, x+3, y+3, agent_index)
    #            if abs(local_score) >= 4:
    #                score = max_score if local_score > 0 else -max_score
    #                found_final = True
    #                break
    #        score += local_score
    #        if found_final:
    #            break
    #print("Left diagonal pattern -> Score: ", score)

    ## check vertical '|' pattern
    #if not found_final:
    #    for x in range(board.width()):
    #        #for y in range(board.get_column_empty_row(x)+1, board.height(), 4):
    #        for y in range(0, board.height(), 4):
    #            cell_score = score_cell(board, x, y, agent_index)
    #            local_score = cell_score
    #            if y < (board.height()-1):
    #                local_score += score_cell(board, x, y+1, agent_index)
    #            if y < (board.height()-2):
    #                local_score += score_cell(board, x, y+2, agent_index)
    #            if y < (board.height()-3):
    #                local_score += score_cell(board, x, y+3, agent_index)
    #            if abs(local_score) >= 4:
    #                score = max_score if local_score > 0 else -max_score
    #                found_final = True
    #                break
    #        score += local_score
    #        if found_final:
    #            break
    #print("Vertical pattern -> Score: ", score)

    #max_score = 1.0
    #if game_state.is_final():
    #    if game_state.is_winner(agent_index):
    #        score = max_score
    #    elif game_state.is_tie():
    #        score = 0
    #    else:
    #        score = -max_score
    #else:
    #    found_final = False
    #    lookahead = 1
    #    score = score_lookahead(game_state, agent_index, lookahead, max_score)
    #    score /= (lookahead+1)
    #score /= max_score*(depth if depth > 0 else 1)

    #max_score = float("+inf")
    max_score = 10000
    if game_state.is_final() and not game_state.is_tie():
        if game_state.is_winner(agent_index):
            score = max_score
        else:
            score = -max_score
    else:
        # Count how many threats have been blocked
        count = count_blocked_threats(game_state, agent_index, 3)
        #print("Blocked threats of len 3: ", count)
        score += count*16
        count = count_blocked_threats(game_state, agent_index, 2)
        #print("Blocked threats of len 2: ", count)
        score += count*8
        # Count how many winning opportunities are open
        count = count_blocked_threats(game_state, agent_index, 3)
        for other_agent_index in range(game_state.num_agents()):
            count = count_winning_opportunities(game_state, other_agent_index, 3)
            if other_agent_index != agent_index:
                count *= -1
            else:
                count *= 0.25
            #print("Winning opportunities of len 3 for agent ", other_agent_index, ": ", count)
            score += count*16
        score /= (depth if depth > 0 else 1)

        #found_final = False
        #lookahead = 1
        #score = score_lookahead(game_state, agent_index, lookahead, max_score)
        #score /= (lookahead+1)
    #score /= (depth if depth > 0 else 1)
    score /= max_score

    if agent.get_verbosity_level() > 1:
        print("Agent: ", agent_index, ", State: ", game_state, ", Depth: ", depth, " =>  Score: ", score)

    return score

################################################################################

better_evaluation_function = token_patterns_evaluation_function
