from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, View
)
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Task
from .forms import TaskForm


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).order_by('-created_at')


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:task_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Задача успешно создана!')
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:task_list')

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Задача успешно обновлена!')
        return super().form_valid(form)


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('tasks:task_list')

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Задача успешно удалена!')
        return super().delete(request, *args, **kwargs)


class TaskStatusUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk, status):
        task = get_object_or_404(Task, pk=pk, user=request.user)
        task.status = status
        task.save()
        messages.success(request, f'Статус задачи изменен на "{task.get_status_display()}"')
        return redirect('tasks:task_list')