from django.contrib import admin
from django.urls import path, include # Make sure include is imported

urlpatterns = [
    path('admin/', admin.site.urls),
    path('app/', include('mcmi_app.urls')), # Include app URLs
]
