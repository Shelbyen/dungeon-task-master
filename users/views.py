from django.shortcuts import render, redirect
from django.contrib.auth import login, update_session_auth_hash, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .forms import UserRegistrationForm, UserProfileForm, ChangePasswordForm, UserAuthenticationForm


def register(request):
    """Регистрация нового пользователя"""
    # If user is already authenticated, allow registration but warn them
    if request.user.is_authenticated:
        # Log out the current user to allow registration of a new user
        from django.contrib.auth import logout
        logout(request)

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


class CustomLoginView(LoginView):
    """Custom login view that forces logout before login"""
    template_name = 'users/login.html'
    authentication_form = UserAuthenticationForm

    def dispatch(self, request, *args, **kwargs):
        # If user is already logged in, log them out first
        if request.user.is_authenticated:
            from django.contrib.auth import logout
            logout(request)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('tasks:task_list')


def profile(request):
    """Профиль пользователя"""
    # If user is not authenticated, redirect to login
    if not request.user.is_authenticated:
        return redirect('users:login')

    user = request.user
    context = {
        'user': user,
        'total_tasks': user.tasks.count(),
        'finished_tasks': user.tasks.filter(status='finished').count(),
        'in_progress_tasks': user.tasks.filter(status='in_progress').count(),
    }
    return render(request, 'users/profile.html', context)


def force_logout_and_login(request):
    """Force logout and redirect to login"""
    from django.contrib.auth import logout
    logout(request)
    return redirect('users:login')


def custom_logout(request):
    """Custom logout view that ensures complete session cleanup"""
    from django.contrib.auth import logout
    from django.contrib import messages

    if request.user.is_authenticated:
        username = request.user.username if hasattr(request.user, 'username') else request.user.email
        logout(request)
        messages.success(request, 'Вы успешно вышли из системы.')

    return redirect('users:login')


@login_required(login_url='users:login')
def delete_account(request):
    """Delete user account"""
    from .models import User  # Import User model locally

    if request.method == 'POST':
        user_id = request.user.id
        user_email = request.user.email

        # Log out the user before deletion to prevent session issues
        from django.contrib.auth import logout
        logout(request)

        # Delete the user account
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            messages.success(request, f'Аккаунт {user_email} успешно удален.')
        except User.DoesNotExist:
            messages.error(request, 'Ошибка: Аккаунт не найден.')

        return redirect('users:login')

    return render(request, 'users/delete_account_confirmation.html', {'user': request.user})


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