from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser,
    Event,
    Tiket,
    EventPurchase,
    SavedEvents,
    # Review,  # jika nanti aktifkan model Review
    Footer,
)

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

admin.site.register(CustomUser, CustomUserAdmin)


# ============================
# Admin untuk Event
# ============================
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('judul', 'kategori', 'tanggal_kegiatan', 'lokasi', 'rating')
    list_filter = ('kategori', 'tanggal_kegiatan')
    search_fields = ('judul', 'deskripsi', 'lokasi')
    ordering = ('-tanggal_kegiatan',)


# ============================
# Admin untuk Tiket
# ============================
@admin.register(Tiket)
class TiketAdmin(admin.ModelAdmin):
    list_display = ('judul', 'event_terkait', 'harga')
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
    ordering = ('-created_at',)


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
