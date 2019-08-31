from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from .models import User, Board, BoardInfo
from django.core import serializers
import django.utils.timezone as timezone
import re


# Create your views here.
class ChessBoard:
    def __init__(self, m, n):
        self.size = (m, n)
        self.matrix = [[0 for j in range(n)] for i in range(m)]

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
        print(pos, sign)
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


"""
"""


def players(request):
    if request.user.is_authenticated:
        boarding = BoardInfo.objects.filter(players=request.user)[0].board
        result = {
             'msg': 'success',
             'players': [
                 {
                     'name': boarding.players.all()[0].nickname
                 },
                 {
                     'name': boarding.players.all()[1].nickname
                 }
             ]
         }
        return JsonResponse(result)
    else:
        return JsonResponse({'msg': 'User unauthorized!'})


def init_match(request):
    print(request.user)
    if request.user.is_authenticated:
        boards = Board.objects.all()
        for board in boards:
            print(board.players.all())
            if len(board.players.all()) == 1 and request.user not in board.players.all():
                BoardInfo(board=board, players=request.user).save()
                return JsonResponse({'msg': 'success'})
            if len(board.players.all()) == 2 and request.user in board.players.all() and \
                    BoardInfo(board=board, players=request.user).endTime == None:
                print('reconnect!')
                return JsonResponse({'msg': 'success'})
        if len(Board.objects.filter(board=request.user.username + str(request.user.games))) == 0:
            new_board = Board.objects.create(board=request.user.username + str(request.user.games))
            new_board.save()
            BoardInfo(board=new_board, players=request.user).save()
        return JsonResponse({'msg': 'pending'})
    else:
        return JsonResponse({'msg': 'User unauthorized!'})


def init_state(request):
    if request.user.is_authenticated:
        result = {
            'state': True
        }
        return JsonResponse(result)
    else:
        result = {
            'state': False
        }
        return JsonResponse(result)


def register(request):
    name = request.POST.get('username')
    password = request.POST.get('password')
    email = request.POST.get('email')
    if User.objects.filter(nickname=name).length() != 0:
        data = {
            'msg': 'The name has already been used!'
        }
        return JsonResponse(data)
    else:
        User.objects.create(nickname=name, password=password, email=email)
    data = {
        'msg': 'success!'
    }
    return JsonResponse(data)


def account_login(request):
    name = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username=name, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            data = {
                'msg': 'success'
            }
            return JsonResponse(data)
        else:
            data = {
                'msg': 'You account is not active, please contact the manager'
            }
            return JsonResponse(data)
    else:
        data = {
            'msg': 'Invalid username and password！'
        }
    return JsonResponse(data)


def account_logout(request):
    logout(request)
    return JsonResponse({'msg': '成功登出!'})


def profile(request, name):
    if request.user.is_authenticated:
        Profile = User.objects.get(username=request.user)
        data = {
            'username': Profile.username,
            'nickname': Profile.nickname,
            'games': Profile.games,
            # todo: serializer
            'email': Profile.email,
            'wins': Profile.wins,
            'remark': Profile.remark,
        }
        if str(request.user) == name:
            data['check'] = True
        else:
            data['check'] = False
        return JsonResponse(data)
    else:
        return JsonResponse({'msg': "You didn't login"})


def init_game(request):
    global b
    global sign
    sign = 1
    b = ChessBoard(5, 5)
    data = {'board': b.matrix}
    return JsonResponse(data)


def update(request):
    global b
    global sign
    post = request.body.decode()
    row = int(re.search(':[0-9]+,', post).group()[1:-1])
    column = int(re.search(':[0-9]+}', post).group()[1:-1])
    data = {}
    if row == -1:
        data["matrix"] = b.matrix
        data["msg"] = "NA"
        return JsonResponse(data)
    mark = {0: "", 1: "×", -1: "⚪"}
    if b.update((row, column), sign) == False:
        data["msg"] = "no"
    else:
        if b.ifwin(sign):
            data["msg"] = mark[sign] + " win!!"
        elif b.iflose(sign):
            data["msg"] = mark[sign] + " lose!!"
        else:
            data["msg"] = "NA"
            sign = -sign
    data["matrix"] = b.matrix
    print(data)
    return JsonResponse(data)
