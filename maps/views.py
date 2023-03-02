from django.shortcuts import render

from picture.models import Picture
from Final_Project.local_settings import mapbox_access_token


def picture_detail_map(request, uuid):
    """
    This was just to test out the map functionality. This view should
    be integrated inside the picture_detail view.
    """
    picture = Picture.objects.get(uuid=uuid) # Already in view, no need to add

    latitude = picture.exif.get("GPSLatitude", {}).get("num", "")
    longitude = picture.exif.get("GPSLongitude", {}).get("num", "")
    lon_lat = latitude + longitude

    context = {
        "mapbox_access_token": mapbox_access_token,
        "latitude": latitude,
        "longitude": longitude,
        "lon_lat": lon_lat,
    }
    return render(request, "maps/picture_detail_map.html", context)
