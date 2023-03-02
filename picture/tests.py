from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import resolve, reverse
from gallery.models import Gallery
from PIL import Image

from .forms import PictureForm
from .models import Picture, PicturesContainer
from .views import (picture_upload, picture_upload_dnd,
                    picture_upload_to_gallery)


class TestUrls(TestCase):
    """ Test urls """
    
    def test_upload_picture_resolves(self):
        url = reverse("picture-upload")
        self.assertEqual(resolve(url).func, picture_upload)
        
    def test_upload_picture_dnd_resolves(self):
        url = reverse("picture-upload-dnd")
        self.assertEqual(resolve(url).func, picture_upload_dnd)
        
    def test_upload_picture_to_gallery_resolves(self):
        gallery = Gallery.objects.create(title="test")
        url = reverse("picture-upload-to-gallery", kwargs={'gallery_name': gallery})
        self.assertEqual(resolve(url).func, picture_upload_to_gallery)



def create_image(storage, filename, size=(100, 100), image_mode='RGB', image_format='PNG'):
    
    """
    Generate a test image, returning the filename that it was saved as.

    If ``storage`` is ``None``, the BytesIO containing the image data
    will be passed instead.
    """
    data = BytesIO()
    Image.new(image_mode, size).save(data, image_format)
    data.seek(0)
    if not storage:
        return data
    image_file = ContentFile(data.read())
    return storage.save(filename, image_file)

class TestViewUploadImages(TestCase):
    def setUp(self):
        super(TestViewUploadImages, self).setUp()


    def test_valid_form(self):
        '''
        valid post data should redirect
        The expected behavior is to show the image
        '''
        url = reverse('picture-upload')
        img = create_image(None, 'image1.png')
        img_file = SimpleUploadedFile('front.png', img.getvalue())
        user = User.objects.create_user('Jane', 'jane@test.com', 'janejane')
        data = {'image': img_file, user: user}
        response = self.client.post(url, data, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('picture/upload_picture.html')

    def test_upload_image_get(self):
        user = User.objects.create_user('Jane', 'jane@test.com', 'janejane')
        self.client.login(username='Jane', password='janejane')
        response = self.client.get(reverse("picture-upload"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "picture/upload_picture.html")
        

        
class TestPictureModel(TestCase):
    """ Test models """
    @staticmethod
    def temporary_image():
        bts = BytesIO()
        img = Image.new("RGB", (100, 100))
        img.save(bts, 'jpeg')
        return SimpleUploadedFile("test.jpg", bts.getvalue())
    
    def setUp(self):
        user = User.objects.create_user('John', 'johnn@test.com', 'johnpassword')
        image = self.temporary_image()
        pictures_container = PicturesContainer(user=user)
        pictures_container.save()
        picture1 = Picture.objects.create(image=image, pictures_container=pictures_container)
        # picture1.save()
        
    def test_add_photo(self):
        
        user = User.objects.create_user('Jane', 'jane@test.com', 'janejane')
        image = self.temporary_image()
        container = PicturesContainer(user=user)
        container.save()
        picture2 = Picture.objects.create(image=image, pictures_container=container)
        self.assertEqual(Picture.objects.count(), 2)
    
    def test_title_label(self):
        picture = Picture.objects.get(id=1)
        field_label = picture._meta.get_field('title').verbose_name
        self.assertEqual(field_label, 'title')
    
    def test_description_label(self):
        picture = Picture.objects.get(id=1)
        field_label = picture._meta.get_field('description').verbose_name
        self.assertEqual(field_label, 'description')
        

    def test_str(self):
        picture = Picture.objects.get(id=1)
        self.assertEqual(picture.__str__(), "Image 1")
        
class TestPictureForm(TestCase):
    """ Test forms """
    
    @staticmethod
    def temporary_image():
        bts = BytesIO()
        img = Image.new("RGB", (100, 100))
        img.save(bts, 'jpeg')
        return SimpleUploadedFile("test.jpg", bts.getvalue())
    
    def test_empty_form(self):
        form = PictureForm()
        self.assertInHTML('<input type="file" name="image" multiple accept="image/*" required id="id_image">', str(form))
        self.assertIn("image", form.fields)
