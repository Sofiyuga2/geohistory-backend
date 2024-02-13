import requests
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.http import HttpResponse
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .jwt_helper import *
from .permissions import *
from .serializers import *
from .utils import identity_user

#checking_in_archive

@api_view(["PUT"])
@permission_classes([IsRemoteService])
def checking_in_archive(request, discoveries_id):
    print(request)
    if not Discovery.objects.filter(pk=discoveries_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    discovery = Discovery.objects.get(pk=discoveries_id)
    serializer = DiscoverySerializer(discovery, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
    print(discovery.verify)
    # print(serializer.data)
    return Response(serializer.data)



def get_draft_discovery(request):
    user = identity_user(request)

    if user is None:
        return None

    discovery = Discovery.objects.filter(owner_id=user.pk).filter(status=1).first()

    if discovery is None:
        return None

    return discovery


@api_view(["GET"])
def search_pioneers(request):
    query = request.GET.get("query", "")

    pioneers = Pioneer.objects.filter(status=1).filter(name__icontains=query)

    serializer = PioneerSerializer(pioneers, many=True)

    draft_discovery = get_draft_discovery(request)

    resp = {
        "pioneers": serializer.data,
        "draft_discovery_id": draft_discovery.pk if draft_discovery else None
    }

    return Response(resp)


@api_view(["GET"])
def get_pioneer_by_id(request, pioneer_id):
    if not Pioneer.objects.filter(pk=pioneer_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    pioneer = Pioneer.objects.get(pk=pioneer_id)
    serializer = PioneerSerializer(pioneer, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsModerator])
def update_pioneer(request, pioneer_id):
    if not Pioneer.objects.filter(pk=pioneer_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    pioneer = Pioneer.objects.get(pk=pioneer_id)
    serializer = PioneerSerializer(pioneer, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)
#  service = Service.objects.create()

#     serializer = ServiceSerializer(service)

#     return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsModerator])
def create_pioneer(request):
    Pioneer.objects.create()
   
    # pioneers = Pioneer.objects.filter(status=1)
    pioneers = Pioneer.objects.all()
    serializer = PioneerSerializer(pioneers, many=True)
    print(serializer.data)
    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_pioneer(request, pioneer_id):
    if not Pioneer.objects.filter(pk=pioneer_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    pioneer = Pioneer.objects.get(pk=pioneer_id)
    pioneer.status = 5
    pioneer.save()

    pioneers = Pioneer.objects.filter(status=1)
    serializer = PioneerSerializer(pioneers, many=True)

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_pioneer_to_discovery(request, pioneer_id):
    if not Pioneer.objects.filter(pk=pioneer_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    pioneer = Pioneer.objects.get(pk=pioneer_id)

    discovery = get_draft_discovery(request)

    if discovery is None:
        discovery = Discovery.objects.create()

    if discovery.pioneers.contains(pioneer):
        return Response(status=status.HTTP_409_CONFLICT)

    user = identity_user(request)
    discovery.pioneers.add(pioneer)
    discovery.owner = CustomUser.objects.get(pk=user.pk)
    discovery.save()

    serializer = DiscoverySerializer(discovery)

    return Response(serializer.data)


@api_view(["GET"])
def get_pioneer_image(request, pioneer_id):
    if not Pioneer.objects.filter(pk=pioneer_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    pioneer = Pioneer.objects.get(pk=pioneer_id)

    return HttpResponse(pioneer.image, content_type="image/png")


@api_view(["PUT"])
@permission_classes([IsModerator])
def update_pioneer_image(request, pioneer_id):
    if not Pioneer.objects.filter(pk=pioneer_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    pioneer = Pioneer.objects.get(pk=pioneer_id)
    serializer = PioneerSerializer(pioneer, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_discoveries(request):
    print("request", request)
    user = identity_user(request)
    print("---", user)
    status_id = int(request.GET.get("status", -1))
    date_start = request.GET.get("date_start")
    date_end = request.GET.get("date_end")
    
    discoveries = Discovery.objects.exclude(status__in=[1, 5])

    if not user.is_moderator:
        discoveries = discoveries.filter(owner_id=user.pk)

    if status_id != -1:
        discoveries = discoveries.filter(status=status_id)

    if date_start:
        discoveries = discoveries.filter(date_formation__gte=parse_datetime(date_start))

    if date_end:
        discoveries = discoveries.filter(date_formation__lte=parse_datetime(date_end))

    # serializer = DiscoveriesSerializer(discoveries, many=True)
    print("---")
    serializer =  DiscoveriesSerializer(discoveries, many=True)
    print(serializer.data)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_discovery_by_id(request, discovery_id):
    if not Discovery.objects.filter(pk=discovery_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    discovery = Discovery.objects.get(pk=discovery_id)
    serializer = DiscoverySerializer(discovery, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_discovery(request, discovery_id):
    if not Discovery.objects.filter(pk=discovery_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    discovery = Discovery.objects.get(pk=discovery_id)
    serializer = DiscoverySerializer(discovery, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_status_user(request, discovery_id):
    if not Discovery.objects.filter(pk=discovery_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    discovery = Discovery.objects.get(pk=discovery_id)

    discovery.owner = identity_user(request)
    discovery.status = 2
    discovery.date_formation = timezone.now()
    discovery.save()

    serializer = DiscoverySerializer(discovery, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsModerator])
def update_status_admin(request, discovery_id):
    if not Discovery.objects.filter(pk=discovery_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = request.data["status"]

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    discovery = Discovery.objects.get(pk=discovery_id)

    if discovery.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    discovery.moderator = identity_user(request)
    discovery.status = request_status
    discovery.date_complete = timezone.now()
    discovery.save()

    serializer = DiscoverySerializer(discovery, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_discovery(request, discovery_id):
    if not Discovery.objects.filter(pk=discovery_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    discovery = Discovery.objects.get(pk=discovery_id)

    if discovery.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    discovery.owner = identity_user(request)
    discovery.status = 5
    discovery.save()

    return Response(status=status.HTTP_200_OK)

@api_view(["GET"])
def discoveries_pioneers(request, discovery_id, pioneer_id):
     return Response(status=status.HTTP_200_OK)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_pioneer_from_discovery(request, discovery_id, pioneer_id):
    if not Discovery.objects.filter(pk=discovery_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not Pioneer.objects.filter(pk=pioneer_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    discovery = Discovery.objects.get(pk=discovery_id)
    discovery.pioneers.remove(Pioneer.objects.get(pk=pioneer_id))
    discovery.save()

    serializer = DiscoverySerializer(discovery)

    return Response(serializer.data)

####!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!

def get_draft_order(request):
    user = identity_user(request)

    if user is None:
        return None

    order = Order.objects.filter(owner_id=user.pk).filter(status=1).first()

    if order is None:
        return None

    return order


@api_view(["GET"])
def search_services(request):
    query = request.GET.get("query", "")

    services = Service.objects.filter(status=1).filter(name__icontains=query)

    serializer = ServiceSerializer(services, many=True)

    draft_order = get_draft_order(request)

    data = {
        "draft_order_id": draft_order.pk if draft_order else None,
        "services": serializer.data
    }

    return Response(data)


@api_view(["GET"])
def get_service_by_id(request, service_id):
    if not Service.objects.filter(pk=service_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    service = Service.objects.get(pk=service_id)
    serializer = ServiceSerializer(service, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsModerator])
def update_service(request, service_id):
    if not Service.objects.filter(pk=service_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    service = Service.objects.get(pk=service_id)
    serializer = ServiceSerializer(service, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsModerator])
def create_service(request):
    service = Service.objects.create()

    serializer = ServiceSerializer(service)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsModerator])
def delete_service(request, service_id):
    if not Service.objects.filter(pk=service_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    service = Service.objects.get(pk=service_id)
    service.status = 2
    service.save()

    services = Service.objects.filter(status=1)
    serializer = ServiceSerializer(services, many=True)

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_service_to_order(request, service_id):
    if not Service.objects.filter(pk=service_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    service = Service.objects.get(pk=service_id)

    order = get_draft_order(request)

    if order is None:
        order = Order.objects.create()

    if order.services.contains(service):
        return Response(status=status.HTTP_409_CONFLICT)

    order.owner = identity_user(request)
    order.services.add(service)
    order.save()

    serializer = OrderSerializer(order, many=False)

    return Response(serializer.data)


@api_view(["GET"])
def get_service_image(request, service_id):
    if not Service.objects.filter(pk=service_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    service = Service.objects.get(pk=service_id)

    return HttpResponse(service.image, content_type="image/png")


@api_view(["PUT"])
@permission_classes([IsModerator])
def update_service_image(request, service_id):
    if not Service.objects.filter(pk=service_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    service = Service.objects.get(pk=service_id)
    serializer = ServiceSerializer(service, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_orders(request):
    user = identity_user(request)

    status_id = int(request.GET.get("status", -1))
    date_start = request.GET.get("date_start", -1)
    date_end = request.GET.get("date_end", -1)

    orders = Order.objects.exclude(status__in=[1, 5])

    if not user.is_moderator:
        orders = orders.filter(owner_id=user.pk)

    if status_id != -1:
        orders = orders.filter(status=status_id)

    if date_start != -1:
        orders = orders.filter(date_formation__gte=parse_datetime(date_start))

    if date_end != -1:
        orders = orders.filter(date_formation__lte=parse_datetime(date_end))

    serializer = OrdersSerializer(orders, many=True)

    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_order_by_id(request, order_id):
    if not Order.objects.filter(pk=order_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Order.objects.get(pk=order_id)
    serializer = OrderSerializer(order, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_order(request, order_id):
    if not Order.objects.filter(pk=order_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Order.objects.get(pk=order_id)
    serializer = OrderSerializer(order, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsRemoteService])
def update_order_execution_time(request, order_id):
    if not Order.objects.filter(pk=order_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Order.objects.get(pk=order_id)
    serializer = OrderSerializer(order, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_status_user(request, discovery_id):
    if not Discovery.objects.filter(pk=discovery_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Discovery.objects.get(pk=discovery_id)

    if order.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    order.status = 2
    order.date_formation = timezone.now()
    order.save()

    calculate_execution_time(discovery_id)

    serializer = DiscoverySerializer(order, many=False)

    return Response(serializer.data)


def calculate_execution_time(discovery_id):
    data = {
        "discovery_id": discovery_id
    }

    requests.post("http://127.0.0.1:8080/calc_execution_time/", json=data, timeout=3)


@api_view(["PUT"])
@permission_classes([IsModerator])
def update_status_admin(request, discovery_id):
    if not Discovery.objects.filter(pk=discovery_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    order = Discovery.objects.get(pk=discovery_id)

    if order.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    order.status = request_status
    order.date_complete = timezone.now()
    order.save()

    serializer = DiscoverySerializer(order, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_order(request, order_id):
    if not Order.objects.filter(pk=order_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Order.objects.get(pk=order_id)
    order.status = 5
    order.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_service_from_order(request, order_id, service_id):
    if not Order.objects.filter(pk=order_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not Service.objects.filter(pk=service_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Order.objects.get(pk=order_id)
    order.services.remove(Service.objects.get(pk=service_id))
    order.save()

    serializer = OrderSerializer(order)

    return Response(serializer.data)


access_token_lifetime = settings.JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#1!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(**serializer.data)
    if user is None:
        message = {"message": "invalid credentials"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    access_token = create_access_token(user.id)

    user_data = {
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "is_moderator": user.is_moderator,
        "access_token": access_token,
    }
    cache.set(access_token, user_data, access_token_lifetime)

    response = Response(user_data, status=status.HTTP_201_CREATED)

    response.set_cookie('access_token', access_token, httponly=True, expires=access_token_lifetime)

    return response


@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    access_token = create_access_token(user.id)

    user_data = {
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "is_moderator": user.is_moderator,
        "access_token": access_token
    }

    cache.set(access_token, user_data, access_token_lifetime)

    message = {
        'message': 'User registered successfully',
        'user_id': user.id,
        "access_token": access_token
    }

    response = Response(message, status=status.HTTP_201_CREATED)

    response.set_cookie('access_token', access_token, httponly=False, expires=access_token_lifetime)

    return response


@api_view(["POST"])
def check(request):
    print("request",request)
    access_token = get_access_token(request)
    if access_token is None:
        message = {"message": "Token is not found"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    if not cache.has_key(access_token):
        message = {"message": "Token is not valid"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    user_data = cache.get(access_token)
    return Response(user_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    access_token = get_access_token(request)

    if cache.has_key(access_token):
        cache.delete(access_token)

    message = {"message": "Вы успешно вышли из аккаунта!"}
    response = Response(message, status=status.HTTP_200_OK)

    response.delete_cookie('access_token')

    return response
