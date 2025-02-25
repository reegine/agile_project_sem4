from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import EventPurchase, Notification

@receiver(post_save, sender=EventPurchase)
def create_notification_on_purchase(sender, instance, created, **kwargs):
    if created and instance.status_pembelian == "berhasil":
        instance.generate_qr_code()
        instance.save()

        Notification.objects.create(
            user=instance.user,
            event=instance.tiket.event_terkait,  
            purchase=instance,
            message=f"Pesanan tiket '{instance.tiket.judul}' berhasil dibeli!",
            link=f"/event/history/"
        )
