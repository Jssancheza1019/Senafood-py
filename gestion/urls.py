from django.urls import path
from . import views

urlpatterns = [
    # Cuando entres a /login/ se ejecutará la función login_view
    path('login/', views.login_view, name='login'),
    # Cuando entres a /registro/ se ejecutará la función registro_view
    path('registro/', views.registro_view, name='registro'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
]