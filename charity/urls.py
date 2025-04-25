from django.urls import path
from . import views

app_name = 'charity'

urlpatterns = [
    path('', views.home, name='home'),
    path('cases/', views.case_list, name='case_list'),
    path('cases/<int:pk>/', views.case_detail, name='case_detail'),
    path('cases/<int:pk>/donate/', views.make_donation, name='make_donation'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
] 