from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache

# Create your views here.

# @never_cache
def home(request):
<<<<<<< HEAD
    return render(request, 'store/index.html', {'title':'Home'})
=======
    return render(request, 'dashboard/home.html', {'title':'Home'})
>>>>>>> main
