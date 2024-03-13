from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect ,HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserLoginForm, CustomUserRegistrationForm
from .models import CustomUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

from django.contrib import messages
from django.contrib.auth import logout

@login_required
def contact(request):
    return HttpResponse('Contact page')
   

@login_required
def index(request):
    
    print(request.user)
    print(request.GET.get('next'))

   
    return render(request, 'index.html')

def custom_user_login(request):
    if request.method == 'POST':
        form = CustomUserLoginForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Authenticate the user
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Log in the user
                login(request, user)
                return redirect('canteen:index')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid form data.')
    else:
        form = CustomUserLoginForm()

    return render(request, 'login.html', {'form': form})

def custom_user_register(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            email = username+"@gmail.com"  # Get email from the form

            # Create the user using create_user method
            user = User.objects.create_user(username, email, password)

            # Log in the user
            login(request, user)

            return redirect('canteen:index')
        else:
            messages.error(request, 'Invalid form data.')
    else:
        form = CustomUserRegistrationForm()

    return render(request, 'register.html', {'form': form})




def custom_user_logout(request):
    logout(request)
    # Redirect to a non-protected page
    return redirect('canteen:index')
