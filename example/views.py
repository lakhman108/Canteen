
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from example.forms import CustomUserLoginForm, CustomUserRegistrationForm
from canteen.models import CustomUser

def contact(request):
    return HttpResponse("<h1>m name is lakhman</h1>")

@login_required
def index(request):

    # newsdata = News.objects.all()
    # news_data = []
    # for data in newsdata:
    #     print(data.title)
    #     print(data.content)
    #     print(data.created_at)
    #     print(data.updated_at)
    #     print(data.is_published)
    #     news_data.append({
    #         'title': data.title,
    #         'content': data.content,
    #         'created_at': data.created_at,
    #         'updated_at': data.updated_at,
    #         'is_published': data.is_published
    #     })
  
    return render(request, 'example/index.html')


def custom_user_login(request):
    if request.method == 'POST':
        form = CustomUserLoginForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('example:index')
    else:
        form = CustomUserLoginForm()
    return render(request, 'login.html', {'form': form})

def custom_user_register(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('example:index')
    else:
        form = CustomUserRegistrationForm()
    return render(request, 'register.html', {'form': form})


