from django.contrib.auth.backends import ModelBackend
import re

from apps.users.models import User


# 进行判断前后端请求
class MeiduoModelBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):

        # 判断是否是后端请求，如果request为空则为后端请求
        if request is None:

            try:
                # 判断用户输入的是否是用户名，并且是内部员工
                user = User.objects.get(username=username,is_staff=True)
            except:
                # 判断用户输入的是否是手机号，并且是内部员工
                user = User.objects.get(mobile=username,is_staff=True)

            # 进行校验用户名和密码
            if user.check_password(password):
                return user
            # 如果校验失败 则返回None
            return None

        else:
            # 如果request不为空 则是前端请求
            try:
                # 判断用户输入的是否是手机号
                user = User.objects.get(mobile=username)

            except:
                # 判断用户输入的是否是用户名
                user = User.objects.get(username=username)

            # 进行校验用户名和密码
            if user.check_password(password):
                return user
            # 如果校验失败 则返回None
            return None




# #课件中的
# class MeiduoModelBackend(ModelBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         # 判断是否通过vue组件发送请求
#         if request is None:
#             try:
#                 user = User.objects.get(username=username, is_staff=True)
#             except:
#                 return None
#             # 判断密码
#             if user.check_password(password):
#                 return user
#
#         else:
#             # 变量username的值，可以是用户名，也可以是手机号，需要判断，再查询
#             try:
#                 # if re.match(r'^1[3-9]\d{9}$', username):
#                 #     user = User.objects.get(mobile=username)
#                 # else:
#                 #     user = User.objects.get(username=username)
#                 user = User.objects.get(username=username)
#             except:
#                 # 如果未查到数据，则返回None，用于后续判断
#                 try:
#                     user = User.objects.get(mobile=username)
#                 except:
#                     return None
#                     # return None
#
#             # 判断密码
#             if user.check_password(password):
#                 return user
#             else:
#                 return None