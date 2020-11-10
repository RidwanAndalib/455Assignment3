from gtp_connection import GtpConnection, point_to_coord, format_point
from board_util import GoBoardUtil, PASS, where1d, BORDER, BLACK, WHITE
from board import GoBoard
import numpy as np
import argparse
import sys


class Gomoku3:
    def __init__(self, sim, sim_rule, size=7, limit=1000):
        """
        Go player that selects moves by simulation.
        """
        self.name = "Go3"
        self.version = 1.0
        self.komi = 6.5
        self.sim = sim
        self.limit = limit
        self.random_simulation = True if sim_rule == "random" else False

    def simulate(self, board, move, toplay):
        """
        Run a simulated game for a given move.
        """
        cboard = board.copy()
        cboard.play_move(move, toplay)
        opp = GoBoardUtil.opponent(toplay)
        return self.playGame(cboard, opp)

    def simulateMove(self, board, move, toplay):
        """
        Run simulations for a given move.
        """
        wins = 0
        for _ in range(self.sim):
            result = self.simulate(board, move, toplay)
            if result == toplay:
                wins += 1
        return wins

    def get_move(self, board, color):
        """
        Run one-ply MC simulations to get a move to play.
        """
        cboard = board.copy()
        emptyPoints = board.get_empty_points()
        moves = []
        for p in emptyPoints:
            if board.is_legal(p, color):
                moves.append(p)
        if not moves:
            return None
        moves.append(None)
        moveWins = []
        for move in moves:
            wins = self.simulateMove(cboard, move, color)
            moveWins.append(wins)
        writeMoves(cboard, moves, moveWins, self.sim)
        return select_best_move(board, moves, moveWins)

    def playGame(self, board, color):
        """
        Run a simulation game.
        """
        moveType = None
        moveList = None
        if not self.random_simulation:
            moveList = getOneWinning(board, color)
            if len(moveList) == 0:
                moveType = "Win"
                moveList = getBlockWin(board, color)
                if len(moveList) == 0:
                    moveType = "OpenFour"
                    moveList = getOpenFour(board, color)
                    if len(moveList) == 0:
                        moveType = "BlockOpenFour"
                        moveList = getBlockOpenFour(board, color)

            if len(moveList) == 0:
                moveType = "Random"
                moveList = getRandom(board, color)

        numPasses = 0
        for _ in range(self.limit):
            color = board.current_player
            move = GoBoardUtil.generate_random_move(board, color)
            board.play_move(move, color)
            if move == PASS:
                numPasses += 1
            else:
                numPasses = 0
            if numPasses >= 2:
                break
        return winner(board, self.komi)

        return [moveType, moveList]
            



def byPercentage(pair):
    return pair[1]

def percentage(wins, numSimulations):
    return float(wins) / float(numSimulations)

def writeMoves(board, moves, count, numSimulations):
    """
    Write simulation results for each move.
    """
    gtp_moves = []
    for i in range(len(moves)):
        move_string = "Pass"
        if moves[i] != None:
            x, y = point_to_coord(moves[i], board.size)
            move_string = format_point((x, y))
        gtp_moves.append((move_string, 
                          percentage(count[i], numSimulations)))
    sys.stderr.write("win rates: {}\n".format(sorted(gtp_moves,
                     key = byPercentage, reverse = True)))
    sys.stderr.flush()

def select_best_move(board, moves, moveWins):
    """
    Move select after the search.
    """
    max_child = np.argmax(moveWins)
    return moves[max_child]

def score_board(board, komi):
    """ Score board from Black's point of view """
    score = -komi
    counted = np.full(board.maxpoint, False, dtype=bool)
    for point in range(board.maxpoint):
            color = board.get_color(point)
            if color == BORDER or (point in counted):
                continue
            if color == BLACK:
                score += 1
            elif color == WHITE:
                score -= 1
            else:
                black_flag = False
                white_flag = False
                empty_points = where1d(board.connected_component(point))
                for p in empty_points:
                    counted[p] = True 
                    # TODO faster to boolean-or the whole array
                    if board.find_neighbor_of_color(p, BLACK):
                        black_flag = True
                    if board.find_neighbor_of_color(p, WHITE):
                        white_flag = True
                    if black_flag and white_flag:
                        break
                if black_flag and not white_flag:
                    score += len(empty_points)
                if white_flag and not black_flag:
                    score -= len(empty_points)
    return score

def winner(board, komi):
    score = score_board(board, komi)
    if score > 0:
        return BLACK
    elif score < 0:
        return WHITE
    else:
        return None

def run(sim, sim_rule):
    """
    Start the gtp connection and wait for commands.
    """
    board = GoBoard(7)
    con = GtpConnection(Gomoku3(sim, sim_rule), board)
    con.start_connection()


def parse_args():
    """
    Parse the arguments of the program.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--sim",
        type=int,
        default=10,
        help="number of simulations per move, so total playouts=sim*legal_moves",
    )
    parser.add_argument(
        "--simrule",
        type=str,
        default="random",
        help="type of simulation policy: random or rulebased",
    )

    args = parser.parse_args()
    sim = args.sim
    sim_rule = args.simrule

    return sim, sim_rule


if __name__ == "__main__":
    sim, sim_rule = parse_args()
    run(sim, sim_rule)