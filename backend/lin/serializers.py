from rest_framework import serializers
from .models import Board, BoardInfo, User


class BoardSerializers(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = '__all__'

    def create(self, validated_data):
        print('board created!!')
        board = Board.objects.create(**validated_data)
        board.save()
        return board

    def update(self, instance, validated_data):
        print('Board updated!!')
        instance.endTime = validated_data.get('endTime', instance.endTime)
        instance.save()
        return instance


class BoardInfoSerializers(serializers.ModelSerializer):
    class Meta:
        model = BoardInfo
        fields = '__all__'

    def create(self, validated_data):
        print('boardInfo created!!')
        b = BoardInfo.objects.create(**validated_data)
        b.save()
        return b

    def update(self, instance, validated_data):
        print('BoardInfo updated!!')
        # only update endTime info
        instance.endTime = validated_data.get('endTime', instance.endTime)
        instance.save()
        return instance


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'wins', 'games', 'remark', 'nickname']

    def create(self, validated_data):
        print('User created!!')
        user = User.objects.create(**validated_data)
        user.save()
        return user

    def update(self, instance, validated_data):
        print('User updated!!')
        instance.email = validated_data.get('email', instance.email)
        instance.nickname = validated_data.get('nickname', instance.nickname)
        instance.remark = validated_data.get('remark', instance.remark)
        instance.password = validated_data.get('password', instance.password)
        instance.wins = validated_data.get('wins', instance.wins)
        instance.games = validated_data.get('games', instance.games)
        instance.save()
        return instance
