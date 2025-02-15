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