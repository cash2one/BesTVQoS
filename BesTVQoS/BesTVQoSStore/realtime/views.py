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
             'viewtype':1, 'sucratio':0.89, 'fluency':0.80, 'records':10000},
            {...}
        ]
    store the result in Redis:
        string: AiShangVOD
        format '201503311430 sucratio1:0.8 sucratio2:0.7 sucratio3:0.78 ...'
    '''
    result = "ok"
    if request.method == "POST":
        try:
            contents = json.loads(request.body)
            logger.debug("realtime contents: %s" % contents)
            r = redis.StrictRedis(redis_host)
            # latest_tag = ''
            latest_dev = ''
            for item in contents:
                current_time = item['time']
                service_type = item['servicetype']
                dev = item['dev']
                view_type = item['viewtype']
                sucratio = item['sucratio']
                fluency = item['fluency']
                records = item['records']
                logger.debug('realtime data: (%s,%s,%s,%s,%s,%s,%s)' % (
                    current_time, service_type, dev,
                    view_type, sucratio, fluency, records))

                # tag = dev + current_time
                # if latest_tag != tag:
                #     if latest_dev != '':
                #         r.expire(latest_dev, expire_time)
                #     latest_tag = tag
                #     latest_dev = dev
                #     r.set(latest_dev, current_time)
                latest_dev = dev
                if view_type == u'1':
                    r.set(latest_dev, current_time)
                if view_type in [u'1', u'2', u'3', u'4']:
                    r.append(latest_dev, ' sucratio%s:%.2f' %
                             (view_type, 100.0 * float(sucratio)))
                    r.append(latest_dev, ' fluency%s:%.2f' %
                             (view_type, 100.0 * float(fluency)))
                    r.append(latest_dev, ' records%s:%s' %
                             (view_type, records))
                try:
                    baseinfo_obj = RealtimeBaseInfo(
                        Time=current_time,
                        ServiceType=service_type,
                        DeviceType=dev,
                        ViewType=view_type,
                        SucRate=sucratio,
                        Fluency=fluency,
                        Records=records)
                    baseinfo_obj.save()
                except Exception, e:
                    logger.debug('MySQL error: (%s,%s,%s,%s,%s,%s,%s)' % (
                        current_time, service_type, dev,
                        view_type, sucratio, fluency, records))

            # r.expire(latest_dev, expire_time)
        except Exception, e:
            result = "Exception: %s" % e
    else:
        result = "error"

    respStr = json.dumps({"result": result})
    logger.debug("update realtime baseinfo: %s" % (respStr))

    return HttpResponse(respStr, content_type="application/json")
