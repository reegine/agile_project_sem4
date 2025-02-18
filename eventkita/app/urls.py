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
    path('payment1/', views.payment_1, name='payment_1'), 

]
