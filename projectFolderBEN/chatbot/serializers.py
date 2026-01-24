from rest_framework import serializers
from .models import *


class ChatbotSerializer1(serializers.ModelSerializer):
    class Meta:
        model = Chatbot1
        fields = ("id","user","title","timestamp_parent")
        read_only_field =  ("id","user", "timestamp_parent")


class ChatHistorySerializer1(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory1
        fields = ("id","chat","role","message","timestamp_child")
        read_only_field =  ("id","chat", "timestamp_child")


class ChatbotSerializer2(serializers.ModelSerializer):
    class Meta:
        model = Chatbot2
        fields = ("id","user","title","timestamp_parent")
        read_only_field =  ("id","user", "timestamp_parent")


class ChatHistorySerializer2(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory2
        fields = ("chat","role","message","timestamp_child")
        read_only_field =  ("chat", "timestamp_child")


class ChatbotSerializer3(serializers.ModelSerializer):
    class Meta:
        model = Chatbot3
        fields = ("id","user","title","timestamp_parent")
        read_only_field =  ("id","user", "timestamp_parent")


class ChatHistorySerializer3(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory3
        fields = ("chat","role","message","timestamp_child")
        read_only_field =  ("chat", "timestamp_child")


class ChatbotSerializer4(serializers.ModelSerializer):
    class Meta:
        model = Chatbot4
        fields = ("id","user","title","timestamp_parent")
        read_only_field =  ("id","user", "timestamp_parent")


class ChatHistorySerializer4(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory4
        fields = ("chat","role","message","timestamp_child")
        read_only_field =  ("chat", "timestamp_child")


class ChatbotSerializer5(serializers.ModelSerializer):
    class Meta:
        model = Chatbot5
        fields = ("id","user","title","timestamp_parent")
        read_only_field =  ("id","user", "timestamp_parent")

class ChatHistorySerializer5(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory5
        fields = ("chat","role","message","timestamp_child")
        read_only_field =  ("chat", "timestamp_child")


class ChatbotSerializer6(serializers.ModelSerializer):
    class Meta:
        model = Chatbot6
        fields = ("id","user","title","timestamp_parent")
        read_only_field =  ("id","user", "timestamp_parent")


class ChatHistorySerializer6(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory6
        fields = ("chat","role","message","timestamp_child")
        read_only_field =  ("chat", "timestamp_child")


class ChatbotSerializer7(serializers.ModelSerializer):
    class Meta:
        model = Chatbot7
        fields = ("id","user","title","timestamp_parent")
        read_only_field =  ("id","user", "timestamp_parent")


class ChatHistorySerializer7(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory7
        fields = ("chat","role","message","timestamp_child")
        read_only_field =  ("chat", "timestamp_child")



class ChatbotSerializer8(serializers.ModelSerializer):
    class Meta:
        model = Chatbot8
        fields = ("id","user","title","timestamp_parent")
        read_only_field =  ("id","user", "timestamp_parent")


class ChatHistorySerializer8(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory8
        fields = ("chat","role","message","timestamp_child")
        read_only_field =  ("chat", "timestamp_child")



class ChatbotSerializer9(serializers.ModelSerializer):
    class Meta:
        model = Chatbot9
        fields = ("id","user","title","timestamp_parent")
        read_only_field =  ("id","user", "timestamp_parent")


class ChatHistorySerializer9(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory9
        fields = ("chat","role","message","timestamp_child")
        read_only_field =  ("chat", "timestamp_child")



class ChatbotSerializer10(serializers.ModelSerializer):
    class Meta:
        model = Chatbot10
        fields = ("id","user","title","timestamp_parent")
        read_only_field =  ("id","user", "timestamp_parent")


class ChatHistorySerializer10(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory10
        fields = ("chat","role","message","timestamp_child")
        read_only_field =  ("chat", "timestamp_child")


class ChatbotSerializer11(serializers.ModelSerializer):
    class Meta:
        model = Chatbot11
        fields = ("id","user","title","timestamp_parent")
        read_only_field =  ("id","user", "timestamp_parent")


class ChatHistorySerializer11(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory11
        fields = ("chat","role","message","timestamp_child")
        read_only_field =  ("chat", "timestamp_child")


class ChatbotSerializer12(serializers.ModelSerializer):
    class Meta:
        model = Chatbot12
        fields = ("id","user","title","timestamp_parent")
        read_only_field =  ("id","user", "timestamp_parent")


class ChatHistorySerializer12(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory12
        fields = ("chat","role","message","timestamp_child")
        read_only_field =  ("chat", "timestamp_child")