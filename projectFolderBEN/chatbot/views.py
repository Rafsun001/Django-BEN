from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from .serializers import *
from django.contrib.auth.models import User
from .models import *
import random
import string
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
import tempfile

from Academy_Behaviour_strategies.behave import generate_behaviour_strategy
from Academy_communication_assistant.communication import improve_communication
from Academy_Heads_and_SLT.hs import generate_hs_response
from Academy_Lesson_generator.lesson import generate_lesson
from Academy_Resource_generator.resource import generate_resource
from Academy_sow.scope import get_support_response_sow_academy_new

from primary_behaviour.taught_ai_behaviour import generate_behaviour_gp
from primary_Communication.taught_ai_communication import generate_communication_gp
from primary_head.taught_ai_head import generate_head_gp
from primary_lesson.taught_ai_lesson import generate_lesson_gp
from primary_resource.taught_ai_resource import generate_resource_gp
from primary_sow.taught_ai_scope import generate_scheme_gp

# Create your views here.

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_all_chat(request):
    user = request.user

    model_name = request.data.get('model_name')
    
    if model_name == "Academy_Behaviour_strategies":

        all_chat = Chatbot1.objects.filter(user = user)

        serializer = ChatbotSerializer1(all_chat, many=True)

        return Response(
            {
                "Data": serializer.data,
                "model": "Academy_Behaviour_strategies"
            },
            status=200
        )
    
    elif model_name == "Academy_communication_assistant":
        all_chat = Chatbot2.objects.filter(user = user)

        serializer = ChatbotSerializer2(all_chat, many=True)

        return Response(
            {
                "Data": serializer.data,
                "model": "Academy_communication_assistant"
            },
            status=200
        )
        
    
    elif model_name == "Academy_Heads_and_SLT":
        all_chat = Chatbot3.objects.filter(user = user)

        serializer = ChatbotSerializer3(all_chat, many=True)

        return Response(
            {
                "Data": serializer.data,
                "Model":"Academy_Heads_and_SLT"
            },
            status=200
        )
    

    elif model_name == "Academy_Lesson_generator":
        all_chat = Chatbot4.objects.filter(user = user)

        serializer = ChatbotSerializer4(all_chat, many=True)

        return Response(
            {
                "Data": serializer.data,
                "model" : "Academy_Lesson_generator"
            },
            status=200
        )
    
    elif model_name == "Academy_Resource_generator":
        all_chat = Chatbot5.objects.filter(user = user)

        serializer = ChatbotSerializer5(all_chat, many=True)

        return Response(
            {
                "Data": serializer.data,
                "Model": "Academy_Resource_generator"
            },
            status=200
        )
    
    elif model_name == "Academy_sow":
        all_chat = Chatbot6.objects.filter(user = user)

        serializer = ChatbotSerializer6(all_chat, many=True)

        return Response(
            {
                "Data": serializer.data,
                "Model":"Academy_sow"
            },
            status=200
        )
    
    elif model_name == "primary_behaviour":
        all_chat = Chatbot7.objects.filter(user = user)

        serializer = ChatbotSerializer7(all_chat, many=True)

        return Response(
            {
                "Data": serializer.data,
                "Model" : "primary_behaviour"
            },
            status=200
        )
    
    elif model_name == "primary_Communication":
        all_chat = Chatbot8.objects.filter(user = user)

        serializer = ChatbotSerializer8(all_chat, many=True)

        return Response(
            {
                "Data": serializer.data,
                "model" : "primary_Communication"
            },
            status=200
        )
    
    elif model_name == "primary_head":
        all_chat = Chatbot9.objects.filter(user = user)

        serializer = ChatbotSerializer9(all_chat, many=True)

        return Response(
            {
                "Data": serializer.data,
                "model" : "primary_head"
            },
            status=200
        )
    
    elif model_name == "primary_lesson":
        all_chat = Chatbot10.objects.filter(user = user)

        serializer = ChatbotSerializer10(all_chat, many=True)

        return Response(
            {
                "Data": serializer.data,
                "Model" : "primary_lesson"
            },
            status=200
        )
    
    elif model_name == "primary_resource":
        all_chat = Chatbot11.objects.filter(user = user)

        serializer = ChatbotSerializer11(all_chat, many=True)

        return Response(
            {
                "Data": serializer.data,
                "Model" : "primary_resource"
            },
            status=200
        )
    
    else:
        all_chat = Chatbot12.objects.filter(user = user)

        serializer = ChatbotSerializer12(all_chat, many=True)

        return Response(
            {
                "Data": serializer.data,
                "model"  : "primary_sow"
            },
            status=200
        )
    
   

