from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class CustomUser(AbstractUser):
    username = None 
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_set",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_set",
        blank=True
    )

    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = []  
    
    def __str__(self):
        return self.email
    
class Event(models.Model):
    CATEGORY_CHOICES = [
        ('concert', 'Konser Musik'),
        ('conference', 'Conference'),
        ('bazaar', 'Bazaar'),
        ('workshop', 'Workshop'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    judul = models.CharField(max_length=255)
    deskripsi = models.TextField(blank=True, null=True)
    kategori = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    tanggal_kegiatan = models.DateTimeField()
    lokasi = models.CharField(max_length=255)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)

class Tiket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    judul = models.CharField(max_length=255)
    deskripsi = models.TextField(blank=True, null=True)
    harga = models.DecimalField(max_digits=20, decimal_places=2)
    event_terkait = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')

class EventPurchase(models.Model):
    STATUS_PEMBELIAN = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='purchases')
    tiket = models.ForeignKey(Tiket, on_delete=models.CASCADE, related_name='purchases')
    status_pembelian = models.CharField(max_length=10, choices=STATUS_PEMBELIAN)
    created_at = models.DateTimeField(auto_now_add=True)

# class SavedEvents(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='saved_events')
#     event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='saved_by_users')
#     saved_at = models.DateTimeField(auto_now_add=True)

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
    