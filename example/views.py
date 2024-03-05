from django.shortcuts import render, redirect ,HttpResponse

def index(request):
    return HttpResponse('Contact page')