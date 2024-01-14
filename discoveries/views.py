from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import *
from .models import *


def get_draft_discovery_id():
    discovery = Discovery.objects.filter(status=1).first()

    if discovery is None:
        return None

    return discovery.pk


@api_view(["GET"])
def search_pioneers(request):
    query = request.GET.get("query", "")

    pioneers = Pioneer.objects.filter(status=1).filter(name__icontains=query)

    serializer = PioneerSerializer(pioneers, many=True)

    data = {
        "pioneers": serializer.data,
        "draft_vacancy": get_draft_discovery_id()
    }

    return Response(data)


@api_view(["GET"])
def get_pioneer_by_id(request, pioneer_id):
    if not Pioneer.objects.filter(pk=pioneer_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    pioneer = Pioneer.objects.get(pk=pioneer_id)
    serializer = PioneerSerializer(pioneer, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_pioneer(request, pioneer_id):
    if not Pioneer.objects.filter(pk=pioneer_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    pioneer = Pioneer.objects.get(pk=pioneer_id)
    serializer = PioneerSerializer(pioneer, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def create_pioneer(request):
    Pioneer.objects.create()

    pioneers = Pioneer.objects.all()
    serializer = PioneerSerializer(pioneers, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_pioneer(request, pioneer_id):
    if not Pioneer.objects.filter(pk=pioneer_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    pioneer = Pioneer.objects.get(pk=pioneer_id)
    pioneer.status = 2
    pioneer.save()

    pioneers = Pioneer.objects.filter(status=1)
    serializer = PioneerSerializer(pioneers, many=True)

    return Response(serializer.data)


@api_view(["POST"])
def add_pioneer_to_discovery(request, pioneer_id):
    if not Pioneer.objects.filter(pk=pioneer_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    pioneer = Pioneer.objects.get(pk=pioneer_id)

    discovery = Discovery.objects.filter(status=1).last()

    if discovery is None:
        discovery = Discovery.objects.create()

    discovery.pioneers.add(pioneer)
    discovery.save()

    serializer = PioneerSerializer(discovery.pioneers, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_pioneer_image(request, pioneer_id):
    if not Pioneer.objects.filter(pk=pioneer_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    pioneer = Pioneer.objects.get(pk=pioneer_id)

    return HttpResponse(pioneer.image, content_type="image/png")


@api_view(["PUT"])
def update_pioneer_image(request, pioneer_id):
    if not Pioneer.objects.filter(pk=pioneer_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    pioneer = Pioneer.objects.get(pk=pioneer_id)
    serializer = PioneerSerializer(pioneer, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["GET"])
def get_discoveries(request):
    discoveries = Discovery.objects.all()
    serializer = DiscoverySerializer(discoveries, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_discovery_by_id(request, discovery_id):
    if not Discovery.objects.filter(pk=discovery_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    discovery = Discovery.objects.get(pk=discovery_id)
    serializer = DiscoverySerializer(discovery, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_discovery(request, discovery_id):
    if not Discovery.objects.filter(pk=discovery_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    discovery = Discovery.objects.get(pk=discovery_id)
    serializer = DiscoverySerializer(discovery, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    discovery.status = 1
    discovery.save()

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_user(request, discovery_id):
    if not Discovery.objects.filter(pk=discovery_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = request.data["status"]

    if request_status not in [1, 5]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    discovery = Discovery.objects.get(pk=discovery_id)
    lesson_status = discovery.status

    if lesson_status == 5:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    discovery.status = request_status
    discovery.save()

    serializer = DiscoverySerializer(discovery, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_admin(request, discovery_id):
    if not Discovery.objects.filter(pk=discovery_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = request.data["status"]

    if request_status in [1, 5]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    discovery = Discovery.objects.get(pk=discovery_id)

    lesson_status = discovery.status

    if lesson_status in [3, 4, 5]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    discovery.status = request_status
    discovery.save()

    serializer = DiscoverySerializer(discovery, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_discovery(request, discovery_id):
    if not Discovery.objects.filter(pk=discovery_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    discovery = Discovery.objects.get(pk=discovery_id)
    discovery.status = 5
    discovery.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
def delete_pioneer_from_discovery(request, discovery_id, pioneer_id):
    if not Discovery.objects.filter(pk=discovery_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not Pioneer.objects.filter(pk=pioneer_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    discovery = Discovery.objects.get(pk=discovery_id)
    discovery.pioneers.remove(Pioneer.objects.get(pk=pioneer_id))
    discovery.save()

    serializer = PioneerSerializer(discovery.pioneers, many=True)

    return Response(serializer.data)

