from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), 
    path('login/', views.login_view, name='login'),
    path('forgotpassword/', views.forgotpassword_view, name='forgotpassword'),
    path('verify/', views.verify_view, name='verify'),
    path('reset/', views.reset_view, name='reset'),
    path('aboutus/', views.about_us, name='about_us'), 
    path('detailpage/', views.detail_page, name='detail_page'), 
    path('detailpagefree/', views.detail_page_free, name='detail_page_free'), 
    path('register/', views.register_view, name='register'), 
    path('finishsignup/', views.finishsignup_view, name='finishsignup'), 
    path('detailpage/payment1/', views.payment_1, name='payment_1'), 
    path('profile/', views.profile_view, name='profile'),
    path('editprofile/', views.editprofile_view, name='editprofile'),  
    path('detailpage/payment1/payment2/', views.payment_2, name='payment_2'), 
    path('detailpage/payment1/payment2/payment3/', views.payment_3, name='payment_3'), 
    path('saved/', views.saved_view, name='saved'), 
    path('notifikasi/', views.notifikasi, name='notifikasi'), 
    path('calendar/', views.calendar, name='calendar'), 

]
