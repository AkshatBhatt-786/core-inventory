from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, SignupForm


def login_view(request):
    # Already logged in — go to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    form = LoginForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard:index')
        else:
            messages.error(request, 'Invalid login ID or password.')

    return render(request, 'accounts/login.html', {'form': form})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    form = SignupForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created! Welcome, {user.username}!')
            return redirect('dashboard:index')
        else:
            messages.error(request, 'Please fix the errors below.')

    return render(request, 'accounts/signup.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')