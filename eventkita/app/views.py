import random
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import  get_user_model, authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import now
from django.utils import timezone
from django.utils.timezone import localtime, localdate, make_aware, is_aware
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from .models import *
from .models import AdminMessage
from typing import cast
from .models import NewsletterSubscriber
from datetime import datetime
import locale
from .models import Event
import locale
from django.shortcuts import get_object_or_404, render
from .models import Event, SavedEvents

from django.contrib.auth.decorators import login_required

User = get_user_model()
searchStatus = 'not_empty'

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

    # Get the 5 most upcoming events
    banner_events = Event.objects.filter(tanggal_kegiatan__gte=today).order_by('tanggal_kegiatan')[:5]
        
    # Convert banner_events to JSON
    recent_events_json = json.dumps([
        {
            "id": str(event.id),  # Convert UUID to string
            "date": event.tanggal_kegiatan.strftime('%Y-%m-%d %H:%M:%S'),  # Format datetime
            "image": event.foto_event.url if event.foto_event else "",  # Handle empty image field
            "title": event.judul,  # Event title
            "description": event.deskripsi if event.deskripsi else "No description available."  # Handle empty description
        }
        for event in banner_events
    ])

    # Get upcoming events
    upcoming_events = Event.objects.filter(tanggal_kegiatan__gte=today).order_by('tanggal_kegiatan')

    # Limit to 4 events per category
    semua_event = {
        'konser': upcoming_events.filter(kategori='konser')[:4],
        'konferensi': upcoming_events.filter(kategori='konferensi')[:4],
        'bazaar': upcoming_events.filter(kategori='bazaar')[:4],
        'workshop': upcoming_events.filter(kategori='workshop')[:4],
    }

    
    big_events = Event.objects.filter(big_event=True, tanggal_kegiatan__gte=today).order_by('tanggal_kegiatan')


    context = {
        'semua_event': semua_event,
        'recent_events_json': recent_events_json,
        'big_events': big_events,  # Add big events to context
    }
    return render(request, 'index.html', context)


def detail_page(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    # Check if the user is authenticated
    if request.user.is_authenticated:
        isSaved = SavedEvents.objects.filter(user=request.user, event=event).exists()
    else:
        isSaved = False  # User is not logged in, so the event cannot be saved

    tickets = event.tiket.all() 

    # Set locale for currency formatting
    locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8') 

    # Format prices for each ticket
    formatted_tickets = []
    for ticket in tickets:
        formatted_price = locale.currency(ticket.harga, grouping=True)
        formatted_tickets.append({
            'ticket': ticket,
            'formatted_price': formatted_price
        })
    
    context = {
        'event': event,
        'tickets': formatted_tickets,  # Pass the formatted tickets to the template
        'isSaved': isSaved,
    }
    
    return render(request, 'detail_page.html', context)
    
def detail_page_free(request, id):
    event = get_object_or_404(Event, id=id, is_free=True)
    isSaved = SavedEvents.objects.filter(user=request.user, event=event).exists()  
    
    context = {'event': event, 'isSaved': isSaved,}

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
        otp_input = (
            request.POST.get('otp_code_1', '') +
            request.POST.get('otp_code_2', '') +
            request.POST.get('otp_code_3', '') +
            request.POST.get('otp_code_4', '')
        )

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
                    return redirect('reset')
                else:
                    messages.error(request, "Kode OTP sudah kadaluarsa.")
            else:
                messages.error(request, "Kode OTP salah.")
        else:
            messages.error(request, "Tidak ada kode OTP yang valid untuk user ini.")

    return render(request, 'verify.html')

def resend_otp_view(request):
    if request.method == 'POST':
        email = request.session.get('reset_email')
        User = get_user_model()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User  not found'}, status=404)

        otp_code = ''.join(str(random.randint(0, 9)) for _ in range(4))
        PasswordResetOTP.objects.create(user=user, otp_code=otp_code)

        subject = "Kode Reset Password Anda"
        message = f"Kode OTP Anda adalah: {otp_code}. Kode ini berlaku selama 5 menit."
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)

        return JsonResponse({'success': 'OTP has been sent'})

    return JsonResponse({'error': 'Invalid request'}, status=400)

