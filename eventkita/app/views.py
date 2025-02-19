from django.shortcuts import render

def home(request):
    return render(request, 'index.html')

def login_view(request):
    return render(request, 'login.html')

def forgotpassword_view(request):
    return render(request, 'forgotpassword.html')

def verify_view(request):
    return render(request, 'verify.html')

def reset_view(request):
    return render(request, 'reset.html')

def about_us(request):
    return render(request, 'about_us.html')

def detail_page(request):
    return render(request, 'detail_page.html')

def detail_page_free(request):
    return render(request, 'detail_page_free.html')

def register_view(request):
    return render(request, 'register.html')

def finishsignup_view(request):
    return render(request, 'finishsignup.html')

def payment_1(request):
    return render(request, 'payment_1.html')

def payment_2(request):
    return render(request, 'payment_2.html')

def payment_3(request):
    return render(request, 'payment_3.html')

def profile_view(request):
    return render(request, 'profile.html')

def editprofile_view(request):
    return render(request, 'editprofile.html')

def saved_view(request):
    return render(request, 'saved.html')

def notifikasi(request):
    return render(request, 'notifikasi.html')
