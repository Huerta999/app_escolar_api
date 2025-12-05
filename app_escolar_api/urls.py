from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from app_escolar_api.views import users, alumnos, maestros, auth
from app_escolar_api.views.materias import MateriasAll, MateriasView, VerificarNrcView
from app_escolar_api.views.users import TotalUsers

urlpatterns = [
    path("api/", include([
        path("admin/", users.AdminView.as_view()),
        path("lista-admins/", users.AdminAll.as_view()),

        path("alumnos/", alumnos.AlumnosView.as_view()),
        path("lista-alumnos/", alumnos.AlumnosAll.as_view()),

        path("maestros/", maestros.MaestrosView.as_view()),
        path("lista-maestros/", maestros.MaestrosAll.as_view()),

        path("materias-all/", MateriasAll.as_view()),
        path("materias/", MateriasView.as_view()),
        path("materias/<int:id>/", MateriasView.as_view()),
        path("materias/verificar-nrc/<str:nrc>/", VerificarNrcView.as_view()),

        path("total-users/", TotalUsers.as_view()),

        path("login/", auth.CustomAuthToken.as_view()),
        path("logout/", auth.Logout.as_view()),
    ])),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
