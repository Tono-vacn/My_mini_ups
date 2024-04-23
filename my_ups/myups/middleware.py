from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout

class LoginRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.path == reverse('user_login'):
                return redirect('index')
        else:
            allowed_paths = [reverse('user_login'), reverse('user_register'), reverse('index')]
            if request.path not in allowed_paths:
                return redirect('user_login')

        response = self.get_response(request)
        return response