@csrf_exempt
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def create_chat(request):

    user = request.user

    model_name = request.data.get('model_name')
    first_message = request.data.get('first_message')
    uploaded_file = request.FILES.get('file')

    # -------------------------------------
    # (1) Handle uploaded file (Optional)
    # -------------------------------------
    temp_path = None
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            for chunk in uploaded_file.chunks():
                tmp.write(chunk)
            temp_path = tmp.name   # real file path stored on disk


    # Prepare uploaded file list for the AI function
    uploaded_files_list = [temp_path] if temp_path else []


    if model_name == "Academy_Behaviour_strategies":

        # ✅ Create Chatbot1 entry
        chatbot1 = Chatbot1(user=user)
        chatbot1.title = first_message
        chatbot1.save()

        # ✅ Save user's message
        chat_history_user = ChatHistory1(chat=chatbot1)
        chat_history_user.role = "user"
        chat_history_user.message = first_message
        chat_history_user.save()

        # ✅ Save bot's reply
        
        answer = generate_behaviour_strategy(first_message, uploaded_files_list, history=None)
        chat_history_bot = ChatHistory1(chat=chatbot1)
        chat_history_bot.role = "assistant"
        chat_history_bot.message = answer
        chat_history_bot.save()

        # ✅ Build response
        return Response(
            {
                "message": "Saved successfully",
                "user_id": user.id,
                "username": user.username,
                "chat_id": chatbot1.id,
                "title": chatbot1.title,
                "timestamp": chatbot1.timestamp_parent.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "chat_history": [
                    {
                        "role": chat_history_user.role,
                        "message_id": chat_history_user.id,
                        "timestamp": chat_history_user.timestamp_child.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        "message": chat_history_user.message
                    },
                    {
                        "role": chat_history_bot.role,
                        "message_id": chat_history_bot.id,
                        "timestamp": chat_history_bot.timestamp_child.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        "message": chat_history_bot.message
                    }
                ]
            },
            status=200
        )
 
    elif model_name == "Academy_communication_assistant":
        # ✅ Create Chatbot1 entry
        chatbot1 = Chatbot2(user=user)
        chatbot1.title = first_message
        chatbot1.save()

        # ✅ Save user's message
        chat_history_user = ChatHistory2(chat=chatbot1)
        chat_history_user.role = "user"
        chat_history_user.message = first_message
        chat_history_user.save()

        # ✅ Save bot's reply
        answer = improve_communication(first_message, uploaded_files_list, history=None)
        chat_history_bot = ChatHistory2(chat=chatbot1)
        chat_history_bot.role = "assistant"
        chat_history_bot.message = answer
        chat_history_bot.save()

        # ✅ Build response
        return Response(
            {
                "message": "Saved successfully",
                "user_id": user.id,
                "username": user.username,
                "chat_id": chatbot1.id,
                "title": chatbot1.title,
                "timestamp": chatbot1.timestamp_parent.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "chat_history": [
                    {
                        "role": chat_history_user.role,
                        "message_id": chat_history_user.id,
                        "timestamp": chat_history_user.timestamp_child.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        "message": chat_history_user.message
                    },
                    {
                        "role": chat_history_bot.role,
                        "message_id": chat_history_bot.id,
                        "timestamp": chat_history_bot.timestamp_child.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        "message": chat_history_bot.message
                    }
                ]
            },
            status=200
        )
        
    elif model_name == "Academy_Heads_and_SLT":
        # ✅ Create Chatbot1 entry
        chatbot1 = Chatbot3(user=user)
        chatbot1.title = first_message
        chatbot1.save()

        # ✅ Save user's message
        chat_history_user = ChatHistory3(chat=chatbot1)
        chat_history_user.role = "user"
        chat_history_user.message = first_message
        chat_history_user.save()

        # ✅ Save bot's reply
        answer = generate_hs_response(first_message, uploaded_files_list, history=None)
        chat_history_bot = ChatHistory3(chat=chatbot1)
        chat_history_bot.role = "assistant"
        chat_history_bot.message = answer
        chat_history_bot.save()

        # ✅ Build response
        return Response(
            {
                "message": "Saved successfully",
                "user_id": user.id,
                "username": user.username,
                "chat_id": chatbot1.id,
                "title": chatbot1.title,
                "timestamp": chatbot1.timestamp_parent.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "chat_history": [
                    {
                        "role": chat_history_user.role,
                        "message_id": chat_history_user.id,
                        "timestamp": chat_history_user.timestamp_child.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        "message": chat_history_user.message
                    },
                    {
                        "role": chat_history_bot.role,
                        "message_id": chat_history_bot.id,
                        "timestamp": chat_history_bot.timestamp_child.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        "message": chat_history_bot.message
                    }
                ]
            },
            status=200
        )
    
    elif model_name == "Academy_Lesson_generator":
        # ✅ Create Chatbot1 entry
        chatbot1 = Chatbot4(user=user)
        chatbot1.title = first_message
        chatbot1.save()

        # ✅ Save user's message
        chat_history_user = ChatHistory4(chat=chatbot1)
        chat_history_user.role = "user"
        chat_history_user.message = first_message
        chat_history_user.save()

        # ✅ Save bot's reply
        answer = generate_lesson(first_message, uploaded_files_list, history=None)
        chat_history_bot = ChatHistory4(chat=chatbot1)
        chat_history_bot.role = "assistant"
        chat_history_bot.message = answer
        chat_history_bot.save()

        # ✅ Build response
        return Response(
            {
                "message": "Saved successfully",
                "user_id": user.id,
                "username": user.username,
                "chat_id": chatbot1.id,
                "title": chatbot1.title,
                "timestamp": chatbot1.timestamp_parent.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "chat_history": [
                    {
                        "role": chat_history_user.role,
                        "message_id": chat_history_user.id,
                        "timestamp": chat_history_user.timestamp_child.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        "message": chat_history_user.message
                    },
                    {
                        "role": chat_history_bot.role,
                        "message_id": chat_history_bot.id,
                        "timestamp": chat_history_bot.timestamp_child.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        "message": chat_history_bot.message
                    }
                ]
            },
            status=200
        )
    
    elif model_name == "Academy_Resource_generator":
        # ✅ Create Chatbot1 entry
        chatbot1 = Chatbot5(user=user)
        chatbot1.title = first_message
        chatbot1.save()

        # ✅ Save user's message
        chat_history_user = ChatHistory5(chat=chatbot1)
        chat_history_user.role = "user"
        chat_history_user.message = first_message
        chat_history_user.save()

        # ✅ Save bot's reply
        answer = generate_resource(first_message, uploaded_files_list, history=None)
        chat_history_bot = ChatHistory5(chat=chatbot1)
        chat_history_bot.role = "assistant"
        chat_history_bot.message = answer
        chat_history_bot.save()

        # ✅ Build response
        return Response(
            {
                "message": "Saved successfully",
                "user_id": user.id,
                "username": user.username,
                "chat_id": chatbot1.id,
                "title": chatbot1.title,
                "timestamp": chatbot1.timestamp_parent.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "chat_history": [
                    {
                        "role": chat_history_user.role,
                        "message_id": chat_history_user.id,
                        "timestamp": chat_history_user.timestamp_child.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        "message": chat_history_user.message
                    },
                    {
                        "role": chat_history_bot.role,
                        "message_id": chat_history_bot.id,
                        "timestamp": chat_history_bot.timestamp_child.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        "message": chat_history_bot.message
                    }
                ]
            },
            status=200
        )
    
    elif model_name == "Academy_sow":
        # ✅ Create Chatbot1 entry
        chatbot1 = Chatbot6(user=user)
        chatbot1.title = first_message
        chatbot1.save()

        # ✅ Save user's message
        chat_history_user = ChatHistory6(chat=chatbot1)
        chat_history_user.role = "user"
        chat_history_user.message = first_message
        chat_history_user.save()

        # ✅ Save bot's reply
        answer = get_support_response_sow_academy_new(first_message, uploaded_files_list, history=None)
        chat_history_bot = ChatHistory6(chat=chatbot1)
        chat_history_bot.role = "assistant"
        chat_history_bot.message = answer
        chat_history_bot.save()

        # ✅ Build response
        return Response(
            {
                "message": "Saved successfully",
                "user_id": user.id,
                "username": user.username,
                "chat_id": chatbot1.id,
                "title": chatbot1.title,
                "timestamp": chatbot1.timestamp_parent.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "chat_history": [
                    {
                        "role": chat_history_user.role,
                        "message_id": chat_history_user.id,
                        "timestamp": chat_history_user.timestamp_child.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        "message": chat_history_user.message
                    },
                    {
                        "role": chat_history_bot.role,
                        "message_id": chat_history_bot.id,
                        "timestamp": chat_history_bot.timestamp_child.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        "message": chat_history_bot.message
                    }
                ]
            },
            status=200
        )
    
    elif model_name == "primary_behaviour":
        # ✅ Create Chatbot1 entry
        chatbot1 = Chatbot7(user=user)
        chatbot1.title = first_message
        chatbot1.save()

        # ✅ Save user's message
        chat_history_user = ChatHistory7(chat=chatbot1)
        chat_history_user.role = "user"
        chat_history_user.message = first_message
        chat_history_user.save()

        # ✅ Save bot's reply
        answer = generate_behaviour_gp(first_message, uploaded_files_list, history=None)
        chat_history_bot = ChatHistory7(chat=chatbot1)
        chat_history_bot.role = "assistant"
        chat_history_bot.message = answer
        chat_history_bot.save()

        # ✅ Build response
        return Response(
            {
                "message": "Saved successfully",
                "user_id": user.id,
                "username": user.username,
                "chat_id": chatbot1.id,
                "title": chatbot1.title,
                "timestamp": chatbot1.timestamp_parent.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "chat_history": [
                    {
                        "role": chat_history_user.role,
                        "message_id": chat_history_user.id,
                        "timestamp": chat_history_user.timestamp_child.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        "message": chat_history_user.message
                    },
                    {
                        "role": chat_history_bot.role,
                        "message_id": chat_history_bot.id,
                        "timestamp": chat_history_bot.timestamp_child.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        "message": chat_history_bot.message
                    }
                ]
            },
            status=200
        )
    
    elif model_name == "primary_Communication":
        # ✅ Create Chatbot1 entry
        chatbot1 = Chatbot8(user=user)
        chatbot1.title = first_message
        chatbot1.save()

        # ✅ Save user's message
        chat_history_user = ChatHistory8(chat=chatbot1)
        chat_history_user.role = "user"
        chat_history_user.message = first_message
        chat_history_user.save()

        # ✅ Save bot's reply
        answer = generate_communication_gp(first_message, uploaded_files_list, history=None)
        chat_history_bot = ChatHistory8(chat=chatbot1)
        chat_history_bot.role = "assistant"
        chat_history_bot.message = answer
        chat_history_bot.save()

        # ✅ Build response
        return Response(
            {
                "message": "Saved successfully",
                "user_id": user.id,
                "username": user.username,
                "chat_id": chatbot1.id,
                "title": chatbot1.title,
                "timestamp": chatbot1.timestamp_parent.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "chat_history": [
                    {
                        "role": chat_history_user.role,
                        "message_id": chat_history_user.id,
                        "timestamp": chat_history_user.timestamp_child.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        "message": chat_history_user.message
                    },
                    {
                        "role": chat_history_bot.role,
                        "message_id": chat_history_bot.id,
                        "timestamp": chat_history_bot.timestamp_child.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        "message": chat_history_bot.message
                    }
                ]
            },
            status=200
        )
    
    elif model_name == "primary_head":
        # ✅ Create Chatbot1 entry
        chatbot1 = Chatbot9(user=user)
        chatbot1.title = first_message
        chatbot1.save()

        # ✅ Save user's message
        chat_history_user = ChatHistory9(chat=chatbot1)
        chat_history_user.role = "user"
        chat_history_user.message = first_message
        chat_history_user.save()

        # ✅ Save bot's reply
        answer = generate_head_gp(first_message, uploaded_files_list, history=None)
        chat_history_bot = ChatHistory9(chat=chatbot1)
        chat_history_bot.role = "assistant"
        chat_history_bot.message = answer
        chat_history_bot.save()

        # ✅ Build response
        return Response(
            {
                "message": "Saved successfully",
                "user_id": user.id,
                "username": user.username,
                "chat_id": chatbot1.id,
                "title": chatbot1.title,
                "timestamp": chatbot1.timestamp_parent.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "chat_history": [
                    {
                        "role": chat_history_user.role,
                        "message_id": chat_history_user.id,
                        "timestamp": chat_history_user.timestamp_child.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        "message": chat_history_user.message
                    },
                    {
                        "role": chat_history_bot.role,
                        "message_id": chat_history_bot.id,
                        "timestamp": chat_history_bot.timestamp_child.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        "message": chat_history_bot.message
                    }
                ]
            },
            status=200
        )
    
    elif model_name == "primary_lesson":
        # ✅ Create Chatbot1 entry
        chatbot1 = Chatbot10(user=user)
        chatbot1.title = first_message
        chatbot1.save()

        # ✅ Save user's message
        chat_history_user = ChatHistory10(chat=chatbot1)
        chat_history_user.role = "user"
        chat_history_user.message = first_message
        chat_history_user.save()

        # ✅ Save bot's reply
        answer = generate_lesson_gp(first_message, uploaded_files_list, history=None)
        chat_history_bot = ChatHistory10(chat=chatbot1)
        chat_history_bot.role = "assistant"
        chat_history_bot.message = answer
        chat_history_bot.save()

        # ✅ Build response
        return Response(
            {
                "message": "Saved successfully",
                "user_id": user.id,
                "username": user.username,
                "chat_id": chatbot1.id,
                "title": chatbot1.title,
                "timestamp": chatbot1.timestamp_parent.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "chat_history": [
                    {
                        "role": chat_history_user.role,
                        "message_id": chat_history_user.id,
                        "timestamp": chat_history_user.timestamp_child.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        "message": chat_history_user.message
                    },
                    {
                        "role": chat_history_bot.role,
                        "message_id": chat_history_bot.id,
                        "timestamp": chat_history_bot.timestamp_child.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        "message": chat_history_bot.message
                    }
                ]
            },
            status=200
        )
    
    elif model_name == "primary_resource":
        # ✅ Create Chatbot1 entry
        chatbot1 = Chatbot11(user=user)
        chatbot1.title = first_message
        chatbot1.save()

        # ✅ Save user's message
        chat_history_user = ChatHistory11(chat=chatbot1)
        chat_history_user.role = "user"
        chat_history_user.message = first_message
        chat_history_user.save()

        # ✅ Save bot's reply
        answer = generate_resource_gp(first_message, uploaded_files_list, history=None)
        chat_history_bot = ChatHistory11(chat=chatbot1)
        chat_history_bot.role = "assistant"
        chat_history_bot.message = answer
        chat_history_bot.save()

        # ✅ Build response
        return Response(
            {
                "message": "Saved successfully",
                "user_id": user.id,
                "username": user.username,
                "chat_id": chatbot1.id,
                "title": chatbot1.title,
                "timestamp": chatbot1.timestamp_parent.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "chat_history": [
                    {
                        "role": chat_history_user.role,
                        "message_id": chat_history_user.id,
                        "timestamp": chat_history_user.timestamp_child.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        "message": chat_history_user.message
                    },
                    {
                        "role": chat_history_bot.role,
                        "message_id": chat_history_bot.id,
                        "timestamp": chat_history_bot.timestamp_child.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        "message": chat_history_bot.message
                    }
                ]
            },
            status=200
        )
    
    else:
        # ✅ Create Chatbot1 entry
        chatbot1 = Chatbot12(user=user)
        chatbot1.title = first_message
        chatbot1.save()

        # ✅ Save user's message
        chat_history_user = ChatHistory12(chat=chatbot1)
        chat_history_user.role = "user"
        chat_history_user.message = first_message
        chat_history_user.save()

        # ✅ Save bot's reply
        answer = generate_scheme_gp(first_message, uploaded_files_list, history=None)
        chat_history_bot = ChatHistory12(chat=chatbot1)
        chat_history_bot.role = "assistant"
        chat_history_bot.message = answer
        chat_history_bot.save()

        # ✅ Build response
        return Response(
            {
                "message": "Saved successfully",
                "user_id": user.id,
                "username": user.username,
                "chat_id": chatbot1.id,
                "title": chatbot1.title,
                "timestamp": chatbot1.timestamp_parent.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "chat_history": [
                    {
                        "role": chat_history_user.role,
                        "message_id": chat_history_user.id,
                        "timestamp": chat_history_user.timestamp_child.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        "message": chat_history_user.message
                    },
                    {
                        "role": chat_history_bot.role,
                        "message_id": chat_history_bot.id,
                        "timestamp": chat_history_bot.timestamp_child.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        "message": chat_history_bot.message
                    }
                ]
            },
            status=200
        )


