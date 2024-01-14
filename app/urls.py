from django.urls import path
from .views import *

urlpatterns = [
    # Набор методов для услуг
    path('api/pioneers/search/', search_pioneers),  # GET
    path('api/pioneers/<int:pioneer_id>/', get_pioneer_by_id),  # GET
    path('api/pioneers/<int:pioneer_id>/image/', get_pioneer_image),  # GET
    path('api/pioneers/<int:pioneer_id>/update/', update_pioneer),  # PUT
    path('api/pioneers/<int:pioneer_id>/update_image/', update_pioneer_image),  # PUT
    path('api/pioneers/<int:pioneer_id>/delete/', delete_pioneer),  # DELETE
    path('api/pioneers/create/', create_pioneer),  # POST
    path('api/pioneers/<int:pioneer_id>/add_to_discovery/', add_pioneer_to_discovery),  # POST

    # Набор методов для заявок
    path('api/discoveries/search/', search_discoveries),  # GET
    path('api/discoveries/<int:discovery_id>/', get_discovery_by_id),  # GET
    path('api/discoveries/<int:discovery_id>/update/', update_discovery),  # PUT
    path('api/discoveries/<int:discovery_id>/update_verify/', update_discovery_verify),  # PUT
    path('api/discoveries/<int:discovery_id>/update_status_user/', update_status_user),  # PUT
    path('api/discoveries/<int:discovery_id>/update_status_admin/', update_status_admin),  # PUT
    path('api/discoveries/<int:discovery_id>/delete/', delete_discovery),  # DELETE
    path('api/discoveries/<int:discovery_id>/delete_pioneer/<int:pioneer_id>/', delete_pioneer_from_discovery),  # DELETE

    # Набор методов для аутентификации и авторизации
    path("api/register/", register),
    path("api/login/", login),
    path("api/check/", check),
    path("api/logout/", logout)
]
