from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView

from app_escolar_api.models import Materias, Maestros
from app_escolar_api.serializers import MateriaSerializer
from datetime import datetime


def normalizar_hora(valor):
    """
    Acepta:
      - 'HH:MM'
      - 'HH:MM:SS'
      - 'h:MM AM/PM'  (ej. '2:00 PM')
    y devuelve siempre 'HH:MM:SS'.
    Si no se puede parsear, regresa el valor original.
    """
    if not valor:
        return None

    valor = str(valor).strip()

    # 1) Formatos 24h
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            dt = datetime.strptime(valor, fmt)
            return dt.strftime("%H:%M:%S")
        except ValueError:
            pass

    # 2) Formatos 12h con AM/PM
    for fmt in ("%I:%M %p", "%I:%M%p"):
        try:
            dt = datetime.strptime(valor.upper(), fmt)
            return dt.strftime("%H:%M:%S")
        except ValueError:
            pass

    # Si nada coincide, lo dejamos tal cual (el serializer se quejará)
    return valor


class MateriasAll(APIView):
    """
    Vista de compatibilidad:
    GET /materias-all/  -> lista todas las materias
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        materias = Materias.objects.all().order_by("id")
        serializer = MateriaSerializer(materias, many=True)
        return Response(serializer.data, 200)


class VerificarNrcView(APIView):
    """
    GET /materias/verificar-nrc/<nrc>/
    Responde: { "existe": true/false }
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, nrc, *args, **kwargs):
        existe = Materias.objects.filter(nrc=nrc).exists()
        return Response({"existe": existe}, 200)


class MateriasView(GenericAPIView):
    """
    Vista principal que se adapta al FRONT actual:

      - GET    /materias/           -> lista todas
      - GET    /materias/<id>/      -> detalle
      - POST   /materias/           -> crear
      - PUT    /materias/<id>/      -> actualizar
      - DELETE /materias/<id>/      -> eliminar

    Además mapea:
      - 'nombre'       -> 'nombre_materia'
      - 'profesor_id'  -> 'profesor'
      - 'dias' (lista) -> string "Lunes, Martes, ..."
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = MateriaSerializer

    def _get_id(self, request, **kwargs):
        # intentamos obtener el id de:
        # 1) kwargs (path param)
        # 2) query param ?id=
        # 3) body
        return kwargs.get("id") or request.GET.get("id") or request.data.get("id")

    # =========================
    # GET (lista o detalle)
    # =========================
    def get(self, request, *args, **kwargs):
        materia_id = self._get_id(request, **kwargs)

        if materia_id:
            materia = get_object_or_404(Materias, id=materia_id)
            serializer = MateriaSerializer(materia)
            return Response(serializer.data, 200)

        # Sin id: lista todas
        materias = Materias.objects.all().order_by("id")
        serializer = MateriaSerializer(materias, many=True)
        return Response(serializer.data, 200)

    # =========================
    # POST (crear)
    # =========================
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.data.copy()

        # 1) Validar NRC único
        nrc = data.get("nrc")
        if Materias.objects.filter(nrc=nrc).exists():
            return Response(
                {"nrc": ["El NRC ya existe en la base de datos."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2) Mapear campos del FRONT a modelo/serializer
        # nombre -> nombre_materia
        if "nombre" in data and "nombre_materia" not in data:
            data["nombre_materia"] = data["nombre"]

        # profesor_id -> profesor (FK a Maestros)
        profesor_id = data.get("profesor_id")
        if profesor_id:
            if not Maestros.objects.filter(id=profesor_id).exists():
                return Response(
                    {"profesor": ["El profesor seleccionado no existe."]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            data["profesor"] = profesor_id

        # dias: si viene como lista, lo convertimos a string "Lunes, Martes"
        dias = data.get("dias")
        if isinstance(dias, list):
            data["dias"] = ", ".join(dias)

        # ⭐ Normalizar horas: acepta '2:00 PM', '14:00', etc.
        if "hora_inicio" in data:
            data["hora_inicio"] = normalizar_hora(data["hora_inicio"])
        if "hora_fin" in data:
            data["hora_fin"] = normalizar_hora(data["hora_fin"])

        serializer = MateriaSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"materia_created_id": serializer.data["id"]}, 201)

        print("ERRORES SERIALIZER MATERIA (POST):", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # =========================
    # PUT (actualizar)
    # =========================
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        materia_id = self._get_id(request, **kwargs)
        materia = get_object_or_404(Materias, id=materia_id)
        data = request.data.copy()

        # Mapear nombre -> nombre_materia
        if "nombre" in data:
            data["nombre_materia"] = data["nombre"]

        # profesor_id -> profesor
        profesor_id = data.get("profesor_id")
        if profesor_id:
            if not Maestros.objects.filter(id=profesor_id).exists():
                return Response(
                    {"profesor": ["El profesor seleccionado no existe."]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            data["profesor"] = profesor_id

        # dias lista -> string
        dias = data.get("dias")
        if isinstance(dias, list):
            data["dias"] = ", ".join(dias)

        # ⭐ Normalizar horas también en actualización
        if "hora_inicio" in data:
            data["hora_inicio"] = normalizar_hora(data["hora_inicio"])
        if "hora_fin" in data:
            data["hora_fin"] = normalizar_hora(data["hora_fin"])

        serializer = MateriaSerializer(materia, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Materia actualizada correctamente"}, 200)

        print("ERRORES SERIALIZER MATERIA (PUT):", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # =========================
    # DELETE
    # =========================
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        materia_id = self._get_id(request, **kwargs)
        materia = get_object_or_404(Materias, id=materia_id)
        materia.delete()
        return Response({"message": "Materia eliminada correctamente"}, 200)
