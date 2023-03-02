from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from picture.models import Picture
from gallery.models import Gallery
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse

from Final_Project.local_settings import FORCE_SCHEMA
from django.db.models import Q

# Create your views here.
def main_page(request):
    if request.user.is_authenticated:
        return redirect("loggedin")
    return render(request, "main.html")


@login_required(login_url="login")
@never_cache
def logged_in(request):
    user = request.user
    pictures = Picture.objects.filter(pictures_container__user=user.id).filter( Q(gallery__isnull = True) | Q(gallery__slug='portfolio')).order_by("-pk")[:9]
    galleries = Gallery.objects.filter(user_id=user.id).exclude(slug="portfolio")[:6]
    
    gallery_pics = []
    for gallery in galleries:
        gallery_pic = Picture.objects.filter(gallery__id=gallery.id).order_by("-pk")[:1]
        gallery_pics.append(gallery_pic)

    context = {
        "pictures": pictures,
        "galleries": galleries,
        "gallery_pics": gallery_pics,
    }

    return render(request, "logged_in.html", context)


@login_required(login_url="login")
@never_cache
def portfolios(request):
    user = request.user

    pictures = Picture.objects.filter(pictures_container__user=user.id).filter( Q(gallery__isnull = True) | Q(gallery__slug='portfolio')).order_by("-pk")

    if request.method == "POST" and request.POST.get("operation") == "download":
        urls = []
        picture_ids = request.POST.getlist("id[]")
        for id in picture_ids:
            picture = Picture.objects.get(pk=id)
            current_site = get_current_site(request)
            picture_url = f"{FORCE_SCHEMA}://{current_site.domain}{ picture.image.url}"
            urls.append(picture_url)
        returnData = {"urls": urls}
        return JsonResponse(returnData)

    if request.method == "POST" and request.POST.get("operation") == "delete":
        picture_ids = request.POST.getlist("id[]")
        for id in picture_ids:
            picture = Picture.objects.get(pk=id)
            picture.delete()
        returnData = {"response": "ok"}
        return JsonResponse(returnData)

    context = {
        "pictures": pictures,
    }

    return render(request, "portfolio_pics.html", context)


@login_required(login_url="login")
@never_cache
def galleries(request):
    user = request.user
    galleries = Gallery.objects.filter(user_id=user.id).exclude(slug="portfolio")
    gallery_pics = []
    for gallery in galleries:
        gallery_pic = Picture.objects.filter(gallery__id=gallery.id).order_by("-pk")[:1]
        gallery_pics.append(gallery_pic)

    context = {
        "galleries": galleries,
        "gallery_pics": gallery_pics,
    }

    return render(request, "galleries.html", context)


def form_submit(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        message = request.POST["message"]
        phone = request.POST["phone"]

        mail_subject = "Mesage from your Webpage."
        message = render_to_string(
            "email_contact_message.html",
            {
                "name": name,
                "email": email,
                "phone": phone,
                "message": message,
            },
        )

        email = EmailMessage(mail_subject, message, to=[settings.CONTACT_EMAIL])

        email.send()
        return HttpResponse('{"response": "OK"}')
    else:
        return HttpResponse('{"response": "NOK"}')
