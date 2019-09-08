from .models import Board


class ChessBoard:
    def __init__(self, m=5, n=5, exist_board=None):
        self.size = (m, n)
        if not exist_board:
            self.matrix = [[0 for j in range(n)] for i in range(m)]
        else:
            self.matrix = exist_board

    def __str__(self):
        mark = {0: "", 1: "×", -1: "⚪"}
        board = ""
        board += " \t"
        for j in range(self.size[1]):
            board += str(j) + "\t"
        board += "\n"
        for i in range(self.size[0]):
            board += str(i) + "\t"
            for item in self.matrix[i]:
                board += mark[item] + "\t"
            board += "\n"
        return board

    def update(self, pos, sign):
        i = pos[0]
        j = pos[1]
        if (
            i not in range(0, self.size[0])
            or j not in range(0, self.size[1])
            or sign not in [-1, 0, 1]
        ):
            return False
        if self.matrix[i][j] != 0:
            return False
        else:
            self.matrix[i][j] = sign
            return True

    def check(self, target, directions, sign):
        t = self.matrix[target[0]][target[1]]
        if t != sign:
            return False
        for d in directions:
            try:
                if self.matrix[target[0] + d[0]][target[1] + d[1]] != t:
                    return False
            except IndexError:
                return False
        return True

    def copy(self):
        size = self.size
        newboard = Board(size[0], size[1])
        newboard.matrix = [row[:] for row in self.matrix]
        return newboard

    def ifwin(self, sign, pos=None):
        win = [
            [(-1, 1), (-2, 2), (-3, 3)],
            [(0, 1), (0, 2), (0, 3)],
            [(1, 1), (2, 2), (3, 3)],
            [(1, 0), (2, 0), (3, 0)],
        ]
        if pos != None:
            return self.simulate(pos, sign).ifwin(sign)
        else:
            for i in range(self.size[0]):
                for j in range(self.size[1]):
                    for pos in win:
                        if self.check((i, j), pos, sign) == True:
                            return True
        return False

    def iflose(self, sign, pos=None):
        lose = [
            [(-1, 1), (-2, 2)],
            [(0, 1), (0, 2)],
            [(1, 1), (2, 2)],
            [(1, 0), (2, 0)],
        ]
        if pos != None:
            return self.simulate(pos, sign).iflose(sign)
        else:
            for i in range(self.size[0]):
                for j in range(self.size[1]):
                    for pos in lose:
                        if self.check((i, j), pos, sign) == True:
                            return True
        return False

    def ifover(self):
        if self[0] == []:
            return True
        else:
            return False

    def simulate(self, pos, sign):
        newboard = self.copy()
        newboard.update(pos, sign)
        return newboard

    def __getitem__(self, sign):
        positions = []
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                if self.matrix[i][j] == sign:
                    positions.append((i, j))
        return positions

    def auto(self, sign):
        import random

        empty_pos = self[0]
        win_pos = []
        enemy_win_pos = []
        normal_pos = []
        for pos in empty_pos:
            if self.ifwin(sign, pos) == True:
                win_pos.append(pos)
            elif self.ifwin(-sign, pos) == True:
                enemy_win_pos.append(pos)
            elif self.iflose(sign, pos) == False:
                normal_pos.append(pos)
        if win_pos != []:
            decision = random.choice(win_pos)
        elif enemy_win_pos != []:
            decision = random.choice(enemy_win_pos)
        elif normal_pos != []:
            decision = random.choice(normal_pos)
        else:
            decision = None
        self.update(decision, sign)
        return decision, sign