@csrf_exempt
@api_view(['POST'])  # ✅ use POST instead of GET because you’re saving data
@permission_classes([IsAuthenticated])
def conversation(request):
    user = request.user
    chat_id = request.data.get('chat_id')
    user_message = request.data.get('user_message')
    model_name = request.data.get('model_name')
    uploaded_file = request.FILES.get('file')

    # -------------------------------------
    # (1) Handle uploaded file (Optional)
    # -------------------------------------
    temp_path = None
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            for chunk in uploaded_file.chunks():
                tmp.write(chunk)
            temp_path = tmp.name   # real file path stored on disk


    # Prepare uploaded file list for the AI function
    uploaded_files_list = [temp_path] if temp_path else []

    if model_name == "Academy_Behaviour_strategies": 

        chatbot = Chatbot1.objects.get(id=chat_id, user=user)

        # ✅ Save user's message linked to that chat
        chat_history_user = ChatHistory1(chat=chatbot)
        chat_history_user.role = "user"
        chat_history_user.message = user_message
        chat_history_user.save()

        # Fetch last 5 messages for this chat (before adding bot reply)
        last_messages = ChatHistory1.objects.filter(chat=chatbot).order_by('-timestamp_child')[:5]

        # Reverse so they are oldest → newest (better for LLM)
        last_messages = reversed(last_messages)

        # Convert to role/content list
        context = [
            {"role": msg.role, "content": msg.message}
            for msg in last_messages
        ]

        # ✅ Save bot's reply
        answer = generate_behaviour_strategy(user_message,uploaded_files_list, context)
        chat_history_bot = ChatHistory1(chat=chatbot)
        chat_history_bot.role = "assistant"
        chat_history_bot.message = answer
        chat_history_bot.save()

        # ✅ Get all chat history entries for this chat
        chat_history = ChatHistory1.objects.filter(chat=chatbot).order_by('timestamp_child')

        # ✅ Serialize data
        serializer = ChatHistorySerializer1(chat_history, many=True)

        # ✅ Return full response
        return Response(
            {
                "chat_id": chatbot.id,
                "user_id": chatbot.user.id,
                "title": chatbot.title,
                "total_messages": len(chat_history),
                "messages": serializer.data
            },
            status=200
        )
    elif model_name == "Academy_communication_assistant":

        chatbot = Chatbot2.objects.get(id=chat_id, user=user)

        # ✅ Save user's message linked to that chat
        chat_history_user = ChatHistory2(chat=chatbot)
        chat_history_user.role = "user"
        chat_history_user.message = user_message
        chat_history_user.save()
        
        # Fetch last 5 messages for this chat (before adding bot reply)
        last_messages = ChatHistory2.objects.filter(chat=chatbot).order_by('-timestamp_child')[:5]

        # Reverse so they are oldest → newest (better for LLM)
        last_messages = reversed(last_messages)

        # Convert to role/content list
        context = [
            {"role": msg.role, "content": msg.message}
            for msg in last_messages
        ]

        # ✅ Save bot's reply
        answer = improve_communication(user_message,uploaded_files_list, context)
        chat_history_bot = ChatHistory2(chat=chatbot)
        chat_history_bot.role = "assistant"
        chat_history_bot.message = answer
        chat_history_bot.save()

        # ✅ Get all chat history entries for this chat
        chat_history = ChatHistory2.objects.filter(chat=chatbot).order_by('timestamp_child')

        # ✅ Serialize data
        serializer = ChatHistorySerializer2(chat_history, many=True)

        # ✅ Return full response
        return Response(
            {
                "chat_id": chatbot.id,
                "user_id": chatbot.user.id,
                "title": chatbot.title,
                "total_messages": len(chat_history),
                "messages": serializer.data
            },
            status=200
        )

    elif model_name == "Academy_Heads_and_SLT":
        chatbot = Chatbot3.objects.get(id=chat_id, user=user)

        # ✅ Save user's message linked to that chat
        chat_history_user = ChatHistory3(chat=chatbot)
        chat_history_user.role = "user"
        chat_history_user.message = user_message
        chat_history_user.save()

        # Fetch last 5 messages for this chat (before adding bot reply)
        last_messages = ChatHistory3.objects.filter(chat=chatbot).order_by('-timestamp_child')[:5]

        # Reverse so they are oldest → newest (better for LLM)
        last_messages = reversed(last_messages)

        # Convert to role/content list
        context = [
            {"role": msg.role, "content": msg.message}
            for msg in last_messages
        ]
        # assistant

        # ✅ Save bot's reply
        answer = generate_hs_response(user_message,uploaded_files_list, context)
        chat_history_bot = ChatHistory3(chat=chatbot)
        chat_history_bot.role = "assistant"
        chat_history_bot.message = answer
        chat_history_bot.save()

        # ✅ Get all chat history entries for this chat
        chat_history = ChatHistory3.objects.filter(chat=chatbot).order_by('timestamp_child')

        # ✅ Serialize data
        serializer = ChatHistorySerializer3(chat_history, many=True)

        # ✅ Return full response
        return Response(
            {
                "chat_id": chatbot.id,
                "user_id": chatbot.user.id,
                "title": chatbot.title,
                "total_messages": len(chat_history),
                "messages": serializer.data
            },
            status=200
        )

    elif model_name == "Academy_Lesson_generator":
        chatbot = Chatbot4.objects.get(id=chat_id, user=user)

        # ✅ Save user's message linked to that chat
        chat_history_user = ChatHistory4(chat=chatbot)
        chat_history_user.role = "user"
        chat_history_user.message = user_message
        chat_history_user.save()

       # Fetch last 5 messages for this chat (before adding bot reply)
        last_messages = ChatHistory4.objects.filter(chat=chatbot).order_by('-timestamp_child')[:5]

        # Reverse so they are oldest → newest (better for LLM)
        last_messages = reversed(last_messages)

        # Convert to role/content list
        context = [
            {"role": msg.role, "content": msg.message}
            for msg in last_messages
        ]
        # assistant

        # ✅ Save bot's reply
        answer = generate_lesson(user_message,uploaded_files_list, context)
        chat_history_bot = ChatHistory4(chat=chatbot)
        chat_history_bot.role = "assistant"
        chat_history_bot.message = answer
        chat_history_bot.save()

        # ✅ Get all chat history entries for this chat
        chat_history = ChatHistory4.objects.filter(chat=chatbot).order_by('timestamp_child')

        # ✅ Serialize data
        serializer = ChatHistorySerializer4(chat_history, many=True)

        # ✅ Return full response
        return Response(
            {
                "chat_id": chatbot.id,
                "user_id": chatbot.user.id,
                "title": chatbot.title,
                "total_messages": len(chat_history),
                "messages": serializer.data
            },
            status=200
        )
    
    elif model_name == "Academy_Resource_generator":
        chatbot = Chatbot5.objects.get(id=chat_id, user=user)

        # ✅ Save user's message linked to that chat
        chat_history_user = ChatHistory5(chat=chatbot)
        chat_history_user.role = "user"
        chat_history_user.message = user_message
        chat_history_user.save()

        # Fetch last 5 messages for this chat (before adding bot reply)
        last_messages = ChatHistory5.objects.filter(chat=chatbot).order_by('-timestamp_child')[:5]

        # Reverse so they are oldest → newest (better for LLM)
        last_messages = reversed(last_messages)

        # Convert to role/content list
        context = [
            {"role": msg.role, "content": msg.message}
            for msg in last_messages
        ]
        # assistant

        # ✅ Save bot's reply
        answer = generate_resource(user_message,uploaded_files_list, context)
        chat_history_bot = ChatHistory5(chat=chatbot)
        chat_history_bot.role = "assistant"
        chat_history_bot.message = answer
        chat_history_bot.save()

        # ✅ Get all chat history entries for this chat
        chat_history = ChatHistory5.objects.filter(chat=chatbot).order_by('timestamp_child')

        # ✅ Serialize data
        serializer = ChatHistorySerializer5(chat_history, many=True)

        # ✅ Return full response
        return Response(
            {
                "chat_id": chatbot.id,
                "user_id": chatbot.user.id,
                "title": chatbot.title,
                "total_messages": len(chat_history),
                "messages": serializer.data
            },
            status=200
        )
    elif model_name == "Academy_sow":
        chatbot = Chatbot6.objects.get(id=chat_id, user=user)

        # ✅ Save user's message linked to that chat
        chat_history_user = ChatHistory6(chat=chatbot)
        chat_history_user.role = "user"
        chat_history_user.message = user_message
        chat_history_user.save()

        # Fetch last 5 messages for this chat (before adding bot reply)
        last_messages = ChatHistory6.objects.filter(chat=chatbot).order_by('-timestamp_child')[:5]

        # Reverse so they are oldest → newest (better for LLM)
        last_messages = reversed(last_messages)

        # Convert to role/content list
        context = [
            {"role": msg.role, "content": msg.message}
            for msg in last_messages
        ]
        # assistant

        # ✅ Save bot's reply
        answer = get_support_response_sow_academy(user_message,uploaded_files_list, context)
        chat_history_bot = ChatHistory6(chat=chatbot)
        chat_history_bot.role = "assistant"
        chat_history_bot.message = answer
        chat_history_bot.save()

        # ✅ Get all chat history entries for this chat
        chat_history = ChatHistory6.objects.filter(chat=chatbot).order_by('timestamp_child')

        # ✅ Serialize data
        serializer = ChatHistorySerializer6(chat_history, many=True)

        # ✅ Return full response
        return Response(
            {
                "chat_id": chatbot.id,
                "user_id": chatbot.user.id,
                "title": chatbot.title,
                "total_messages": len(chat_history),
                "messages": serializer.data
            },
            status=200
        )
    elif model_name == "primary_behaviour":
        chatbot = Chatbot7.objects.get(id=chat_id, user=user)

        # ✅ Save user's message linked to that chat
        chat_history_user = ChatHistory7(chat=chatbot)
        chat_history_user.role = "user"
        chat_history_user.message = user_message
        chat_history_user.save()

        # Fetch last 5 messages for this chat (before adding bot reply)
        last_messages = ChatHistory7.objects.filter(chat=chatbot).order_by('-timestamp_child')[:5]

        # Reverse so they are oldest → newest (better for LLM)
        last_messages = reversed(last_messages)

        # Convert to role/content list
        context = [
            {"role": msg.role, "content": msg.message}
            for msg in last_messages
        ]
        # assistant

        # ✅ Save bot's reply
        answer = generate_behaviour_gp(user_message,uploaded_files_list, context)
        chat_history_bot = ChatHistory7(chat=chatbot)
        chat_history_bot.role = "assistant"
        chat_history_bot.message = answer
        chat_history_bot.save()

        # ✅ Get all chat history entries for this chat
        chat_history = ChatHistory7.objects.filter(chat=chatbot).order_by('timestamp_child')

        # ✅ Serialize data
        serializer = ChatHistorySerializer7(chat_history, many=True)

        # ✅ Return full response
        return Response(
            {
                "chat_id": chatbot.id,
                "user_id": chatbot.user.id,
                "title": chatbot.title,
                "total_messages": len(chat_history),
                "messages": serializer.data
            },
            status=200
        )
    elif model_name == "primary_Communication":
        chatbot = Chatbot8.objects.get(id=chat_id, user=user)

        # ✅ Save user's message linked to that chat
        chat_history_user = ChatHistory8(chat=chatbot)
        chat_history_user.role = "user"
        chat_history_user.message = user_message
        chat_history_user.save()

        # Fetch last 5 messages for this chat (before adding bot reply)
        last_messages = ChatHistory8.objects.filter(chat=chatbot).order_by('-timestamp_child')[:5]

        # Reverse so they are oldest → newest (better for LLM)
        last_messages = reversed(last_messages)

        # Convert to role/content list
        context = [
            {"role": msg.role, "content": msg.message}
            for msg in last_messages
        ]
        # assistant

        # ✅ Save bot's reply
        answer = generate_communication_gp(user_message,uploaded_files_list, context)
        chat_history_bot = ChatHistory8(chat=chatbot)
        chat_history_bot.role = "assistant"
        chat_history_bot.message = answer
        chat_history_bot.save()

        # ✅ Get all chat history entries for this chat
        chat_history = ChatHistory8.objects.filter(chat=chatbot).order_by('timestamp_child')

        # ✅ Serialize data
        serializer = ChatHistorySerializer8(chat_history, many=True)

        # ✅ Return full response
        return Response(
            {
                "chat_id": chatbot.id,
                "user_id": chatbot.user.id,
                "title": chatbot.title,
                "total_messages": len(chat_history),
                "messages": serializer.data
            },
            status=200
        )
    elif model_name == "primary_head":
        chatbot = Chatbot9.objects.get(id=chat_id, user=user)

        # ✅ Save user's message linked to that chat
        chat_history_user = ChatHistory9(chat=chatbot)
        chat_history_user.role = "user"
        chat_history_user.message = user_message
        chat_history_user.save()

        # Fetch last 5 messages for this chat (before adding bot reply)
        last_messages = ChatHistory9.objects.filter(chat=chatbot).order_by('-timestamp_child')[:5]

        # Reverse so they are oldest → newest (better for LLM)
        last_messages = reversed(last_messages)

        # Convert to role/content list
        context = [
            {"role": msg.role, "content": msg.message}
            for msg in last_messages
        ]
        # assistant

        # ✅ Save bot's reply
        answer = generate_head_gp(user_message,uploaded_files_list, context)
        chat_history_bot = ChatHistory9(chat=chatbot)
        chat_history_bot.role = "assistant"
        chat_history_bot.message = answer
        chat_history_bot.save()

        # ✅ Get all chat history entries for this chat
        chat_history = ChatHistory9.objects.filter(chat=chatbot).order_by('timestamp_child')

        # ✅ Serialize data
        serializer = ChatHistorySerializer9(chat_history, many=True)

        # ✅ Return full response
        return Response(
            {
                "chat_id": chatbot.id,
                "user_id": chatbot.user.id,
                "title": chatbot.title,
                "total_messages": len(chat_history),
                "messages": serializer.data
            },
            status=200
        )
    elif model_name == "primary_lesson":
        chatbot = Chatbot10.objects.get(id=chat_id, user=user)

        # ✅ Save user's message linked to that chat
        chat_history_user = ChatHistory10(chat=chatbot)
        chat_history_user.role = "user"
        chat_history_user.message = user_message
        chat_history_user.save()

        # Fetch last 5 messages for this chat (before adding bot reply)
        last_messages = ChatHistory10.objects.filter(chat=chatbot).order_by('-timestamp_child')[:5]

        # Reverse so they are oldest → newest (better for LLM)
        last_messages = reversed(last_messages)

        # Convert to role/content list
        context = [
            {"role": msg.role, "content": msg.message}
            for msg in last_messages
        ]
        # assistant

        # ✅ Save bot's reply
        answer = generate_lesson_gp(user_message,uploaded_files_list, context)
        chat_history_bot = ChatHistory10(chat=chatbot)
        chat_history_bot.role = "assistant"
        chat_history_bot.message = answer
        chat_history_bot.save()

        # ✅ Get all chat history entries for this chat
        chat_history = ChatHistory10.objects.filter(chat=chatbot).order_by('timestamp_child')

        # ✅ Serialize data
        serializer = ChatHistorySerializer10(chat_history, many=True)

        # ✅ Return full response
        return Response(
            {
                "chat_id": chatbot.id,
                "user_id": chatbot.user.id,
                "title": chatbot.title,
                "total_messages": len(chat_history),
                "messages": serializer.data
            },
            status=200
        )
    elif model_name == "primary_resource":
        chatbot = Chatbot11.objects.get(id=chat_id, user=user)

        # ✅ Save user's message linked to that chat
        chat_history_user = ChatHistory11(chat=chatbot)
        chat_history_user.role = "user"
        chat_history_user.message = user_message
        chat_history_user.save()

        # Fetch last 5 messages for this chat (before adding bot reply)
        last_messages = ChatHistory11.objects.filter(chat=chatbot).order_by('-timestamp_child')[:5]

        # Reverse so they are oldest → newest (better for LLM)
        last_messages = reversed(last_messages)

        # Convert to role/content list
        context = [
            {"role": msg.role, "content": msg.message}
            for msg in last_messages
        ]
        # assistant

        # ✅ Save bot's reply
        answer = generate_resource_gp(user_message,uploaded_files_list, context)
        chat_history_bot = ChatHistory11(chat=chatbot)
        chat_history_bot.role = "assistant"
        chat_history_bot.message = answer
        chat_history_bot.save()

        # ✅ Get all chat history entries for this chat
        chat_history = ChatHistory11.objects.filter(chat=chatbot).order_by('timestamp_child')

        # ✅ Serialize data
        serializer = ChatHistorySerializer11(chat_history, many=True)

        # ✅ Return full response
        return Response(
            {
                "chat_id": chatbot.id,
                "user_id": chatbot.user.id,
                "title": chatbot.title,
                "total_messages": len(chat_history),
                "messages": serializer.data
            },
            status=200
        )
    else:
        chatbot = Chatbot12.objects.get(id=chat_id, user=user)

        # ✅ Save user's message linked to that chat
        chat_history_user = ChatHistory12(chat=chatbot)
        chat_history_user.role = "user"
        chat_history_user.message = user_message
        chat_history_user.save()

       # Fetch last 5 messages for this chat (before adding bot reply)
        last_messages = ChatHistory12.objects.filter(chat=chatbot).order_by('-timestamp_child')[:5]

        # Reverse so they are oldest → newest (better for LLM)
        last_messages = reversed(last_messages)

        # Convert to role/content list
        context = [
            {"role": msg.role, "content": msg.message}
            for msg in last_messages
        ]
        # assistant

        # ✅ Save bot's reply
        answer = generate_scheme_gp(user_message,uploaded_files_list, context)
        chat_history_bot = ChatHistory12(chat=chatbot)
        chat_history_bot.role = "assistant"
        chat_history_bot.message = answer
        chat_history_bot.save()

        # ✅ Get all chat history entries for this chat
        chat_history = ChatHistory12.objects.filter(chat=chatbot).order_by('timestamp_child')

        # ✅ Serialize data
        serializer = ChatHistorySerializer12(chat_history, many=True)

        # ✅ Return full response
        return Response(
            {
                "chat_id": chatbot.id,
                "user_id": chatbot.user.id,
                "title": chatbot.title,
                "total_messages": len(chat_history),
                "messages": serializer.data
            },
            status=200
        )


