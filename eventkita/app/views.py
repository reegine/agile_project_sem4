import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import  get_user_model, authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import now
from django.utils import timezone
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from .models import *
from typing import cast
import locale

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

@login_required
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

        request.session['temp_email'] = email

        messages.success(request, "Akun berhasil dibuat! Silakan lengkapi data Anda.")
        return redirect('finishsignup')

    return render(request, 'register.html')

def finishsignup_view(request):
    email = request.session.get('temp_email', None)
    if not email:
        messages.error(request, "Anda belum mendaftar atau sesi sudah berakhir.")
        return redirect('register')

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "User  tidak ditemukan.")
            return redirect('register')

        # Update user information
        user.first_name = first_name
        user.last_name = last_name
        user.phone_number = phone_number
        user.save()

        # Clear the session variable
        request.session.pop('temp_email', None)

        messages.success(request, "Data tambahan berhasil disimpan! Silakan login.")
        return redirect('login')

    return render(request, 'finishsignup.html')

# def home(request):
#     today = timezone.now()

#     upcoming_events = Event.objects.filter(tanggal_kegiatan__gte=today).order_by('tanggal_kegiatan')

#     semua_event = {
#         'konser': upcoming_events.filter(kategori='konser'),
#         'konferensi': upcoming_events.filter(kategori='konferensi'),
#         'bazaar': upcoming_events.filter(kategori='bazaar'),
#         'workshop': upcoming_events.filter(kategori='workshop'),
#     }

#     context = {
#         'semua_event': semua_event
#     }
#     return render(request, 'index.html', context)

def home(request):
    today = timezone.now()

    # Get upcoming events
    upcoming_events = Event.objects.filter(tanggal_kegiatan__gte=today).order_by('tanggal_kegiatan')

    # Limit to 4 events per category
    semua_event = {
        'konser': upcoming_events.filter(kategori='konser')[:4],
        'konferensi': upcoming_events.filter(kategori='konferensi')[:4],
        'bazaar': upcoming_events.filter(kategori='bazaar')[:4],
        'workshop': upcoming_events.filter(kategori='workshop')[:4],
    }

    context = {
        'semua_event': semua_event
    }
    return render(request, 'index.html', context)

def detail_page(request, event_id):
    event = get_object_or_404(Event, id=event_id, is_free=False)
    tickets = event.tiket.all() 

    context = {
        'event': event,
        'tickets': tickets
    }

    return render(request, 'detail_page.html', context)
    
def detail_page_free(request, id):
    event = get_object_or_404(Event, id=id, is_free=True)
    
    context = {'event': event}

    return render(request, 'detail_page_free.html', context)

def forgotpassword_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        User = get_user_model()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Email tidak terdaftar.")
            return redirect('forgot_password')  

        otp_code = ''.join(str(random.randint(0, 9)) for _ in range(4))

        PasswordResetOTP.objects.create(user=user, otp_code=otp_code)

        subject = "Kode Reset Password Anda"
        message = f"Kode OTP Anda adalah: {otp_code}. Kode ini berlaku selama 5 menit."
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)

        request.session['reset_email'] = email
        messages.success(request, "Kode OTP telah dikirim ke email Anda.")
        return redirect('verify') 

    return render(request, 'forgotpassword.html')


def verify_view(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('forgot_password')

    if request.method == 'POST':
        otp_input = request.POST.get('otp_code')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "User tidak ditemukan.")
            return redirect('forgot_password')

        otp_record = PasswordResetOTP.objects.filter(user=user, is_used=False).order_by('-created_at').first()

        if otp_record:
            if otp_record.otp_code == otp_input:
                if not otp_record.is_expired():
                    otp_record.is_used = True
                    otp_record.save()
                    return redirect('reset_password')
                else:
                    messages.error(request, "Kode OTP sudah kadaluarsa.")
            else:
                messages.error(request, "Kode OTP salah.")
        else:
            messages.error(request, "Tidak ada kode OTP yang valid untuk user ini.")

    return render(request, 'verify.html')


