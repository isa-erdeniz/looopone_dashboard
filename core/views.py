from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Container, CollectionRoute, Alert, Municipality


def login_view(request):
    """Giriş Sayfası"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Hoş geldiniz, {user.get_full_name() or user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Kullanıcı adı veya şifre hatalı!')
    
    return render(request, 'login.html')


def logout_view(request):
    """Çıkış"""
    logout(request)
    messages.info(request, 'Başarıyla çıkış yaptınız.')
    return redirect('login')


@login_required
def dashboard(request):
    """Ana Dashboard"""
    
    # İstatistikler
    total_containers = Container.objects.filter(status='active').count()
    full_containers = Container.objects.filter(fill_level__gte=80, status='active').count()
    avg_fill_level = Container.objects.filter(status='active').aggregate(Avg('fill_level'))['fill_level__avg'] or 0
    
    # Uyarılar
    active_alerts = Alert.objects.filter(is_resolved=False).order_by('-priority', '-created_at')[:10]
    critical_alerts_count = Alert.objects.filter(is_resolved=False, priority='critical').count()
    
    # Bugünkü rotalar
    today = timezone.now().date()
    today_routes = CollectionRoute.objects.filter(
        scheduled_date__date=today
    ).order_by('scheduled_date')
    
    # Son 7 gün toplanma sayıları
    last_week = timezone.now() - timedelta(days=7)
    completed_routes = CollectionRoute.objects.filter(
        completed_at__gte=last_week,
        status='completed'
    ).count()
    
    # Dikkat gerektiren konteynerler
    attention_needed = Container.objects.filter(
        Q(fill_level__gte=70) | 
        Q(battery_level__lt=20) | 
        Q(status__in=['maintenance', 'damaged'])
    ).order_by('-fill_level')[:5]
    
    context = {
        'total_containers': total_containers,
        'full_containers': full_containers,
        'avg_fill_level': round(avg_fill_level, 1),
        'active_alerts': active_alerts,
        'critical_alerts_count': critical_alerts_count,
        'today_routes': today_routes,
        'completed_routes': completed_routes,
        'attention_needed': attention_needed,
    }
    
    return render(request, 'dashboard.html', context)


@login_required
def map_view(request):
    """Harita Görünümü"""
    
    # Filtreler
    container_type = request.GET.get('type', 'all')
    fill_level_min = request.GET.get('fill_min', 0)
    status_filter = request.GET.get('status', 'all')
    
    containers = Container.objects.filter(status='active')
    
    if container_type != 'all':
        containers = containers.filter(container_type=container_type)
    
    if fill_level_min:
        containers = containers.filter(fill_level__gte=int(fill_level_min))
    
    if status_filter != 'all':
        containers = containers.filter(status=status_filter)
    
    # Belediye merkez noktası
    try:
        municipality = Municipality.objects.filter(is_active=True).first()
        center_lat = float(municipality.center_lat) if municipality else 38.3692
        center_lng = float(municipality.center_lng) if municipality else 27.0468
    except:
        center_lat = 38.3692  # Balçova default
        center_lng = 27.0468
    
    context = {
        'containers': containers,
        'center_lat': center_lat,
        'center_lng': center_lng,
        'container_types': Container.CONTAINER_TYPES,
    }
    
    return render(request, 'map.html', context)


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


# API Endpoints (AJAX için)

@login_required
def api_containers_json(request):
    """Konteyner verilerini JSON olarak döndür (Harita için)"""
    
    containers = Container.objects.filter(status='active').values(
        'id', 'container_id', 'container_type', 'fill_level',
        'latitude', 'longitude', 'address', 'neighborhood',
        'status', 'battery_level', 'last_updated'
    )
    
    return JsonResponse(list(containers), safe=False)


@login_required
def api_stats_json(request):
    """Dashboard istatistiklerini JSON olarak döndür"""
    
    stats = {
        'total_containers': Container.objects.filter(status='active').count(),
        'full_containers': Container.objects.filter(fill_level__gte=80, status='active').count(),
        'avg_fill_level': Container.objects.filter(status='active').aggregate(Avg('fill_level'))['fill_level__avg'] or 0,
        'active_alerts': Alert.objects.filter(is_resolved=False).count(),
        'critical_alerts': Alert.objects.filter(is_resolved=False, priority='critical').count(),
    }
    
    return JsonResponse(stats)
