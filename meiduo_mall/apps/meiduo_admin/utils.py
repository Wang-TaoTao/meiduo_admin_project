
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response




# 设置cors返回值
def jwt_response_payload_handler(token, user=None, request=None):

    """
    自定义jwt认证成功后返回的数据
    """
    return {
        'token': token,
        'id': user.id,
        'username': user.username
    }




# 重写分页功能
class CustomPageNumberPagination(PageNumberPagination):

    # 设置每页条数
    page_size = 4

    # 设置url中每页条数的关键字
    page_size_query_param = 'pagesize'

    # 设置每页能返回的最大条数
    max_page_size = 15

    # 重写分页返回方法，按照指定的字段进行分页数据返回
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,      # 用户总数量
            'lists': data,                           # 用户数据
            'page':self.page.number,                 # 当前页数
            'pages': self.page.paginator.num_pages,  # 总页数
            'pagesize': self.page_size               # 后端指定的每页条数
        })
