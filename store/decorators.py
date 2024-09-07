from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.http import HttpRequest
import sweetify

def blocked_user_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Ensure `request` is of type `HttpRequest`
        if not isinstance(request, HttpRequest):
            print(f"Error: 'request' is not an HttpRequest! It is {type(request)}")
        
        # Ensure `request.user` is an `User` object
        if hasattr(request, 'user'):
            print(f"request.user: {request.user}, type: {type(request.user)}")
        else:
            print("Error: 'request' does not have 'user' attribute.")

        # Check if the user is authenticated and inactive
        if request.user.is_authenticated and not request.user.is_active:
            logout(request)
            sweetify.toast(request, "Your account has been blocked. You cannot perform this action.", icon='error', timer=5000)
            return redirect('store:home')
        
        return view_func(request, *args, **kwargs)
    return wrapper
