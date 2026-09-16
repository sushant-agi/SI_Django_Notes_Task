from django.shortcuts import render, redirect
from django.contrib.auth.models import User

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
