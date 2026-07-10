from django.urls import path
from . import views
urlpatterns = {
    path('', views.home, name = 'small_app_home'),
    path('about/', views.about, name = 'small_app_about'),
}