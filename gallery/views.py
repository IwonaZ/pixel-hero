from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import View
from picture.forms import EditPictureForm, PublicPictureForm
from picture.models import Picture
from taggit.models import Tag

from .models import Gallery
from .forms import GalleryForm
from picture.forms import EditPictureForm, PublicPictureForm
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.cache import never_cache
from Final_Project.local_settings import mapbox_access_token, FORCE_SCHEMA

from django.db import IntegrityError
from django.db.models import Q


@login_required(login_url="login")
@never_cache
def all_pictures(request):
    """
    Shows all the pictures the user has uploaded, including a list of
    all galleries.
    Pictures are shown from most to least recent, while galleries
    appear according of their order of creation.
    """
    user = request.user
    pictures = Picture.objects.filter(pictures_container__user=user.id).order_by("-pk")
    galleries = Gallery.objects.filter(user_id=user.id)
    #     tags = Tag.objects.filter(picture__pictures_container__user=user)
    tags = Tag.objects.filter(picture__pictures_container__user=user.id)

    context = {
        "user": user,
        "pictures": pictures,
        "galleries": galleries,
        "tags": tags,
    }

    return render(request, "gallery/all_pictures.html", context)


@login_required(login_url="login")
def all_tagged_pictures(request, tag_slug):
    """shows all pictures that have a tag"""

    user = request.user
    pictures = Picture.objects.filter(
        tags__slug__in=[tag_slug], pictures_container__user=user.id
    )

    context = {
        "user": user,
        "pictures": pictures,
        "tag": tag_slug,
    }

    return render(request, "gallery/taglist.html", context)


@login_required(login_url="login")
def new_gallery(request):
    """
    Create a new gallery and get redirected to the new gallery's page.
    """
    try:
        # code that produces error
        if request.method == "POST":
            form = GalleryForm(request.POST)
            if form.is_valid():
                new_gallery = form.save()
                new_gallery.user = request.user
                new_gallery.save()
                return redirect("gallery_detail", gallery=new_gallery.slug)
        else:
            form = GalleryForm()
        return render(request, "gallery/new_gallery.html", {"form": form})
    except IntegrityError as e:
        message = "Gallery already exists"
        form = GalleryForm()
        return render(
            request, "gallery/new_gallery.html", {"message": message, "form": form}
        )


@login_required(login_url="login")
def gallery_detail(request, gallery):
    """
    Show pictures assigned only to a specific gallery.
    Pictures are sorted from most to least recent.
    """
    user = request.user
    gallery_object = get_object_or_404(Gallery, slug=gallery, user=user.id)
    pictures = Picture.objects.filter(
        gallery__title__contains=gallery_object.title.replace("-", " "),
        pictures_container__user=user.id,
    ).order_by("-pk")

    context = {
        "gallery": gallery_object,
        "pictures": pictures,
    }

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

    return render(request, "gallery/gallery_detail.html", context)


def picture_detail(request, uuid):
    """
    Shows specific picture and allows everyone to view and download it.
    If the logged in user is the author, it'll show two extra buttons to
    update the galleries the picture's in.
    """
    user = request.user
    picture = Picture.objects.get(uuid=uuid)
    galleries = picture.gallery.all()
    current_site = get_current_site(request)

    picture_owner = picture.pictures_container.user.id

    # Checking if user is either anonymous, other user or owner of picture
    if user.is_anonymous:
        is_picture_owner = False
    elif user.is_authenticated:
        if user.id == picture_owner:
            is_picture_owner = True
        else:
            is_picture_owner = False

    # public_picture form
    if request.method == "POST":
        form = PublicPictureForm(request.POST, instance=picture)
        if form.is_valid():
            form.save()
            return redirect("picture_detail", uuid=picture.uuid)
    else:
        form = PublicPictureForm(instance=picture)

    context = {
        "picture": picture,
        "galleries": galleries,
        "is_picture_owner": is_picture_owner,
        "form": form,
        "domain": current_site.domain,
    }
    return render(request, "gallery/picture_detail.html", context)


