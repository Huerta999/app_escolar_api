from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from app_escolar_api.views import  materias, users, alumnos, maestros, auth

urlpatterns = [
    # Create Admin
    path('admin/', users.AdminView.as_view()),
    # Admin Data
    path('lista-admins/', users.AdminAll.as_view()),
    # Create Alumno
    path('alumnos/', alumnos.AlumnosView.as_view()),
    path('lista-alumnos/', alumnos.AlumnosAll.as_view()),
    # Create Maestro
    path('maestros/', maestros.MaestrosView.as_view()),
    # Listar Maestros
    path('lista-maestros/', maestros.MaestrosAll.as_view()),
    # Total de usuarios
    path('total-usuarios/', users.TotalUsers.as_view()),
    # Login
    path('login/', auth.CustomAuthToken.as_view()),
    # Logout
    path('logout/', auth.Logout.as_view()),
    # Materias
    path('lista-materias/', materias.MateriasAll.as_view()),
    path('materias/', materias.MateriasView.as_view()),
    path('materias/<int:id>/', materias.MateriasView.as_view()),
    path('materias/verificar-nrc/<str:nrc>/', materias.VerificarNrcView.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
