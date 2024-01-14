from django.urls import path
from .views import index, discovererPage

urlpatterns = [
    path('', index),
    path('discoverer/<int:discoverer_id>', discovererPage)
]