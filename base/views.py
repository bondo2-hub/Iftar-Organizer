from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegistrationForm, OrganizeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User , Notification

@login_required(login_url='login')
def home(request):
    return render(request, 'base/home.html')

def notif_center(request):
    user_notif = Notification.objects.filter(user=request.user).order_by('created_at')
    user_notif.update(is_read=True)
    return render(request, 'base/notification_center.html', {'notifications': user_notif})

def register_view(request):
    page = 'register'

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST,request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            print('error')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'base/auth.html', {'page': page, 'form': form})

def login_view(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            print('Authentication failed')

    return render(request, 'base/auth.html', {'page': page})

def logout_view(request):

    logout(request)
    return redirect('home')

@login_required(login_url='login')
def organize_view(request):
    page = 'organize'
    form = OrganizeForm()

    if request.method == 'POST':
        form = OrganizeForm(request.POST, request.FILES)
        if form.is_valid():
            iftar = form.save(commit=False)
            iftar.host = request.user
            iftar.save()
            messages.success(request, 'Iftar organized successfully.')
            return redirect('home')
        else:
            print('error')
            messages.error(request, 'Iftar organization process failed.')

    return render(request, 'base/auth.html', {'page': page, 'form': form})


