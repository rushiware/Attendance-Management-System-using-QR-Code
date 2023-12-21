from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signin/', views.signin, name='signin'),
    path('signin/reset-pass/', views.forgot_pass, name='fgtpass'),
    path('logout/', views.lg_out, name='logout'),
    path('sout/', views.sout, name='sout'),
    path('courses/get/<str:teacher_uid>/', views.courses, name='courses'),
    path('courses/view/<str:branch>/<str:yr>/<str:c_code>/', views.view_courses, name='view_courses'),
    path('lec/create/<str:branch>/<str:yr>/<str:c_code>/', views.lec_create, name='lec_create'),
    path('lec/view/<str:branch>/<str:yr>/<str:c_code>/', views.view_lec, name='view_lec'),
    path('lec/view/stud-att/<str:branch>/<str:yr>/<str:c_code>/', views.stud_att, name='stud_att'),
    path('lec/create/genQR/', views.genQR_url, name='gen_qr'),
    path('lec/ended/<str:branch>/<str:yr>/<str:c_code>/', views.lec_ended, name='lec_end'),
    path('users/students/', views.users_stud, name='users_stud'),
    path('users/faculty/', views.users_faculty, name='users_faculty'),
]