from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def process_get_view(request: HttpRequest) -> HttpResponse:
    a = request.GET.get('a', '')
    b = request.GET.get('b', '')
    result = a + b
    context = {
        'a': a,
        "b": b,
        'result': result,
    }
    return render(request,'requestdataapp/request-query-params.html', context=context)


def user_form(request: HttpRequest) -> HttpResponse:
    return render(request,'requestdataapp/user-bio-form.html')


def handle_file_upload(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST' and request.FILES.get('myfile'):
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        if request.FILES['myfile'].size < 1e+6:
            filename = fs.save(myfile.name, myfile)
            print('saved file', filename)
        else:
            return HttpResponse('<h2>Слишком большой размер файла</h2>')
    return render(request, 'requestdataapp/file-upload.html')


