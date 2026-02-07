# 🚀 LOOOPONE DASHBOARD - HIZLI KURULUM REHBERİ

## ⚡ 30 DAKİKADA ÇALIŞIR HALE GETİR

### 📋 ADIM 1: Gerekli Yazılımları Yükle (5 dakika)

```bash
# Python 3.10+ yüklü olduğundan emin ol
python --version

# pip güncellemesi
pip install --upgrade pip
```

---

### 📂 ADIM 2: Proje Klasörünü Hazırla (2 dakika)

```bash
# looopone_dashboard klasörüne git
cd looopone_dashboard

# Virtual environment oluştur
python -m venv venv

# Virtual environment'ı aktif et
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Paketleri yükle
pip install -r requirements.txt
```

---

### 🏗️ ADIM 3: Django Projesini Kur (5 dakika)

```bash
# Django projesi oluştur
django-admin startproject looopone_config .

# Core app oluştur
python manage.py startapp core

# Dosyaları taşı
# models.py, views.py, urls.py, admin.py dosyalarını core/ klasörüne kopyala
# templates/ klasörünü core/ içine kopyala
```

**looopone_config/settings.py dosyasını düzenle:**

```python
# INSTALLED_APPS'e ekle:
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'core',  # Bunu ekle
]

# TEMPLATES ayarı:
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'core' / 'templates'],  # Bunu değiştir
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Dil ayarları:
LANGUAGE_CODE = 'tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

**looopone_config/urls.py dosyasını düzenle:**

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # Bunu ekle
]
```

---

### 🗄️ ADIM 4: Veritabanını Oluştur (3 dakika)

```bash
# Migrations oluştur
python manage.py makemigrations

# Veritabanını oluştur
python manage.py migrate
```

---

### 🎭 ADIM 5: Demo Verileri Yükle (5 dakika)

**create_demo_data.py dosyasını Django management command'a dönüştür:**

```bash
# core/management/commands/ klasörünü oluştur
mkdir -p core/management/commands

# __init__.py dosyalarını oluştur
touch core/management/__init__.py
touch core/management/commands/__init__.py

# create_demo_data.py dosyasını core/management/commands/ içine taşı
mv create_demo_data.py core/management/commands/
```

**Sonra çalıştır:**

```bash
python manage.py create_demo_data
```

**ÇIKTI BÖYLE OLMALI:**
```
Demo veriler oluşturuluyor...
✓ Superuser oluşturuldu (admin/admin123)
✓ Belediye bilgisi oluşturuldu
✓ 35 konteyner oluşturuldu
✓ 3 sürücü kullanıcısı oluşturuldu
✓ 5 örnek rota oluşturuldu

==================================================
DEMO VERİLER BAŞARIYLA OLUŞTURULDU!
==================================================
Konteynerler: 35
Aktif Uyarılar: 8
Rotalar: 5

Giriş Bilgileri:
  Admin: admin / admin123
  Sürücü: surucu1 / surucu123

Dashboard URL: http://localhost:8000/dashboard/
```

---

### 🚀 ADIM 6: Sunucuyu Başlat (1 dakika)

```bash
python manage.py runserver
```

**Tarayıcıda aç:** http://localhost:8000

**Giriş yap:** admin / admin123

---

## 🗺️ GOOGLE MAPS API KURULUMU (Opsiyonel - 10 dakika)

### 1. Google Cloud Console'a Git
https://console.cloud.google.com/

### 2. Yeni Proje Oluştur
- "New Project" tıkla
- İsim: "Looopone Maps"
- Create

### 3. Maps JavaScript API'yi Aktif Et
- APIs & Services → Library
- "Maps JavaScript API" ara
- Enable tıkla

### 4. API Key Oluştur
- Credentials → Create Credentials → API Key
- Key'i kopyala

### 5. Template'lere Ekle

**core/templates/map.html** ve **core/templates/container_detail.html** dosyalarında:

```html
<!-- Eski satırı bul: -->
<script src="https://maps.googleapis.com/maps/api/js?key=YOUR_GOOGLE_MAPS_API_KEY&callback=initMap"></script>

<!-- Yeni haliyle değiştir: -->
<script src="https://maps.googleapis.com/maps/api/js?key=BURAYA_SENIN_API_KEY_YAPISIR&callback=initMap"></script>
```

---

## ✅ TEST ET - 5 DAKİKA

### Dashboard Test
1. http://localhost:8000 → Login yap
2. Dashboard'u gör → İstatistikler görünüyor mu?
3. Harita'ya tıkla → Konteynerler görünüyor mu?
4. Bir konteynere tıkla → Detaylar açılıyor mu?

### Demo Senaryosu
1. **Login:** admin / admin123
2. **Dashboard:** 35 konteyner, ~5 dolu, ~8 uyarı görmeli
3. **Harita:** Balçova'da konteynerleri görmeli (Google Maps API varsa)
4. **Filtre:** "%80+ dolu" filtresi uygula
5. **Konteyner Detay:** Bir konteyner seç, detayları gör
6. **Uyarılar:** Uyarılar sayfasına git, bir uyarıyı çöz
7. **Rotalar:** Bugünkü rotaları gör

---

## 🎯 BELEDİYE SUNUMU İÇİN HAZIRLIK

### Sunum Öncesi Checklist
- [ ] Sunucu çalışıyor (python manage.py runserver)
- [ ] Demo veriler yüklü
- [ ] Google Maps API çalışıyor (eğer varsa)
- [ ] Tarayıcıda tam ekran mod (F11)
- [ ] Giriş yapılmış (admin/admin123)

### Sunum Akışı (7 Dakika)
1. **[1 dk]** Login → Dashboard genel bakış
2. **[2 dk]** Harita → Balçova'daki konteynerler, filtreler
3. **[1 dk]** Konteyner detayı → Doluluk, batarya, sensörler
4. **[1 dk]** Uyarılar → Dolu konteyner uyarısı, çözme
5. **[1 dk]** Rotalar → Bugünkü planlanan rotalar
6. **[1 dk]** Soru-cevap

---

## 🆘 SORUN GIDERME

### "Port already in use" Hatası
```bash
# Çözüm 1: Başka port kullan
python manage.py runserver 8001

# Çözüm 2: Windows'ta port'u öldür
netstat -ano | findstr :8000
taskkill /PID [PID_NUMARASI] /F
```

### "No module named 'core'" Hatası
```bash
# core app'inin settings.py'de INSTALLED_APPS'te olduğundan emin ol
```

### Template Bulunamıyor Hatası
```bash
# settings.py'de TEMPLATES → DIRS ayarını kontrol et
'DIRS': [BASE_DIR / 'core' / 'templates'],
```

### Harita Görünmüyor
```bash
# Google Maps API key'i doğru mu?
# map.html ve container_detail.html'de key güncellendi mi?
```

---

## 📞 DESTEK

**Sorularınız için:**
- Email: info@erdeniztech.com
- GitHub: github.com/isa-erdeniz/erdeniztech

---

## 🎉 BAŞARILI!

Artık Looopone Dashboard çalışıyor. Belediye sunumunda başarılar! 🚀
