# -*- coding: utf-8 -*-

import json
import logging
import redis

from django.http import HttpResponse
from realtime.models import RealtimeBaseInfo

logger = logging.getLogger("django.request")

# redis_host = '192.168.182.129'
redis_host = 'localhost'
expire_time = 360


def baseinfo(request):
    '''
    interface:
        [
            {'time':'201503311630', 'servietype':'B2B', 'dev':'BesTV_OS_Lite',
             'viewtype':1, 'secrate':0.89, 'fluency':0.80, 'records':10000},
            {...}
        ]
    store the result in Redis:
        string: AiShangVOD
        format '201503311430 secratio1:0.8 secratio2:0.7 secratio3:0.78 ...'
    '''
    result = "ok"
    if request.method == "POST":
        try:
            contents = json.loads(request.body)
            r = redis.StrictRedis(redis_host)
            latest_tag = ''
            latest_dev = ''
            for item in contents:
                current_time = item['time']
                service_type = item['servicetype']
                dev = item['dev']
                view_type = item['viewtype']
                secrate = item['secrate']
                fluency = item['fluency']
                records = item['records']
                tag = dev + current_time
                if latest_tag != tag:
                    if latest_dev != '':
                        r.expire(latest_dev, expire_time)
                    latest_tag = tag
                    latest_dev = dev
                    r.set(latest_dev, current_time)
                r.append(latest_dev, ' secrate%d:%s' % (view_type, secrate))
                r.append(latest_dev, ' fluency%d:%s' % (view_type, fluency))
                r.append(latest_dev, ' records%d:%s' % (view_type, records))
                try:
                    baseinfo_obj = RealtimeBaseInfo(
                        Time=current_time,
                        ServiceType=service_type,
                        DeviceType=dev,
                        ViewType=view_type,
                        SucRate=secrate,
                        Fluency=fluency,
                        Records=records)
                    baseinfo_obj.save()
                except Exception, e:
                    logger.debug('MySQL: (%s,%s,%s,%d,%s,%s,%d)' % (
                        current_time, service_type, dev,
                        view_type, secrate, fluency, records))

            # r.expire(latest_dev, expire_time)
        except Exception, e:
            result = "Exception: %s" % e
    else:
        result = "error"

    respStr = json.dumps({"result": result})
    logger.debug("update playinfo: %s" % (respStr))

    return HttpResponse(respStr, content_type="application/json")
