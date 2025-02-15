from django.shortcuts import render

def home(request):
    return render(request, 'detail_page_free.html')

def login_view(request):
    return render(request, 'login.html')

def forgotpassword_view(request):
    return render(request, 'forgotpassword.html')

def verify_view(request):
    return render(request, 'verify.html')

def reset_view(request):
    return render(request, 'reset.html')
