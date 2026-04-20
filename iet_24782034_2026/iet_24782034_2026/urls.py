from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # MAIN APP
    path('', include('main_app.urls')),

    # 🔥 TAMBAHAN
    path('about/', include('about.urls')),
    path('contacts/', include('contacts.urls')),
]