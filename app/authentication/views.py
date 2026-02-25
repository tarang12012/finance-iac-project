from django.shortcuts import render, redirect
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib import auth

class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({'email_error': 'Invalid Email'}, status=400)
        return JsonResponse({'email_valid': True})

class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse({'username_error': 'Username should only contain alphanumeric characters'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'Username already exists'}, status=409)
        return JsonResponse({'username_valid': True})

class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')

    def post(self, request):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context = {
            'fieldValues': request.POST
        }

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Enter a valid email address.')
            return render(request, 'authentication/register.html', context)

        if not User.objects.filter(username=username).exists():
            if len(password) < 6:
                messages.error(request, 'Password too short')
                return render(request, 'authentication/register.html', context)

            user = User.objects.create_user(username=username, email=email)
            user.set_password(password)
            user.is_active = True  
            user.save()

            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')

        messages.error(request, 'Username already exists')
        return render(request, 'authentication/register.html', context)

class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, 'Welcome, ' + user.username + '. You are now logged in.')
                    return redirect('expenses')
                messages.error(request, 'Account is not active.')
                return render(request, 'authentication/login.html')
            messages.error(request, 'Invalid credentials. Try again.')
            return render(request, 'authentication/login.html')

        messages.error(request, 'Please fill in all fields.')
        return render(request, 'authentication/login.html')

class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been logged out.')
        return redirect('login')
