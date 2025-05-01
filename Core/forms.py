from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Asignatura
import random
import string

class UsuarioAdminForm(UserCreationForm):
    asignaturas = forms.ModelMultipleChoiceField(
        queryset=Asignatura.objects.filter(activa=True),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Asignaturas que imparte'
    )

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'rut', 'tipo_usuario', 'telefono', 'fecha_nacimiento', 'direccion', 'asignaturas']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'tipo_usuario': forms.Select(attrs={'onchange': 'toggleAsignaturas(this)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ocultar los campos de contraseña ya que se generan automáticamente
        self.fields['password1'].widget = forms.HiddenInput()
        self.fields['password2'].widget = forms.HiddenInput()
        # Ocultar el campo de asignaturas inicialmente
        self.fields['asignaturas'].widget.attrs['style'] = 'display: none;'

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if Usuario.objects.filter(rut=rut).exists():
            raise forms.ValidationError('Este RUT ya está registrado')
        return rut

    def clean(self):
        cleaned_data = super().clean()
        print("=== INICIO DE CLEAN ===")
        print("Datos limpios:", cleaned_data)
        
        # Generar email automáticamente
        first_name = cleaned_data.get('first_name', '').lower()
        last_name = cleaned_data.get('last_name', '').lower()
        email = f"{first_name}.{last_name}@gem.edu"
        
        # Verificar si el email ya existe
        counter = 1
        while Usuario.objects.filter(email=email).exists():
            email = f"{first_name}.{last_name}{counter}@gem.edu"
            counter += 1
            
        cleaned_data['email'] = email
        
        # Generar password automáticamente
        password = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=12))
        cleaned_data['password1'] = password
        cleaned_data['password2'] = password

        # Validar asignaturas para profesores
        tipo_usuario = cleaned_data.get('tipo_usuario')
        if tipo_usuario == 'profesor' and not cleaned_data.get('asignaturas'):
            self.add_error('asignaturas', 'Los profesores deben tener al menos una asignatura asignada')
        
        print("=== FIN DE CLEAN ===")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            if hasattr(self, 'save_m2m'):
                self.save_m2m()
        return user
