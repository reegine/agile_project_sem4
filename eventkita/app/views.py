from django.shortcuts import render, redirect
from django.contrib.auth import  get_user_model, authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from .models import *

User = get_user_model()

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login berhasil!")
            return redirect('home')
        else:
            messages.error(request, "Username atau password salah!")
            return redirect('login')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "Logout berhasil!")
    return redirect('home')

def register_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email sudah digunakan!")
            return redirect('register')

        user = User.objects.create_user(email=email, password=password)
        user.save()

        messages.success(request, "Akun berhasil dibuat! Silakan login.")
        return redirect('login')

    return render(request, 'register.html')

def home(request):
    return render(request, 'index.html')

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

def get_upcoming_events():
    # Get the current date and time
    now = timezone.now()
    # Fetch all events starting from now
    events = Event.objects.filter(tanggal_kegiatan__gte=now).order_by('tanggal_kegiatan')
    return events

def calendar(request):
    events = get_upcoming_events()  # Fetch upcoming events
    return render(request, 'calendar.html', {'events': events})

def get_events_for_date(date):
    # Convert the date string to a date object
    # Assuming date is in 'YYYY-MM-DD' format
    date_obj = timezone.datetime.strptime(date, '%Y-%m-%d').date()
    # Query the database for events on the given date
    events = Event.objects.filter(tanggal_kegiatan__date=date_obj)  # Use __date to filter by date
    return events

def calendar_detail(request, date):
    events = get_events_for_date(date)  # Fetch events for the specific date
    return render(request, 'calendar_detail.html', {'events': events, 'date': date})