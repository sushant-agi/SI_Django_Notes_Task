from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Note, Profile
import re
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password

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
        security_question = request.POST['security_question']
        security_answer = request.POST['security_answer']

        password_pattern = (
            r'^(?=.*[a-z])'
            r'(?=.*[A-Z])'
            r'(?=.*\d)'
            r'(?=.*[@$!%*?&#])'
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

        user=User.objects.create_user(
            username=username,
            password=password
        )
        Profile.objects.create(
            user=user,
            security_question=security_question,
            security_answer=make_password(security_answer)
        )
        messages.success(
            request,
            'Registration successful! You can now login.'
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

def forgot_password(request):

    if request.method == 'POST':

        username = request.POST['username']

        try:
            user = User.objects.get(username=username)
            profile = Profile.objects.get(user=user)

        except (User.DoesNotExist, Profile.DoesNotExist):
            return render(
                request,
                'notes/forgot_password.html',
                {'error': 'Invalid username.'}
            )

        request.session['reset_user_id'] = user.id

        return render(
            request,
            'notes/security_question.html',
            {'question': profile.security_question}
        )

    return render(
        request,
        'notes/forgot_password.html'
    )

def verify_security_answer(request):

    if request.method != 'POST':
        return redirect('forgot_password')

    user_id = request.session.get('reset_user_id')

    if not user_id:
        return redirect('forgot_password')

    try:
        user = User.objects.get(id=user_id)
        profile = Profile.objects.get(user=user)

    except (User.DoesNotExist, Profile.DoesNotExist):
        return redirect('forgot_password')

    answer = request.POST['security_answer']

    if not check_password(answer, profile.security_answer):
        return render(
            request,
            'notes/security_question.html',
            {
                'question': profile.security_question,
                'error': 'Incorrect answer. Please try again.'
            }
        )

    request.session['password_reset_verified'] = True

    return redirect('reset_password')

def reset_password(request):

    if not request.session.get('password_reset_verified'):
        return redirect('forgot_password')

    user_id = request.session.get('reset_user_id')

    if not user_id:
        return redirect('forgot_password')

    try:
        user = User.objects.get(id=user_id)

    except User.DoesNotExist:
        return redirect('forgot_password')

    if request.method == 'POST':

        new_password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        password_pattern = (
            r'^(?=.*[a-z])'
            r'(?=.*[A-Z])'
            r'(?=.*\d)'
            r'(?=.*[@$!%*?&#])'
            r'.{8,}$'
        )

        if not re.match(password_pattern, new_password):
            return render(
                request,
                'notes/reset_password.html',
                {
                    'error': (
                        'Password must be at least 8 characters long and contain '
                        'at least one uppercase letter, lowercase letter, number, '
                        'and special character (@$!%*?&#).'
                    )
                }
            )

        if new_password != confirm_password:
            return render(
                request,
                'notes/reset_password.html',
                {'error': 'Passwords do not match.'}
            )

        user.set_password(new_password)
        user.save()

        request.session.pop('reset_user_id', None)
        request.session.pop('password_reset_verified', None)

        messages.success(
            request,
            'Password reset successful! You can now log in.'
        )

        return redirect('login')

    return render(
        request,
        'notes/reset_password.html'
    )
