from django import http
from django.contrib.auth.mixins import LoginRequiredMixin
from utils.response_code import RETCODE


class LoginRequiredJSONMixin(LoginRequiredMixin):
    def handle_no_permission(self):
        return http.JsonResponse({'code': RETCODE.SESSIONERR, 'errmsg': '用户未登录'})