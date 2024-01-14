from django.shortcuts import render, redirect

from .models import *


def index(request):
    query = request.GET.get("query")
    thematics = Pioneer.objects.filter(name__icontains=query).filter(status=1) if query else Pioneer.objects.filter(status=1)

    context = {
        "search_query": query if query else "",
        "pioneers": thematics
    }

    return render(request, "home_page.html", context)


def pioneer_details(request, pioneer_id):
    context = {
        "pioneer": Pioneer.objects.get(id=pioneer_id)
    }

    return render(request, "pioneer_page.html", context)


def pioneer_delete(request, pioneer_id):
    reactor = Pioneer.objects.get(id=pioneer_id)
    reactor.delete()

    return redirect("/")
