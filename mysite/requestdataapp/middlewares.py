from django.http import HttpRequest, HttpResponse
import time
from datetime import timedelta

def set_useragent_on_request_middleware(get_response):

    print('Initial call')

    def middleware(request: HttpRequest):
        print('before get response')
        request.user_agent = request.META['HTTP_USER_AGENT']
        response = get_response(request)
        print('after getresponse')
        return response
    return middleware


class CountRequestsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests_count = 0
        self.responses_count = 0
        self.exceptions_count = 0

    def __call__(self, request: HttpRequest):
        self.requests_count += 1
        print('requests count', self.requests_count)
        response = self.get_response(request)
        self.responses_count += 1
        print('responses count', self.responses_count)
        return response

    def process_exception(self,request:HttpRequest, exception: Exception):
        self.exceptions_count += 1
        print('got', self.exceptions_count, 'exceptions so far')


class ThrottlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.time = None
        self.ip_address = None

    def __call__(self, request: HttpRequest):
        time_of_req = time.time()
        new_address = request.META['REMOTE_ADDR']
        if new_address == self.ip_address and (time_of_req - self.time) < 5:
            return HttpResponse('<h2>Превышено количество запросов,попробуйте зайти позже</h2>')
        else:
            self.ip_address = new_address
            self.time = time_of_req
            response = self.get_response(request)
            return response
