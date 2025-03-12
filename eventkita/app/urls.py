from django.urls import path
from . import views
from .views import contact_view
from .views import subscribe_newsletter

urlpatterns = [
    path('', views.home, name='home'), 
    path('login/', views.login_view, name='login'),
    path('forgotpassword/', views.forgotpassword_view, name='forgotpassword'),
    path('verify/', views.verify_view, name='verify'),
    path('reset/', views.reset_view, name='reset'),
    path('aboutus/', views.about_us, name='about_us'), 
    path('subscribe/', subscribe_newsletter, name='subscribe_newsletter'),
    path('contact/', contact_view, name='contact_us'),
    path('detailpage/<uuid:event_id>', views.detail_page, name='detail_page'), 
    path('detailpagefree/<uuid:event_id>', views.detail_page_free, name='detail_page_free'), 
    path('register/', views.register_view, name='register'), 
    path('finishsignup/', views.finishsignup_view, name='finishsignup'), 
    path('detailpage/payment1/<uuid:tiket_id>', views.payment_1, name='payment_1'), 
    path('profile/', views.profile_view, name='profile'),
    path('editprofile/', views.editprofile_view, name='editprofile'),  
    path('detailpage/payment1/payment2/<uuid:purchase_id>', views.payment_2, name='payment_2'), 
    path('detailpage/payment1/payment2/payment3/<uuid:purchase_id>', views.payment_3, name='payment_3'), 
    path('saved/', views.saved_view, name='saved'), 
    path('save/<uuid:event_id>/', views.save_event_view, name='save_event'),
    path('unsave/<uuid:event_id>/', views.unsave_event_view, name='unsave_event'),
    path('notifikasi/', views.notifikasi, name='notifikasi'), 
    path('calendar/', views.calendar, name='calendar'), 
    path('calendar/detail/<str:date>/', views.calendar_detail, name='calendar_detail'),
    path('selengkapnya/<str:category>', views.selengkapnya, name='selengkapnya'), 
    path('riwayattransaksi/', views.riwayattransaksi, name='riwayattransaksi'),
    path('logout/', views.logout_view, name='logout'), 
    path('batalkantransaksi/<uuid:purchase_id>', views.batalkantransaksi, name='batalkantransaksi'), 
    path('notifikasi/mark/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('syaratdanketentuan/', views.syaratdanketentuan, name='syaratdanketentuan'), 
    path('resend-otp/', views.resend_otp_view, name='resend_otp'),
    path('pencarian/', views.search_page, name='pencarian'),
    path('search/', views.search_events, name='search_events'),
    path('faq/', views.faq, name='faq'), 
    path('selengkapnya/bigevents/', views.selengkapnya_bigevent, name='selengkapnya_bigevent'), 



]
