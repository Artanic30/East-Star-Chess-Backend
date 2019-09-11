from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from .models import User, Board, BoardInfo
import django.utils.timezone as timezone
from .chess import ChessBoard
import json
from .serializers import UserSerializers, BoardInfoSerializers, BoardSerializers
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view


# Create your views here.
@api_view(['GET'])
def players(request, board_id):
    if request.user.is_authenticated:
        boarding = checking_board(request.user, board_id)
        if boarding:
            sign = 1
            for player in boarding.players.all():
                tem = BoardInfo.objects.get(players=player, board=boarding)
                boinfo_s = BoardInfoSerializers(tem, data={'sign': sign}, partial=True)
                test_valid(boinfo_s)
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
            return Response({'msg': "Due to error, we can't find your game, please match again!"}, status=status.HTTP_404_NOT_FOUND)
        return Response(result, status=status.HTTP_200_OK)

    else:
        return Response({'msg': 'User unauthorized!'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def init_match(request):
    if request.user.is_authenticated:
        boards = Board.objects.all()
        for board in boards:
            if len(board.players.all()) == 1 and request.user not in board.players.all():
                se_boinfo = BoardInfoSerializers(data={'board': board.pk, 'players': request.user.pk})
                test_valid(se_boinfo)
                # BoardInfo(board=board, players=request.user).save()
                return Response({'msg': 'success', 'board_id': board.pk}, status=status.HTTP_200_OK)
            if len(board.players.all()) == 2 and request.user in board.players.all() and \
                    not BoardInfo.objects.get(board=board, players=request.user).endTime:
                return Response({'msg': 'success', 'board_id': board.pk}, status=status.HTTP_200_OK)
        if len(Board.objects.filter(board=request.user.username + ' ' + str(request.user.games))) == 0:
            se_board = BoardSerializers(data={'board': request.user.username + ' ' + str(request.user.games)}, context={'user': request.user})
            test_valid(se_board)
            # new_board = Board.objects.create(board=request.user.username + ' ' + str(request.user.games))
            # new_board.save()
            # BoardInfo(board=new_board, players=request.user).save()
        return Response({'msg': 'pending'}, status=status.HTTP_200_OK)
    else:
        return Response({'msg': 'User unauthorized!'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def init_state(request):
    if request.user.is_authenticated:
        return Response({'state': True}, status=status.HTTP_200_OK)
    return Response({'state': False}, status=status.HTTP_200_OK)


@api_view(['POST'])
def register(request):
    name = request.POST.get('username')
    password = request.POST.get('password')
    email = request.POST.get('email')
    if len(User.objects.filter(username=name)) != 0:
        data = {
            'msg': 'The name has already been used!'
        }
        return Response(data, status=status.HTTP_409_CONFLICT)
    else:
        user = UserSerializers(data={'username': name, 'password': password, 'email': email})
        test_valid(user)
        # User.objects.create(username=name, password=password, email=email).save()
    data = {
        'msg': 'success'
    }
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
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
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {
                'msg': 'You account is not active, please contact the manager'
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)
    else:
        data = {
            'msg': 'Invalid username and password！'
        }
    return JsonResponse(data, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def account_logout(request):
    logout(request)
    return Response({'msg': '成功登出!'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def profile(request, name):
    if request.user.is_authenticated:
        Profile = User.objects.get(username=request.user)
        se_user = UserSerializers(Profile)
        data = se_user.data
        if str(request.user) == name:
            data['check'] = True
        else:
            data['check'] = False
        return Response(data, status=status.HTTP_200_OK)
    else:
        return Response({'msg': "You didn't login"}, status=status.HTTP_401_UNAUTHORIZED)


class GameViewSet(viewsets.ViewSet):
    @action(methods=['GET'], detail=True)
    def init_game(self, request, pk=None):
        board_id = pk
        boarding = checking_board(request.user, board_id)
        se_board = BoardSerializers(boarding)
        if not boarding:
            data = {
                'msg': "Due to error, we can't find your game, please match again!"
            }
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            if se_board.data.get('content') == '':
                empty = [[0 for j in range(5)] for i in range(5)]
                boarding = BoardSerializers(boarding, data={'content': json.dumps(empty)}, partial=True)
                test_valid(boarding)
                data = {
                    'board': empty,
                    'msg': 'success'
                }
            else:
                data = {
                    'board': json.loads(se_board.data.get('content')),
                    'msg': 'success'
                }
            if se_board.data.get('end_msg') != '':
                data = {
                    'board': se_board.data.get('end_msg'),
                    'msg': 'end'
                }
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    def update_game(self, request, pk=None):
        board_id = pk
        board = checking_board(request.user, board_id)
        se_board = BoardSerializers(board)
        data = {}
        if board:
            sign = se_board.data.get('sign')
            tem_boinfo = BoardInfo.objects.get(board=board, players=request.user)
            if sign == BoardInfoSerializers(tem_boinfo).data.get('sign'):
                b = ChessBoard(exist_board=json.loads(se_board.data.get('content')))
                row = int(request.POST.get('row'))
                column = int(request.POST.get('col'))
                if row == -1:
                    data["matrix"] = b.matrix
                    data["msg"] = "NA"
                    return Response(data, status=status.HTTP_200_OK)
                mark = {0: "", 1: "×", -1: "⚪"}
                if not b.update((row, column), sign):
                    data["msg"] = "no"
                else:
                    if b.ifwin(sign):
                        data["msg"] = mark[sign] + " win!!"
                        # board.end_msg = mark[sign] + " win!!"
                        # board.board += 'ended'
                        se_board = BoardSerializers(board, data={'end_msg': mark[sign] + " win!!", 'board': 'ended'},
                                                    partial=True)
                        test_valid(se_board)
                        end_info(board, sign, True)
                    elif b.iflose(sign):
                        end_info(board, sign, False)
                        se_board = BoardSerializers(board, data={'end_msg': mark[sign] + " lose!!", 'board': 'ended'},
                                                    partial=True)
                        test_valid(se_board)
                        # board.board += 'ended'
                        # board.end_msg = mark[sign] + " lose!!"
                        data["msg"] = mark[sign] + " lose!!"
                    else:
                        data["msg"] = "NA"
                        sign = -sign
                data["matrix"] = b.matrix
                se_board = BoardSerializers(board, data={'content': json.dumps(b.matrix), 'sign': sign})
                test_valid(se_board)
                # board.content = json.dumps(b.matrix)
                # board.sign = sign
                # board.save()
                return Response(data, status=status.HTTP_200_OK)
            else:
                data["msg"] = "no"
                return Response(data, status=status.HTTP_200_OK)
        else:
            data['msg'] = "Due to error, we can't find your game, please match again!"
            return Response(data, status=status.HTTP_404_NOT_FOUND)


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


# check before serializer is saved
def test_valid(serializer):
    if serializer.is_valid():
        serializer.save()
    else:
        JsonResponse({'msg': serializer.errors})
