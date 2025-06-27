import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models.usuarios import Docente, Estudiante
from ..models.cursos import Curso
from ..models.academico import AlumnoEvaluacion, Asistencia
from ..models.notas import NotaFinal
from ..servicios.helpers.ia_service import IAService
from ..servicios.helpers.ia_config import PROMPT_TEMPLATES, ANALYSIS_TYPES

class TestIACursoView(TestCase):
    def setUp(self):
        # Crear usuario administrador
        self.admin_user = get_user_model().objects.create_user(
            username='admin_test',
            password='admin123',
            is_staff=True,
            is_superuser=True
        )
        
        # Crear usuario docente
        self.docente_user = get_user_model().objects.create_user(
            username='docente_test',
            password='docente123'
        )
        self.docente = Docente.objects.create(
            usuario=self.docente_user,
            especialidad='Matemáticas'
        )
        
        # Crear curso
        self.curso = Curso.objects.create(
            nivel=1,
            letra='A',
            año=2025
        )
        
        # Crear algunos estudiantes
        self.estudiantes = []
        for i in range(3):
            user = get_user_model().objects.create_user(
                username=f'estudiante_{i}',
                password='estudiante123'
            )
            estudiante = Estudiante.objects.create(
                usuario=user,
                curso=self.curso
            )
            self.estudiantes.append(estudiante)
            
            # Crear algunas notas
            NotaFinal.objects.create(
                estudiante=estudiante,
                asignatura=self.curso.asignaturas.first(),
                nota=5.5
            )
            
            # Crear asistencias
            Asistencia.objects.create(
                estudiante=estudiante,
                fecha='2025-03-01',
                presente=True
            )
        
        self.client = Client()
        self.ia_service = IAService()

    def test_generar_reporte_rendimiento(self):
        """Prueba la generación de reporte de rendimiento con IA"""
        self.client.login(username='docente_test', password='docente123')
        
        response = self.client.post(
            reverse('generar_reporte_ia'),
            {
                'tipo_reporte': 'rendimiento',
                'curso_id': self.curso.id
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('titulo', data)
        self.assertIn('analisis_detallado', data)
        self.assertIn('recomendaciones', data)

    def test_generar_reporte_asistencia(self):
        """Prueba la generación de reporte de asistencia con IA"""
        self.client.login(username='docente_test', password='docente123')
        
        response = self.client.post(
            reverse('generar_reporte_ia'),
            {
                'tipo_reporte': 'asistencia',
                'curso_id': self.curso.id
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('porcentaje_general', data['asistencia'])
        self.assertIn('estudiantes_riesgo', data['asistencia'])

    def test_generar_sugerencias_intervencion(self):
        """Prueba la generación de sugerencias de intervención con IA"""
        self.client.login(username='docente_test', password='docente123')
        
        response = self.client.post(
            reverse('generar_sugerencias_ia'),
            {
                'curso_id': self.curso.id,
                'area': 'rendimiento'
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('objetivos', data)
        self.assertIn('estrategias', data)
        self.assertIn('recursos_necesarios', data)

    def test_generar_comunicado(self):
        """Prueba la generación de comunicados con IA"""
        self.client.login(username='docente_test', password='docente123')
        
        response = self.client.post(
            reverse('generar_comunicado_ia'),
            {
                'tipo_comunicado': 'rendimiento',
                'curso_id': self.curso.id
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('asunto', data)
        self.assertIn('cuerpo', data)
        self.assertIn('firma', data)

    def test_permisos_acceso(self):
        """Prueba los permisos de acceso a las herramientas IA"""
        # Probar acceso como estudiante (no debería tener acceso)
        self.client.login(username='estudiante_0', password='estudiante123')
        
        response = self.client.post(
            reverse('generar_reporte_ia'),
            {
                'tipo_reporte': 'rendimiento',
                'curso_id': self.curso.id
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_validacion_contenido(self):
        """Prueba la validación de contenido sensible"""
        self.client.login(username='docente_test', password='docente123')
        
        # Intentar generar un reporte con datos sensibles
        response = self.client.post(
            reverse('generar_reporte_ia'),
            {
                'tipo_reporte': 'comportamiento',
                'curso_id': self.curso.id,
                'incluir_datos_sensibles': True  # Esto debería ser filtrado
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        # Verificar que no hay datos sensibles en la respuesta
        self.assertNotIn('rut', str(data))
        self.assertNotIn('dirección', str(data))
        self.assertNotIn('teléfono', str(data))

    def test_rate_limiting(self):
        """Prueba el límite de solicitudes"""
        self.client.login(username='docente_test', password='docente123')
        
        # Hacer múltiples solicitudes
        for _ in range(6):  # Más que el límite por minuto
            response = self.client.post(
                reverse('generar_reporte_ia'),
                {
                    'tipo_reporte': 'rendimiento',
                    'curso_id': self.curso.id
                },
                content_type='application/json'
            )
        
        # La última solicitud debería ser rechazada
        self.assertEqual(response.status_code, 429)  # Too Many Requests 