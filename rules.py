from board_util import (
    GoBoardUtil,
    BLACK,
    WHITE,
    EMPTY,
    PASS,
    BORDER,
    where1d
)

class Rules:
    def __init__(self, board, color, random):
        self.board = board.copy()
        self.color = color
        self.random = random


    def getMoves(self):
        moveType = None
        moveList = []
        if not self.random:
            moveType = "Win"
            moveList = self.getOneWinning()
            if len(moveList) == 0:
                moveType = "BlockWin"
                moveList = self.getBlockWin()
                if len(moveList) == 0:
                    moveType = "OpenFour"
                    moveList = self.getOpenFour()
                    if len(moveList) == 0:
                        moveType = "BlockOpenFour"
                        moveList = self.getBlockOpenFour()

        if len(moveList) == 0:
            moveType = "Random"
            moveList = self.getRandom()

        return moveType, moveList


    def getOneWinning(self):
        winning = []
        emptyPoints = self.board.get_empty_points()
        moves = []
        for p in emptyPoints:
            if self.board.is_legal(p, self.color):
                moves.append(p)

        for move in moves:
            board = self.board.copy()
            board.play_move(move, self.color)
            winner = board.detect_five_in_a_row()
            if winner == self.color:
                winning.append(move)

        return winning



    def getBlockWin(self):
        winning = []
        emptyPoints = self.board.get_empty_points()
        moves = []
        for p in emptyPoints:
            if self.board.is_legal(p, self.color):
                moves.append(p)

        for move in moves:
            board = self.board.copy()
            board.play_move(move, GoBoardUtil.opponent(self.color))
            winner = board.detect_five_in_a_row()
            if winner == GoBoardUtil.opponent(self.color):
                winning.append(move)

        return winning



    def getOpenFour(self):
        return self.getOpenFourUtil(self.board, self.color, False)



    def getBlockOpenFour(self):
        moves = self.getOpenFourUtil(self.board, GoBoardUtil.opponent(self.color), True)
        winning = []
        for move in moves:
            board2 = self.board.copy()
            board2.play_move(move, self.color)
            opMoves = self.getOpenFourUtil(board2, GoBoardUtil.opponent(self.color), False)
            if len(opMoves) == 0:
                winning.append(move)

        return winning



    def getRandom(self):
        return self.board.get_empty_points()



    def has_open_four_in_list(self, board, list, color):
        """
        Returns BLACK or WHITE if any five in a rows exist in the list.
        EMPTY otherwise.
        """
        for i in range(len(list) - 5):
            four = board.get_color(list[i]) == EMPTY
            four = four and board.get_color(list[i + 1]) == color
            four = four and board.get_color(list[i + 2]) == color
            four = four and board.get_color(list[i + 3]) == color
            four = four and board.get_color(list[i + 4]) == color
            four = four and board.get_color(list[i + 5]) == EMPTY

            if four:
                return list[i], list[i + 5]

        return None


    def getOpenFourUtil(self, board, color, block):
        winning = []
        moves = []
        emptyPoints = board.get_empty_points()
        for p in emptyPoints:
            if board.is_legal(p, color):
                moves.append(p)

        for move in moves:
            board2 = board.copy()
            board2.play_move(move, color)
            for r in board2.rows:
                result = self.has_open_four_in_list(board2, r, color)
                if result:
                    winning.append(move)
                    if block:
                        winning.append(result[0])
                        winning.append(result[1])

            for c in board2.cols:
                result = self.has_open_four_in_list(board2, c, color)
                if result:
                    winning.append(move)
                    if block:
                        winning.append(result[0])
                        winning.append(result[1])

            for d in board2.diags:
                result = self.has_open_four_in_list(board2, d, color)
                if result:
                    winning.append(move)
                    if block:
                        winning.append(result[0])
                        winning.append(result[1])


        newWinning = []
        for m in winning:
            if m not in newWinning:
                newWinning.append(m)

        return newWinning
