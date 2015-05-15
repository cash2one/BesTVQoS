#!/bin/env python
# coding=utf-8
import sys
from tplay.models import Title, BestvFbuffer

reload(sys)
sys.setdefaultencoding( "utf-8" )
import logging
from django.core.management.base import BaseCommand


def refreshTitle():
    # 更新Title文件
    titles = Title.objects.all()
    titles_names = set()
    for title in titles:
        titles_names.add("{0}{1}{2}".format(title.Date, title.ServiceType, title.DeviceType))
    fbuffers = BestvFbuffer.objects.values("Date","ServiceType","DeviceType").distinct()
    for fbuffer in fbuffers:
        key = "{0}{1}{2}".format(fbuffer["Date"], fbuffer["ServiceType"], fbuffer["DeviceType"])
        if key not in titles_names:
            title = Title(Date=fbuffer["Date"], ServiceType=fbuffer["ServiceType"], DeviceType=fbuffer["DeviceType"])
            title.save()

class Command(BaseCommand):
    args = ""
    help = "set notice delete."

    def handle(self, *args, **options):
        logging.debug("refreshTitle start")
        refreshTitle()
        logging.debug("refreshTitle end")
