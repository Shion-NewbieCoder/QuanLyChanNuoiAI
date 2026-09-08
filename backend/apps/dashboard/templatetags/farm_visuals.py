"""Decorative illustrations only; no additional animal or pen data is stored."""
from django import template

register = template.Library()
ICONS = {"dashboard", "herds", "animals", "animal-groups", "pens", "care", "feed",
         "medicine", "vaccines", "growth", "reproduction", "sales", "statistics", "ai",
         "view", "edit", "delete", "plus"}


@register.inclusion_tag("management/icon.html")
def farm_icon(name):
    return {"icon_name": name if name in ICONS else "herds"}


@register.simple_tag
def farm_avatar(obj=None, section="herds"):
    if section == "pens":
        name = "barn"
    elif obj is None:
        name = "herd" if section in ("herds", "animal-groups") else "animal"
    else:
        herd = obj if section == "herds" else getattr(obj, "herd", None)
        animal_type = str(getattr(herd, "animal_type", "")).strip().casefold()
        # Match known text for illustration only; unknown types use a neutral badge.
        names = {"bò": "cow", "cattle": "cow", "cow": "cow", "bò sữa": "cow",
                 "heo": "pig", "lợn": "pig", "pig": "pig", "pigs": "pig",
                 "dê": "goat", "goat": "goat", "goats": "goat",
                 "cừu": "sheep", "sheep": "sheep", "trâu": "buffalo", "buffalo": "buffalo"}
        name = names.get(animal_type, "animal")
    return f"images/farm/{name}.svg"