@csrf_exempt
@api_view(['POST'])  # ✅ use POST instead of GET because you’re saving data
@permission_classes([IsAuthenticated])
def get_chat_history(request):
    user = request.user
    chat_id = request.data.get('chat_id')
    model_name = request.data.get('model_name')

    if model_name == "Academy_Behaviour_strategies": 

        chatbot = Chatbot1.objects.get(id=chat_id, user=user)

        # ✅ Get all chat history entries for this chat
        chat_history = ChatHistory1.objects.filter(chat=chatbot).order_by('timestamp_child')

        # ✅ Serialize data
        serializer = ChatHistorySerializer1(chat_history, many=True)

        # ✅ Return full response
        return Response(
            {
                "chat_id": chatbot.id,
                "Model": "Academy_Behaviour_strategies",
                "user_id": chatbot.user.id,
                "title": chatbot.title,
                "total_messages": len(chat_history),
                "messages": serializer.data
            },
            status=200
        )
    elif model_name == "Academy_communication_assistant":

        chatbot = Chatbot2.objects.get(id=chat_id, user=user)

        # ✅ Get all chat history entries for this chat
        chat_history = ChatHistory2.objects.filter(chat=chatbot).order_by('timestamp_child')

        # ✅ Serialize data
        serializer = ChatHistorySerializer2(chat_history, many=True)

        # ✅ Return full response
        return Response(
            {
                "chat_id": chatbot.id,
                "Model": "Academy_communication_assistant",
                "user_id": chatbot.user.id,
                "title": chatbot.title,
                "total_messages": len(chat_history),
                "messages": serializer.data
            },
            status=200
        )

    elif model_name == "Academy_Heads_and_SLT":
        chatbot = Chatbot3.objects.get(id=chat_id, user=user)

        # ✅ Get all chat history entries for this chat
        chat_history = ChatHistory3.objects.filter(chat=chatbot).order_by('timestamp_child')

        # ✅ Serialize data
        serializer = ChatHistorySerializer3(chat_history, many=True)

        # ✅ Return full response
        return Response(
            {
                "chat_id": chatbot.id,
                "Model": "Academy_Heads_and_SLT",
                "user_id": chatbot.user.id,
                "title": chatbot.title,
                "total_messages": len(chat_history),
                "messages": serializer.data
            },
            status=200
        )

    elif model_name == "Academy_Lesson_generator":
        chatbot = Chatbot4.objects.get(id=chat_id, user=user)

        # ✅ Get all chat history entries for this chat
        chat_history = ChatHistory4.objects.filter(chat=chatbot).order_by('timestamp_child')

        # ✅ Serialize data
        serializer = ChatHistorySerializer4(chat_history, many=True)

        # ✅ Return full response
        return Response(
            {
                "chat_id": chatbot.id,
                "model": "Academy_Lesson_generator",
                "user_id": chatbot.user.id,
                "title": chatbot.title,
                "total_messages": len(chat_history),
                "messages": serializer.data
            },
            status=200
        )
    
    elif model_name == "Academy_Resource_generator":
        chatbot = Chatbot5.objects.get(id=chat_id, user=user)

        # ✅ Get all chat history entries for this chat
        chat_history = ChatHistory5.objects.filter(chat=chatbot).order_by('timestamp_child')

        # ✅ Serialize data
        serializer = ChatHistorySerializer5(chat_history, many=True)

        # ✅ Return full response
        return Response(
            {
                "chat_id": chatbot.id,
                "Model": "Academy_Resource_generator",
                "user_id": chatbot.user.id,
                "title": chatbot.title,
                "total_messages": len(chat_history),
                "messages": serializer.data
            },
            status=200
        )
    elif model_name == "Academy_sow":
        chatbot = Chatbot6.objects.get(id=chat_id, user=user)

        # ✅ Get all chat history entries for this chat
        chat_history = ChatHistory6.objects.filter(chat=chatbot).order_by('timestamp_child')

        # ✅ Serialize data
        serializer = ChatHistorySerializer6(chat_history, many=True)

        # ✅ Return full response
        return Response(
            {
                "chat_id": chatbot.id,
                "Model" : "Academy_sow",
                "user_id": chatbot.user.id,
                "title": chatbot.title,
                "total_messages": len(chat_history),
                "messages": serializer.data
            },
            status=200
        )
    elif model_name == "primary_behaviour":
        chatbot = Chatbot7.objects.get(id=chat_id, user=user)

        # ✅ Get all chat history entries for this chat
        chat_history = ChatHistory7.objects.filter(chat=chatbot).order_by('timestamp_child')

        # ✅ Serialize data
        serializer = ChatHistorySerializer7(chat_history, many=True)

        # ✅ Return full response
        return Response(
            {
                "chat_id": chatbot.id,
                "Model" : "primary_behaviour",
                "user_id": chatbot.user.id,
                "title": chatbot.title,
                "total_messages": len(chat_history),
                "messages": serializer.data
            },
            status=200
        )
    elif model_name == "primary_Communication":
        chatbot = Chatbot8.objects.get(id=chat_id, user=user)

        # ✅ Get all chat history entries for this chat
        chat_history = ChatHistory8.objects.filter(chat=chatbot).order_by('timestamp_child')

        # ✅ Serialize data
        serializer = ChatHistorySerializer8(chat_history, many=True)

        # ✅ Return full response
        return Response(
            {
                "chat_id": chatbot.id,
                "Model" : "primary_Communication",
                "user_id": chatbot.user.id,
                "title": chatbot.title,
                "total_messages": len(chat_history),
                "messages": serializer.data
            },
            status=200
        )
    elif model_name == "primary_head":
        chatbot = Chatbot9.objects.get(id=chat_id, user=user)

        # ✅ Get all chat history entries for this chat
        chat_history = ChatHistory9.objects.filter(chat=chatbot).order_by('timestamp_child')

        # ✅ Serialize data
        serializer = ChatHistorySerializer9(chat_history, many=True)

        # ✅ Return full response
        return Response(
            {
                "chat_id": chatbot.id,
                "Model" : "primary_head",
                "user_id": chatbot.user.id,
                "title": chatbot.title,
                "total_messages": len(chat_history),
                "messages": serializer.data
            },
            status=200
        )
    elif model_name == "primary_lesson":
        chatbot = Chatbot10.objects.get(id=chat_id, user=user)

        # ✅ Get all chat history entries for this chat
        chat_history = ChatHistory10.objects.filter(chat=chatbot).order_by('timestamp_child')

        # ✅ Serialize data
        serializer = ChatHistorySerializer10(chat_history, many=True)

        # ✅ Return full response
        return Response(
            {
                "chat_id": chatbot.id,
                "Model" : "primary_lesson",
                "user_id": chatbot.user.id,
                "title": chatbot.title,
                "total_messages": len(chat_history),
                "messages": serializer.data
            },
            status=200
        )
    elif model_name == "primary_resource":
        chatbot = Chatbot11.objects.get(id=chat_id, user=user)

        # ✅ Get all chat history entries for this chat
        chat_history = ChatHistory11.objects.filter(chat=chatbot).order_by('timestamp_child')

        # ✅ Serialize data
        serializer = ChatHistorySerializer11(chat_history, many=True)

        # ✅ Return full response
        return Response(
            {
                "chat_id": chatbot.id,
                "Model" : "primary_resource",
                "user_id": chatbot.user.id,
                "title": chatbot.title,
                "total_messages": len(chat_history),
                "messages": serializer.data
            },
            status=200
        )
    else:
        chatbot = Chatbot12.objects.get(id=chat_id, user=user)

        # ✅ Get all chat history entries for this chat
        chat_history = ChatHistory12.objects.filter(chat=chatbot).order_by('timestamp_child')

        # ✅ Serialize data
        serializer = ChatHistorySerializer12(chat_history, many=True)

        # ✅ Return full response
        return Response(
            {
                "chat_id": chatbot.id,
                "Model" :"primary_sow",
                "user_id": chatbot.user.id,
                "title": chatbot.title,
                "total_messages": len(chat_history),
                "messages": serializer.data
            },
            status=200
        )
        
