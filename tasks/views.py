from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Task
from .forms import TaskForm


@login_required(login_url='users:login')
def task_list(request):
    """Список всех задач пользователя"""
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')

    # Фильтрация по статусу
    status_filter = request.GET.get('status', None)
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    # Фильтрация по приоритету
    priority_filter = request.GET.get('priority', None)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)

    context = {
        'tasks': tasks,
        'status_choices': Task._meta.get_field('status').choices,
        'priority_choices': Task._meta.get_field('priority').choices,
        'current_status': status_filter,
        'current_priority': priority_filter,
    }

    return render(request, 'tasks/task_list.html', context)


@login_required(login_url='users:login')
def task_detail(request, pk):
    """Детальный просмотр задачи"""
    task = get_object_or_404(Task, pk=pk, user=request.user)
    return render(request, 'tasks/task_detail.html', {'task': task})


@login_required(login_url='users:login')
def task_create(request):
    """Создание новой задачи"""
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, 'Задача создана!')
            return redirect('tasks:task_list')
    else:
        form = TaskForm()

    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Создать задачу'})


@login_required(login_url='users:login')
def task_edit(request, pk):
    """Редактирование задачи"""
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Задача обновлена!')
            return redirect('tasks:task_list')
    else:
        form = TaskForm(instance=task)

    return render(request, 'tasks/task_form.html', {'form': form, 'task': task, 'title': 'Редактировать задачу'})


@login_required(login_url='users:login')
def task_delete(request, pk):
    """Удаление задачи"""
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Задача удалена!')
        return redirect('tasks:task_list')

    return render(request, 'tasks/task_confirm_delete.html', {'task': task})


@login_required(login_url='users:login')
def task_toggle_status(request, pk):
    """Переключение статуса задачи"""
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST' and request.content_type == 'application/json':
        # Handle AJAX request from Kanban board
        try:
            data = json.loads(request.body)
            new_status = data.get('status')

            if new_status in ['open', 'in_progress', 'finished']:
                task.status = new_status
                task.save()

                return JsonResponse({
                    'success': True,
                    'message': f'Статус изменен на: {task.get_status_display()}',
                    'task_id': task.id,
                    'new_status': task.status
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Неверный статус задачи'
                }, status=400)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Неверный формат данных'
            }, status=400)
    else:
        # Handle regular form submission
        if task.status == 'open':
            task.status = 'in_progress'
        elif task.status == 'in_progress':
            task.status = 'finished'
        # If task is already finished, don't change the status

        task.save()
        messages.success(request, f'Статус изменен на: {task.get_status_display()}')

        return redirect('tasks:task_list')


@login_required(login_url='users:login')
def kanban_board(request):
    """Отображение Kanban доски задач"""
    # Получаем задачи пользователя и группируем по статусам
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')

    open_tasks = tasks.filter(status='open')
    progress_tasks = tasks.filter(status='in_progress')
    finished_tasks = tasks.filter(status='finished')

    context = {
        'open_tasks': open_tasks,
        'progress_tasks': progress_tasks,
        'finished_tasks': finished_tasks,
    }

    return render(request, 'tasks/kanban_board.html', context)