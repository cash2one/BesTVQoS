#!/bin/env python
# coding=utf-8
import sys
import re
from django.db.utils import IntegrityError
from tplay.models import Title, BestvFbuffer

reload(sys)
sys.setdefaultencoding( "utf-8" )
import logging
from django.core.management.base import BaseCommand


def refreshTitle():
    # 更新Title文件
    # device_type_pattern = re.compile(r'^([^\d]+)([\.\d]+)$')
    version_pattern = re.compile(r'(V?\d+\.+[\.\d]+\d+)$')

    titles = Title.objects.all()
    titles_names = set()
    for title in titles:
        titles_names.add("{0}{1}{2}".format(title.ServiceType, title.DeviceType, title.Version))

    records = BestvFbuffer.objects.values("ServiceType", "DeviceType").filter(DeviceType__contains='.').distinct()
    for record in records:
        rst = re.search(version_pattern, record["DeviceType"])
        if rst:
            version = rst.group(1)
            device_type = record["DeviceType"][:-len(version)].rstrip('_').rstrip('\x7f')
            key = "{0}{1}{2}".format(record["ServiceType"], device_type, version)
            if key not in titles_names:
                title = Title(ServiceType=record["ServiceType"],
                              DeviceType=device_type,
                              Version=version)
                try:
                    title.save()
                    titles_names.add(key)
                except IntegrityError, e:
                    print('key:{0}, error:{1}'.format(key, e))
        else:
            print '{0} match {1} results {2}'.format(record["DeviceType"], version_pattern, rst)

class Command(BaseCommand):
    args = ""
    help = "set notice delete."

    def handle(self, *args, **options):
        logging.debug("refreshTitle start")
        refreshTitle()
        logging.debug("refreshTitle end")