# @csrf_exempt
# @api_view(['POST'])  # ✅ use POST instead of GET because you’re saving data
# @permission_classes([IsAuthenticated])
# def get_chat_history(request):
#     user = request.user
#     chat_id = request.data.get('chat_id')
#     user_message = request.data.get('user_message')

#     if not chat_id or not user_message:
#         return Response({"error": "chat_id and user_message are required."}, status=400)

#     try:
#         # ✅ Fetch the existing chat
#         chatbot = Chatbot1.objects.get(id=chat_id, user=user)
#     except Chatbot1.DoesNotExist:
#         return Response({"error": "Chat not found for this user."}, status=404)

#     # ✅ Save user's message linked to that chat
#     chat_history_user = ChatHistory1(chat=chatbot)
#     chat_history_user.role = "User"
#     chat_history_user.message = user_message
#     chat_history_user.save()

#     # ✅ Save bot's reply
#     answer = "answer of the question 0000"
#     chat_history_bot = ChatHistory1(chat=chatbot)
#     chat_history_bot.role = "Bot"
#     chat_history_bot.message = answer
#     chat_history_bot.save()

#     # ✅ Get all chat history entries for this chat
#     chat_history = ChatHistory1.objects.filter(chat=chatbot).order_by('timestamp_child')

#     # ✅ Serialize data
#     serializer = ChatHistorySerializer1(chat_history, many=True)

