from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
import json
import urllib.request
import urllib.error
from .models import Container, CollectionRoute, Alert, Municipality

# Fallback: Nominatim ulaşılamazsa kullanılacak yaklaşık dikdörtgen (Lat 38.37-38.42, Lng 27.02-27.08)
BALCOVA_FALLBACK_LAT_MIN = 38.370
BALCOVA_FALLBACK_LAT_MAX = 38.420
BALCOVA_FALLBACK_LNG_MIN = 27.020
BALCOVA_FALLBACK_LNG_MAX = 27.080


def _fetch_balcova_boundary_from_api():
    """Nominatim'den Balçova sınır GeoJSON'unu çeker. Rate limit: 1 istek/saniye."""
    url = (
        'https://nominatim.openstreetmap.org/search?'
        'q=Bal%C3%A7ova,+%C4%B0zmir,+Turkey&format=json&polygon_geojson=1&limit=1'
    )
    req = urllib.request.Request(url, headers={'User-Agent': 'LoooponeApp/1.0 (Belediye Atık Yönetimi)'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if data and len(data) > 0 and data[0].get('geojson'):
                return data[0]['geojson']
    except (urllib.error.URLError, json.JSONDecodeError, KeyError) as e:
        print(f"[Balçova sınır] Nominatim hatası, fallback kullanılacak: {e}")
    return None


def _get_balcova_boundary_geojson():
    """Balçova sınırını cache'den veya API'den alır (24 saat TTL)."""
    cache_key = getattr(settings, 'BALCOVA_BOUNDARY_CACHE_KEY', 'balcova_boundary_geojson')
    ttl = getattr(settings, 'BALCOVA_BOUNDARY_CACHE_TTL', 86400)
    geojson = cache.get(cache_key)
    if geojson is not None:
        return geojson
    geojson = _fetch_balcova_boundary_from_api()
    if geojson is not None:
        cache.set(cache_key, geojson, timeout=ttl)
        return geojson
    return None


def _is_in_balcova_shapely(lat, lng):
    """Shapely ile gerçek polygon içinde mi kontrol eder. Yoksa fallback dikdörtgen."""
    try:
        from shapely.geometry import Point, shape
        geojson = _get_balcova_boundary_geojson()
        if geojson is not None:
            geom = shape(geojson)
            point = Point(float(lng), float(lat))  # Shapely: (longitude, latitude)
            return geom.contains(point)
        # Fallback dikdörtgen
        la, ln = float(lat), float(lng)
        return (BALCOVA_FALLBACK_LAT_MIN <= la <= BALCOVA_FALLBACK_LAT_MAX and
                BALCOVA_FALLBACK_LNG_MIN <= ln <= BALCOVA_FALLBACK_LNG_MAX)
    except (TypeError, ValueError, ImportError) as e:
        print(f"[Balçova sınır] Shapely/koordinat hatası, fallback: {e}")
        la, ln = float(lat), float(lng)
        return (BALCOVA_FALLBACK_LAT_MIN <= la <= BALCOVA_FALLBACK_LAT_MAX and
                BALCOVA_FALLBACK_LNG_MIN <= ln <= BALCOVA_FALLBACK_LNG_MAX)


# 1. VATANDAŞ BİLDİRİM API (POST /report-issue-api/)
@csrf_exempt
def report_issue_api(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Sadece POST isteği kabul edilir'}, status=400)

    # Veriyi POST form veya JSON body'den al
    if request.content_type and 'application/json' in request.content_type:
        try:
            data = json.loads(request.body)
            issue_type = data.get('issue_type') or data.get('container_type')
            lat = data.get('lat')
            lng = data.get('lng')
            description = data.get('description', 'Vatandaş Bildirimi')
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Geçersiz JSON'}, status=400)
    else:
        issue_type = request.POST.get('issue_type') or request.POST.get('container_type')
        lat = request.POST.get('lat')
        lng = request.POST.get('lng')
        description = request.POST.get('description', 'Vatandaş Bildirimi')

    if not issue_type:
        issue_type = 'HALK_PAZARI'

    try:
        final_lat = float(lat) if lat else 38.3894
        final_lng = float(lng) if lng else 27.0461
    except (ValueError, TypeError):
        final_lat, final_lng = 38.3894, 27.0461

    # Güvenlik: Sadece Balçova sınırları içinden kabul et (Nominatim polygon veya fallback)
    if not _is_in_balcova_shapely(final_lat, final_lng):
        return JsonResponse(
            {'status': 'error', 'error': 'Sadece Balçova sınırları içinden sorun bildirilebilir.'},
            status=403
        )

    # Container modeli: organic, paper, plastic, glass, metal, general kabul eder; diğerlerini general yap
    allowed_types = ['organic', 'paper', 'plastic', 'glass', 'metal', 'general']
    container_type = issue_type if issue_type in allowed_types else 'general'

    # Benzersiz container_id (zorunlu alan)
    container_id = f"RPT-{timezone.now().strftime('%Y%m%d%H%M%S')}-{id(request) % 10000}"

    # Ekrana yazdır (terminal log)
    print(f"[report-issue-api] tip={issue_type}, lat={final_lat}, lng={final_lng}, açıklama={description[:50]}...")

    # Veritabanına kaydet (report_type = haritada gösterilecek sorun tipi)
    Container.objects.create(
        container_id=container_id,
        container_type=container_type,
        report_type=issue_type,
        latitude=final_lat,
        longitude=final_lng,
        address=(description or '')[:255],
        neighborhood='Vatandaş Bildirimi',
        fill_level=100,
        status='active',
    )

    print(f"✅ Yeni bildirim kaydedildi: {container_id}")
    return JsonResponse({'status': 'success'})

# 2. HARİTA İÇİN CANLI VERİ (TEK YETKİLİ FONKSİYON)
@login_required
def api_containers_json(request):
    containers = Container.objects.filter(status='active').values(
        'id', 'fill_level', 'latitude', 'longitude', 'address', 'container_type', 'report_type'
    )
    data = []
    for c in containers:
        # Vatandaş bildirimlerinde harita ikonu için report_type (HALK_PAZARI, MOLOZ vb.)
        display_type = c.get('report_type') or c['container_type']
        data.append({
            "id": c['id'],
            "lat": float(c['latitude']) if c['latitude'] else 0,
            "lng": float(c['longitude']) if c['longitude'] else 0,
            "fill": c['fill_level'],
            "address": c['address'],
            "type": display_type if isinstance(display_type, str) else str(display_type or ''),
        })
    return JsonResponse(data, safe=False)

# 3. SAYFA GÖRÜNÜMLERİ
def report_issue(request):
    return render(request, 'report_issue.html')

@login_required
def map_view(request):
    context = {'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY}
    return render(request, 'map.html', context)


@login_required
def analytics_view(request):
    return render(request, 'analytics.html')


# 4. GİRİŞ / ÇIKIŞ
def login_view(request):
    if request.method == 'POST':
        u, p = request.POST.get('username'), request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def containers_list(request):
    """Konteyner Listesi"""
    
    containers = Container.objects.all().order_by('-fill_level')
    
    # Filtreler
    search = request.GET.get('search', '')
    if search:
        containers = containers.filter(
            Q(container_id__icontains=search) |
            Q(address__icontains=search) |
            Q(neighborhood__icontains=search)
        )
    
    context = {
        'containers': containers,
        'search': search,
    }
    
    return render(request, 'containers_list.html', context)


@login_required
def container_detail(request, container_id):
    """Konteyner Detayı"""
    
    container = get_object_or_404(Container, id=container_id)
    
    # Son uyarılar
    alerts = Alert.objects.filter(container=container).order_by('-created_at')[:10]
    
    # Son toplama rotaları
    routes = CollectionRoute.objects.filter(containers=container).order_by('-scheduled_date')[:5]
    
    context = {
        'container': container,
        'alerts': alerts,
        'routes': routes,
    }
    
    return render(request, 'container_detail.html', context)


@login_required
def routes_list(request):
    """Rota Listesi"""
    
    routes = CollectionRoute.objects.all().order_by('-scheduled_date')
    
    context = {
        'routes': routes,
    }
    
    return render(request, 'routes_list.html', context)


@login_required
def alerts_list(request):
    """Uyarılar Listesi"""
    
    # Filtreler
    show_resolved = request.GET.get('resolved', 'false') == 'true'
    
    if show_resolved:
        alerts = Alert.objects.all()
    else:
        alerts = Alert.objects.filter(is_resolved=False)
    
    alerts = alerts.order_by('-priority', '-created_at')
    
    context = {
        'alerts': alerts,
        'show_resolved': show_resolved,
    }
    
    return render(request, 'alerts_list.html', context)


@login_required
def resolve_alert(request, alert_id):
    """Uyarıyı Çöz"""
    
    if request.method == 'POST':
        alert = get_object_or_404(Alert, id=alert_id)
        alert.resolve(request.user)
        messages.success(request, 'Uyarı başarıyla çözüldü.')
    
    return redirect('alerts_list')


@login_required
def dashboard(request):
    """Ana Dashboard – tüm değerler veritabanından dinamik."""
    # Toplam konteyner: veritabanındaki TÜM kayıtlar (Admin ile aynı sayı)
    total_containers = Container.objects.count()
    full_containers = Container.objects.filter(fill_level__gte=80).count()
    avg_fill_level = Container.objects.aggregate(Avg('fill_level'))['fill_level__avg'] or 0

    active_alerts = Alert.objects.filter(is_resolved=False).order_by('-priority', '-created_at')[:10]
    critical_alerts_count = Alert.objects.filter(is_resolved=False, priority='critical').count()

    today = timezone.now().date()
    today_routes = CollectionRoute.objects.filter(scheduled_date__date=today).order_by('scheduled_date')
    last_week = timezone.now() - timedelta(days=7)
    completed_routes = CollectionRoute.objects.filter(
        completed_at__gte=last_week, status='completed'
    ).count()

    attention_needed = Container.objects.filter(
        Q(fill_level__gte=70) | Q(battery_level__lt=20) | Q(status__in=['maintenance', 'damaged'])
    ).order_by('-fill_level')[:5]

    total_users = User.objects.count()
    total_vehicles = CollectionRoute.objects.values('vehicle_plate').distinct().count()
    total_neighborhoods = Container.objects.values('neighborhood').distinct().count()

    context = {
        'total_containers': total_containers,
        'full_containers': full_containers,
        'avg_fill_level': round(avg_fill_level, 1),
        'active_alerts': active_alerts,
        'critical_alerts_count': critical_alerts_count,
        'today_routes': today_routes,
        'completed_routes': completed_routes,
        'attention_needed': attention_needed,
        'total_users': total_users,
        'total_vehicles': total_vehicles,
        'total_neighborhoods': total_neighborhoods,
    }
    return render(request, 'dashboard.html', context)


@login_required
def api_stats_json(request):
    """Dashboard istatistiklerini JSON olarak döndür (veritabanından dinamik)"""
    stats = {
        'total_containers': Container.objects.count(),
        'full_containers': Container.objects.filter(fill_level__gte=80).count(),
        'avg_fill_level': Container.objects.aggregate(Avg('fill_level'))['fill_level__avg'] or 0,
        'active_alerts': Alert.objects.filter(is_resolved=False).count(),
        'critical_alerts': Alert.objects.filter(is_resolved=False, priority='critical').count(),
    }
    return JsonResponse(stats)