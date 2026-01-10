from django.shortcuts import render, redirect
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .forms import UserRegistrationForm, UserProfileForm, ChangePasswordForm, UserAuthenticationForm


def register(request):
    """Регистрация нового пользователя"""
    if request.user.is_authenticated:
        return redirect('tasks:task_list')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('name')
            messages.success(request, f'Аккаунт создан для {username}! Вы авторизованы.')
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('tasks:task_list')
    else:
        form = UserRegistrationForm()

    return render(request, 'users/register.html', {'form': form})


@login_required(login_url='users:login')
def profile(request):
    """Профиль пользователя"""
    return render(request, 'users/profile.html', {'user': request.user})


@login_required(login_url='users:login')
def edit_profile(request):
    """Редактирование профиля"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлен!')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'users/edit_profile.html', {'form': form})


@login_required(login_url='users:login')
def change_password(request):
    """Смена пароля"""
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            user = request.user
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password1']

            # Проверяем старый пароль
            if not user.check_password(old_password):
                messages.error(request, 'Старый пароль неверный!')
            else:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Пароль изменен!')
                return redirect('users:profile')
    else:
        form = ChangePasswordForm()

    return render(request, 'users/change_password.html', {'form': form})