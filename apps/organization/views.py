from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.base import View
from django.contrib.auth import authenticate
from django.db.models import Q
from organization.models import *
from course.models import *
from operation.models import UserFavorite
from pure_pagination import Paginator,PageNotAnInteger
from .froms import UserAskForm


'''课程机构'''
class OrgView(View):
    
    def get(self, request):
        all_orgs = CourseOrg.objects.all()   # 所有课程机构
        all_citys = CityDict.objects.all()   # 所有城市
        org_nums = all_orgs.count()    # 有多少家机构
        hot_orgs = all_orgs.order_by('-click_nums')[:3]   # 热门课程机构排名
        # 机构搜索功能
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            # 在name字段进行操作,做like语句的操作。i代表不区分大小写,,or操作使用Q
            all_orgs = all_orgs.filter(Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords))
        
        # 城市筛选
        city_id = request.GET.get('city','')
        if city_id:
            all_orgs = all_orgs.filter(city_id=int(city_id))

        # 类别筛选
        category = request.GET.get('ct','')
        if category:
            all_orgs = all_orgs.filter(category=category)

        # 学习人数和课程数筛选
        sort = request.GET.get('sort', "")
        if sort:
            if sort == "students":
                all_orgs = all_orgs.order_by("-students")
            elif sort == "courses":
                all_orgs = all_orgs.order_by("-course_nums")
        
        try:
            # 对课程机构进行分页
            # 尝试获取前台get请求传递过来的page参数
            # 如果是不合法的配置参数默认返回第一页
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        # 这里指从allorg中取3个出来，每页显示3个
        p = Paginator(all_orgs, 3, request=request)
        orgs = p.page(page)

        return render(request, "org-list.html", {
            "all_orgs": orgs,
            "all_citys": all_citys,
            "org_nums": org_nums,
            'city_id':city_id,
            "category": category,
            'hot_orgs':hot_orgs,
            'sort':sort,
        })


'''用户添加咨询'''
class AddUserAskView(View):
    def post(self,request):
        userask_form = UserAskForm(request.POST)
        if userask_form.is_valid():
            user_ask = userask_form.save(commit=True)
            # 如果保存成功,返回json字符串,后面content type是告诉浏览器返回的数据类型
            return HttpResponse("{'status':'success'}",content_type='application/json')
        else:
             # 如果保存失败，返回json字符串,并将form的报错信息通过msg传递到前端
            return HttpResponse("{'status':'fail'},{'msg':'添加出错'}",content_type='application/json')


'''机构首页'''
class OrgHomeView(View):
    def get(self,request,org_id):
        current_page = 'home'
        # 根据id找到课程机构
        course_org = CourseOrg.objects.get(id=int(org_id))
        # 反向查询课程机构的所有课程和老师
        all_courses = course_org.course_set.all()[:4]
        all_teacher = course_org.teacher_set.all()[:2]
        # 判断收藏状态
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        return render(request,'org-detail-homepage.html',{
            'course_org':course_org,'all_courses':all_courses,'all_teacher':all_teacher,'current_page':current_page
        })


'''机构课程列表页'''
class OrgCourseView(View):
    def get(self,request,org_id):
        current_page = 'course'
        # 根据id获取课程机构
        course_org = CourseOrg.objects.get(id=int(org_id))
        # 通过课程机构找到课程。内建的变量，找到指向这个字段的外检引用
        all_courses = course_org.course_set.all()
        # 判断收藏状态
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        return render(request,'org-detail-course.html',{
            'all_courses':all_courses,'course_org':course_org,'current_page':current_page
        })


'''机构介绍页'''
class OrgDescView(View):
    def get(self,request,org_id):
        current_page = 'desc'
        # 根据id获取课程机构
        course_org = CourseOrg.objects.get(id=int(org_id))
        # 判断收藏状态
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        return render(request,'org-detail-desc.html',{
            'course_org':course_org,'current_page':current_page
        })


'''机构教师页'''
class OrgTeacherView(View):
    def get(self,request,org_id):
        current_page = 'teacher'
        # 根据id获取课程机构
        course_org = CourseOrg.objects.get(id=int(org_id))
        all_teacher = course_org.teacher_set.all()
        # 判断收藏状态
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        return render(request,'org-detail-teachers.html',{
            'course_org':course_org,'current_page':current_page,'all_teacher':all_teacher
        })


'''用户收藏和取消收藏'''
class AddFavView(View):
    def post(self, request):
        id = request.POST.get('fav_id', 0)         # 防止后边int(fav_id)时出错
        type = request.POST.get('fav_type', 0)     # 防止int(fav_type)出错

        if not request.user.is_authenticated:
            # 未登录时返回json提示未登录，跳转到登录页面是在ajax中做的
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')

        exist_record = UserFavorite.objects.filter(user=request.user, fav_id=int(id), fav_type=int(type))
        if exist_record:
            # 如果记录已经存在，表示用户取消收藏
            exist_record.delete()
            if int(type) == 1:
                course = Course.objects.get(id=int(id))
                course.fav_nums -= 1
                if course.fav_nums < 0:
                    course.fav_nums = 0
                course.save()
            elif int(type) == 2:
                org = CourseOrg.objects.get(id=int(id))
                org.fav_nums -= 1
                if org.fav_nums < 0:
                    org.fav_nums = 0
                org.save()
            elif int(type) == 3:
                teacher = Teacher.objects.get(id=int(id))
                teacher.fav_nums -= 1
                if teacher.fav_nums < 0:
                    teacher.fav_nums = 0
                teacher.save()
            return HttpResponse('{"status":"success", "msg":"收藏"}', content_type='application/json')
        else:
            user_fav = UserFavorite()
            if int(type) > 0 and int(id) > 0:
                user_fav.fav_id = int(id)
                user_fav.fav_type = int(type)
                user_fav.user = request.user
                user_fav.save()

                if int(type) == 1:
                    course = Course.objects.get(id=int(id))
                    course.fav_nums += 1
                    course.save()
                elif int(type) == 2:
                    org = CourseOrg.objects.get(id=int(id))
                    org.fav_nums += 1
                    org.save()
                elif int(type) == 3:
                    teacher = Teacher.objects.get(id=int(id))
                    teacher.fav_nums += 1
                    teacher.save()
                return HttpResponse('{"status":"success", "msg":"已收藏"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"fail", "msg":"收藏出错"}', content_type='application/json')


        

