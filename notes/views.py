from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

def home(request):
    return render(request, 'notes/home.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        User.objects.create_user(
            username=username,
            password=password
        )

        return redirect('home')

    return render(request, 'notes/register.html')

def login_view(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']

        user=authenticate(
            request,
            username=username, 
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('home')

        return render(
            request,
            'notes/login.html',
            {'error': 'Invalid username or password'}
        )
    return render(request, 'notes/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')
