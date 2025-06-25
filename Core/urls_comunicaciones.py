from django.urls import path
from Core.views import comunicaciones as comunicaciones_views

urlpatterns = [
    path('', comunicaciones_views.BandejaEntradaView.as_view(), name='bandeja_entrada'),
    path('crear/', comunicaciones_views.CrearComunicacionView.as_view(), name='crear_comunicacion'),
    path('<int:comunicacion_id>/', comunicaciones_views.ComunicacionDetalleView.as_view(), name='detalle_comunicacion'),
    path('<int:comunicacion_id>/editar/', comunicaciones_views.EditarComunicacionView.as_view(), name='editar_comunicacion'),
    path('<int:comunicacion_id>/eliminar/', comunicaciones_views.EliminarComunicacionView.as_view(), name='eliminar_comunicacion'),
    path('adjunto/<int:adjunto_id>/eliminar/', comunicaciones_views.EliminarAdjuntoView.as_view(), name='eliminar_adjunto'),
] 