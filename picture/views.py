from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from .forms import PictureForm, DragAndDropPictureForm, PicturesContainerForm
from .models import Picture
from gallery.models import Gallery
# Imports the Google Cloud client library
from google.cloud import vision
import os
import io


# def picture_upload_view(request):
#     """Process picture uploaded by users"""
#     if request.method == 'POST':
#         form = PictureForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save(commit=False)
#             # get the instance of the object and assigned current user to author field
#             form.instance.author = request.user
#             # Get the current instance object to display in the template
#             picture = form.instance
#             form.save()

#             return render(request, 'picture/upload_picture.html', {'form': form, 'picture': picture})
#     else:
#         form = PictureForm()
#     return render(request, 'picture/upload_picture.html', {'form': form})


@login_required(login_url="login")
def picture_upload(request):
    """Process pictures uploaded by users"""

    PictureFormSet = modelformset_factory(
        Picture, form=PictureForm, extra=1
    )  # one form as default

    if request.method == "GET":
        pictures_container_form = PicturesContainerForm(user=request.user)
        formset = PictureFormSet(queryset=Picture.objects.none())
        return render(
            request,
            "picture/upload_picture.html",
            {"pictures_container_form": pictures_container_form, "formset": formset},
        )

    elif request.method == "POST":
        pictures_container_form = PicturesContainerForm(request.POST, user=request.user)
        formset = PictureFormSet(request.POST, request.FILES)

        if pictures_container_form.is_valid() and formset.is_valid():
            container_obj = pictures_container_form.save()

            for form in formset.cleaned_data:
                if form:
                    image = form["image"]
                    description = form["description"]
                    title = form["title"]
                    public_exif = form["public_exif"]

                    tags = form["tags"]
                    # to use `save`  we can't `create` as it will persist into the db right away. Simply create an instance of picture
                    ins = Picture.objects.create(
                        image=image,
                        description=description,
                        title=title,
                        public_exif=public_exif,
                        pictures_container=container_obj,
                    )

                    robot_tags = []
                    
                    if request.POST.get('aitags') and request.user.username == "demo":
                        robot_tags = get_google_vision(ins)

                    for tag in tags:
                        ins.tags.add(tag)

                    if robot_tags and robot_tags != []:
                        for tag in robot_tags[:3]:
                            ins.tags.add(tag.description)

                    portfolio_gallery = Gallery.objects.filter(slug='portfolio')
                    if portfolio_gallery:
                        ins.gallery.add(portfolio_gallery[0].id)

                    ins.save()
            try:
                return render(
                    request,
                    "picture/upload_picture.html",
                    {
                        "pictures_container_form": pictures_container_form,
                        "formset": formset,
                        "image": image,
                        "robot_tags": robot_tags[:3],
                    },
                )
            except Exception as e:
                if hasattr(e, 'message'):
                    print(e.message)
                else:
                    print(e)
                return redirect('picture-upload')
        else:
            print(pictures_container_form.errors, formset.errors)
            return redirect('picture-upload')

@login_required(login_url="login")
def picture_upload_dnd(request):
    """Process pictures uploaded by users"""

    PictureFormSet = modelformset_factory(
        Picture, form=DragAndDropPictureForm, extra=1
    )  # one form as default

    if request.method == "GET":
        pictures_container_form = PicturesContainerForm(user=request.user)
        formset = PictureFormSet(queryset=Picture.objects.none())
        return render(
            request,
            "picture/upload_picture_dnd.html",
            {"pictures_container_form": pictures_container_form, "formset": formset},
        )

    elif request.method == "POST":
        pictures_container_form = PicturesContainerForm(request.POST, user=request.user)
        formset = PictureFormSet(request.POST, request.FILES)

        if pictures_container_form.is_valid() and formset.is_valid():
            container_obj = pictures_container_form.save()

            for form in formset.cleaned_data:
                if form:
                    
                    image = form["image"]

                    # to use `save`  we can't `create` as it will persist into the db right away. Simply create an instance of picture
                    ins = Picture.objects.create(
                        image=image,
                        pictures_container=container_obj,
                    )
                    
                    robot_tags = []

                    if request.POST.get('aitags') and request.user.username == "demo":
                        print("Will do AI tags now")
                        robot_tags = get_google_vision(ins)

                    if robot_tags and robot_tags != []:
                        for tag in robot_tags[:3]:
                            ins.tags.add(tag.description)

                    portfolio_gallery = Gallery.objects.filter(slug='portfolio')
                    if portfolio_gallery:
                        ins.gallery.add(portfolio_gallery[0].id)

                    ins.save()
    
            try:
                return render(
                    request,
                    "picture/upload_picture_dnd.html",
                    {
                        "pictures_container_form": pictures_container_form,
                        "formset": formset,
                        "image": image,
                        "robot_tags": robot_tags[:3],
                    },
                )
            except Exception as e:
                if hasattr(e, 'message'):
                    print(e.message)
                else:
                    print(e)
                return redirect('picture-upload-dnd')
        else:
            print(pictures_container_form.errors, formset.errors)
            return redirect('picture-upload-dnd')


@login_required(login_url="login")
def picture_upload_to_gallery(request, gallery_name):
    """Process pictures uploaded by users"""
    PictureFormSet = modelformset_factory(
        Picture, form=PictureForm, extra=1
    )  # one form as default

    if request.method == "GET":

        pictures_container_form = PicturesContainerForm(user=request.user)
        formset = PictureFormSet(queryset=Picture.objects.none())
        return render(
            request,
            "picture/upload_picture.html",
            {"pictures_container_form": pictures_container_form, "formset": formset},
        )

    elif request.method == "POST":

        pictures_container_form = PicturesContainerForm(request.POST, user=request.user)
        formset = PictureFormSet(request.POST, request.FILES)
        gallery = Gallery.objects.filter(title=gallery_name).first()

        if pictures_container_form.is_valid() and formset.is_valid():
            container_obj = pictures_container_form.save()

            for form in formset.cleaned_data:
                if form:
                    image = form["image"]
                    description = form["description"]
                    title = form["title"]
                    public_exif = form["public_exif"]

                    tags = form["tags"]
                    # to use `save`  we can't `create` as it will persist into the db right away. Simply create an instance of picture
                    ins = Picture.objects.create(
                        image=image,
                        description=description,
                        title=title,
                        public_exif=public_exif,
                        pictures_container=container_obj,
                    )
                    ins.gallery.add(gallery)

                    for tag in tags:
                        ins.tags.add(tag)
                    ins.save()
            messages.success(request, "Pictures has been successfully upload!")
            return render(
                request,
                "picture/upload_picture.html",
                {
                    "pictures_container_form": pictures_container_form,
                    "formset": formset,
                    "image": image,
                    "gallery": gallery,
                },
            )
        else:
            print(pictures_container_form.errors, formset.errors)


def get_google_vision(ins):
    # Instantiates a client
    file_counter = open('googlecounter','r')
    use_counter = file_counter.readline()
    
    use_value = 200
    file_counter.close()

    if use_counter: # only go on if the line was not blank
        use_value = int(use_counter)
    
    if use_value != 200 and use_value < 500:
        client = vision.ImageAnnotatorClient()
        file_name = os.path.abspath(ins.image.path)

        # Loads the image into memory
        with io.open(file_name, 'rb') as image_file:
            content = image_file.read()

        gc_image = vision.Image(content=content)
   
        use_value += 1

        file_counter = open("googlecounter", 'w')
        file_counter.write("%d\n" %use_value)
        file_counter.close()

        # Performs label detection on the image file
        response = client.label_detection(image=gc_image)
        return response.label_annotations
    else:
        return []