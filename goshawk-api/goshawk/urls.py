from django.contrib import admin
from django.conf.urls import url
from django.urls import path, include

from rest_framework import routers

from core import views as core_views

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

router = routers.DefaultRouter()
router.register(r'collections', core_views.CollectionViewSet)
router.register(r'reporters', core_views.ReporterViewSet)
router.register(r'lists', core_views.ListViewSet)
router.register(r'records', core_views.RecordViewSet)


schema_view = get_schema_view(
   openapi.Info(
      title="Goshawk API Docs",
      default_version='v1',
      description="Goshawk API Docs",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

	path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
	path('api-auth/', include('rest_framework.urls'))
]
