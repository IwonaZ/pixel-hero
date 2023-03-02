from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import SignupForm
from django.views.decorators.cache import never_cache
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from .tokens import account_activation_token
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import PasswordResetForm
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator


@never_cache
def register(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = "Activate your blog account."
            message = render_to_string(
                "acc_active_email.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": account_activation_token.make_token(user),
                },
            )
            to_email = form.cleaned_data.get("email")
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return render(request=request, template_name="register_confirm.html")
        else:
            return render(request, "register.html", {"form": form})
    else:
        form = SignupForm()

    return render(request, "register.html", {"form": form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return render(request=request, template_name="register_success.html")

    else:
        return HttpResponse("Activation link is invalid!")


@never_cache
def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            if request.POST.get("rememberme") == "on":
                request.session.set_expiry(60 * 60 * 24 * 21)  # Three weeks
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("/logged_in")
            else:
                print("user is none")
                messages.error(request, "Invalid username or password.")
        else:
            print("invalid form")
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(
        request=request,
        template_name="login.html",
        context={"login_form": form},
    )


def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("login")


def reset_the_password(request):
    return render(
        request=request,
        template_name="password_reseting.html",
    )


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data["email"]
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Reset your Password."
                    message = render_to_string(
                        "password_reset.txt",
                        {
                            "email": user.email,
                            "domain": "development.pixel-hero.net",
                            "site_name": "Pixel Hero",
                            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                            "user": user,
                            "token": default_token_generator.make_token(user),
                            "protocol": "http",
                        },
                    )
                    to_email = data
                    email = EmailMessage(subject, message, to=[to_email])
                    print(email.send(False))
                    return redirect("../password_reset_done/")
    password_reset_form = PasswordResetForm()
    return render(
        request=request,
        template_name="password_reset_done.html",
        context={"password_reset_form": password_reset_form},
    )
