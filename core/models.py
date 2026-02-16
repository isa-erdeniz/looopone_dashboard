from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Container(models.Model):
    """Akıllı Çöp Konteynerleri"""
    
    CONTAINER_TYPES = [
        ('organic', 'Organik'),
        ('paper', 'Kağıt'),
        ('plastic', 'Plastik'),
        ('glass', 'Cam'),
        ('metal', 'Metal'),
        ('general', 'Genel'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Aktif'),
        ('maintenance', 'Bakımda'),
        ('damaged', 'Arızalı'),
        ('inactive', 'Pasif'),
    ]
    
    container_id = models.CharField(max_length=50, unique=True, verbose_name='Konteyner ID')
    container_type = models.CharField(max_length=20, choices=CONTAINER_TYPES, verbose_name='Konteyner Tipi')
    capacity = models.IntegerField(default=100, verbose_name='Kapasite (Litre)')
    fill_level = models.IntegerField(default=0, verbose_name='Doluluk Seviyesi (%)')
    
    # Lokasyon
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Enlem')
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Boylam')
    address = models.CharField(max_length=255, verbose_name='Adres')
    neighborhood = models.CharField(max_length=100, verbose_name='Mahalle')
    
    # Durum
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Durum')
    last_emptied = models.DateTimeField(null=True, blank=True, verbose_name='Son Boşaltma')
    last_updated = models.DateTimeField(auto_now=True, verbose_name='Son Güncelleme')
    
    # IoT Sensor Data
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Sıcaklık (°C)')
    battery_level = models.IntegerField(default=100, verbose_name='Batarya (%)')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma')
    # Vatandaş bildirimi için: HALK_PAZARI, MOLOZ, ROAD vb. (haritada ikon için)
    report_type = models.CharField(max_length=50, blank=True, null=True, verbose_name='Bildirim tipi')
    
    class Meta:
        verbose_name = 'Konteyner'
        verbose_name_plural = 'Konteynerler'
        ordering = ['-fill_level']
    
    def __str__(self):
        return f"{self.container_id} - {self.get_container_type_display()} ({self.fill_level}%)"
    
    @property
    def is_full(self):
        """Konteyner dolu mu?"""
        return self.fill_level >= 80
    
    @property
    def needs_attention(self):
        """Dikkat gerektiriyor mu?"""
        return self.fill_level >= 70 or self.status != 'active' or self.battery_level < 20


class CollectionRoute(models.Model):
    """Çöp Toplama Rotaları"""
    
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('in_progress', 'Devam Ediyor'),
        ('completed', 'Tamamlandı'),
        ('cancelled', 'İptal Edildi'),
    ]
    
    route_name = models.CharField(max_length=100, verbose_name='Rota Adı')
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Sürücü')
    vehicle_plate = models.CharField(max_length=20, verbose_name='Araç Plakası')
    
    containers = models.ManyToManyField(Container, verbose_name='Konteynerler')
    
    scheduled_date = models.DateTimeField(verbose_name='Planlanan Tarih')
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='Başlangıç')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Bitiş')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Durum')
    total_distance = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='Toplam Mesafe (km)')
    
    notes = models.TextField(blank=True, verbose_name='Notlar')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma')
    
    class Meta:
        verbose_name = 'Toplama Rotası'
        verbose_name_plural = 'Toplama Rotaları'
        ordering = ['-scheduled_date']
    
    def __str__(self):
        return f"{self.route_name} - {self.scheduled_date.strftime('%d/%m/%Y')}"
    
    @property
    def containers_count(self):
        return self.containers.count()


class Alert(models.Model):
    """Sistem Uyarıları"""
    
    ALERT_TYPES = [
        ('full', 'Konteyner Dolu'),
        ('maintenance', 'Bakım Gerekli'),
        ('damage', 'Arıza'),
        ('battery', 'Düşük Batarya'),
        ('temperature', 'Yüksek Sıcaklık'),
        ('offline', 'Bağlantı Kesildi'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Düşük'),
        ('medium', 'Orta'),
        ('high', 'Yüksek'),
        ('critical', 'Kritik'),
    ]
    
    container = models.ForeignKey(Container, on_delete=models.CASCADE, verbose_name='Konteyner')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES, verbose_name='Uyarı Tipi')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, verbose_name='Öncelik')
    
    message = models.TextField(verbose_name='Mesaj')
    is_resolved = models.BooleanField(default=False, verbose_name='Çözüldü')
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Çözen Kişi')
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name='Çözülme Zamanı')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma')
    
    class Meta:
        verbose_name = 'Uyarı'
        verbose_name_plural = 'Uyarılar'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.container.container_id}"
    
    def resolve(self, user):
        """Uyarıyı çöz"""
        self.is_resolved = True
        self.resolved_by = user
        self.resolved_at = timezone.now()
        self.save()


class Municipality(models.Model):
    """Belediye Bilgileri"""
    
    name = models.CharField(max_length=100, verbose_name='Belediye Adı')
    city = models.CharField(max_length=50, verbose_name='İl')
    district = models.CharField(max_length=50, verbose_name='İlçe')
    
    # İletişim
    address = models.TextField(verbose_name='Adres')
    phone = models.CharField(max_length=20, verbose_name='Telefon')
    email = models.EmailField(verbose_name='E-posta')
    
    # Koordinat (Merkez nokta)
    center_lat = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Merkez Enlem')
    center_lng = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Merkez Boylam')
    
    # Ayarlar
    alert_threshold = models.IntegerField(default=80, verbose_name='Uyarı Eşiği (%)')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma')
    
    class Meta:
        verbose_name = 'Belediye'
        verbose_name_plural = 'Belediyeler'
    
    def __str__(self):
        return f"{self.name} - {self.district}/{self.city}"
