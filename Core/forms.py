from django import forms
from .models import Usuario, Estudiante, Docente, Administrativo, Curso, Asignatura, ProfesorJefe, AsignaturaImpartida, Especialidad
from Core.servicios.helpers.validadores import es_cadena_valida, es_correo_valido, es_correo_existente

class UsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido_paterno', 'apellido_materno', 'rut', 'div', 'correo', 'telefono', 'direccion', 'fecha_nacimiento']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido_paterno': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido_materno': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'div': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '1'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'type': 'tel'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': '2'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
        }

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if not es_cadena_valida(rut):
            raise forms.ValidationError("El RUT no es válido.")
        return rut

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if not es_correo_valido(correo):
            raise forms.ValidationError("El correo electrónico no es válido.")
        if es_correo_existente(correo):
            raise forms.ValidationError("El correo electrónico ya está en uso.")
        return correo

class EstudianteForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = ['contacto_emergencia', 'curso']
        widgets = {
            'contacto_emergencia': forms.TextInput(attrs={'class': 'form-control'}),
            'curso': forms.Select(attrs={'class': 'form-select'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['curso'] = forms.ModelChoiceField(
            queryset=Curso.objects.all(),
            widget=forms.Select(attrs={'class': 'form-select'}),
            empty_label="Seleccione un curso"
        )

class DocenteForm(forms.ModelForm):
    class Meta:
        model = Docente
        fields = ['especialidad']
        widgets = {
            'especialidad': forms.Select(attrs={'class': 'form-select'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['especialidad'] = forms.ModelChoiceField(
            queryset=Especialidad.objects.all(),
            widget=forms.Select(attrs={'class': 'form-select'}),
            empty_label="Seleccione una especialidad"
        )

class AdministrativoForm(forms.ModelForm):
    class Meta:
        model = Administrativo
        fields = []

class AsignaturaImpartidaForm(forms.ModelForm):
    class Meta:
        model = AsignaturaImpartida
        fields = ['asignatura', 'docente', 'horario']
        widgets = {
            'horario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Lunes 08:00-09:30'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['asignatura'] = forms.ModelChoiceField(
            queryset=Asignatura.objects.all(),
            widget=forms.Select(attrs={'class': 'form-select'}),
            empty_label="Seleccione una asignatura"
        )
        
        # Inicialmente mostramos todos los docentes
        self.fields['docente'] = forms.ModelChoiceField(
            queryset=Docente.objects.none(),
            widget=forms.Select(attrs={'class': 'form-select'}),
            empty_label="Seleccione un profesor"
        )

        # Si hay una instancia, actualizamos el queryset de docentes
        if self.instance.pk:
            self.fields['docente'].queryset = Docente.objects.filter(
                especialidad__nombre=self.instance.asignatura.nombre
            )

    def clean(self):
        cleaned_data = super().clean()
        asignatura = cleaned_data.get('asignatura')
        docente = cleaned_data.get('docente')

        if asignatura and docente:
            # Verificar que el docente tenga la especialidad correcta
            if docente.especialidad.nombre != asignatura.nombre:
                raise forms.ValidationError(
                    "El profesor seleccionado no tiene la especialidad requerida para esta asignatura."
                )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Generar el código usando las tres primeras letras y el ID
        codigo_base = instance.asignatura.nombre[:3].upper()
        
        # Obtener el último ID para esta asignatura
        ultimo_id = AsignaturaImpartida.objects.filter(
            asignatura=instance.asignatura
        ).count() + 1
        
        # Generar el código con el formato especificado
        instance.codigo = f"{codigo_base}{ultimo_id:02d}"
        
        if commit:
            instance.save()
        return instance

class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['nivel', 'letra']
        widgets = {
            'nivel': forms.Select(attrs={'class': 'form-select'}),
            'letra': forms.Select(attrs={'class': 'form-select'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nivel'].choices = [(i, f'{i}°') for i in range(1, 9)]
        self.fields['letra'].choices = [(letra, letra) for letra in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']

class AsignaturaForm(forms.ModelForm):
    class Meta:
        model = Asignatura
        fields = ['nombre', 'es_electivo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre de la asignatura'
            }),
            'es_electivo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre:
            raise forms.ValidationError("El nombre de la asignatura es requerido.")
        if len(nombre) < 3:
            raise forms.ValidationError("El nombre debe tener al menos 3 caracteres.")
        return nombre

class ProfesorJefeForm(forms.ModelForm):
    class Meta:
        model = ProfesorJefe
        fields = ['docente', 'curso']
        widgets = {
            'docente': forms.Select(attrs={'class': 'form-select'}),
            'curso': forms.Select(attrs={'class': 'form-select'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['docente'] = forms.ModelChoiceField(
            queryset=Docente.objects.all(),
            widget=forms.Select(attrs={'class': 'form-select'}),
            empty_label="Seleccione un docente"
        )
        self.fields['curso'] = forms.ModelChoiceField(
            queryset=Curso.objects.all(),
            widget=forms.Select(attrs={'class': 'form-select'}),
            empty_label="Seleccione un curso"
        )
