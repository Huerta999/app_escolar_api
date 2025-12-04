from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views.bootstrap import VersionView
from app_escolar_api.views import bootstrap
from app_escolar_api.views import users
from app_escolar_api.views import alumnos
from app_escolar_api.views import maestros
from app_escolar_api.views import auth
from app_escolar_api.views.materias import MateriasAll, MateriasView, VerificarNrcView
from app_escolar_api.views.users import TotalUsers 


urlpatterns = [
    #Create Admin
        path('admin/', users.AdminView.as_view()),
    #Admin Data
        path('lista-admins/', users.AdminAll.as_view()),
    #Edit Admin
        #path('admins-edit/', users.AdminsViewEdit.as_view())
     #Create Alumno
        path('alumnos/', alumnos.AlumnosView.as_view()),
    #Listar Alumno
        path('lista-alumnos/', alumnos.AlumnosAll.as_view()),
    #Create Maestro
        path('maestros/', maestros.MaestrosView.as_view()),
    #Listar Maestros
        path('lista-maestros/', maestros.MaestrosAll.as_view()),
    #Total de usuarios
        path('total-usuarios/', users.TotalUsers.as_view()),
    # Materias
        path('materias-all/', MateriasAll.as_view()),                  
        path('materias/', MateriasView.as_view()),                     
        path('materias/<int:id>/', MateriasView.as_view()),             
        path('materias/verificar-nrc/<str:nrc>/', VerificarNrcView.as_view()),
    # Gráficas 
        path('total-users/', TotalUsers.as_view()),
        
    path('login/', auth.CustomAuthToken.as_view()),
path('logout/', auth.LogoutView.as_view()),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
