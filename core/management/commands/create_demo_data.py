"""
Demo Data Generator for Looopone Dashboard
Balçova, İzmir için örnek konteyner verileri oluşturur
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Container, Municipality, Alert, CollectionRoute
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Looopone için demo verileri oluştur'

    def handle(self, *args, **kwargs):
        self.stdout.write('Demo veriler oluşturuluyor...\n')
        
        # 1. Superuser oluştur (eğer yoksa)
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@looopone.com',
                password='admin123',
                first_name='Admin',
                last_name='Looopone'
            )
            self.stdout.write(self.style.SUCCESS('✓ Superuser oluşturuldu (admin/admin123)'))
        
        # 2. Belediye bilgisi oluştur
        municipality, created = Municipality.objects.get_or_create(
            name='Balçova Belediyesi',
            defaults={
                'city': 'İzmir',
                'district': 'Balçova',
                'address': 'Şair Eşref Bulvarı No:11, 35330 Balçova/İzmir',
                'phone': '0232 259 00 00',
                'email': 'bilgi@balcova.bel.tr',
                'center_lat': 38.3692,
                'center_lng': 27.0468,
                'alert_threshold': 80,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Belediye bilgisi oluşturuldu'))
        
        # 3. Balçova mahalleleri ve konteynerleri
        neighborhoods = [
            {'name': 'İnciraltı', 'lat': 38.3862, 'lng': 27.0374},
            {'name': 'Alaybey', 'lat': 38.3692, 'lng': 27.0468},
            {'name': 'Onur', 'lat': 38.3801, 'lng': 27.0603},
            {'name': 'Teleferik', 'lat': 38.3584, 'lng': 27.0391},
            {'name': 'Mithatpaşa', 'lat': 38.3726, 'lng': 27.0542},
        ]
        
        container_types = ['organic', 'paper', 'plastic', 'glass', 'metal', 'general']
        addresses = [
            'Cumhuriyet Caddesi',
            'Atatürk Bulvarı',
            'İnönü Caddesi',
            'Gazi Mustafa Kemal Bulvarı',
            'Mithatpaşa Caddesi',
            'Tevfik Bey Caddesi',
            'Şair Eşref Bulvarı',
        ]
        
        container_count = 0
        for neighborhood in neighborhoods:
            # Her mahallede 6-8 konteyner
            num_containers = random.randint(6, 8)
            for i in range(num_containers):
                lat_offset = random.uniform(-0.005, 0.005)
                lng_offset = random.uniform(-0.005, 0.005)
                
                container_id = f"BLV-{neighborhood['name'][:3].upper()}-{container_count + 1:03d}"
                
                # Realistic doluluk değerleri - çoğu normal, birkaçı dolu
                if random.random() < 0.15:  # %15 ihtimalle yüksek doluluk
                    fill_level = random.randint(75, 95)
                elif random.random() < 0.3:  # %30 ihtimalle orta doluluk
                    fill_level = random.randint(50, 74)
                else:  # Geri kalanı düşük doluluk
                    fill_level = random.randint(10, 49)
                
                status = 'active'
                if random.random() < 0.05:  # %5 ihtimalle bakımda
                    status = 'maintenance'
                elif random.random() < 0.02:  # %2 ihtimalle arızalı
                    status = 'damaged'
                
                container = Container.objects.create(
                    container_id=container_id,
                    container_type=random.choice(container_types),
                    capacity=random.choice([240, 360, 660, 1100]),
                    fill_level=fill_level,
                    latitude=neighborhood['lat'] + lat_offset,
                    longitude=neighborhood['lng'] + lng_offset,
                    address=f"{random.choice(addresses)} No:{random.randint(1, 150)}",
                    neighborhood=neighborhood['name'],
                    status=status,
                    last_emptied=timezone.now() - timedelta(days=random.randint(1, 7)),
                    temperature=random.uniform(15, 35),
                    battery_level=random.randint(60, 100) if status == 'active' else random.randint(10, 40)
                )
                
                container_count += 1
                
                # Dolu konteynerler için uyarı oluştur
                if fill_level >= 80 and status == 'active':
                    Alert.objects.create(
                        container=container,
                        alert_type='full',
                        priority='high' if fill_level >= 90 else 'medium',
                        message=f"{container_id} konteyneri %{fill_level} dolu - boşaltılması gerekiyor"
                    )
                
                # Bakım/arıza durumları için uyarı
                if status == 'maintenance':
                    Alert.objects.create(
                        container=container,
                        alert_type='maintenance',
                        priority='medium',
                        message=f"{container_id} konteyneri bakım gerektiriyor"
                    )
                elif status == 'damaged':
                    Alert.objects.create(
                        container=container,
                        alert_type='damage',
                        priority='critical',
                        message=f"{container_id} konteyneri arızalı - acil müdahale gerekli"
                    )
                
                # Düşük batarya uyarıları
                if container.battery_level < 20:
                    Alert.objects.create(
                        container=container,
                        alert_type='battery',
                        priority='high',
                        message=f"{container_id} batarya seviyesi kritik - %{container.battery_level}"
                    )
        
        self.stdout.write(self.style.SUCCESS(f'✓ {container_count} konteyner oluşturuldu'))
        
        # 4. Sürücü kullanıcıları oluştur (yoksa ekle, varsa listeye al)
        drivers = list(User.objects.filter(username__in=['surucu1', 'surucu2', 'surucu3']))
        for i in range(3):
            username = f"surucu{i+1}"
            if not User.objects.filter(username=username).exists():
                driver = User.objects.create_user(
                    username=username,
                    password='surucu123',
                    first_name=f'Sürücü {i+1}',
                    last_name='Looopone'
                )
                drivers.append(driver)
        
        self.stdout.write(self.style.SUCCESS('✓ 3 sürücü kullanıcısı oluşturuldu'))
        
        # 5. Örnek rotalar oluştur
        vehicles = ['35 ABC 123', '35 DEF 456', '35 GHI 789']
        
        for i in range(5):
            route_date = timezone.now() + timedelta(days=i-2)  # 2 gün önce, bugün, 2 gün sonra
            
            # Her rota için 5-10 rastgele konteyner seç
            route_containers = Container.objects.filter(status='active').order_by('?')[:random.randint(5, 10)]
            
            if drivers and route_containers.exists():
                route = CollectionRoute.objects.create(
                    route_name=f"Rota {neighborhoods[i % len(neighborhoods)]['name']} - {route_date.strftime('%d/%m')}",
                    driver=random.choice(drivers),
                    vehicle_plate=random.choice(vehicles),
                    scheduled_date=route_date.replace(hour=random.randint(8, 16), minute=0),
                    status='completed' if i < 2 else ('in_progress' if i == 2 else 'pending'),
                    total_distance=random.uniform(5.5, 15.8)
                )
                route.containers.set(route_containers)
                
                if route.status == 'completed':
                    route.started_at = route.scheduled_date
                    route.completed_at = route.scheduled_date + timedelta(hours=2, minutes=random.randint(0, 45))
                    route.save()
        
        self.stdout.write(self.style.SUCCESS('✓ 5 örnek rota oluşturuldu'))
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('DEMO VERİLER BAŞARIYLA OLUŞTURULDU!'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(f'Konteynerler: {Container.objects.count()}')
        self.stdout.write(f'Aktif Uyarılar: {Alert.objects.filter(is_resolved=False).count()}')
        self.stdout.write(f'Rotalar: {CollectionRoute.objects.count()}')
        self.stdout.write('\nGiriş Bilgileri:')
        self.stdout.write('  Admin: admin / admin123')
        self.stdout.write('  Sürücü: surucu1 / surucu123')
        self.stdout.write('\nDashboard URL: http://localhost:8000/dashboard/')
