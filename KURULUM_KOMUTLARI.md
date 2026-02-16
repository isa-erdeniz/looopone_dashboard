# Looopone Dashboard – Terminal Komutları (Sırayla)

Aşağıdaki komutları **proje kökünde** (`looopone_dashboard` klasöründe) çalıştır.  
Mac/Linux için; Windows’ta `source venv/bin/activate` yerine `venv\Scripts\activate` kullan.

---

## ADIM 1: Python ve pip

```bash
python --version
pip install --upgrade pip
```

---

## ADIM 2: Proje klasörü ve sanal ortam

```bash
cd looopone_dashboard
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

*(Zaten `looopone_dashboard` içindeysen sadece `cd` satırını atla. Projede `env` kullanıyorsan: `source env/bin/activate`)*

---

## ADIM 3: Django projesi (sıfırdan kurulum için)

*Proje zaten kuruluysa bu adımı atla.*

```bash
django-admin startproject looopone_config .
python manage.py startapp core
```

**Sonrasında elle yapılacaklar:**  
- `looopone_config/settings.py`: INSTALLED_APPS’e `'core'`, TEMPLATES DIRS’a `BASE_DIR / 'core' / 'templates'`  
- `looopone_config/urls.py`: `path('', include('core.urls'))` ekle

---

## ADIM 4: Veritabanı

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## ADIM 5: Demo veriler

*(Komut zaten `core/management/commands/` altındaysa sadece aşağıdaki satırı çalıştır.)*

```bash
python manage.py create_demo_data
```

*(İlk kez kurulumda komut dosyası proje kökündeyse ve taşımadıysan:)*

```bash
mkdir -p core/management/commands
touch core/management/__init__.py
touch core/management/commands/__init__.py
mv create_demo_data.py core/management/commands/
python manage.py create_demo_data
```

---

## ADIM 6: Sunucuyu başlat

```bash
python manage.py runserver
```

Tarayıcıda: **http://localhost:8000**  
Giriş: **admin** / **admin123**

---

## Sorun giderme

**Port meşgulse:**

```bash
python manage.py runserver 8001
```

**Windows’ta 8000 portunu kapatmak için:**

```bash
netstat -ano | findstr :8000
taskkill /PID <PID_NUMARASI> /F
```
