from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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

    if task.status == 'open':
        task.status = 'in_progress'
    elif task.status == 'in_progress':
        task.status = 'finished'
    # If task is already finished, don't change the status

    task.save()
    messages.success(request, f'Статус изменен на: {task.get_status_display()}')

    return redirect('tasks:task_list')