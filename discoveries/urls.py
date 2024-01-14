from django.urls import path

from .views import *

urlpatterns = [
    path('', index, name="home"),
    path('thematics/<int:pioneer_id>', pioneer_details, name="pioneer_details"),
    path('thematics/<int:pioneer_id>/delete/', pioneer_delete, name="pioneer_delete")
]