def edit_gallery_picture(request, uuid, galleryid):
    """
    Update the galleries the picture's in.
    """
    user = request.user
    picture = get_object_or_404(Picture, uuid=uuid)
    pictures = Picture.objects.filter(
        pictures_container__user=user.id, gallery__id=galleryid
    ).order_by("-pk")
    picture_owner = picture.pictures_container.user.id
    current_site = get_current_site(request)

    if request.method == "POST" and request.POST.get("operation") == "download":
        picture_id = request.POST.get("id")
        picture = Picture.objects.get(pk=picture_id)
        current_site = get_current_site(request)
        picture_url = f"{FORCE_SCHEMA}://{current_site.domain}{ picture.image.url }"
        returnData = {"url": picture_url}
        return JsonResponse(returnData)

    if request.method == "POST" and request.POST.get("operation") == "delete":
        picture_id = request.POST.get("id")
        picture = Picture.objects.get(pk=picture_id)
        next_picture_id = request.POST.get("nextid")
        next_picture = Picture.objects.get(pk=next_picture_id)
        picture.delete()
        returnData = {"next_uuid": next_picture.uuid}
        return JsonResponse(returnData)

    if request.method == "POST":
        picture = get_object_or_404(Picture, uuid=request.POST.get("uuid"))
        form = EditPictureForm(request.user, request.POST, instance=picture)
        if form.is_valid():
            form.save()
            return redirect(
                "edit_gallery_picture", uuid=picture.uuid, galleryid=galleryid
            )
        else:
            for error in form.errors:
                error

    context = {}

    is_picture_in_slideshow=False
    forms = []

    for pic in pictures:
        forms.append(EditPictureForm(request.user, instance=pic))
        if pic.image.url == picture.image.url:
            is_picture_in_slideshow = True

    if user.is_authenticated:
        form = EditPictureForm(request.user, instance=picture)

        if user.id == picture_owner:
            is_picture_owner = True
        else:
            is_picture_owner = False

        context = {
            "form": form,
            "forms" : forms,
            "picture": picture,
            "pictures": pictures,
            "is_picture_owner": is_picture_owner,
            "domain": current_site.domain,
            "mapbox_access_token": mapbox_access_token,
        }
    else:
        context = {
            "picture": picture,
            "is_picture_owner": False,
            "domain": current_site.domain,
            "mapbox_access_token": mapbox_access_token,
        }
    if is_picture_in_slideshow:
        return render(request, "gallery/edit_picture.html", context)
    else:
        return redirect('mainpage')


def edit_picture(request, uuid):
    """
    Update the galleries the picture's in.
    """
    user = request.user
    picture = get_object_or_404(Picture, uuid=uuid)
    pictures = Picture.objects.filter(pictures_container__user=user.id).filter( Q(gallery__isnull = True) | Q(gallery__slug='portfolio')).order_by("-pk")

    picture_owner = picture.pictures_container.user.id
    current_site = get_current_site(request)

    if request.method == "POST" and request.POST.get("operation") == "download":
        picture_id = request.POST.get("id")
        picture = Picture.objects.get(pk=picture_id)
        current_site = get_current_site(request)
        picture_url = f"{FORCE_SCHEMA}://{current_site.domain}{ picture.image.url }"
        returnData = {"url": picture_url}
        return JsonResponse(returnData)

    if request.method == "POST" and request.POST.get("operation") == "delete":
        picture_id = request.POST.get("id")
        picture = Picture.objects.get(pk=picture_id)
        next_picture_id = request.POST.get("nextid")
        next_picture = Picture.objects.get(pk=next_picture_id)
        picture.delete()
        returnData = {"next_uuid": next_picture.uuid}
        return JsonResponse(returnData)

    if request.method == "POST":
        picture = get_object_or_404(Picture, uuid=request.POST.get("uuid"))
        form = EditPictureForm(request.user, request.POST, instance=picture)
        if form.is_valid():
            form.save()
            return redirect("edit_picture", uuid=picture.uuid)
        else:
            for error in form.errors:
                error

    context = {}

    #if the picture is not in pictures to show on the slideshow, then redirect to main page
    is_picture_in_slideshow=False
    forms = []

    for pic in pictures:
        forms.append(EditPictureForm(request.user, instance=pic))
        if pic.image.url == picture.image.url:
            is_picture_in_slideshow = True
            

    if user.is_authenticated:
        picture_form = EditPictureForm(request.user, instance=picture)

        if user.id == picture_owner:
            is_picture_owner = True
        else:
            is_picture_owner = False

        context = {
            "form": picture_form,
            "forms" : forms,
            "picture": picture,
            "pictures": pictures,
            "is_picture_owner": is_picture_owner,
            "domain": current_site.domain,
            "mapbox_access_token": mapbox_access_token,
        }
    else:
        context = {
            "picture": picture,
            "is_picture_owner": False,
            "domain": current_site.domain,
            "mapbox_access_token": mapbox_access_token,
        }
        if picture.public_picture == True:
            return render(request, "gallery/edit_picture.html", context)

    if is_picture_in_slideshow:
        return render(request, "gallery/edit_picture.html", context)
    else:
        return redirect('mainpage')


