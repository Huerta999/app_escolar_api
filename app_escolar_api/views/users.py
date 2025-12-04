from django.db.models import *
from django.db import transaction
from app_escolar_api.serializers import UserSerializer
from app_escolar_api.serializers import *
from app_escolar_api.models import *
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import Group
import json
from django.shortcuts import get_object_or_404

class AdminAll(generics.CreateAPIView):
    #Esta función es esencial para todo donde se requiera autorización de inicio de sesión (token)
    permission_classes = (permissions.IsAuthenticated,)
    # Invocamos la petición GET para obtener todos los administradores
    def get(self, request, *args, **kwargs):
        admin = Administradores.objects.filter(user__is_active = 1).order_by("id")
        lista = AdminSerializer(admin, many=True).data
        return Response(lista, 200)

class AdminView(generics.CreateAPIView):
   # Permisos por método (sobrescribe el comportamiento default)
    # Verifica que el usuario esté autenticado para las peticiones GET, PUT y DELETE
    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return []  # POST no requiere autenticación
    
    #Obtener usuario por ID
    def get(self, request, *args, **kwargs):
        admin = get_object_or_404(Administradores, id = request.GET.get("id"))
        admin = AdminSerializer(admin, many=False).data
        # Si todo es correcto, regresamos la información
        return Response(admin, 200)
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):

        required_fields = [
        "rol", "first_name", "last_name", "email", "password",
        "clave_admin", "telefono", "rfc", "edad", "ocupacion"
         ]

     # Validar campos faltantes
        for field in required_fields:
            if field not in request.data or request.data[field] in ["", None]:
                return Response(
                {"error": f"El campo '{field}' es obligatorio."},
                status=400
            )

        # Extraer datos
        role = request.data["rol"]
        first_name = request.data["first_name"]
        last_name = request.data["last_name"]
        email = request.data["email"]
        password = request.data["password"]

        # Validación mínima de email
        if "@" not in email:
            return Response({"error": "El correo no es válido."}, 400)

        # Validar duplicado
        if User.objects.filter(email=email).exists():
            return Response({"error": f"El email {email} ya está registrado."}, 400)

        # Crear usuario
        user = User.objects.create(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=True
        )
        user.set_password(password)
        user.save()

        # Crear o asignar grupo
        group, created = Group.objects.get_or_create(name=role)
        group.user_set.add(user)

        # Crear Administrador
        admin = Administradores.objects.create(
            user=user,
            clave_admin=request.data["clave_admin"],
            telefono=request.data["telefono"],
            rfc=request.data["rfc"].upper(),
            edad=int(request.data["edad"]),
            ocupacion=request.data["ocupacion"]
        )

        return Response(
            {"message": "Administrador creado exitosamente", "id": admin.id},
            status=201
        )

    # Actualizar datos del administrador
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        # Verifica que el usuario esté autenticado
        permission_classes = (permissions.IsAuthenticated,)
        # Primero obtenemos el administrador a actualizar
        admin = get_object_or_404(Administradores, id=request.data["id"])
        admin.clave_admin = request.data["clave_admin"]
        admin.telefono = request.data["telefono"]
        admin.rfc = request.data["rfc"]
        admin.edad = request.data["edad"]
        admin.ocupacion = request.data["ocupacion"]
        admin.save()
        # Actualizamos los datos del usuario asociado (tabla auth_user de Django)
        user = admin.user
        user.first_name = request.data["first_name"]
        user.last_name = request.data["last_name"]
        user.save()
        
        return Response({"message": "Administrador actualizado correctamente", "admin": AdminSerializer(admin).data}, 200)
        # return Response(user,200)
          
    # Eliminar administrador con delete (Borrar realmente)
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        administrador = get_object_or_404(Administradores, id=request.GET.get("id"))
        try:
            administrador.user.delete()
            return Response({"details":"Administrador eliminado"},200)
        except Exception as e:
            return Response({"details":"Algo pasó al eliminar"},400)
        
class TotalUsers(generics.CreateAPIView):
    #Contar el total de cada tipo de usuarios
    def get(self, request, *args, **kwargs):
        # TOTAL ADMINISTRADORES
        admin_qs = Administradores.objects.filter(user__is_active=True)
        total_admins = admin_qs.count()

        # TOTAL MAESTROS
        maestros_qs = Maestros.objects.filter(user__is_active=True)
        lista_maestros = MaestroSerializer(maestros_qs, many=True).data

        # Convertir materias_json solo si existen maestros
        for maestro in lista_maestros:
            try:
                maestro["materias_json"] = json.loads(maestro["materias_json"])
            except Exception:
                maestro["materias_json"] = []  # fallback seguro

        total_maestros = maestros_qs.count()

        # TOTAL ALUMNOS
        alumnos_qs = Alumnos.objects.filter(user__is_active=True)
        total_alumnos = alumnos_qs.count()

        # Respuesta final SIEMPRE válida
        return Response(
            {
                "admins": total_admins,
                "maestros": total_maestros,
                "alumnos": total_alumnos
            },
            status=200
        )
