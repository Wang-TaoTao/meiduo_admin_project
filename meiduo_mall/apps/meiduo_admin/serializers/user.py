from rest_framework import serializers

from apps.users.models import User

# 查询用户序列化器
class UserSerializer(serializers.ModelSerializer):


    class Meta:
        model = User

        fields = ['id','username','mobile','email']



# 新增用户序列化器
class UserAddSerializer(serializers.ModelSerializer):

    # 新增password2 确认密码字段
    passcheck = serializers.CharField(write_only=True)

    class Meta:

        model = User
        fields = ['id','username','password','mobile','email','passcheck']

        # 设置密码只在反序列化时候输入使用，在序列化的时候输出此字段
        extra_kwargs={
            'password':{'write_only':True}
        }


    # 重写校验密码
    def validate(self, attrs):

        password = attrs.get('password')
        passcheck = attrs.get('passcheck')

        if password != passcheck:
            raise serializers.ValidationError("密码输入不一致")

        return attrs



    # 重写新增用户方法
    def create(self, validated_data):
        # 删除多余的password2数据
        del validated_data['passcheck']

        # 创建用户 并加密密码
        user = User.objects.create_user(**validated_data)

        return user


