
from navi import Navi


def do_mobile_support(request, dev, context):
    if dev == "m":
        navi = Navi()
        navi_path = navi.get_path(request.path)
        context["is_mobile"] = True
        context["show_topbar"] = True
        context["top_title"] = navi_path[-1].name
        context["path"] = navi_path[:-1]

    return context
