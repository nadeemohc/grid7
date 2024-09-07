from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
import sweetify

def blocked_user_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if the user is authenticated and is inactive (blocked)
        if request.user.is_authenticated and not request.user.is_active:
            # Log the user out
            logout(request)
            # Add a message to inform the user that they are blocked
            sweetify.toast(request, "Your account has been blocked. You cannot perform this action.", icon='error', timer=5000)
            # Redirect the user to the login page or another page
            return redirect('store:home')  # Change 'login' to the appropriate name of your login page
        # If the user is not blocked, continue with the view
        return view_func(request, *args, **kwargs)
    return wrapper
