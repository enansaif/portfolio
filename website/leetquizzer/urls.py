from django.urls import path
from . import views

app_name = 'leetquizzer'
urlpatterns = [
    path('', views.MainMenu.as_view(), name='main_menu'),
    path('<str:sorted_by>/', views.MainMenu.as_view(), name='main_menu'),
    path('problem/<int:problem_id>/', views.ProblemMenu.as_view(), name='problem_menu'),
    path('problem/create_problem/', views.CreateProblem.as_view(), name='create_problem'),
    path('problem/create_topic/', views.CreateTopic.as_view(), name='create_topic'),
    path('problem/success/', views.success, name='success'),
    path('problem/failure/', views.failure, name='failure'),
]