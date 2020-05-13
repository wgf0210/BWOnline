from django.urls import path,re_path,include
from .views import *


app_name = 'users'

urlpatterns = [
    path('info/',UserinfoView.as_view(),name='user_info'),
    path("image/upload", UploadImageView.as_view(),name='image_upload'),
    path("update/pwd/", UpdatePwdView.as_view(),name='update_pwd'),
    path("sendemail_code/", SendEmailCodeView.as_view(),name='sendemail_code'),
    path("update_email/", UpdateEmailView.as_view(),name='update_email'),
    path("mycourse/", MyCourseView.as_view(),name='mycourse'),
    path("myfav/org/", MyFavOrgView.as_view(),name='myfav_org'),     # 我的收藏，课程机构
    path("myfav/teacher/", MyFavTeacherView.as_view(),name='myfav_teacher'),     # 我的收藏，授课讲师
    path("myfav/course/", MyFavCourseView.as_view(),name='myfav_course'),     # 我的收藏，课程
    path("my_message/", MyMessageView.as_view(),name='my_message'),     # 我的消息 
]