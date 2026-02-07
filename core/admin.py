from django.contrib import admin
from .models import Container, CollectionRoute, Alert, Municipality


@admin.register(Container)
class ContainerAdmin(admin.ModelAdmin):
    list_display = ['container_id', 'container_type', 'fill_level', 'status', 'neighborhood', 'battery_level', 'last_updated']
    list_filter = ['container_type', 'status', 'neighborhood']
    search_fields = ['container_id', 'address', 'neighborhood']
    list_editable = ['fill_level', 'status']
    readonly_fields = ['created_at', 'last_updated']
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('container_id', 'container_type', 'capacity', 'status')
        }),
        ('Doluluk & Sensör', {
            'fields': ('fill_level', 'temperature', 'battery_level')
        }),
        ('Lokasyon', {
            'fields': ('latitude', 'longitude', 'address', 'neighborhood')
        }),
        ('Zaman Bilgileri', {
            'fields': ('last_emptied', 'created_at', 'last_updated'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('-fill_level')


@admin.register(CollectionRoute)
class CollectionRouteAdmin(admin.ModelAdmin):
    list_display = ['route_name', 'driver', 'vehicle_plate', 'scheduled_date', 'status', 'containers_count']
    list_filter = ['status', 'scheduled_date']
    search_fields = ['route_name', 'vehicle_plate', 'driver__username']
    filter_horizontal = ['containers']
    readonly_fields = ['created_at', 'containers_count']
    
    fieldsets = (
        ('Rota Bilgileri', {
            'fields': ('route_name', 'driver', 'vehicle_plate')
        }),
        ('Konteynerler', {
            'fields': ('containers',)
        }),
        ('Zamanlama', {
            'fields': ('scheduled_date', 'started_at', 'completed_at', 'status')
        }),
        ('Diğer', {
            'fields': ('total_distance', 'notes', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def containers_count(self, obj):
        return obj.containers.count()
    containers_count.short_description = 'Konteyner Sayısı'


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['container', 'alert_type', 'priority', 'is_resolved', 'created_at']
    list_filter = ['alert_type', 'priority', 'is_resolved', 'created_at']
    search_fields = ['container__container_id', 'message']
    readonly_fields = ['created_at', 'resolved_at']
    
    fieldsets = (
        ('Uyarı Bilgileri', {
            'fields': ('container', 'alert_type', 'priority', 'message')
        }),
        ('Durum', {
            'fields': ('is_resolved', 'resolved_by', 'resolved_at')
        }),
        ('Zaman', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('-priority', '-created_at')


@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ['name', 'district', 'city', 'is_active']
    list_filter = ['is_active', 'city']
    search_fields = ['name', 'district', 'city']
    
    fieldsets = (
        ('Belediye Bilgileri', {
            'fields': ('name', 'city', 'district', 'is_active')
        }),
        ('İletişim', {
            'fields': ('address', 'phone', 'email')
        }),
        ('Harita Merkezi', {
            'fields': ('center_lat', 'center_lng')
        }),
        ('Ayarlar', {
            'fields': ('alert_threshold',)
        }),
    )


# Admin site başlıklarını özelleştir
admin.site.site_header = "Looopone Yönetim Paneli"
admin.site.site_title = "Looopone Admin"
admin.site.index_title = "Akıllı Çöp Yönetim Sistemi"
