from django.shortcuts import render

def home(request):
    return render(request, 'detail_page_free.html')