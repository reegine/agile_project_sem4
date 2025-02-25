# Generated by Django 5.1.6 on 2025-02-25 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_tiket_created_at_alter_event_tanggal_kegiatan_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventpurchase',
            name='bukti_pembayaran',
        ),
        migrations.RemoveField(
            model_name='eventpurchase',
            name='qr_code',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='event',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='is_read',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='link',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='purchase',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='user',
        ),
        migrations.RemoveField(
            model_name='tiket',
            name='created_at',
        ),
        migrations.AlterField(
            model_name='event',
            name='tanggal_kegiatan',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='eventpurchase',
            name='status_pembelian',
            field=models.CharField(choices=[('pending', 'Pending'), ('berhasil', 'Berhasil'), ('gagal', 'Gagal')], max_length=10),
        ),
    ]
