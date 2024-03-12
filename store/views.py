from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache

# Create your views here.

# @never_cache
def home(request):
    return render(request, 'dashboard/home.html', {'title':'Home'})