#     # ✅ Return full response
#     return Response(
#         {
#             "chat_id": chatbot.id,
#             "user_id": chatbot.user.id,
#             "title": chatbot.title,
#             "total_messages": len(chat_history),
#             "messages": serializer.data
#         },
#         status=200
#     )



    {
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MjU3MzMzNCwiaWF0IjoxNzYxMDM3MzM0LCJqdGkiOiI4NTJkYTY3ZTM0ZDg0MjZkOWU4ZDkxNjMxODZmYmUwYSIsInVzZXJfaWQiOiI3In0.6zICoSL-3J8K-KrsL8QZYyuoZ7ydLPY8ipL5gZh8hPM",
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzkxMjc3MzM0LCJpYXQiOjE3NjEwMzczMzQsImp0aSI6IjFlZmUwYjZhNjhkNDRkZDViYTNkNTk2N2U0YjEzYjcwIiwidXNlcl9pZCI6IjcifQ.uj9g1B2IvJ3w_9rZsbuNuXu0So_YMYJR4vo29swuM9I",
    "profile_data": {
        "user": 7,
        "email": "rafsunahmadofficial@gmail.com",
        "first_name": "",
        "last_name": "",
        "full_name": "",
        "phone_number": "01837523658",
        "image": null,
        "auth_provider": "email_password"
    },
    "message": "Successfully authenticated."
}
    

"""  
"email": "rafsunahmadofficial@gmail.com",
    "password": "raf001",
    "full_name": "rafsun ahamd",
    "phone_number":"01837523658"

"""