from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseBadRequest
from django.core.servers.basehttp import FileWrapper
import os
import shutil
from forms import FileForm

def update_log(request):
    if request.method == "POST":
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            handle_uploaded_file(cd)
            return HttpResponse("Ok: File %s update success."%cd['name'])
        else:
            return HttpResponseBadRequest("<h1>Need more arguments</h1>")
    else:
        return HttpResponseBadRequest("<h1>Wrong request type</h1>")

def handle_uploaded_file(cd):
    file_name = cd['name']
    file_date = cd['date']
    file_content = cd['content']

    try:
        path = "./logdata/%s/"%file_date
        if not os.path.isdir(path):
            os.makedirs(path)
        dest_file = path + file_name
        if os.path.exists(dest_file):
            os.remove(dest_file)
        destination = open(dest_file, 'wb+')
        for chunk in file_content.chunks():
            destination.write(chunk)
        destination.close()
    except Exception, e:
        print e

    return file_name

def get_img(request):
    date = request.GET.get("date", "")
    name = request.GET.get("name", "")

    if not date or not name:
        return HttpResponseBadRequest("<h1>Need more arguments</h1>")
    else:
        if not os.path.exists("./logdata/%s/%s"%(date, name)):
            return HttpResponseNotFound("<h1>Image %s Not Found</h1>"%name)
        else:
            image_data = open("./logdata/%s/%s"%(date, name), 'rb').read()
            f,e = os.path.splitext(name)
            if e == ".png":
                ct = "image/png"
            else:
                ct = "image/jpeg"
            return HttpResponse(image_data, content_type=ct)

def get_log(request):
    date = request.GET.get("date", "")
    name = request.GET.get("name", "")

    if not date or not name:
        return HttpResponseBadRequest("<h1>Need more arguments</h1>")
    else:
        dest_file = "./logdata/%s/%s"%(date, name)
        if not os.path.exists(dest_file):
            return HttpResponseNotFound("<h1>Log %s Not Found</h1>"%name)
        else:
            wrapper = FileWrapper(open(dest_file))
            response = HttpResponse(wrapper, content_type="text/plain")
            response['Content-Length'] = os.path.getsize(dest_file)
            response['Content-Encoding'] = 'utf-8'
            response['Content-Disposition'] = 'attachment;filename=%s'%name
            return response

def delete(request):
    date = request.GET.get("date", "")
    name = request.GET.get("name", "")

    if not date:
        return HttpResponseBadRequest("<h1>Need more argument</h1>")
    elif not name:
        path = "./logdata/%s/"%date
        if not os.path.isdir(path):
            return HttpResponseBadRequest("<h1>No such directory %s</h1>"%date)
        else:
            shutil.rmtree(path)
            return HttpResponse("Ok: Logs in %s deleted success."%date)
    else:
        file = "./logdata/%s/%s"%(date, name)
        if not os.path.exists(file):
            return HttpResponseNotFound("<h1>File %s Not Found</h1>"%name)
        else:
            os.remove(file)
            return HttpResponse("Ok: File %s deleted success."%name)
