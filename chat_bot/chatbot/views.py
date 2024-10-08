import os
from ai21 import AI21Client
from ai21.models.chat import ChatMessage, ResponseFormat
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat
from django.utils import timezone
# Initialize the AI21 client with your API key
client = AI21Client(api_key='m9X4LBmTUXFaXHACo9xSlfm70kQoABzX')

def ask_new_api(message):
    try:
        # Define the chat completion request
        response = client.chat.completions.create(
            model="jamba-1.5-large",
            messages=[ChatMessage(role="user", content=message)],
            max_tokens=150,
            temperature=0.7,
            response_format=ResponseFormat(type="text"),
        )
        
        # Extract the answer from the response
        answer = response.choices[0].message.content.strip()
        return answer
    except Exception as e:
        return f"Error: {str(e)}"

@csrf_exempt
def chatbot(request):
    chats = Chat.objects.filter(user=request.user)
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            response = ask_new_api(message)

            chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
            chat.save()
            return JsonResponse({'message': message, 'response': response})
        else:
            return JsonResponse({'error': 'No message provided'}, status=400)
    return render(request, 'chatbot.html', {'chats':chats})

def login(request):
    if request.method =='POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password) #checks if user actually exists
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error = "Invalid user"
            return render(request, 'login.html' , {'error':error})
    else:
        return render(request, 'login.html')

def logout(request):
    auth.logout(request)
    return redirect('login')  # Redirect to login or another appropriate page after logout

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 == password2:
            try:
                # Create user
                user = User.objects.create_user(username=username, email=email, password=password1)
                
                # Authenticate user
                user = auth.authenticate(username=username, password=password1)
                if user is not None:
                    auth.login(request, user)
                    return redirect('chatbot')
                else:
                    return render(request, 'register.html', {'error': 'Authentication failed'})
            except Exception as e:
                error = "Error in creating account: " + str(e)
                return render(request, 'register.html', {'error': error})
        else:
            error = 'Passwords do not match'
            return render(request, 'register.html', {'error': error})
    
    return render(request, 'register.html')
