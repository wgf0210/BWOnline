from django.urls import path,include,re_path
from django.views.generic.base import TemplateView
from apps.users.views import *
from apps.organization.views import OrgView
import xadmin
from .settings import MEDIA_ROOT,STATICFILES_DIRS
from django.views.static import serve

urlpatterns = [
    path('captcha/',include('captcha.urls')),
    
    path('xadmin/',xadmin.site.urls),
    
    path('login/',LoginView.as_view(),name='login'),
    path('logout/',LogoutView.as_view(),name='logout'),
    path('register/',RegisterView.as_view(),name='register'),
    path('forget/',ForgetPwdView.as_view(),name='forget_pwd'),
    re_path('active/(?P<active_code>.*)/',ActiveUserView.as_view(),name='user_active'),
    re_path('reset/(?P<active_code>.*)/',ResetView.as_view(),name='reset_pwd'),
    path('modify_pwd/',ModifyPwdView.as_view(),name='modify_pwd'),
    
    # path('org-list/',OrgView.as_view(),name='org-list'),
    path('org/',include('organization.urls',namespace='org')),
    
    path("course/", include('course.urls', namespace="course")),

    path("users/", include('users.urls', namespace="users")),
    
    path('', IndexView.as_view(),name='index'),
    # path('',TemplateView.as_view(template_name='index.html'),name='index'),

    # 处理图片的url
    re_path(r'^media/(?P<path>.*)',serve,{'document_root':MEDIA_ROOT}),
    # 静态文件（一旦debug改为false，django就不会代管你的静态文件，所以这里要设置一个url处理静态文件）
    re_path(r'^static/(?P<path>.*)',serve,{'document_root':STATICFILES_DIRS}),

    # 富文本编辑器url
    path('ueditor/',include('DjangoUeditor.urls' )),

    # url('^login/',LoginUnsafeView.as_view(),name='login'),
]


'''404和500,生成环境汇总，必须设置debug = False'''
# 全局404页面配置
handler404 = 'users.views.pag_not_found'
# 全局500页面配置
handler500 = 'users.views.page_error'
