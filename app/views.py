from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.utils.dateparse import parse_datetime
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .jwt_helper import *
from .permissions import *
from .serializers import *
from .utils import identity_user


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


@api_view(["POST"])
@permission_classes([IsModerator])
def create_pioneer(request):
    pioneer = Pioneer.objects.create()

    serializer = PioneerSerializer(pioneer)

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
    user = identity_user(request)

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

    serializer = DiscoveriesSerializer(discoveries, many=True)

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
@permission_classes([IsRemoteService])
def update_discovery_verify(request, discovery_id):
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

    request_status = int(request.data["status"])

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


@swagger_auto_schema(method='post', request_body=UserLoginSerializer)
@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        message = {"message": "Введенные данные невалидны"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    access_token = create_access_token(user.id)

    serializer = UserSerializer(
        user,
        context={
            "access_token": access_token
        }
    )

    response = Response(serializer.data, status=status.HTTP_200_OK)

    response.set_cookie('access_token', access_token, httponly=False, expires=settings.JWT["ACCESS_TOKEN_LIFETIME"])

    return response


@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    access_token = create_access_token(user.id)

    message = {
        'message': 'Пользователь успешно зарегистрирован',
        'user_id': user.id,
        "access_token": access_token
    }

    response = Response(message, status=status.HTTP_201_CREATED)

    response.set_cookie('access_token', access_token, httponly=False, expires=settings.JWT["ACCESS_TOKEN_LIFETIME"])

    return response


@api_view(["POST"])
def check(request):
    user = identity_user(request)

    user = CustomUser.objects.get(pk=user.pk)
    serializer = UserSerializer(user, many=False)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    access_token = get_access_token(request)

    if access_token not in cache:
        cache.set(access_token, settings.JWT["ACCESS_TOKEN_LIFETIME"])

    message = {"message": "Вы успешно вышли из аккаунта"}
    response = Response(message, status=status.HTTP_200_OK)

    response.delete_cookie('access_token')

    return response
