# example/views.py
from datetime import datetime

from django.http import HttpResponse
from database.models import News
from django.shortcuts import render

def contanct(request):
    return HttpResponse("<h1>m name is lakhman</h1>")

def index(request):
    newsdata = News.objects.all()
    news_data = []
    for data in newsdata:
        print(data.title)
        print(data.content)
        print(data.created_at)
        print(data.updated_at)
        print(data.is_published)
        news_data.append({
            'title': data.title,
            'content': data.content,
            'created_at': data.created_at,
            'updated_at': data.updated_at,
            'is_published': data.is_published
        })
  
    return render(request, 'index.html', {'news_data': news_data})
