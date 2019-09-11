from rest_framework import serializers
from .models import Board, BoardInfo, User


class BoardSerializers(serializers.ModelSerializer):
    board = serializers.CharField(max_length=300, required=False)
    players = serializers.PrimaryKeyRelatedField(many=True, read_only=True, required=False)

    class Meta:
        model = Board
        fields = '__all__'

    def create(self, validated_data):
        board = Board.objects.create(**validated_data)
        board.save()
        BoardInfo(board=board, players=self.context['user']).save()
        return board

    def update(self, instance, validated_data):
        instance.end_msg = validated_data.get('end_msg', instance.end_msg)
        instance.content = validated_data.get('content', instance.content)
        instance.sign = validated_data.get('sign', instance.sign)
        if instance.board == validated_data.get('content', instance.content):
            pass
        else:
            instance.board = validated_data.get('board', instance.board) + instance.board
        instance.save()
        return instance


class BoardInfoSerializers(serializers.ModelSerializer):
    class Meta:
        model = BoardInfo
        fields = '__all__'

    def create(self, validated_data):
        b = BoardInfo.objects.create(players=validated_data.get('players'), board=validated_data.get('board'))
        b.save()
        return b

    def update(self, instance, validated_data):
        # only update endTime info and sign
        instance.endTime = validated_data.get('endTime', instance.endTime)
        instance.sign = validated_data.get('sign', instance.sign)
        instance.save()
        return instance


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'wins', 'games', 'remark', 'nickname']

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.nickname = validated_data.get('nickname', instance.nickname)
        instance.remark = validated_data.get('remark', instance.remark)
        instance.password = validated_data.get('password', instance.password)
        instance.wins = validated_data.get('wins', instance.wins)
        instance.games = validated_data.get('games', instance.games)
        instance.save()
        return instance
