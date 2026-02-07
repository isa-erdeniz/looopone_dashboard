# 🌿 Looopone Dashboard

**Akıllı Çöp Yönetim Sistemi** - Belediyeler için IoT tabanlı çöp konteyneri takip ve yönetim platformu

![Django](https://img.shields.io/badge/Django-4.2-green)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📋 Özellikler

### 🎯 Ana Özellikler
- ✅ **Gerçek Zamanlı İzleme** - Tüm konteynerlerin canlı doluluk takibi
- ✅ **İnteraktif Harita** - Google Maps entegrasyonu ile konum bazlı görünüm
- ✅ **Akıllı Uyarılar** - Dolu konteyner, düşük batarya ve arıza bildirimleri
- ✅ **Rota Optimizasyonu** - Çöp toplama rotalarının planlanması
- ✅ **Dashboard & Analytics** - Detaylı istatistikler ve raporlar
- ✅ **Mobil Uyumlu** - Responsive tasarım

### 📊 Dashboard Modülleri
1. **Ana Sayfa** - İstatistikler, uyarılar, günlük rotalar
2. **Harita Görünümü** - Konteynerlerin harita üzerinde görselleştirilmesi
3. **Konteyner Yönetimi** - Tüm konteynerlerin listesi ve detayları
4. **Rota Planlama** - Çöp toplama rotalarının yönetimi
5. **Uyarı Sistemi** - Aktif uyarıların takibi ve çözülmesi

---

## 🚀 Hızlı Başlangıç

### Gereksinimler
- Python 3.10+
- PostgreSQL (veya SQLite test için)
- pip & virtualenv

### 1. Kurulum

```bash
# Projeyi klonla veya indir
cd looopone_dashboard

# Virtual environment oluştur
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt
```

### 2. Django Projesini Kur

```bash
# Django projesi oluştur
django-admin startproject looopone_config .

# Core app oluştur
python manage.py startapp core

# models.py, views.py, urls.py dosyalarını core/ klasörüne kopyala
# templates/ klasörünü core/ içine kopyala
# admin.py dosyasını core/ içine kopyala
```

### 3. settings.py Ayarları

`looopone_config/settings.py` dosyasını düzenle:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',  # API için
    'core',  # Ana uygulama
]

# Templates ayarı
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'core' / 'templates'],
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

# Türkçe dil ayarları
LANGUAGE_CODE = 'tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

### 4. urls.py Ayarları

`looopone_config/urls.py` dosyasını düzenle:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]
```

### 5. Veritabanını Oluştur

```bash
# Migrations oluştur
python manage.py makemigrations

# Veritabanını oluştur
python manage.py migrate

