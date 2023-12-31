"""
Defines all endpoints of the portfolio application.
"""
from django.urls import path
from . import views

app_name = 'portfolio'
urlpatterns = [
    path('', views.base, name='base'),
    path('about/', views.about, name='about'),
    path('projects/', views.projects, name='projects'),
    path('contact/', views.ContactView.as_view(), name='contact'),
]
