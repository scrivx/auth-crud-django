from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone

# Create your views here.
def home(request) :
  return render(request, 'home.html')

def signup(request) :
  if request.method == 'GET':
    print('↗️ enviando datos')
    return render(request, 'signup.html', {
      'form' : UserCreationForm
    })
  else :
    if request.POST ['password1'] == request.POST ['password2'] :
      # register user
      try :
        user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
        user.save()
        login(request, user)
        return redirect('tasks')
      except IntegrityError:
        return render(request, 'signup.html', {
          'form' : UserCreationForm,
          'error' : 'username already exists'
        })
    
    return render(request, 'signup.html', {
      'form' : UserCreationForm,
      'error' : 'passwords do not match'
    })

def tasks(request):
  tasks = Task.objects.filter(user=request.user, date_completed__isnull=True)
  return render(request, 'tasks.html', {
    'tasks' : tasks
  })

# para las tareas completadas
def tasks_completed(request):
  tasks = Task.objects.filter(user=request.user, date_completed__isnull=True)
  return render(request, 'tasks.html', {
    'tasks' : tasks
  })


def create_task(request):
  if request.method == 'GET':
    return render(request, 'create.task.html', {
      'form' : TaskForm
    })
  else :
    try:
      form = TaskForm(request.POST)
      new_task = form.save(commit=False)
      new_task.user = request.user
      new_task.save()
      return redirect('tasks')
    except ValueError:
      return render(request, 'create.task.html', {
        'form' : TaskForm,
        'error' : 'Please provide valida data'
      })      

def task_detail(request, task_id):
  if request.method == 'GET':
    # tasks = Task.objects.get(pk=task_id) -> una forma de usar (poco eficiente)
    task = get_object_or_404(Task, pk=task_id, user=request.user) # una forma mas eficiente
    form = TaskForm(instance=task)
    return render(request, 'task.detail.html', { 'task' : task, 'form' : form })
  else :
    try:
      task =get_object_or_404(Task, pk=task_id, user=request.user)
      form = TaskForm(request.POST, instance=task)
      form.save()
      return redirect('tasks')
    except ValueError:
      return render(request, 'task.detail.html', { 
        'task' : task, 
        'form' : form, 
        'error' : 'Error updating task' 
      })

def task_complete(request, task_id):
  task = get_object_or_404(Task, pk=task_id, user=request.user)
  if request.method == 'POST':
    task.date_completed = timezone.now()
    task.save()
    return redirect('tasks')

def task_delete(request, task_id):
  task = get_object_or_404(Task, pk=task_id, user=request.user)
  if request.method == 'POST':
    task.delete()
    return redirect('tasks')
    

def signout(request):
  logout(request)
  return redirect('home')


def signin(request):
  if request.method == 'GET':
    return render(request, 'signin.html', {
      'form' : AuthenticationForm
    })
  else :
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    
    if user is None :
      return render(request, 'signin.html', {
        'form' : AuthenticationForm,
        'error' : 'username or password is incorrect'
      })
    else :
      login(request, user)
      return redirect('tasks')