def reset_view(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('forgot_password')

    if request.method == 'POST':
        password1 = request.POST.get('password1')  # Match the name in the HTML
        password2 = request.POST.get('password2')  # Match the name in the HTML

        if password1 != password2:
            messages.error(request, "Password dan konfirmasi tidak sama.")
            return redirect('reset_password')

        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "User  tidak ditemukan.")
            return redirect('forgot_password')

        user.set_password(password1)
        user.save()

        request.session['reset_email'] = None
        messages.success(request, "Password berhasil direset. Silakan login.")
        return redirect('login') 

    return render(request, 'reset.html')

def about_us(request):
    return render(request, 'about_us.html')

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if not name or not email or not message:
            messages.error(request, "Semua field harus diisi!")
            return redirect('contact_us')

        # Ambil pesan tambahan dari admin
        admin_message = AdminMessage.objects.last()  # Ambil pesan terbaru dari admin
        additional_message = admin_message.default_message if admin_message else "Terima kasih telah menghubungi kami!"

        subject = "Pesan Baru dari Formulir Kontak"
        message_body = f"""
        Halo {name},

        Kami telah menerima pesan Anda:
        ------------------------
        {message}
        ------------------------

        {additional_message}

        Salam,
        EventKita Team
        """

        try:
            send_mail(
                subject,
                message_body,
                settings.EMAIL_HOST_USER,  # Sender
                [email],  # Recipient (user yang mengisi form)
                fail_silently=False,
            )
            messages.success(request, "Pesan berhasil dikirim! Silakan cek email Anda.")
        except Exception as e:
            messages.error(request, f"Terjadi kesalahan: {str(e)}")

        return redirect('home')

    return render(request, 'index.html')

