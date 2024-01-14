from django.shortcuts import render
from discovery.utils.db import db


def index(request):
    query = request.GET.get("discoverer", "")

    context = {
        "discoverers": searchDiscoverers(query),
        "query": query,
    }

    return render(request, "home_page.html", context)


def discovererPage(request, discoverer_id):
    context = {
        "discoverer": getDiscoverer(discoverer_id)
    }

    return render(request, "discoverer_page.html", context)

def searchDiscoverers(discoverer_name=""):
    res = []

    for discoverer in db["discoverers"]:
        if discoverer_name.lower() in discoverer["name"].lower():
            res.append(discoverer)

    return res


def getDiscoverer(discoverer_id):
    for discoverer in db["discoverers"]:
        if discoverer["id"] == discoverer_id:
            return discoverer