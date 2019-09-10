from datetime import datetime, timedelta

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.goods.models import GoodsVisitCount
from apps.meiduo_admin.serializers.statistical import GoodsVisitCountSerializer
from apps.users.models import User
from datetime import date









# 获取日分类商品访问量
class UserCategoryCountAPIView(APIView):

    def get(self,request):

        # 1.获取当前日期
        today = date.today()
        # 2.根据当前日期查询商品分类访问量表中的符合今天日期的对象数据 [GoodsVisit1,GoodsVisit2,...]
        gvcs = GoodsVisitCount.objects.filter(date=today)
        # 3.使用序列化器构造数据
        s = GoodsVisitCountSerializer(instance=gvcs,many=True)
        # 4.返回数据
        return Response(s.data)



# 获取月新增用户
class UserMonthCountAPIView(APIView):

    def get(self,request):

        # 1.获取当天日期
        today = date.today() - timedelta(days=40)
        # 2.获取30天前的日期
        month_start_date = today - timedelta(days=30)
        # 创建空列表保存每天的用户量
        data = []
        # 3.遍历
        for i in range(30):
            # 3.1 确定开始日期
            start_date = month_start_date + timedelta(days=i)

            # 3.2 确定结束日期
            end_date = month_start_date + timedelta(days=i+1)
            # 3.3 求出开始和结束日期的日增用数量
            count = User.objects.filter(date_joined__gte=start_date,
                                        date_joined__lte=end_date).count()
            # 3.4 添加到列表中
            data.append({
                'count':count,
                'date':start_date,
            })
        # 4 返回数据
        return Response(data)



# 获取日下单用户
class UserDailyOrderCountAPIView(APIView):

    def get(self,request):

        # 1.获取当天日期
        today = date.today()
        # 2.查询下单日期大于等于今天的所有用户对象
        try:
            users = User.objects.filter(orderinfo__create_time__gte=today)
        except:
            return
        data = []
        # 3.遍历所有用户对象 去重id
        for user in users:
            if user.id not in data:
                data.append(
                    user.id,
                )
        # 4.求出列表长度 即用户人数
        count =  len(data)
        # 5.返回数据
        return Response({
            'count':count,
            'date':today,
        })



# 获取日活跃用户
class UserDailyActiveCountAPIView(APIView):

    def get(self,request):

        # 1.获取当天日期
        today = date.today()
        # 2.查询最后下线日期是今天的
        try:
            count = User.objects.filter(last_login__gte=today).count()
        except:
            return
        # 3.返回数据
        return Response({
            'count':count,
            'date':today,
        })



# 获取日增用户
class UserDailyCountAPIView(APIView):

    # 设置权限
    permission_classes = [IsAdminUser]

    def get(self,request):


        # 1.获取当天日期
        today = date.today()

        # 2 查询大于等于今天0点日期，并且创建用户的数量
        try:
            dailyactive = User.objects.filter(date_joined__gte=today).count()
        except:
            return Response(404)

        # 3.返回数据
        return Response({
            'count':dailyactive,
            'date':today,
        })



# 统计用户总数
class UserAllCountAPIView(APIView):

    # 管理员权限
    permission_classes = [IsAdminUser]


    def get(self,request):

        today = datetime.today()
        # 1.获取所有用户
        try:
            count = User.objects.all().count()
        except:
            return
        # 2.响应结果
        return Response({
            'count':count,
            'date':today,
        })

