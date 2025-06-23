from django.urls import path
from Core.views import comunicaciones as comunicaciones_views

urlpatterns = [
    path('', comunicaciones_views.BandejaEntradaView.as_view(), name='bandeja_entrada'),
    path('<int:comunicacion_id>/', comunicaciones_views.ComunicacionDetalleView.as_view(), name='detalle_comunicacion'),
] 