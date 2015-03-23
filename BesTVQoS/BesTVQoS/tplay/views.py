# -*- coding: utf-8 -*- 

import json
import logging

from django.http import HttpResponse
from tplay.models import *

logger = logging.getLogger("django.request")

def playinfo(request):
    result="ok"
    if request.method=="POST":
        try:
            contents=json.loads(request.body)
            for item in contents:
                create_date='%s-%s-%s'%(item['date'][0:4], item['date'][4:6], item['date'][6:8])
                playinfo_obj=playinfo(
                    ServiceType=item['servicetype'],
                    DeviceType=item['dev'],
                    ISP=item['isp'],
                    Area=item['area'],
                    ViewType=item['viewtype'],
                    Date=create_date,
                    Hour=item['hour'],
                    Records=item['records'],
                    Users=item['users'],
                    AvgTimeOfUser=item['avg'])
                playinfo_obj.save(force_update=true)
        except ValueError, e:
            result="error: %s"%e
        except Exception, e:
            result="error: %s"%e
    else:
        result="error"

    respStr=json.dumps({"result":result})
    logger.debug("update_playinfo: %s"%(respStr))
    return HttpResponse(respStr, content_type="application/json")