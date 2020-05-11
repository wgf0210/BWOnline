from django.shortcuts import render,redirect
from django.views.generic.base import View
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import login,logout,authenticate
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from users.models import UserProfile,EmailVerifyRecord
from .forms import Loginform,Registerform,Forgetpwdform,Modifypwdform
from utils.email_send import send_register_email

#邮箱和用户名都可以登录
# 基础ModelBackend类，因为它有authenticate方法
class CustomBackend(ModelBackend):
    def authenticate(self,request,username=None,password=None,**kwargs):
        try:
            # 不希望用户存在两个，get只能有一个。两个是get失败的一种原因 Q为使用并集查询
            user = UserProfile.objects.get(Q(username=username)|Q(email=username))
            # django的后台中密码加密：所以不能password==password
            # UserProfile继承的AbstractUser中有def check_password(self, raw_password):
            if user.check_password(password):
                return user
        except Exception as e:
            return None

class LoginView(View):
    def get(self,request):
        return render(request,'login.html')
    def post(self,request):
        # 实例化
        login_form = Loginform(request.POST)
        if login_form.is_valid():
            # 获取用户提交的用户名和密码
            user_name = request.POST.get('username',None)
            pass_word = request.POST.get('password',None)
            # 成功返回user对象,失败None
            user = authenticate(username=user_name,password=pass_word)
            print(user,user_name)
            # 如果不是null说明验证成功
            if user is not None:
                if user.is_active:
                    # 只有注册激活才能登录
                    login(request,user)
                    return render(request,'index.html')
                else:
                    return render(request,'login.html',{'msg':'用户名未激活','login_form':login_form})
            # 只有当用户名或密码不存在时，才返回错误信息到前端
            else:
                return render(request,'login.html',{'msg':'用户名密码错误','login_form':login_form})
        # form.is_valid（）已经判断不合法了，所以这里不需要再返回错误信息到前端了
        else:
            return render(request,'login.html',{'login_form':login_form})


class RegisterView(View):
    def get(self,request):
        register_form = Registerform()
        return render(request,'register.html',{'register_form':register_form})

    def post(self,request):
        register_form = Registerform(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get('email',None)
            if UserProfile.objects.filter(email=user_name):
                return render(request,'register.html',{'register_form':register_form,'msg':u'用户名已存在'})
            pass_word = request.POST.get('password',None)
            user_profile = UserProfile()
            user_profile.username = user_name
            user_profile.email = user_name
            user_profile.is_active = False

            user_profile.password = make_password(pass_word)
            user_profile.save()
            send_register_email(user_name,'register')
            return render(request,'login.html',{'msg':u'邮箱已发送验证码，进入邮箱激活'})
        else:
            return render(request,'register.html',{'register_form':register_form})
        
# 激活用户的view
class ActiveUserView(View):
    def get(self,request,active_code):
        # 查询邮箱验证记录是否存在
        all_record = EmailVerifyRecord.objects.filter(code=active_code)
        # 如果不为空也就是有用户
        if all_record:
            for record in all_record:
                # 获取对应的邮箱
                email = record.email
                # 查找到有相对应的user
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
                # 激活成功跳转到登录页面
                return render(request,'login.html')
        # 自己瞎输的验证码
        else:
            return render(request,'active_fail.html')


class ForgetPwdView(View):
    def get(self,request):
        forget_form = Forgetpwdform()
        return render(request,'forgetpwd.html',{'forget_form':forget_form})
    def post(self,request):
        forget_form = Forgetpwdform(request.POST)
        if forget_form.is_valid():
            email = request.POST.get('email',None)
            send_register_email(email,'forget')
            return render(request,'send_success.html')
        else:
            return render(request,'forgetpwd.html',{'forget_form':forget_form})


class ResetView(View):
    def get(self,request,active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                print('----------------------------12312312313')
                return render(request,'password_reset.html',{'email':email})
        else:
            return render(request,'active_fail.html')
        return render(request,'login.html')
    def post(self,request,active_code):
        return redirect('modify_pwd')

class ModifyPwdView(View):
    def get(self,request):
        return render(request,'password_reset.html')
    def post(self,request):
        modify_form = Modifypwdform(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get('pwssword1',None)
            pwd2 = request.POST.get('pwssword2',None)
            email = request.POST.get('email',None)
            if pwd1 != pwd2:
                return render(request,'password_reset.html',{'email':email,'msg':'密码不一致'})
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd2)
            user.save()
            return render(request,'login.html')
        else:
            email = request.POST.get('email','')
            return render(request,'password_reset.html',{'email':email,'modify_form':modify_form})