@login_required
def payment_1(request, tiket_id):
    tiket = get_object_or_404(Tiket, id=tiket_id)
    event = tiket.event_terkait

    locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8') 
    formatted_price_per_pax = locale.currency(tiket.harga, grouping=True)

    context = {
        'tiket': tiket,
        'event': event,
        'price_per_pax' : formatted_price_per_pax 
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
        messages.info(request, 'Selesaikan pembyaaran sebelum 10 menit!')
        return redirect('payment_2', purchase_id=purchase.id)
       
    return render(request, 'payment_1.html', context)


@login_required
def payment_2(request, purchase_id):
    purchase = get_object_or_404(EventPurchase, id=purchase_id)
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
    
    if request.method == "POST" and 'bukti_pembayaran' in request.FILES:
         # Check if there is enough stock
        if tiket.stock >= purchase.jumlah_tiket:
            # Update the purchase details
            purchase.bukti_pembayaran = request.FILES['bukti_pembayaran']
            purchase.status_pembelian = 'berhasil'
            purchase.save()

            # Reduce the stock of the ticket
            tiket.stock -= purchase.jumlah_tiket
            tiket.save()  # Save the updated ticket stock

            # Create a notification for the user
            notification_message = f"Pembayaran untuk {event.judul} - {tiket.judul} berhasil. Terima kasih telah melakukan pembayaran."
            Notification.objects.create(
                user=request.user,
                event=event,
                purchase=purchase,
                message=notification_message,
                link=f"http://127.0.0.1:8000/detailpage/payment1/payment2/payment3/{purchase.id}"
            )

            messages.success(request, 'Pembayaran Berhasil!')
            return redirect('payment_3', purchase_id=purchase.id)
        else:
            messages.error(request, 'Stok tiket tidak cukup untuk pemesanan ini.')
            return redirect('payment_2', purchase_id=purchase.id)

    # context = {'purchase': purchase}
    return render(request, 'payment_2.html', context)


@login_required
def batalkantransaksi(request, purchase_id):
    purchase = get_object_or_404(EventPurchase, id=purchase_id)
    
    if request.method == "POST":
        purchase.status_pembelian = 'gagal'
        purchase.save()
        messages.warning(request, "Pembelian tiket telah digagalkan!")

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
    if request.method != 'DELETE':
        return JsonResponse({'message': 'Method not allowed'}, status=405)
        
    user = request.user
    event = get_object_or_404(Event, id=event_id)

    saved_event = SavedEvents.objects.filter(user=user, event=event).first()
    if not saved_event:
        messages.error(request, "Acara tidak ditemukan di daftar saved!")
        return JsonResponse({'message': 'Event tidak ditemukan di daftar saved'}, status=404)

    saved_event.delete()
    messages.warning(request, "Acara telah dihapuskan dari daftar tersimpan!")
    return JsonResponse({'message': 'Event berhasil dihapus dari daftar saved'}, status=200)


@login_required
def save_event_view(request, event_id):
    """Menyimpan event ke dalam daftar saved user."""
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed'}, status=405)
        
    user = request.user
    event = get_object_or_404(Event, id=event_id)

    if SavedEvents.objects.filter(user=user, event=event).exists():
        messages.warning(request, "Acara sudah pernah ditambahkan ke daftar tersimpan!")
        return JsonResponse({'message': 'Event sudah disimpan sebelumnya'}, status=400)

    SavedEvents.objects.create(user=user, event=event)
    messages.success(request, "Acara telah ditambahkan ke daftar tersimpan!")
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

from django.http import JsonResponse

def subscribe_newsletter(request):
    if request.method == "POST":
        email = request.POST.get('email')

        if not email:
            return JsonResponse({'status': 'error', 'message': 'Email tidak boleh kosong!'})

        # Check if the email is already registered
        if NewsletterSubscriber.objects.filter(email=email).exists():
            return JsonResponse({'status': 'exists', 'message': 'Sudah terdaftarkan sebelumnya.'})

        # Save the email to the database
        subscriber = NewsletterSubscriber(email=email)
        subscriber.save()

        # Send email to the user
        subject = "Terima Kasih Telah Berlangganan EventKita 🎉"
        message_body = f"""
        Halo,

        Terima kasih telah bergabung dengan EventKita!
        Kami akan mengirimkan informasi event terbaru langsung ke email Anda.

        Jangan lewatkan berbagai acara menarik di BSD! 🎶✨

        Salam,
        Tim EventKita
        """

        try:
            send_mail(
                subject,
                message_body,
                settings.EMAIL_HOST_USER,  # Sender
                [email],  # Recipient
                fail_silently=False,
            )
            return JsonResponse({'status': 'success', 'message': 'Subscription successful! Thank you for joining.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Terjadi kesalahan: {str(e)}'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})

# def send_test_email():
#     subject = "Test Email from Django"
#     message = "Ini adalah email percobaan dari Django."
#     recipient_list = ["mimintheresa@gmail.com"]
#     send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

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
    """Menampilkan kalender event dengan semua event agar bisa berpindah bulan tanpa fetch ulang."""
    # Ambil **semua event** agar bisa berpindah bulan
    events = Event.objects.all().values('id', 'judul', 'tanggal_kegiatan')

    event_dict = {}
    for event in events:
        event_date = localtime(event['tanggal_kegiatan']).strftime("%Y-%m-%d")  # Pastikan waktu lokal
        event_id = str(event['id'])  # Konversi UUID ke string
        if event_date not in event_dict:
            event_dict[event_date] = []
        event_dict[event_date].append({
            'id': event_id,
            'judul': event['judul'],
            'tanggal_kegiatan': event_date
        })

    # Ambil event mendatang (upcoming events)
    upcoming_events = Event.objects.filter(tanggal_kegiatan__gte=timezone.now()).order_by('tanggal_kegiatan')

    context = {
        'events_json': json.dumps(event_dict),  # Kirim semua event
        'upcoming_events': upcoming_events,  # Tetap menampilkan event mendatang
    }

    return render(request, 'calendar.html', context)

def calendar_detail(request, date):
    """Menampilkan detail event pada tanggal tertentu"""
    try:
        # Konversi string ke datetime dan buat timezone-aware
        naive_date = datetime.strptime(date, "%Y-%m-%d")
        aware_date = make_aware(naive_date)
        selected_date = localdate(aware_date)

        # Ambil event hanya untuk tanggal yang dipilih
        events = Event.objects.filter(tanggal_kegiatan__date=selected_date)

        # Ambil semua event dan pastikan menggunakan timezone lokal
        all_events = Event.objects.all()
        events_json = json.dumps({
            localtime(event.tanggal_kegiatan).date().isoformat(): True
            for event in all_events
        })

        return render(request, 'calendar_detail.html', {
            'date': date,
            'events': events,
            'events_json': events_json
        })

    except ValueError as e:
        print(f"Error parsing date: {e}")
        return render(request, 'calendar_detail.html', {
            'date': date,
            'events': [],
            'events_json': "{}"
        })

# ini yg dari home page, masuk ke selengkapnya
def selengkapnya(request, category):
    today = timezone.now()
    upcoming_events = Event.objects.filter(tanggal_kegiatan__gte=today, kategori=category).order_by('tanggal_kegiatan')

    # Set a default value for new_category
    new_category = 'Unknown Event'  # Default value

    # Assign new_category based on the category
    if category == 'konser':
        new_category = 'Konser'
    elif category == 'konferensi':
        new_category = 'Konferensi'
    elif category == 'bazaar':
        new_category = 'Bazaar'
    elif category == 'workshop':
        new_category = 'Workshop'

    context = {
        'semua_event': upcoming_events,
        'category': new_category,
    }
    return render(request, 'selengkapnya.html', context)


def selengkapnya_bigevent(request):
    print("selengkapnya_bigevent function called")  # Debugging line
    today = timezone.now()
    print("Current date and time:", today)  # Debugging line

    # Fetch big events
    big_events = Event.objects.filter(big_event=True, tanggal_kegiatan__gte=today).order_by('tanggal_kegiatan')
    print("Big events fetched:", big_events)  # Debugging line

    # Set the category
    new_category = 'Event Besar'
    print("New category set to:", new_category)  # Debugging line

    # Prepare context
    context = {
        'semua_event': big_events,
        'category': new_category
    }
    return render(request, 'selengkapnya.html', context)


@login_required
def riwayattransaksi(request):
    user = request.user    
    
    purchases = EventPurchase.objects.filter(
        user=user
    ).exclude(
        status_pembelian='gagal'
    ).select_related('tiket__event_terkait').order_by('-created_at')

    context = {
        'purchases': purchases
    }
    return render(request, 'transactionHistory.html', context)

def syaratdanketentuan(request):
    return render(request, 'termsandcondition.html')

def search_page(request):
    category_choices = Event.CATEGORY_CHOICES
    today = timezone.now().date()
    events = Event.objects.all()
    events = events.filter(tanggal_kegiatan__gte=today)
    return render(request, 'search_page.html', {'category_choices': category_choices, 'events': events})

def search_events(request):
    category = request.GET.get('category', '')
    location = request.GET.get('location', '')
    date = request.GET.get('date', '')

    events = Event.objects.all()
    today = timezone.now().date()
    events = events.filter(tanggal_kegiatan__gte=today)

     # Get the 5 most upcoming events
    banner_events = Event.objects.filter(tanggal_kegiatan__gte=today).order_by('tanggal_kegiatan')[:5]
        
    # Convert banner_events to JSON
    recent_events_json = json.dumps([
        {
            "id": str(event.id),  # Convert UUID to string
            "date": event.tanggal_kegiatan.strftime('%Y-%m-%d %H:%M:%S'),  # Format datetime
            "image": event.foto_event.url if event.foto_event else "",  # Handle empty image field
            "title": event.judul,  # Event title
            "description": event.deskripsi if event.deskripsi else "No description available."  # Handle empty description
        }
        for event in banner_events
    ])


    if category:
        events = events.filter(kategori__icontains=category)
    if location:
        events = events.filter(lokasi__icontains=location) 
    if date: 
        try:
            selected_datetime = datetime.strptime(date, "%Y-%m-%d %H:%M")
            start_of_day = selected_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = selected_datetime.replace(hour=23, minute=59, second=59, microsecond=999999)
            events = events.filter(tanggal_kegiatan__range=(start_of_day, end_of_day))
        except ValueError:
            pass

    searchStatus = 'empty' if not events.exists() else 'not_empty'
    today = timezone.now()
    upcoming_events = Event.objects.filter(tanggal_kegiatan__gte=today).order_by('tanggal_kegiatan')

    semua_event = {
        'konser': upcoming_events.filter(kategori='konser')[:4],
        'konferensi': upcoming_events.filter(kategori='konferensi')[:4],
        'bazaar': upcoming_events.filter(kategori='bazaar')[:4],
        'workshop': upcoming_events.filter(kategori='workshop')[:4],
    }

    big_events = Event.objects.filter(big_event=True, tanggal_kegiatan__gte=today).order_by('tanggal_kegiatan')

    return render(request, 'index.html', {
        'events': events,
        'category_choices': Event.CATEGORY_CHOICES,
        'semua_event': semua_event,
        'searchStatus': searchStatus,
        'selected_category': category,
        'selected_location': location,
        'selected_date': date,
        'big_events': big_events,
        'recent_events_json': recent_events_json,
    })

def faq(request):
    return render(request, 'faq.html')