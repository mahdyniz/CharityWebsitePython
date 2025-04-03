from django.urls import path
from . import views

app_name = 'charity'

urlpatterns = [
    path('', views.home, name='home'),
    path('cases/', views.case_list, name='case_list'),
    path('cases/<int:pk>/', views.case_detail, name='case_detail'),
] 