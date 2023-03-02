from django import forms
from django.forms import ClearableFileInput

from .models import Picture, PicturesContainer
from gallery.models import Gallery
from django.contrib.auth.models import User


class PicturesContainerForm(forms.ModelForm):
    """ Form for uploading multiple pictures """
    class Meta:
        model = PicturesContainer
        fields = []
        
    def __init__(self, *args, **kwargs):
        self._user = kwargs.pop('user')
        super(PicturesContainerForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        inst = super(PicturesContainerForm, self).save(commit=False) # Create, but don't save the new picture container instance.
        inst.user = self._user
        if commit:
            inst.save()  # Save the new instance.
            self.save_m2m()  #save the many-to-many data for the form.
        return inst


class PictureForm(forms.ModelForm):
    """Form for the picture model"""
    class Meta:
        model = Picture
        fields = ['image', 'title', 'description', 'tags', 'public_exif']
        widgets = {
            'image': ClearableFileInput(attrs={'multiple': True}),
        }
        # widget is important to upload multiple files

class DragAndDropPictureForm(forms.ModelForm):
    """Form for the picture model"""
    class Meta:
        model = Picture
        fields = ['image']

        widgets = {
            'image': ClearableFileInput(attrs={'multiple': True}),
        }
        # widget is important to upload multiple files

class EditPictureForm(forms.ModelForm):
    '''
    Form to assign/unassign gallery from an already-published photo.
    '''
    class Meta:
        model = Picture
        fields = ['id', 'title', 'description', 'gallery', 'tags', 'public_exif', 'public_picture', 'public_link']
    
    gallery = forms.ModelMultipleChoiceField(
        queryset=Gallery.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
    )

    def __init__(self, user, *args, **kwargs):
        '''
        Showing user-specific galleries + making choice of gallery
        optional.
        Had to override __init__ because gallery is now a ManyToMany field.
        '''
        super(EditPictureForm, self).__init__(*args, **kwargs)
        self.fields['gallery'].queryset = Gallery.objects.filter(user=user)
        self.fields['gallery'].required = False

class PublicPictureForm(forms.ModelForm):
    class Meta:
        model = Picture
        fields = ["public_picture", "public_link"]

    public_picture = forms.BooleanField(
        label="Set picture as public",
        required=False,
    )

    public_link = forms.BooleanField(
        label="Show picture's direct link",
        required=False,
    )