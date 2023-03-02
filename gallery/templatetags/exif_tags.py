from django import template

register = template.Library()


@register.filter
def get_exif_attribute(pic, attribute):
    if attribute not in ("GPSLongitude", "GPSLatitude"):
        try:
            return pic.exif.get(attribute, {}).get("val", "")
        except:
            return None
    else:
        try:
            return pic.exif.get(attribute, {}).get("num", "")
        except:
            return None

@register.filter
def list_item(lst, i):
    try:
        return lst[i]
    except:
        return None