def reset_view(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('forgot_password')

    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Password dan konfirmasi tidak sama.")
            return redirect('reset_password')

        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "User tidak ditemukan.")
            return redirect('forgot_password')

        user.set_password(password1)
        user.save()

        request.session['reset_email'] = None
        messages.success(request, "Password berhasil direset. Silakan login.")
        return redirect('login') 

    return render(request, 'reset.html')

def about_us(request):
    return render(request, 'about_us.html')

@login_required
def payment_1(request, tiket_id):
    tiket = get_object_or_404(Tiket, id=tiket_id)
    event = tiket.event_terkait
    context = {
        'tiket': tiket,
        'event': event 
    }

    if request.method == "POST":
        ticket_quantity = request.POST.get('ticket_quantity')
        print('Jumlah Tiket:', ticket_quantity)  

        purchase = EventPurchase.objects.create(
            user=request.user,
            tiket=tiket,
            status_pembelian='pending',
            jumlah_tiket=ticket_quantity, 
        )
        return redirect('payment_2', purchase_id=purchase.id)

    
    return render(request, 'payment_1.html', context)


@login_required
def payment_2(request, purchase_id):
    purchase = get_object_or_404(EventPurchase, id=purchase_id)
    tiket = get_object_or_404(Tiket, id=purchase.tiket.id)
    event = tiket.event_terkait
    context = {
        'tiket': tiket,
        'event': event,
        'purchase': purchase
    }
    
    if request.method == "POST" and 'bukti_pembayaran' in request.FILES:
        purchase.bukti_pembayaran = request.FILES['bukti_pembayaran']
        purchase.status_pembelian = 'berhasil'
        purchase.save()
        return redirect('payment_3', purchase_id=purchase.id)

    # context = {'purchase': purchase}
    return render(request, 'payment_2.html', context)


@login_required
def batalkantransaksi(request, purchase_id):
    purchase = get_object_or_404(EventPurchase, id=purchase_id)
    
    if request.method == "POST" :
        purchase.status_pembelian = 'gagal'
        purchase.save()
        return redirect('home')

@login_required
def payment_3(request, purchase_id):
    purchase = get_object_or_404(EventPurchase, id=purchase_id, status_pembelian='berhasil')
    tiket = get_object_or_404(Tiket, id=purchase.tiket.id)
    event = tiket.event_terkait

    total_price = purchase.jumlah_tiket * tiket.harga if purchase.jumlah_tiket and tiket.harga else 0
    locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8') 
    formatted_total_price = locale.currency(total_price, grouping=True)

    context = {
        'tiket': tiket,
        'event': event,
        'purchase': purchase,
        'total_price': formatted_total_price,
    }
    return render(request, 'payment_3.html', context)

@login_required
def profile_view(request):
    user = request.user
    context = {
        'user': user
    }
    return render(request, 'profile.html', context)

@login_required
def editprofile_view(request):
    user = request.user  
    
    if request.method == 'POST':
        new_username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        provinsi = request.POST.get('provinsi')
        kota_kabupaten = request.POST.get('kota_kabupaten')
        kode_pos = request.POST.get('kode_pos')
        alamat_lengkap = request.POST.get('alamat_lengkap')
        new_password = request.POST.get('new_password')
        profile_picture = request.FILES.get('profile_picture')

        user.username = new_username
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.phone_number = phone_number
        user.provinsi = provinsi
        user.kota_kabupaten = kota_kabupaten
        user.kode_pos = kode_pos
        user.alamat_lengkap = alamat_lengkap

        if profile_picture:
            user.profile_picture = profile_picture

        if new_password:
            user.set_password(new_password)
            update_session_auth_hash(request, user)

        user.save()

        return redirect('profile')  
    
    return render(request, 'editprofile.html', {'user': user})

@login_required
def unsave_event_view(request, event_id):
    """Menghapus event dari daftar yang disimpan user."""
    user = request.user
    event = get_object_or_404(Event, id=event_id)

    saved_event = SavedEvents.objects.filter(user=user, event=event).first()
    if not saved_event:
        return JsonResponse({'message': 'Event tidak ditemukan di daftar saved'}, status=404)

    saved_event.delete()
    return JsonResponse({'message': 'Event berhasil dihapus dari daftar saved'}, status=200)

