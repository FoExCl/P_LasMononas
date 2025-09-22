from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_cajas, name='lista_cajas'),
    path('nueva/', views.crear_caja, name='crear_caja'),
    path('editar/<int:pk>/', views.editar_caja, name='editar_caja'),
    path('eliminar/<int:pk>/', views.eliminar_caja, name='eliminar_caja'),
]