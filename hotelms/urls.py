from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('rooms/', include('apps.rooms.urls')),
    path('guests/', include('apps.guests.urls')),
    path('reservations/', include('apps.reservations.urls')),
    path('frontdesk/', include('apps.frontdesk.urls')),
    path('housekeeping/', include('apps.housekeeping.urls')),
    path('billing/', include('apps.billing.urls')),
    path('reports/', include('apps.reports.urls')),
    path('users/', include('apps.users.urls')),
    path('__reload__/', include('django_browser_reload.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
