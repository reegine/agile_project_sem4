from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
from .models import AdminMessage
from .models import NewsletterSubscriber
# ============================
# Admin untuk CustomUser
# ============================
class CustomUserAdmin(UserAdmin):
    # Menyesuaikan fieldsets untuk CustomUser
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'first_name', 'last_name', 'phone_number', 'profile_picture')}),
        ('Address', {'fields': ('provinsi', 'kota_kabupaten', 'kode_pos', 'alamat_lengkap')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    # Kolom yang akan ditampilkan di list view
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    # Filter di sidebar admin
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    # Menambahkan pencarian berdasarkan email dan nama
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    # Jika username tidak ingin diedit melalui admin, bisa dijadikan read-only
    readonly_fields = ('username',)


#FOOTER KEKNYA #Buat masukkin ke dalam adminnya
admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')  # Menampilkan email & waktu daftar
    search_fields = ('email',)

# ============================
# Admin untuk Event
# ============================
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('judul', 'kategori', 'tanggal_kegiatan', 'lokasi', 'rating', 'foto_event', 'big_event')
    list_filter = ('kategori', 'tanggal_kegiatan')
    search_fields = ('judul', 'deskripsi', 'lokasi')
    ordering = ('-tanggal_kegiatan',)


# ============================
# Admin untuk Tiket
# ============================
@admin.register(Tiket)
class TiketAdmin(admin.ModelAdmin):
    list_display = ('judul', 'event_terkait', 'harga', 'date', 'stock')
    list_filter = ('event_terkait',)
    search_fields = ('judul', 'deskripsi')
    ordering = ('event_terkait', 'judul')


# ============================
# Admin untuk EventPurchase
# ============================
@admin.register(EventPurchase)
class EventPurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'tiket', 'status_pembelian', 'created_at')
    list_filter = ('status_pembelian', 'created_at')
    search_fields = ('user__email', 'tiket__judul')
    autocomplete_fields = ('user', 'tiket')

# ============================
# Admin untuk SavedEvents
# ============================
@admin.register(SavedEvents)
class SavedEventsAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'saved_at')
    list_filter = ('saved_at',)
    search_fields = ('user__email', 'event__judul')
    ordering = ('-saved_at',)


# ============================
# Admin untuk Footer
# ============================
@admin.register(Footer)
class FooterAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribe', 'created_at')
    list_filter = ('subscribe', 'created_at')
    search_fields = ('email',)
    ordering = ('-created_at',)

# ============================
# Admin untuk PasswordResetOTP
# ============================
@admin.register(PasswordResetOTP)
class PasswordResetOTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp_code', 'is_used', 'created_at')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__email', 'otp_code')
    ordering = ('-created_at',)


# ============================
# Admin untuk Notification
# ============================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'purchase', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__email', 'message')
    ordering = ('-created_at',)

@admin.register(AdminMessage)
class AdminMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'created_at')  # Menampilkan kolom di admin
    search_fields = ('subject',)