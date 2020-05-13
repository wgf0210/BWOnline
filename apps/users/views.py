from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.views.generic.base import View
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import login,logout,authenticate
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from users.models import *
from operation.models import *
from organization.models import *
from users.forms import *
from utils.email_send import send_register_email
from utils.mixin_utils import LoginRequiredMixin
from pure_pagination import Paginator,PageNotAnInteger
from django.urls import reverse

# sql注入测试代码
class LoginUnsafeView(View):
    def get(self,request):
        return render(request,'login.html',{})
    def post(self,request):
        user_name = request.POST.get('username','')
        pass_word = request.POST.get('password','')
        import MySQLdb
        conn = MySQLdb.connect(host-'127.0.0.1',user='root',password='002598',db='bwonline_db',charset='utf8')
        cursor = conn.cursor()
        sql_select = 'select * from users_userprofile where email="{0}" and password="{1}"'.format(user_name,pass_word)
        result = cursor.execute(sql_select)
        for row in cursor.fetchall():
            # 查询到用户
            pass    
        # print 'test'


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

'''首页'''
class IndexView(View):
    def get(self,request):
        #轮播图
        all_banners = Banner.objects.all().order_by('index')
        #课程
        courses = Course.objects.filter(is_banner=False)[:6]
        #轮播课程
        banner_courses = Course.objects.filter(is_banner=True)[:3]
        #课程机构
        course_orgs = Course.objects.all()[:15]
        return render(request,'index.html',{
            'all_banners':all_banners,
            'courses':courses,
            'banner_courses':banner_courses,
            'course_orgs':course_orgs
        })

# 登录
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
            # 如果不是null说明验证成功
            if user is not None:
                if user.is_active:
                    # 只有注册激活才能登录
                    login(request,user)
                    return HttpResponseRedirect(reverse('index'))
                else:
                    return render(request,'login.html',{'msg':'用户名未激活','login_form':login_form})
            # 只有当用户名或密码不存在时，才返回错误信息到前端
            else:
                return render(request,'login.html',{'msg':'用户名密码错误','login_form':login_form})
        # form.is_valid（）已经判断不合法了，所以这里不需要再返回错误信息到前端了
        else:
            return render(request,'login.html',{'login_form':login_form})

# 注册
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

# 登出
class LogoutView(View):
    def get(self,request):
        logout(request)
        return HttpResponseRedirect(reverse('index'))

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

# 找回密码
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

# 重置密码
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

# 修改用户密码
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

# 用户个人信息
class UserinfoView(View,LoginRequiredMixin):
    def get(self,request):
        return render(request,'usercenter-info.html')
    def post(self,request):
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(user_info_form.errors), content_type='application/json')

# 用户图像修改
class UploadImageView(View,LoginRequiredMixin):
    def post(self,request):
        #上传的文件都在request.FILES里面获取，所以这里要多传一个这个参数
        image_form = UploadImageForm(request.POST,request.FILES)
        if image_form.is_valid():
            image = image_form.cleaned_data['image']
            request.user.image = image
            request.user.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail"}', content_type='application/json')

# 个人中心修改用户密码
class UpdatePwdView(View):
    def post(self,request):
        modify_form = Modifypwdform(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get('password1','')
            pwd2 = request.POST.get('password2','')
            if pwd1 != pwd2:
                return HttpResponse('{"status":"fail","msg":"密码不一致"}',  content_type='application/json')
            user = request.user
            user.password = make_password(pwd2)
            user.save()

            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(modify_form.errors), content_type='application/json')

# 发送邮箱修改验证码
class SendEmailCodeView(View,LoginRequiredMixin):
    def get(self,request):
        email = request.GET.get('email','')
        if UserProfile.objects.filter(email=email):
            return HttpResponse('{"email":"邮箱已存在"}', content_type='application/json')

        send_register_eamil(email,'update_email')
        return HttpResponse('{"status":"success"}', content_type='application/json')

# 修改邮箱
class UpdateEmailView(View,LoginRequiredMixin):
    def post(self,request):
        email = request.POST.get("email", "")
        code = request.POST.get("code", "")

        existed_records = EmailVerifyRecord.objects.filter(email=email, code=code, send_type='update_email')
        if existed_records:
            user = request.user
            user.email = email
            user.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"email":"验证码无效"}', content_type='application/json')

# 我的课程
class MyCourseView(LoginRequiredMixin, View):
    '''我的课程'''
    def get(self, request):
        user_courses = UserCourse.objects.filter(user=request.user)
        return render(request, "usercenter-mycourse.html", {
            "user_courses":user_courses,
        })

# 我收藏的课程机构
class MyFavOrgView(View,LoginRequiredMixin):
    def get(self,request):
        org_list = []
        fav_orgs = UserFavorite.objects.filter(user=request.user,fav_type=2)
        # 上面的fav_orgs只存放了id，还需要通过id找到机构对象
        for fav_org in fav_orgs:
            # 取出fav_id也就是机构的id
            org_id = fav_org.fav_id
            # 获取这个机构对象
            org = CourseOrg.objects.get(id=org_id)
            org_list.append(org)

        return render(request,'usercenter-fav-org.html',{
            'org_list':org_list
        })

# 我收藏的授课讲师
class MyFavTeacherView(View,LoginRequiredMixin):
    def get(self,request):
        teacher_list = []
        fav_teachers = UserFavorite.objects.filter(user=request.user,fav_type=3)
        for fav_teacher in fav_teachers:
            teacher_id = fav_teacher.fav_id
            teacher = Teacher.objects.get(id=teacher_id)
            teacher_list.append(teacher)
        return render(request,'usercenter-fav-teacher.html',{
            'teacher_list':teacher_list
        })
        
# 我收藏的课程
class MyFavCourseView(View,LoginRequiredMixin):
    def get(self,request):
        course_list = []
        fav_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)
        for fav_course in fav_courses:
            course_id = fav_course.fav_id
            course = Course.objects.get(id=course_id)
            course_list.append(course)

        return render(request, 'usercenter-fav-course.html', {
            "course_list":course_list,
        })

# 我的消息
class MyMessageView(View,LoginRequiredMixin):
    def get(self,request):
        all_message = UserMessage.objects.filter(user=request.user.id)
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_message, 4,request=request)
        messages = p.page(page)
        return  render(request, "usercenter-message.html", {
        "messages":messages,
        })

# 全局处理404
from django.shortcuts import render_to_response
def pag_not_found(request,exception, template_name='404.html'):
    response = render_to_response('404.html', {})
    response.status_code = 404
    return response

# 全局500处理函数
def page_error(request,template_name='500.html'):
    from django.shortcuts import render_to_response
    response = render_to_response('500.html', {})
    response.status_code = 500
    return response


