from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mcmi_app.urls')),  # اشاره به فایل urls.py اپلیکیشن mcmi_app
]
