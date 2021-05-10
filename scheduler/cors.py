from django.middleware.common import MiddlewareMixin


class CorsMiddleWare(MiddlewareMixin):

    def process_response(self, request, response):


        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Headers"] = "X-API-KEY, Origin, X-Requested-With, Content-Type, Accept, Access-Control-Request-Method,Access-Control-Request-Headers, Authorization,Referer,User-Agent"
        response["Access-Control-Allow-Methods"] = " POST, GET, OPTIONS,DELETE"
        return response
