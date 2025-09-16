from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='cart.index'),
    path('<int:id>/add/', views.add, name='cart.add'),
    path('clear/', views.clear, name='cart.clear'),
    path('feedback/', views.feedback_index, name='cart.feedback_index'),
    path('feedback/create/', views.feedback_create, name='cart.feedback_create'),
]