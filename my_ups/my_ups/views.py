from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import *
from .forms_tmp import *

def show_index_page(request):
  return render(request, 'index.html')


def user_register(request):
  if request.method == 'POST':
    ipt_form = RegForm(request.POST or None)
    if ipt_form.is_valid():
      new_user = ipt_form.save(commit=False)
      new_user.set_password(ipt_form.cleaned_data['password'])
      new_user.save()
      new_user = authenticate(username=ipt_form.cleaned_data['username'], password=ipt_form.cleaned_data['password'])
      new_acc = Account_tmp()
      new_acc.user = new_user
      world = World.objects.get(active_status = True)
      new_acc.account_world = world
      new_acc.save()
      return redirect('user_login')
    else:
      messages.info(request, 'Invalid form')
      pass
  else:
    ipt_form = RegForm()
  return render(request, 'register.html', {'form': ipt_form})

def user_login(request):
  if request.user.is_authenticated:
    return redirect('show_index_page')
  if request.method == 'POST':
    new_user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if new_user is not None and new_user.is_active:
      # if new_user.is_active:
      login(request, new_user)
      return redirect('show_index_page')
      # else:
      #   messages.info(request, 'invalid login')
    else:
      messages.info(request, 'invalid login')
  return render(request, 'login.html')


def check_package(request):
  pkg_id = request.POST.get('package_id')
  package = Package_tmp.objects.get(pk = pkg_id)
  return render(request, 'package.html', {'packages': package})
  
def check_all_packages(request):
  cur_user = request.user
  cur_acc = Account_tmp.objects.get(user_id = cur_user.id)
  cur_packages = Package_tmp.objects.filter(pkg_user_id = cur_acc.id)
  return render(request, 'package.html', {'packages': cur_packages})

def user_logout(request):
  logout(request)
  return redirect('user_login')