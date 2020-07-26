from django.urls import path

from . import views

urlpatterns = [
    path('', views.login_page, name='index'),
    path('register', views.register, name='register'),
    path('signin', views.signin, name='signin'),
    path('confirm_account/<token_emailid>', views.login_page, name='confirm_account'),
    path('add_random_data', views.add_random_data, name="add_random_data")
]
