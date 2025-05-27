from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from .models import Estudiante, Docente
from .services import UserService

Usuario = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    service = UserService()
    
    def create(self, request):
        """Crear un nuevo usuario"""
        try:
            user = self.service.create_user(
                email=request.data.get('email'),
                password=request.data.get('password'),
                nombre=request.data.get('nombre'),
                apellido=request.data.get('apellido')
            )
            return Response({'message': 'Usuario creado exitosamente'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def create_student(self, request):
        """Crear un nuevo estudiante"""
        try:
            user = self.service.create_user(
                email=request.data.get('email'),
                password=request.data.get('password'),
                nombre=request.data.get('nombre'),
                apellido=request.data.get('apellido')
            )
            estudiante = self.service.create_student(
                user=user,
                rut=request.data.get('rut'),
                fecha_nacimiento=request.data.get('fecha_nacimiento'),
                direccion=request.data.get('direccion'),
                telefono=request.data.get('telefono')
            )
            return Response({'message': 'Estudiante creado exitosamente'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def create_teacher(self, request):
        """Crear un nuevo docente"""
        try:
            user = self.service.create_user(
                email=request.data.get('email'),
                password=request.data.get('password'),
                nombre=request.data.get('nombre'),
                apellido=request.data.get('apellido')
            )
            docente = self.service.create_teacher(
                user=user,
                rut=request.data.get('rut'),
                especialidad=request.data.get('especialidad'),
                telefono=request.data.get('telefono')
            )
            return Response({'message': 'Docente creado exitosamente'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """Actualizar un usuario existente"""
        try:
            user = self.service.update_user(pk, **request.data)
            return Response({'message': 'Usuario actualizado exitosamente'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Desactivar un usuario"""
        try:
            user = self.service.deactivate_user(pk)
            return Response({'message': 'Usuario desactivado exitosamente'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST) 