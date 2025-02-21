import csv
import uuid
import datetime
import logging

from django.core.management.base import BaseCommand
from django.utils import timezone
from app.models import Event  # Ganti 'your_app' dengan nama aplikasi Anda

# Setup logging untuk mencatat error (opsional)
logging.basicConfig(
    filename="import_events.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

class Command(BaseCommand):
    help = "Import events from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to the CSV file")

    def handle(self, *args, **kwargs):
        csv_file = kwargs["csv_file"]

        try:
            with open(csv_file, newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        # --- Validasi dan konversi UUID ---
                        try:
                            event_id = uuid.UUID(row["id"])
                        except ValueError:
                            self.stdout.write(self.style.WARNING(
                                f"Invalid UUID {row['id']} detected, generating new UUID."
                            ))
                            event_id = uuid.uuid4()

                        # --- Konversi tanggal ---
                        # Parsing tanggal dari CSV (contoh: "2025-03-15 19:00:00")
                        naive_dt = datetime.datetime.strptime(row["tanggal_kegiatan"], "%Y-%m-%d %H:%M:%S")
                        # Konversi menjadi timezone-aware dengan zona waktu yang aktif di settings
                        aware_dt = timezone.make_aware(naive_dt, timezone.get_current_timezone())

                        # --- Simpan data ke model Event ---
                        # Catatan: pastikan nama field yang digunakan sesuai dengan model.
                        # Misalnya, dalam model Event, field judul adalah "judul", deskripsi "deskripsi", dst.
                        event, created = Event.objects.update_or_create(
                            id=event_id,
                            defaults={
                                "judul": row["judul"],
                                "deskripsi": row["deskripsi"],
                                "kategori": row["kategori"],
                                "tanggal_kegiatan": aware_dt,
                                "lokasi": row["lokasi"],
                                "foto_event": row["foto_event"],  # Jika Anda hanya menyimpan nama file; pengaturan media perlu dipertimbangkan.
                                "rating": row["rating"],
                            },
                        )

                        if created:
                            self.stdout.write(self.style.SUCCESS(f"Successfully added event: {row['judul']}"))
                        else:
                            self.stdout.write(self.style.WARNING(f"Updated event: {row['judul']}"))

                    except Exception as e:
                        logging.error(f"Error processing event {row.get('judul', 'Unknown')}: {e}")
                        self.stdout.write(self.style.ERROR(f"Error processing event {row.get('judul', 'Unknown')}: {e}"))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File {csv_file} not found."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Unexpected error: {e}"))
