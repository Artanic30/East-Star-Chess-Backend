from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from .models import User, Board, BoardInfo
import django.utils.timezone as timezone
from .chess import ChessBoard
import json
from django.views.generic import View


# Create your views here.
def players(request, board_id):
    if request.user.is_authenticated:
        boarding = checking_board(request.user, board_id)
        if boarding:
            sign = 1
            for player in boarding.players.all():
                tem = BoardInfo.objects.get(players=player, board=boarding)
                tem.sign = sign
                tem.save()
                sign = - sign
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
        else:
            return JsonResponse({'msg': "Due to error, we can't find your game, please match again!"})
        return JsonResponse(result)

    else:
        return JsonResponse({'msg': 'User unauthorized!'})


def init_match(request):
    if request.user.is_authenticated:
        boards = Board.objects.all()
        for board in boards:
            if len(board.players.all()) == 1 and request.user not in board.players.all():
                BoardInfo(board=board, players=request.user).save()
                return JsonResponse({'msg': 'success', 'board_id': board.pk})
            if len(board.players.all()) == 2 and request.user in board.players.all() and \
                    not BoardInfo.objects.get(board=board, players=request.user).endTime:
                return JsonResponse({'msg': 'success', 'board_id': board.pk})
        if len(Board.objects.filter(board=request.user.username + ' ' + str(request.user.games))) == 0:
            new_board = Board.objects.create(board=request.user.username + ' ' + str(request.user.games))
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
    if len(User.objects.filter(username=name)) != 0:
        data = {
            'msg': 'The name has already been used!'
        }
        return JsonResponse(data)
    else:
        User.objects.create(username=name, password=password, email=email).save()
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


def init_game(request, board_id):
    boarding = checking_board(request.user, board_id)
    if not boarding:
        data = {
            'msg': "Due to error, we can't find your game, please match again!"
        }
    else:
        if boarding.content == '':
            empty = [[0 for j in range(5)] for i in range(5)]
            boarding.content = json.dumps(empty)
            boarding.save()
            data = {
                'board': empty,
                'msg': 'success'
            }
        else:
            data = {
                'board': json.loads(boarding.content),
                'msg': 'success'
            }
        if boarding.end_msg != '':
            data = {
                'board': boarding.end_msg,
                'msg': 'end'
            }
    return JsonResponse(data)


def update(request, board_id):
    board = checking_board(request.user, board_id)
    data = {}
    if board:
        sign = board.sign
        if sign == BoardInfo.objects.get(board=board, players=request.user).sign:
            b = ChessBoard(exist_board=json.loads(board.content))
            row = int(request.POST.get('row'))
            column = int(request.POST.get('col'))
            if row == -1:
                data["matrix"] = b.matrix
                data["msg"] = "NA"
                return JsonResponse(data)
            mark = {0: "", 1: "×", -1: "⚪"}
            if not b.update((row, column), sign):
                data["msg"] = "no"
            else:
                if b.ifwin(sign):
                    data["msg"] = mark[sign] + " win!!"
                    board.end_msg = mark[sign] + " win!!"
                    board.board += 'ended'
                    end_info(board, sign, True)
                elif b.iflose(sign):
                    end_info(board, sign, False)
                    board.board += 'ended'
                    data["msg"] = mark[sign] + " lose!!"
                    board.end_msg = mark[sign] + " lose!!"
                else:
                    data["msg"] = "NA"
                    sign = -sign
            data["matrix"] = b.matrix
            board.content = json.dumps(b.matrix)
            board.sign = sign
            board.save()
            return JsonResponse(data)
        else:
            data["msg"] = "no"
            return JsonResponse(data)
    else:
        data['msg'] = "Due to error, we can't find your game, please match again!"
        return JsonResponse(data)


def checking_board(user, board_id):
    # check if board related to board_id exist and return a Board
    b = 0
    try:
        b = Board.objects.get(pk=board_id)
    except Board.DoesNotExist:
        boards = Board.objects.all()
        for board in boards:
            if user in board.players.all() and len(board.players.all()) == 2 and not BoardInfo(board=board,
                                                                                               players=user).endTime:
                b = board
    if b == 0:
        return False
    else:
        return b


def end_info(board, sign, win):
    for info in BoardInfo.objects.filter(board=board):
        if not info.endTime:
            info.endTime = timezone.now()
            info.save()
        for player in board.players.all():
            if (BoardInfo.objects.get(board=board, players=player).sign == sign and win) or \
             (BoardInfo.objects.get(board=board, players=player).sign != sign and not win):
                player.wins += 1
                player.save()


