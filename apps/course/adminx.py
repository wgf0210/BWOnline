import xadmin
from .models import *

# 管理器
class CourseAdmin(object):
    # 课程
    list_display = [ 'name','desc','detail','degree','learn_times','students']   #显示的字段
    search_fields = ['name', 'desc', 'detail', 'degree', 'students']             #搜索
    list_filter = [ 'name','desc','detail','degree','learn_times','students']    #过滤 
    model_icon = 'fa fa-book'            #图标
    ordering = ['-click_nums']           #排序
    readonly_fields = ['click_nums']     #只读字段，不能编辑
    exclude = ['fav_nums']               #不显示的字段
    def queryset(self):
        # 重载queryset方法，来过滤出我们想要的数据的
        qs = super(CourseAdmin, self).queryset()
        # 只显示is_banner=True的课程
        qs = qs.filter(is_banner=False)
        return qs

'''轮播课程'''
class BannerCourseAdmin(object):
    list_display = [ 'name','desc','detail','degree','learn_times','students']
    search_fields = ['name', 'desc', 'detail', 'degree', 'students']
    list_filter = [ 'name','desc','detail','degree','learn_times','students']
    model_icon = 'fa fa-book'
    ordering = ['-click_nums']
    readonly_fields = ['click_nums']
    exclude = ['fav_nums']

    def queryset(self):
        #重载queryset方法，来过滤出我们想要的数据的
        qs = super(BannerCourseAdmin, self).queryset()
        #只显示is_banner=True的课程
        qs = qs.filter(is_banner=True)
        return qs


class LessonAdmin(object):
    # 章节
    list_display = ['course','name','add_time']
    search_fields = ['course','name']
    list_filter = ['course__name','name','add_time']


class VideoAdmin(object):
    list_display = ['lesson','name','add_time']
    search_fields = ['lesson','name']
    list_filter = ['lesson__name','name','add_time']


class CourseResourceAdmin(object):
    list_display = ['course','name','download','add_time']
    search_fields = ['course','name','download']
    list_filter = ['course__name','name','download','add_time']


# 将管理器与model进行注册关联
xadmin.site.register(Course,CourseAdmin)
xadmin.site.register(BannerCourse, BannerCourseAdmin)
xadmin.site.register(Lesson,LessonAdmin)
xadmin.site.register(Video,VideoAdmin)
xadmin.site.register(CourseResource,CourseResourceAdmin)