# Demo verileri yükle
python manage.py shell < create_demo_data.py
```

### 6. Sunucuyu Başlat

```bash
python manage.py runserver
```

Tarayıcıda aç: **http://localhost:8000**

---

## 🔐 Giriş Bilgileri

Demo veriler yüklendikten sonra:

**Admin Paneli:**
- Kullanıcı: `admin`
- Şifre: `admin123`

**Sürücü Hesapları:**
- Kullanıcı: `surucu1` / `surucu2` / `surucu3`
- Şifre: `surucu123`

---

## 🗺️ Google Maps API Kurulumu

Harita özelliğini kullanmak için:

1. [Google Cloud Console](https://console.cloud.google.com/) giriş yap
2. Yeni proje oluştur
3. **Maps JavaScript API** etkinleştir
4. API Key oluştur
5. `templates/map.html` dosyasında `YOUR_GOOGLE_MAPS_API_KEY` yerine kendi key'ini yaz

```html
<script src="https://maps.googleapis.com/maps/api/js?key=BURAYA_API_KEY_YAZ&callback=initMap"></script>
```

---

## 📁 Proje Yapısı

```
looopone_dashboard/
│
├── core/                      # Ana uygulama
│   ├── models.py             # Veritabanı modelleri
│   ├── views.py              # Görünüm fonksiyonları
│   ├── urls.py               # URL yönlendirmeleri
│   ├── admin.py              # Admin panel ayarları
│   └── templates/            # HTML şablonları
│       ├── base.html         # Temel şablon
│       ├── login.html        # Giriş sayfası
│       ├── dashboard.html    # Ana dashboard
│       ├── map.html          # Harita görünümü
│       └── containers_list.html
│
├── looopone_config/          # Django ayarları
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── requirements.txt          # Python bağımlılıkları
├── create_demo_data.py       # Demo veri oluşturucu
└── README.md                 # Bu dosya
```

---

## 🎨 Ekran Görüntüleri

### Dashboard
- İstatistikler (Toplam konteyner, dolu konteyner, ortalama doluluk)
- Dikkat gerektiren konteynerler listesi
- Aktif uyarılar
- Bugünkü rotalar

### Harita Görünümü
- Tüm konteynerlerin harita üzerinde gösterimi
- Renk kodlu doluluk durumu (Yeşil: %0-50, Turuncu: %50-80, Kırmızı: %80+)
- Filtreler (Tip, Doluluk, Durum)
- Marker tıklamayla detay bilgileri

### Konteyner Detayları
- Doluluk grafiği
- Son uyarılar
- Toplama rotası geçmişi
- Sensör verileri (Sıcaklık, Batarya)

---

## 🛠️ Teknolojiler

- **Backend:** Django 4.2, Django REST Framework
- **Frontend:** Bootstrap 5, Font Awesome
- **Harita:** Google Maps JavaScript API
- **Veritabanı:** PostgreSQL (önerilir) / SQLite (geliştirme)
- **Deployment:** Gunicorn, WhiteNoise (static files)

---

## 📞 Belediye Sunumu İçin Notlar

### Demo Senaryosu
1. **Login** → Admin ile giriş yap
2. **Dashboard** → Genel durumu göster (X konteyner, Y dolu, Z uyarı)
3. **Harita** → Balçova haritası üzerinde konteynerleri göster
4. **Filtreler** → "Sadece %80+ dolu" filtresi uygula
5. **Konteyner Detayı** → Bir konteynere tıkla, detayları göster
6. **Uyarılar** → Aktif uyarıları göster ve birini "çözüldü" olarak işaretle
7. **Rotalar** → Bugünkü planlanmış rotaları göster

### Vurgulayacağın Özellikler
- ✅ **Maliyet Tasarrufu** - %30-40 yakıt tasarrufu (sadece dolu konteynerler toplanır)
- ✅ **Çevre Dostu** - Gereksiz araç trafiği azalır
- ✅ **7/24 İzleme** - Gerçek zamanlı takip
- ✅ **Vatandaş Memnuniyeti** - Taşan konteyner problemi ortadan kalkar
- ✅ **Raporlama** - Detaylı istatistikler ve analizler

### Fiyatlandırma Önerisi
- **Setup Fee:** Kurulum + Eğitim
- **Aylık/Yıllık Abonelik:** Konteyner sayısına göre
- **IoT Sensör Maliyeti:** Konteyner başına

---

## 📝 Sonraki Adımlar (Roadmap)

### Faz 1 - MVP (Tamamlandı ✅)
- Web dashboard
- Konteyner izleme
- Harita görünümü
- Temel uyarı sistemi

### Faz 2 - Mobil App (Yakında)
- Android & iOS uygulaması
- Saha görevlileri için mobil erişim
- Push notifications

### Faz 3 - AI & Analytics
- Makine öğrenmesi ile tahmin
- Rota optimizasyonu algoritmaları
- Detaylı raporlama

---

## 👨‍💻 Geliştirici

**ErdenizTech**
- Website: [erdeniztech.com](https://erdeniztech.com)
- Email: info@erdeniztech.com
- GitHub: [github.com/isa-erdeniz](https://github.com/isa-erdeniz)

---

## 📄 Lisans

MIT License - Ticari kullanım için iletişime geçiniz.

---

## 🤝 Destek

Sorular için:
- 📧 Email: info@erdeniztech.com
- 💬 GitHub Issues

**Başarılar! 🚀**
