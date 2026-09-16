from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Note
import re

@login_required
def home(request):
    notes= Note.objects.filter(user=request.user)
    return render(request, 'notes/home.html', {'notes': notes})

@login_required
def create_note(request):
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']
        image=request.FILES.get('image')

        Note.objects.create(
            user=request.user,
            title=title,
            content=content,
            image=image
        )

        return redirect('home')

    return render(request, 'notes/create_note.html')

@login_required
def edit_note(request, pk):
    note = get_object_or_404(
        Note,
        id=pk,
        user=request.user
    )

    if request.method == 'POST':
        note.title = request.POST['title']
        note.content = request.POST['content']

        if request.POST.get('remove_existing_image') == 'true':
            note.image.delete(save=False)
            note.image = None

        if request.FILES.get('image'):
            note.image = request.FILES.get('image')

        note.save()

        return redirect('home')

    return render(
        request,
        'notes/edit_note.html',
        {'note': note}
    )

@login_required
def delete_note(request, pk):
    note = get_object_or_404(
        Note,
        id=pk,
        user=request.user
    )

    if request.method == 'POST':
        note.delete()
        return redirect('home')

    return render(
        request,
        'notes/delete_note.html',
        {'note': note}
    )

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        password_pattern = (
            r'^(?=.*[a-z])'
            r'(?=.*[A-Z])'
            r'(?=.*\d)'
            r'(?=.*[@$!%*?&])'
            r'.{8,}$'
        )

        if not re.fullmatch(password_pattern, password):

            return render(
                request,
                'notes/register.html',
                {
                    'error': 'Password must contain at least 8 characters, one uppercase letter, one lowercase letter, one number, and one special character.'
                }
            )

        if User.objects.filter(username=username).exists():

            return render(
                request,
                'notes/register.html',
                {
                    'error': 'Username already exists.'
                }
            )

        User.objects.create_user(
            username=username,
            password=password
        )

        return redirect('login')

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
