from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction

from .models import *
from .forms_tmp import *

def show_index_page(request):
  return render(request, 'index.html')

@transaction.atomic
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
  return render(request, 'myups/register.html', {'form': ipt_form})

def user_login(request):
  if request.user.is_authenticated:
    return redirect('index')
  if request.method == 'POST':
    new_user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if new_user is not None and new_user.is_active:
      # if new_user.is_active:
      login(request, new_user)
      return redirect('index')
      # else:
      #   messages.info(request, 'invalid login')
    else:
      messages.info(request, 'invalid login')
  return render(request, 'myups/login.html')

def user_logout(request):
  logout(request)
  return redirect('user_login')

@transaction.atomic
def change_email(request):
  email_form = ChangeEmailForm(request.POST or None)
  if request.method == 'POST':
    if email_form.is_valid():
      cur_user = request.user
      cur_user.email = email_form.cleaned_data['email']
      cur_user.save()
      return redirect('index')
    else:
      messages.info(request, 'Invalid form')
  else:
    email_form = ChangeEmailForm(instance=request.user)
  return render(request, 'myups/change_email.html', {'form': email_form})
  

def check_package(request):
  pkg_id = request.POST.get('package_id')
  package = Package_tmp.objects.get(pk = pkg_id)
  return render(request, 'myups/package.html', {'packages': package})
  
def check_all_packages(request, user_id):
  cur_user = request.user
  cur_acc = Account_tmp.objects.get(user_id = cur_user.id)
  cur_packages = Package_tmp.objects.filter(pkg_user_id = cur_acc.id)
  return render(request, 'myups/package.html', {'packages': cur_packages})

def change_dest(request):
  # if request.method == 'POST':
  #   package_id = request.POST.get('package_id')
  #   if package_id is None:
  #     messages.warning(request, 'Please enter a package id')
  #     return redirect('index')
  #   cur_pack = Package_tmp.objects.get(pk = package_id)
  #   if not request.user.is_active or not request.user.is_authenticated or not cur_pack.pkg_user or not request.user == cur_pack.pkg_user.user:
  #     messages.warning(request, 'You do not have permission to change this package, Please log as owner')
  #     return redirect('user_login')
  #   if cur_pack.pkg_status != 'T':
  #     messages.warning(request, 'This package is not in the state to change destination.')    
  # return render(request, 'myups/change_dest.html', {'package':
  pass