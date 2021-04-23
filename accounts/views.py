from django.shortcuts import render, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .forms import RegistrationForm
from api.models import UserIP
import logging

logger = logging.getLogger(__name__)

# view for the registration of a new user
def registration_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password1"]
            User.objects.create_user(username=username, password=password, email=email)
            user = authenticate(username=username, password=password)
            login(request, user)
            return HttpResponseRedirect("/")
    else:
        form = RegistrationForm()
    context = {"form": form}
    return render(request, "accounts/registration.html", context)

# view for the login that tracks users' IP address
def login_view(request):

    if request.user.is_authenticated:
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            address = request.META.get('HTTP_X_FORWARDED_FOR')

            if address:
                ip = address.split(',')[-1].strip()
            else:
                ip = request.META.get('REMOTE_ADDR')

            if UserIP.objects.values('last_ip_address').filter(user=user).count() > 0:

                user_ips = UserIP.objects.values('last_ip_address').filter(user=user)

                for user_ip in user_ips:
                    if user_ip['last_ip_address'] != ip:
                        logger.warning("".join([user.username, ' has logged in from a different IP address!']))
                        messages.warning(request, 'You have logged in from a different IP address!')
                        user_ip['last_ip_address'] = ip
                        UserIP.objects.filter(user=user).update(last_ip_address=ip)
                        return HttpResponseRedirect("/")

            else:
                UserIP.objects.create(user=user, last_ip_address=ip)

            return HttpResponseRedirect("/")

        else:
            messages.info(request, 'Username OR Password not correct.')

    context = {}
    return render(request, 'accounts/login.html')
