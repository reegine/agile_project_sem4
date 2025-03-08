from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.files.base import ContentFile
from django.db import models
import uuid
from django.utils import timezone
from datetime import timedelta

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Membuat dan menyimpan user dengan email dan password.
        """
        if not email:
            raise ValueError('Email harus diisi')
        email = self.normalize_email(email)
        if 'username' not in extra_fields or not extra_fields['username']:
            extra_fields['username'] = email.split('@')[0]
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class AdminMessage(models.Model):
    subject = models.CharField(max_length=255)  # Judul pesan
    default_message = models.TextField()  # Pesan tambahan dari admin
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject
    
    def create_superuser(self, email, password, **extra_fields):
        """
        Membuat dan menyimpan superuser dengan email dan password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser harus memiliki is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser harus memiliki is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)  # Pastikan email tidak bisa duplikat
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    

    provinsi = models.CharField(max_length=100, blank=True, null=True)
    kota_kabupaten = models.CharField(max_length=100, blank=True, null=True)
    kode_pos = models.CharField(max_length=10, blank=True, null=True)
    alamat_lengkap = models.TextField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  

    objects = CustomUserManager()  

    def __str__(self):
        return self.email
    
class Event(models.Model):
    CATEGORY_CHOICES = [
        ('konser', 'Konser Musik'),
        ('konferensi', 'Konferensi'),
        ('bazaar', 'Bazaar'),
        ('workshop', 'Workshop'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    judul = models.CharField(max_length=255)
    deskripsi = models.TextField(blank=True, null=True)
    kategori = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    tanggal_kegiatan = models.DateTimeField(default=timezone.now)
    lokasi = models.CharField(max_length=255)
    foto_event = models.ImageField(upload_to='foto_event/', blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0, blank=True, null=True)
    is_free = models.BooleanField(default=False)
    additional_info = models.TextField(blank=True, null=True)

class Tiket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    judul = models.CharField(max_length=255)
    deskripsi = models.TextField(blank=True, null=True)
    harga = models.DecimalField(max_digits=20, decimal_places=2)
    stock = models.BigIntegerField(blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    event_terkait = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tiket')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

class EventPurchase(models.Model):
    STATUS_PEMBELIAN = [
        ('pending', 'Pending'),
        ('verifikasi', 'Menunggu Verifikasi'),
        ('berhasil', 'Berhasil'),
        ('gagal', 'Gagal'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='purchases')
    tiket = models.ForeignKey(Tiket, on_delete=models.CASCADE, related_name='purchases')
    status_pembelian = models.CharField(max_length=10, choices=STATUS_PEMBELIAN)
    bukti_pembayaran = models.ImageField(upload_to='bukti_pembayaran/', blank=True, null=True)
    # qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    jumlah_tiket = models.IntegerField(blank=True,null=True)

    # def generate_qr_code(self):
    #     qr_data = f"Order ID: {self.id}\nUser: {self.user.email}\nTiket: {self.tiket.judul}"
    #     qr = qrcode.make(qr_data)
    #     buffer = BytesIO()
    #     qr.save(buffer, format="PNG")
    #     self.qr_code.save(f"qr_{self.id}.png", ContentFile(buffer.getvalue()), save=False)


class SavedEvents(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='saved_events')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='saved_by_users')
    saved_at = models.DateTimeField(auto_now_add=True)

# class Review(models.Model):
#     RATING = [
#         (0, '☆☆☆☆☆ (0)'),
#         (1, '★☆☆☆☆ (1)'),
#         (2, '★★☆☆☆ (2)'),
#         (3, '★★★☆☆ (3)'),
#         (4, '★★★★☆ (4)'),
#         (5, '★★★★★ (5)'),
#     ]
    
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews')
#     event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reviews')
#     rating = models.IntegerField(choices=RATING)
#     komentar = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

class Footer(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    subscribe = models.BooleanField(default=True)

    def __str__(self):
        return self.email
    
class PasswordResetOTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return self.created_at + timedelta(minutes=5) < timezone.now()

    def __str__(self):
        return f"OTP for {self.user.email} - {self.otp_code}"
    
class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True) 
    purchase = models.ForeignKey(EventPurchase, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    link = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notif untuk {self.user.email} - {self.event.judul if self.event else 'No Event'}"