@login_required(login_url="login")
def delete_picture(request, uuid):
    """
    Delete picture and get redirected to all pictures page.
    """
    picture = get_object_or_404(Picture, uuid=uuid)
    picture_owner = picture.pictures_container.user.id
    user = request.user

    if user.is_authenticated:
        if user.id == picture_owner:
            is_picture_owner = True
        else:
            is_picture_owner = False

    if request.method == "POST":
        picture.delete()
        return redirect("all_pictures")

    context = {
        "picture": picture,
        "is_picture_owner": is_picture_owner,
    }
    return render(request, "gallery/delete_picture.html", context)


@login_required(login_url="login")
def delete_gallery(request, gallery):
    """
    Delete gallery and get redirected to all pictures page.
    """
    gallery = get_object_or_404(Gallery, slug=gallery)
    gallery_owner = gallery.user.id
    user = request.user

    if user.is_authenticated:
        if user.id == gallery_owner:
            is_gallery_owner = True
        else:
            is_gallery_owner = False

    if request.method == "POST":
        gallery.delete()
        return redirect("galleries")

    context = {
        "gallery": gallery,
        "is_gallery_owner": is_gallery_owner,
    }
    return render(request, "gallery/delete_gallery.html", context)


# class Picture_view(View):
#     def get(self, request):
#         user = request.user
#         all_pictures = Picture.objects.filter(pictures_container__user = user.id)
#         context = {
#             'pictures':all_pictures
#         }
#         return render(request, 'gallery/delete_multiple.html', context)

#     def post(self, request, *args, **kwargs):
#         if request.method=="POST":
#             picture_ids=request.POST.getlist('id[]')
#             for id in picture_ids:
#                 picture = Picture.objects.get(pk=id)
#                 picture.delete()
#             return redirect('delete-multiple-pictures')


def delete_multiple_pictures(request):
    """Select and delate multiple pictures"""
    user = request.user
    pictures = Picture.objects.filter(pictures_container__user=user.id)
    if request.method == "GET":
        return render(request, "gallery/delete_multiple.html", {"pictures": pictures})
    if request.method == "POST":
        picture_ids = request.POST.getlist("id[]")
        for id in picture_ids:
            picture = Picture.objects.get(pk=id)
            picture.delete()
        return redirect("delete-multiple-pictures")


def download_multiple_pictures(request):
    """Select and download multiple pictures"""
    user = request.user
    pictures = Picture.objects.filter(pictures_container__user=user.id)
    if request.method == "GET":
        return render(request, "gallery/download_multiple.html", {"pictures": pictures})
    if request.method == "POST":
        urls = []
        picture_ids = request.POST.getlist("id[]")
        for id in picture_ids:
            picture = Picture.objects.get(pk=id)
            current_site = get_current_site(request)
            picture_url = f"{FORCE_SCHEMA}://{current_site.domain}{ picture.image.url}"
            urls.append(picture_url)
        returnData = {"urls": urls}
        return JsonResponse(returnData)
