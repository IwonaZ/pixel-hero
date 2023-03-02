from django.urls import re_path, path
from main_page import views


urlpatterns = [
    path("main_page/", views.main_page, name="mainpage"),
    path("logged_in/", views.logged_in, name="loggedin"),
    path("portfolios/", views.portfolios, name="portfolios"),
    path("galleries/", views.galleries, name="galleries"),
    path("form_submit/", views.form_submit, name="contactform"),
]