@login_required
def save_event_view(request, event_id):
    """Menyimpan event ke dalam daftar saved user."""
    user = request.user
    event = get_object_or_404(Event, id=event_id)

    if SavedEvents.objects.filter(user=user, event=event).exists():
        return JsonResponse({'message': 'Event sudah disimpan sebelumnya'}, status=400)

    SavedEvents.objects.create(user=user, event=event)
    return JsonResponse({'message': 'Event berhasil disimpan'}, status=201)

@login_required
def saved_view(request):
    """Menampilkan daftar event yang telah disimpan oleh user."""
    user = request.user
    saved_events = SavedEvents.objects.filter(user=user).select_related('event')

    return render(request, 'saved.html', {'saved_events': saved_events})

@login_required
def notifikasi(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifikasi.html', {'notifications': notifications})

@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'success': True})

def get_unread_notifications(request):
    if request.user.is_authenticated:
        return {'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count()}
    return {}

def subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            try:
                subscriber, created = Footer.objects.get_or_create(email=email)
                if created:
                    send_mail(
                        'Terima Kasih Telah Berlangganan',
                        'Anda telah berhasil berlangganan untuk menerima informasi terbaru.',
                        settings.EMAIL_HOST_USER,
                        [email],
                        fail_silently=False,
                    )
                else:
                    subscriber.subscribe = True
                    subscriber.save()
            except BadHeaderError:
                return HttpResponse("Header tidak valid.")
            except Exception as e:
                return HttpResponse(f"Terjadi kesalahan: {str(e)}")
    return render(request, 'footer.html')

def unsubscribe(request, email):
    subscriber = get_object_or_404(Footer, email=email)
    subscriber.subscribe = False  
    subscriber.save()
    return HttpResponse("Anda telah berhasil keluar dari daftar langganan.")

# send_mail(
#     'Subject here',
#     'Here is the message.',
#     'from@example.com',
#     ['to@example.com'],
#     fail_silently=False,
# )

def calendar(request):
    bulan = request.GET.get('bulan', timezone.now().month)
    tahun = request.GET.get('tahun', timezone.now().year)
    events = Event.objects.filter(
        tanggal_kegiatan__year=tahun,
        tanggal_kegiatan__month=bulan
    )

    today = timezone.now().date()
    one_month_later = today + timedelta(days=30)
    upcoming_events = Event.objects.filter(
        tanggal_kegiatan__range=[
            timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time())),
            timezone.make_aware(timezone.datetime.combine(one_month_later, timezone.datetime.min.time()))
        ]
    ).order_by('tanggal_kegiatan')

    context = {
        'events': events,
        'bulan': bulan,
        'tahun': tahun,
        'upcoming_events': upcoming_events
    }
    return render(request, 'calendar.html', context)

# def get_events_for_date(date):
#     # Convert the date string to a date object
#     # Assuming date is in 'YYYY-MM-DD' format
#     date_obj = timezone.datetime.strptime(date, '%Y-%m-%d').date()
#     # Query the database for events on the given date
#     events = Event.objects.filter(tanggal_kegiatan__date=date_obj) 
#     return events

def calendar_detail(request, date):
    events = Event.objects.filter(date=date)
    return render(request, 'calendar_detail.html', {'date': date, 'events': events})

# ini yg dari home page, masuk ke selengkapnya
def selengkapnya(request, category):
    today = timezone.now()
    upcoming_events = Event.objects.filter(tanggal_kegiatan__gte=today, kategori=category).order_by('tanggal_kegiatan')

    # Get upcoming events
    if category == 'konser' :
        new_category = 'Konser'
    elif category == 'konferensi' :
        new_category = 'Konferensi'
    elif category == 'bazaar' :
        new_category = 'Bazaar'
    elif category == 'workshop' :
        new_category = 'Workshop'

    context = {
        'semua_event': upcoming_events,
        'category' : new_category
    }
    return render(request, 'selengkapnya.html', context)

def riwayattransaksi(request, category):
    return render(request, 'transactionHistory.html')
