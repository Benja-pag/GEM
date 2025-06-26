from django.http import HttpResponse
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime
import os
from django.conf import settings
import io

def generar_pdf_horario(estudiante, horario_data):
    """
    Genera un PDF del horario del estudiante con un diseño mejorado.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # --- Cabecera con Logo y Título ---
    logo_path = os.path.join(settings.BASE_DIR, 'Core', 'static', 'img', 'logo.png')
    logo = Image(logo_path, width=0.8*inch, height=0.8*inch)
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )
    
    header_text = Paragraph("Horario de Clases", header_style)
    
    header_table = Table([[logo, header_text]], colWidths=[1*inch, 6.5*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (1, 0), (1, 0), 0),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # --- Información del Estudiante ---
    info_style = ParagraphStyle(
        'Info', parent=styles['Normal'], fontSize=10, leading=14,
        spaceAfter=15, borderBottomWidth=1, borderBottomColor=colors.lightgrey,
        borderBottomPadding=5
    )
    
    info_text = f"""
    <b>Estudiante:</b> {estudiante.usuario.nombre} {estudiante.usuario.apellido_paterno}<br/>
    <b>RUT:</b> {estudiante.usuario.rut}<br/>
    <b>Curso:</b> {estudiante.curso}
    """
    info_paragraph = Paragraph(info_text, info_style)
    elements.append(info_paragraph)
    
    # --- Tabla de Horario ---
    dias = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES']
    bloques = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    
    horas_bloques = {
        '1': '08:00 - 08:45', '2': '08:45 - 09:30', '3': '09:45 - 10:30',
        '4': '10:30 - 11:15', '5': '11:30 - 12:15', '6': '12:15 - 13:00',
        '7': '13:45 - 14:30', '8': '14:30 - 15:15', '9': '15:15 - 16:00'
    }
    
    # Estilos para celdas
    asignatura_style = ParagraphStyle('Asignatura', fontSize=8, fontName='Helvetica-Bold', alignment=TA_CENTER)
    sala_style = ParagraphStyle('Sala', fontSize=7, textColor=colors.dimgrey, alignment=TA_CENTER)
    
    # Encabezados de la tabla
    data = [[Paragraph(f"<b>{d}</b>", styles['Normal']) for d in ['Hora'] + [dia.capitalize() for dia in dias]]]
    
    # Llenar datos del horario
    for bloque in bloques:
        hora_str = horas_bloques.get(bloque, bloque)
        fila = [Paragraph(f"<b>{hora_str}</b>", styles['Normal'])]
        
        for dia in dias:
            clase_data = horario_data.get(dia, {}).get(bloque)
            if clase_data:
                cell_content = [
                    Paragraph(clase_data['asignatura'], asignatura_style),
                    Paragraph(clase_data['sala'], sala_style),
                ]
                fila.append(cell_content)
            else:
                fila.append('')
        data.append(fila)

    table = Table(data, colWidths=[1.1*inch] + [1.3*inch]*5, rowHeights=[0.4*inch] + [0.6*inch]*9)
    
    # Estilos de la tabla
    common_style = [
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
    ]
    
    header_style_tbl = ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4A90E2'))
    header_text_style = ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke)
    
    # Colorear bloques de electivos (tarde)
    elective_blocks_style = ('BACKGROUND', (1, 7), (-1, 9), colors.HexColor('#F3F8FF'))
    
    # Colorear columna de horas
    time_column_style = ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#F7F7F7'))
    
    table.setStyle(TableStyle(common_style + [header_style_tbl, header_text_style, elective_blocks_style, time_column_style]))
    
    elements.append(table)

    # --- Pie de página ---
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        footer_text = f"GEM - Gestión Educativa Modular | Página {doc.page}"
        canvas.drawCentredString(A4[0] / 2, 0.3 * inch, footer_text)
        generation_text = f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        canvas.drawString(0.5 * inch, 0.3 * inch, generation_text)
        canvas.restoreState()

    doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    buffer.seek(0)
    
    return buffer

def generar_pdf_asistencia(estudiante, asistencia_data):
    """
    Genera un PDF de la asistencia del estudiante
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Título
    title = Paragraph(f"Reporte de Asistencia - {estudiante.usuario.nombre} {estudiante.usuario.apellido_paterno}", title_style)
    elements.append(title)
    
    # Información del estudiante
    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=20
    )
    
    info_text = f"""
    <b>Estudiante:</b> {estudiante.usuario.nombre} {estudiante.usuario.apellido_paterno}<br/>
    <b>RUT:</b> {estudiante.usuario.rut}<br/>
    <b>Curso:</b> {estudiante.curso}<br/>
    <b>Período:</b> Mes actual<br/>
    <b>Fecha de generación:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}
    """
    
    info_paragraph = Paragraph(info_text, info_style)
    elements.append(info_paragraph)
    elements.append(Spacer(1, 20))
    
    # Tabla de asistencia
    data = [['Asignatura', 'Total Clases', 'Presentes', 'Ausencias', 'Justificadas', 'Porcentaje', 'Estado']]
    
    for asignatura, datos in asistencia_data.items():
        if datos['sin_registro']:
            estado = 'Sin registro'
            porcentaje = 'N/A'
        else:
            porcentaje = f"{datos['porcentaje']:.1f}%"
            if datos['porcentaje'] >= 90:
                estado = 'Excelente'
            elif datos['porcentaje'] >= 80:
                estado = 'Regular'
            else:
                estado = 'Crítico'
        
        data.append([
            asignatura,
            'Sin registro' if datos['sin_registro'] else str(datos['total']),
            '-' if datos['sin_registro'] else str(datos['presentes']),
            '-' if datos['sin_registro'] else str(datos['ausentes']),
            '-' if datos['sin_registro'] else str(datos['justificados']),
            porcentaje,
            estado
        ])
    
    # Crear tabla
    table = Table(data, colWidths=[2*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1*inch])
    
    # Estilo de la tabla
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Alinear asignaturas a la izquierda
    ]))
    
    elements.append(table)
    
    # Construir PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer

def generar_pdf_calificaciones(estudiante, calificaciones_data, promedio):
    """
    Genera un PDF de calificaciones con un diseño tipo libreta de notas mejorado.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.4*inch, bottomMargin=0.4*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
    elements = []
    
    # --- Estilos ---
    styles = getSampleStyleSheet()
    style_normal_small = ParagraphStyle('NormalSmall', parent=styles['Normal'], fontSize=9)
    style_heading = ParagraphStyle('Heading', parent=styles['h2'], alignment=TA_CENTER, fontSize=14)
    
    # --- Encabezado ---
    logo_path = os.path.join(settings.BASE_DIR, 'Core', 'static', 'img', 'logo.png')
    logo = Image(logo_path, width=0.6*inch, height=0.6*inch)
    
    titulo = Paragraph("<b>INFORME DE CALIFICACIONES</b>", style_heading)
    fecha_actual = datetime.now()
    fecha_generacion = Paragraph(f"Chile, {fecha_actual.strftime('%d de %B de %Y')}", style_normal_small)
    
    header_table = Table([[logo, titulo, fecha_generacion]], colWidths=[0.8*inch, 5.7*inch, 2*inch], rowHeights=[0.6*inch])
    header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (1,0), (1,0), 30)]))
    elements.append(header_table)

    # --- Info del Estudiante ---
    profesor_jefe_nombre = "No asignado"
    if estudiante.curso and estudiante.curso.clases.first():
        docente = estudiante.curso.clases.first().asignatura_impartida.docente
        if docente:
            profesor_jefe_nombre = f"{docente.usuario.nombre} {docente.usuario.apellido_paterno}"
    
    info_data = [
        [Paragraph(f"<b>Nombre:</b> {estudiante.usuario.nombre} {estudiante.usuario.apellido_paterno}", style_normal_small),
         Paragraph(f"<b>Curso:</b> {estudiante.curso}", style_normal_small)],
        [Paragraph(f"<b>RUT:</b> {estudiante.usuario.rut}", style_normal_small),
         Paragraph(f"<b>Profesor(a) Jefe:</b> {profesor_jefe_nombre}", style_normal_small)],
        [Paragraph(f"<b>Año Escolar:</b> {fecha_actual.year}", style_normal_small), Paragraph('', style_normal_small)]
    ]
    info_table = Table(info_data, colWidths=[3.6*inch, 3.6*inch])
    info_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # --- Lógica de Semestres y Separación de Asignaturas ---
    MAX_GRADES_PER_SEMESTER = 6
    asignaturas_procesadas = {}
    no_ponderables = ['Orientación', 'Religión'] # Asignaturas a separar
    
    # Separar ponderables y no ponderables
    ponderables_data = {k: v for k, v in calificaciones_data.items() if k not in no_ponderables}
    no_ponderables_data = {k: v for k, v in calificaciones_data.items() if k in no_ponderables}

    for asignatura, evaluaciones in ponderables_data.items():
        sem1_grades = [ev['nota'] for ev in evaluaciones if ev['fecha'].month <= 7]
        sem2_grades = [ev['nota'] for ev in evaluaciones if ev['fecha'].month > 7]
        promedio_final = sum(sem1_grades + sem2_grades) / len(sem1_grades + sem2_grades) if (sem1_grades + sem2_grades) else 0
        asignaturas_procesadas[asignatura] = {'sem1': sem1_grades, 'sem2': sem2_grades, 'pf': promedio_final}

    # --- Tabla Principal de Calificaciones ---
    def create_calificaciones_table(data_source, title, include_promedio_row=False):
        header_style = ParagraphStyle('HeaderStyle', fontName='Helvetica-Bold', fontSize=8, alignment=TA_CENTER)
        cell_style = ParagraphStyle('CellStyle', fontSize=8, alignment=TA_CENTER)
        title_style = ParagraphStyle('TitleStyle', parent=header_style, alignment=TA_LEFT)

        data = [[Paragraph(f"<b>{title}</b>", title_style)] + [Paragraph('', cell_style)] * (MAX_GRADES_PER_SEMESTER * 2 + 1)]
        span_cmds = []
        
        # Merge de celdas para semestres
        data[0][1] = Paragraph("<b>Primer semestre</b>", header_style)
        data[0][1+MAX_GRADES_PER_SEMESTER] = Paragraph("<b>Segundo semestre</b>", header_style)
        data[0][-1] = Paragraph("<b>PF</b>", header_style)
        span_cmds.extend([
            ('SPAN', (1, 0), (MAX_GRADES_PER_SEMESTER, 0)),
            ('SPAN', (1+MAX_GRADES_PER_SEMESTER, 0), (2*MAX_GRADES_PER_SEMESTER, 0)),
        ])

        def format_grade(grade):
            style = ParagraphStyle('Grade', alignment=TA_CENTER, fontSize=8)
            if grade < 4.0:
                style.textColor = colors.red
            return Paragraph(f"{grade:.1f}", style)

        for asignatura, datos in data_source.items():
            row = [Paragraph(asignatura, ParagraphStyle('Sub', fontSize=8, alignment=TA_LEFT))]
            row.extend([format_grade(datos['sem1'][i]) if i < len(datos['sem1']) else Paragraph('', cell_style) for i in range(MAX_GRADES_PER_SEMESTER)])
            row.extend([format_grade(datos['sem2'][i]) if i < len(datos['sem2']) else Paragraph('', cell_style) for i in range(MAX_GRADES_PER_SEMESTER)])
            row.append(Paragraph(f"<b>{datos['pf']:.1f}</b>", ParagraphStyle('PF', alignment=TA_CENTER, fontSize=8, fontName='Helvetica-Bold')))
            data.append(row)
        
        if include_promedio_row:
            promedio_row = [Paragraph("<b>Promedio del estudiante</b>", ParagraphStyle('Sub', fontSize=8, fontName='Helvetica-Bold'))]
            promedio_row.extend([Paragraph('', cell_style)] * (MAX_GRADES_PER_SEMESTER * 2))
            promedio_row.append(Paragraph(f"<b>{promedio:.1f}</b>", ParagraphStyle('PF', alignment=TA_CENTER, fontSize=8, fontName='Helvetica-Bold')))
            data.append(promedio_row)

        col_widths = [1.8*inch] + [0.35*inch] * (MAX_GRADES_PER_SEMESTER * 2) + [0.4*inch]
        table = Table(data, colWidths=col_widths, rowHeights=0.25*inch)
        table.setStyle(TableStyle(span_cmds + [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E0E0E0')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.darkgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#F0F0F0')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E0E0E0') if include_promedio_row else None),
        ]))
        return table

    elements.append(create_calificaciones_table(asignaturas_procesadas, "Asignaturas ponderables", include_promedio_row=True))
    
    # --- Tabla de Asignaturas No Ponderables (si existen) ---
    if no_ponderables_data:
        elements.append(Spacer(1, 0.2*inch))
        # Se asume que no tienen notas numéricas, por lo que se muestran vacías
        no_ponderables_proc = {k: {'sem1': [], 'sem2': [], 'pf': ''} for k in no_ponderables_data}
        elements.append(create_calificaciones_table(no_ponderables_proc, "Asignaturas no ponderables"))
        
    # --- Firma ---
    elements.append(Spacer(1, 0.5*inch))
    signature_line = Table([
        [Paragraph("________________________", style_normal_small)],
        [Paragraph("Firma Director(a)", style_normal_small)]
    ], colWidths=[2.5*inch])
    signature_line.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    
    # Alinear la firma a la derecha
    signature_container = Table([[signature_line]], colWidths=[8.5*inch])
    signature_container.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'RIGHT')]))
    elements.append(signature_container)

    doc.build(elements)
    buffer.seek(0)
    return buffer

def generar_pdf_reporte_cursos(cursos_data, periodo_info):
    """
    Genera un PDF del reporte de rendimiento por cursos para administradores.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # --- Cabecera con Logo y Título ---
    logo_path = os.path.join(settings.BASE_DIR, 'Core', 'static', 'img', 'logo.png')
    logo = Image(logo_path, width=1*inch, height=1*inch)
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#2c3e50'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=20
    )
    
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#34495e'),
        alignment=TA_CENTER,
        fontName='Helvetica',
        spaceAfter=30
    )
    
    title_text = Paragraph("REPORTE DE RENDIMIENTO POR CURSOS", title_style)
    subtitle_text = Paragraph(f"Colegio GEM - Período: {periodo_info['fecha_inicio']} al {periodo_info['fecha_fin']}", subtitle_style)
    
    # Tabla de cabecera
    header_table = Table([[logo, title_text]], colWidths=[1.5*inch, 6*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (1, 0), (1, 0), 20),
    ]))
    
    elements.append(header_table)
    elements.append(subtitle_text)
    elements.append(Spacer(1, 0.3*inch))
    
    # --- Información General ---
    fecha_generacion = datetime.now().strftime('%d/%m/%Y %H:%M')
    total_cursos = len([c for c in cursos_data if c['total_estudiantes'] > 0])
    total_estudiantes = sum([c['total_estudiantes'] for c in cursos_data])
    total_evaluaciones = sum([c['total_evaluaciones'] for c in cursos_data])
    
    # Calcular promedio general
    promedios_validos = [c['promedio_curso'] for c in cursos_data if c['promedio_curso'] > 0]
    promedio_general = sum(promedios_validos) / len(promedios_validos) if promedios_validos else 0
    
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=20,
        borderBottomWidth=1,
        borderBottomColor=colors.lightgrey,
        borderBottomPadding=10
    )
    
    info_text = f"""
    <b>Fecha de generación:</b> {fecha_generacion}<br/>
    <b>Total de cursos activos:</b> {total_cursos}<br/>
    <b>Total de estudiantes:</b> {total_estudiantes}<br/>
    <b>Total de evaluaciones:</b> {total_evaluaciones:,}<br/>
    <b>Promedio general del colegio:</b> {promedio_general:.2f}
    """
    
    info_paragraph = Paragraph(info_text, info_style)
    elements.append(info_paragraph)
    elements.append(Spacer(1, 0.2*inch))
    
    # --- Tabla Principal de Datos ---
    # Encabezados de la tabla
    headers = [
        'Curso', 'Estudiantes', 'Evaluaciones', 'Promedio', 
        'Aprobación', 'Asistencia', 'Estado'
    ]
    
    data = [headers]
    
    # Datos de los cursos
    for curso in cursos_data:
        if curso['total_estudiantes'] == 0:
            # Curso sin estudiantes
            row = [
                curso['curso'],
                '0',
                '0',
                '0.00',
                '0.0%',
                '0.0%',
                'N/A'
            ]
        else:
            # Curso con estudiantes
            row = [
                curso['curso'],
                str(curso['total_estudiantes']),
                f"{curso['total_evaluaciones']:,}",
                f"{curso['promedio_curso']:.2f}",
                f"{curso['porcentaje_aprobacion']:.1f}%",
                f"{curso['porcentaje_asistencia']:.1f}%",
                curso.get('estado', 'N/A')
            ]
        data.append(row)
    
    # Crear tabla
    table = Table(data, colWidths=[0.8*inch, 0.8*inch, 1*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch])
    
    # Estilos de la tabla
    table_style = [
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Contenido
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        
        # Alternar colores de filas
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]
    
    # Agregar colores específicos para el estado
    for i, curso in enumerate(cursos_data, 1):
        estado = curso.get('estado', 'N/A')
        if estado == 'Crítico':
            table_style.append(('BACKGROUND', (6, i), (6, i), colors.HexColor('#e74c3c')))
            table_style.append(('TEXTCOLOR', (6, i), (6, i), colors.white))
        elif estado == 'Regular':
            table_style.append(('BACKGROUND', (6, i), (6, i), colors.HexColor('#f39c12')))
            table_style.append(('TEXTCOLOR', (6, i), (6, i), colors.white))
        elif estado == 'Bueno':
            table_style.append(('BACKGROUND', (6, i), (6, i), colors.HexColor('#27ae60')))
            table_style.append(('TEXTCOLOR', (6, i), (6, i), colors.white))
    
    table.setStyle(TableStyle(table_style))
    elements.append(table)
    
    # --- Resumen por Estado ---
    elements.append(Spacer(1, 0.3*inch))
    
    # Contar cursos por estado
    estados_count = {'Crítico': 0, 'Regular': 0, 'Bueno': 0, 'N/A': 0}
    for curso in cursos_data:
        estado = curso.get('estado', 'N/A')
        estados_count[estado] = estados_count.get(estado, 0) + 1
    
    resumen_style = ParagraphStyle(
        'ResumenStyle',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica-Bold',
        spaceAfter=10
    )
    
    resumen_title = Paragraph("RESUMEN POR ESTADO DE ASISTENCIA:", resumen_style)
    elements.append(resumen_title)
    
    # Tabla de resumen
    resumen_data = [
        ['Estado', 'Cantidad de Cursos', 'Criterio'],
        ['🔴 Crítico', str(estados_count['Crítico']), '< 83% asistencia'],
        ['🟡 Regular', str(estados_count['Regular']), '83% - 85% asistencia'],
        ['🟢 Bueno', str(estados_count['Bueno']), '> 85% asistencia'],
        ['⚪ N/A', str(estados_count['N/A']), 'Sin estudiantes']
    ]
    
    resumen_table = Table(resumen_data, colWidths=[1.5*inch, 1.5*inch, 2*inch])
    resumen_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    
    elements.append(resumen_table)
    
    # --- Ranking de Cursos ---
    elements.append(Spacer(1, 0.3*inch))
    
    ranking_title = Paragraph("RANKING POR PROMEDIO ACADÉMICO:", resumen_style)
    elements.append(ranking_title)
    
    # Ordenar cursos por promedio (solo los que tienen estudiantes)
    cursos_con_estudiantes = [c for c in cursos_data if c['total_estudiantes'] > 0]
    cursos_ordenados = sorted(cursos_con_estudiantes, key=lambda x: x['promedio_curso'], reverse=True)
    
    ranking_data = [['Posición', 'Curso', 'Promedio', 'Estudiantes']]
    
    for i, curso in enumerate(cursos_ordenados, 1):
        ranking_data.append([
            f"{i}°",
            curso['curso'],
            f"{curso['promedio_curso']:.2f}",
            str(curso['total_estudiantes'])
        ])
    
    ranking_table = Table(ranking_data, colWidths=[0.8*inch, 1*inch, 1*inch, 1*inch])
    ranking_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    
    # Destacar los primeros 3 lugares
    if len(cursos_ordenados) >= 1:
        ranking_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f1c40f')),  # Oro
        ]))
    if len(cursos_ordenados) >= 2:
        ranking_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#bdc3c7')),  # Plata
        ]))
    if len(cursos_ordenados) >= 3:
        ranking_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#cd7f32')),  # Bronce
        ]))
    
    elements.append(ranking_table)
    
    # --- Pie de página ---
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        footer_text = f"GEM - Gestión Educativa Modular | Reporte generado el {fecha_generacion} | Página {doc.page}"
        canvas.drawCentredString(A4[0] / 2, 0.3 * inch, footer_text)
        canvas.restoreState()
    
    # Construir PDF
    doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    buffer.seek(0)
    
    return buffer

def generar_pdf_reporte_asistencia(cursos_data, periodo_info):
    """
    Genera un PDF del reporte de asistencia por cursos para administradores.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # --- Cabecera con Logo y Título ---
    logo_path = os.path.join(settings.BASE_DIR, 'Core', 'static', 'img', 'logo.png')
    logo = Image(logo_path, width=1*inch, height=1*inch)
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#2c3e50'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=20
    )
    
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#34495e'),
        alignment=TA_CENTER,
        fontName='Helvetica',
        spaceAfter=30
    )
    
    title_text = Paragraph("REPORTE DE ASISTENCIA POR CURSOS", title_style)
    subtitle_text = Paragraph(f"Colegio GEM - Período: {periodo_info['fecha_inicio']} al {periodo_info['fecha_fin']}", subtitle_style)
    
    # Tabla de cabecera
    header_table = Table([[logo, title_text]], colWidths=[1.5*inch, 6*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (1, 0), (1, 0), 20),
    ]))
    
    elements.append(header_table)
    elements.append(subtitle_text)
    elements.append(Spacer(1, 0.3*inch))
    
    # --- Información General ---
    fecha_generacion = datetime.now().strftime('%d/%m/%Y %H:%M')
    total_cursos = len([c for c in cursos_data if c['total_estudiantes'] > 0])
    total_estudiantes = sum([c['total_estudiantes'] for c in cursos_data])
    total_registros = sum([c['total_registros'] for c in cursos_data])
    total_presentes = sum([c['presentes'] for c in cursos_data])
    total_ausentes = sum([c['ausentes'] for c in cursos_data])
    
    # Calcular promedio general de asistencia
    promedio_asistencia = (total_presentes / total_registros * 100) if total_registros > 0 else 0
    
    # Contar estudiantes en riesgo
    total_estudiantes_riesgo = sum([c['estudiantes_riesgo'] for c in cursos_data])
    
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=20,
        borderBottomWidth=1,
        borderBottomColor=colors.lightgrey,
        borderBottomPadding=10
    )
    
    info_text = f"""
    <b>Fecha de generación:</b> {fecha_generacion}<br/>
    <b>Total de cursos activos:</b> {total_cursos}<br/>
    <b>Total de estudiantes:</b> {total_estudiantes}<br/>
    <b>Total de registros de asistencia:</b> {total_registros:,}<br/>
    <b>Promedio general de asistencia:</b> {promedio_asistencia:.1f}%<br/>
    <b>Estudiantes en riesgo (&lt;85%):</b> {total_estudiantes_riesgo}
    """
    
    info_paragraph = Paragraph(info_text, info_style)
    elements.append(info_paragraph)
    elements.append(Spacer(1, 0.2*inch))
    
    # --- Tabla Principal de Datos ---
    # Encabezados de la tabla
    headers = [
        'Curso', 'Estudiantes', 'Registros', 'Presentes', 
        'Ausentes', '% Asistencia', 'En Riesgo', 'Estado'
    ]
    
    data = [headers]
    
    # Datos de los cursos
    for curso in cursos_data:
        if curso['total_estudiantes'] == 0:
            # Curso sin estudiantes
            row = [
                curso['curso'],
                '0',
                '0',
                '0',
                '0',
                '0.0%',
                '0',
                'N/A'
            ]
        else:
            # Curso con estudiantes
            row = [
                curso['curso'],
                str(curso['total_estudiantes']),
                f"{curso['total_registros']:,}",
                f"{curso['presentes']:,}",
                f"{curso['ausentes']:,}",
                f"{curso['porcentaje_asistencia']:.1f}%",
                str(curso['estudiantes_riesgo']),
                curso.get('estado', 'N/A')
            ]
        data.append(row)
    
    # Crear tabla
    table = Table(data, colWidths=[0.7*inch, 0.7*inch, 0.8*inch, 0.7*inch, 0.7*inch, 0.8*inch, 0.6*inch, 0.7*inch])
    
    # Estilos de la tabla
    table_style = [
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f39c12')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Contenido
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        
        # Alternar colores de filas
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]
    
    # Agregar colores específicos para el estado
    for i, curso in enumerate(cursos_data, 1):
        estado = curso.get('estado', 'N/A')
        if estado == 'Crítico':
            table_style.append(('BACKGROUND', (7, i), (7, i), colors.HexColor('#e74c3c')))
            table_style.append(('TEXTCOLOR', (7, i), (7, i), colors.white))
        elif estado == 'Regular':
            table_style.append(('BACKGROUND', (7, i), (7, i), colors.HexColor('#f39c12')))
            table_style.append(('TEXTCOLOR', (7, i), (7, i), colors.white))
        elif estado == 'Bueno':
            table_style.append(('BACKGROUND', (7, i), (7, i), colors.HexColor('#27ae60')))
            table_style.append(('TEXTCOLOR', (7, i), (7, i), colors.white))
        
        # Colorear columna de estudiantes en riesgo
        if curso['estudiantes_riesgo'] > 0:
            table_style.append(('BACKGROUND', (6, i), (6, i), colors.HexColor('#e67e22')))
            table_style.append(('TEXTCOLOR', (6, i), (6, i), colors.white))
    
    table.setStyle(TableStyle(table_style))
    elements.append(table)
    
    # --- Análisis por Rangos de Asistencia ---
    elements.append(Spacer(1, 0.3*inch))
    
    # Contar cursos por rango de asistencia
    rangos = {
        'Excelente (>90%)': 0,
        'Bueno (85-90%)': 0,
        'Regular (83-85%)': 0,
        'Crítico (<83%)': 0,
        'Sin datos': 0
    }
    
    for curso in cursos_data:
        asistencia = curso['porcentaje_asistencia']
        if asistencia == 0:
            rangos['Sin datos'] += 1
        elif asistencia >= 90:
            rangos['Excelente (>90%)'] += 1
        elif asistencia >= 85:
            rangos['Bueno (85-90%)'] += 1
        elif asistencia >= 83:
            rangos['Regular (83-85%)'] += 1
        else:
            rangos['Crítico (<83%)'] += 1
    
    resumen_style = ParagraphStyle(
        'ResumenStyle',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica-Bold',
        spaceAfter=10
    )
    
    resumen_title = Paragraph("ANÁLISIS POR RANGOS DE ASISTENCIA:", resumen_style)
    elements.append(resumen_title)
    
    # Tabla de rangos
    rangos_data = [['Rango de Asistencia', 'Cantidad de Cursos', 'Porcentaje']]
    
    total_cursos_con_datos = sum(rangos.values())
    for rango, cantidad in rangos.items():
        porcentaje = (cantidad / total_cursos_con_datos * 100) if total_cursos_con_datos > 0 else 0
        rangos_data.append([rango, str(cantidad), f"{porcentaje:.1f}%"])
    
    rangos_table = Table(rangos_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    rangos_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    
    elements.append(rangos_table)
    
    # --- Cursos con Mayor Riesgo ---
    elements.append(Spacer(1, 0.3*inch))
    
    # Filtrar cursos con estudiantes en riesgo
    cursos_con_riesgo = [c for c in cursos_data if c['estudiantes_riesgo'] > 0]
    cursos_con_riesgo.sort(key=lambda x: x['estudiantes_riesgo'], reverse=True)
    
    if cursos_con_riesgo:
        riesgo_title = Paragraph("CURSOS CON ESTUDIANTES EN RIESGO:", resumen_style)
        elements.append(riesgo_title)
        
        riesgo_data = [['Curso', 'Estudiantes en Riesgo', 'Total Estudiantes', '% en Riesgo']]
        
        for curso in cursos_con_riesgo[:10]:  # Top 10
            porcentaje_riesgo = (curso['estudiantes_riesgo'] / curso['total_estudiantes'] * 100)
            riesgo_data.append([
                curso['curso'],
                str(curso['estudiantes_riesgo']),
                str(curso['total_estudiantes']),
                f"{porcentaje_riesgo:.1f}%"
            ])
        
        riesgo_table = Table(riesgo_data, colWidths=[1*inch, 1.5*inch, 1.5*inch, 1*inch])
        riesgo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        
        elements.append(riesgo_table)
    else:
        no_riesgo_text = Paragraph("✅ <b>¡Excelente!</b> No hay cursos con estudiantes en riesgo de asistencia.", 
                                 ParagraphStyle('NoRiesgo', parent=styles['Normal'], fontSize=12, 
                                              textColor=colors.HexColor('#27ae60'), alignment=TA_CENTER))
        elements.append(no_riesgo_text)
    
    # --- Pie de página ---
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        footer_text = f"GEM - Gestión Educativa Modular | Reporte generado el {fecha_generacion} | Página {doc.page}"
        canvas.drawCentredString(A4[0] / 2, 0.3 * inch, footer_text)
        canvas.restoreState()
    
    # Construir PDF
    doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    buffer.seek(0)
    
    return buffer

def generar_pdf_reporte_estudiantes_riesgo(data_riesgo, periodo_info):
    """
    Genera un PDF del reporte de estudiantes en riesgo para administradores con diseño mejorado.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        topMargin=0.7*inch, 
        bottomMargin=0.7*inch,
        leftMargin=0.7*inch,
        rightMargin=0.7*inch
    )
    elements = []
    
    styles = getSampleStyleSheet()
    
    # --- Cabecera Mejorada con Diseño Profesional ---
    logo_path = os.path.join(settings.BASE_DIR, 'Core', 'static', 'img', 'logo.png')
    logo = Image(logo_path, width=0.8*inch, height=0.8*inch)
    
    # Estilos mejorados con gradientes y sombras visuales
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=26,
        textColor=colors.HexColor('#1a202c'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=15,
        spaceBefore=15,
        borderWidth=0,
        borderPadding=10
    )
    
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#2d3748'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=5
    )
    
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#718096'),
        alignment=TA_CENTER,
        fontName='Helvetica',
        spaceAfter=30
    )
    
    titulo_reporte = periodo_info.get('titulo_reporte', 'REPORTE DE ESTUDIANTES EN RIESGO')
    tipo_reporte = periodo_info.get('tipo_reporte', 'completo')
    
    # Cabecera con fondo de color
    header_bg = Table([['']], colWidths=[7.5*inch])
    header_bg.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f7fafc')),
        ('GRID', (0, 0), (-1, -1), 0, colors.white),
    ]))
    
    title_text = Paragraph(titulo_reporte, title_style)
    subtitle_text = Paragraph(f"Colegio GEM - Sistema de Gestión Educativa", subtitle_style)
    date_text = Paragraph(f"Período: {periodo_info['fecha_inicio']} al {periodo_info['fecha_fin']}", date_style)
    
    # Tabla de cabecera mejorada con diseño más elegante
    header_content = Table([
        [logo, title_text],
        ['', subtitle_text],
        ['', date_text]
    ], colWidths=[1.2*inch, 6.3*inch])
    
    header_content.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('LEFTPADDING', (1, 0), (1, -1), 0),
        ('RIGHTPADDING', (1, 0), (1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 3, colors.HexColor('#4a5568')),
        ('ROUNDEDCORNERS', (0, 0), (-1, -1), 5),
    ]))
    
    elements.append(header_content)
    elements.append(Spacer(1, 0.4*inch))
    
    # --- Información General Mejorada ---
    fecha_generacion = datetime.now().strftime('%d/%m/%Y a las %H:%M hrs')
    
    riesgo_notas = data_riesgo.get('riesgo_notas', [])
    riesgo_asistencia = data_riesgo.get('riesgo_asistencia', [])
    
    total_riesgo_notas = len(riesgo_notas)
    total_riesgo_asistencia = len(riesgo_asistencia)
    
    # Calcular estudiantes únicos en riesgo
    ruts_notas = set([est['rut'] for est in riesgo_notas])
    ruts_asistencia = set([est['rut'] for est in riesgo_asistencia])
    total_estudiantes_unicos = len(ruts_notas.union(ruts_asistencia))
    
    # Calcular estadísticas adicionales
    cursos_afectados = set([est['curso'] for est in riesgo_notas + riesgo_asistencia])
    
    # Panel de información con diseño de tarjetas
    info_title_style = ParagraphStyle(
        'InfoTitleStyle',
        parent=styles['Normal'],
        fontSize=14,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#2d3748'),
        spaceAfter=15
    )
    
    info_title = Paragraph("📊 RESUMEN EJECUTIVO", info_title_style)
    elements.append(info_title)
    
    # Crear tarjetas de estadísticas con diseño mejorado
    stats_data = [
        ['📊 MÉTRICA', 'VALOR', 'ESTADO', 'DESCRIPCIÓN'],
        [
            '🎓 Riesgo Académico',
            str(total_riesgo_notas),
            '🔴 CRÍTICO' if total_riesgo_notas > 0 else '✅ ÓPTIMO',
            'Estudiantes con promedio inferior a 4.0'
        ],
        [
            '📅 Riesgo Asistencia',
            str(total_riesgo_asistencia),
            '🟡 ALERTA' if total_riesgo_asistencia > 0 else '✅ ÓPTIMO',
            'Estudiantes con asistencia inferior al 85%'
        ],
        [
            '👥 Total Únicos',
            str(total_estudiantes_unicos),
            '📋 SEGUIMIENTO' if total_estudiantes_unicos > 0 else '✅ SIN RIESGO',
            'Estudiantes que requieren atención especial'
        ],
        [
            '🏫 Cursos Afectados',
            str(len(cursos_afectados)),
            '🔍 MONITOREO' if len(cursos_afectados) > 0 else '✅ TODOS OK',
            'Cursos con estudiantes en situación de riesgo'
        ]
    ]
    
    stats_table = Table(stats_data, colWidths=[1.6*inch, 1*inch, 1.4*inch, 2.5*inch])
    stats_table.setStyle(TableStyle([
        # Encabezado con gradiente visual
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a202c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 15),
        ('TOPPADDING', (0, 0), (-1, 0), 15),
        
        # Contenido con mejor legibilidad
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (2, -1), 'CENTER'),
        ('ALIGN', (3, 1), (3, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1.5, colors.HexColor('#cbd5e0')),
        
        # Colores alternados más suaves
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f7fafc'), colors.HexColor('#edf2f7')]),
        ('TOPPADDING', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(stats_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # --- Información del Reporte ---
    report_info_style = ParagraphStyle(
        'ReportInfoStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#718096'),
        spaceAfter=20,
        leftIndent=20,
        rightIndent=20
    )
    
    report_info_text = f"""
    <b>📅 Fecha de generación:</b> {fecha_generacion} | 
    <b>📈 Tipo de reporte:</b> {tipo_reporte.upper()} | 
    <b>🎯 Criterios:</b> Académico &lt; 4.0, Asistencia &lt; 85%
    """
    
    report_info = Paragraph(report_info_text, report_info_style)
    
    # Crear caja de información
    info_box = Table([[report_info]], colWidths=[6.5*inch])
    info_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#edf2f7')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0')),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
    ]))
    
    elements.append(info_box)
    elements.append(Spacer(1, 0.3*inch))
    
    # --- Resumen Ejecutivo para Sin Riesgo ---
    if total_estudiantes_unicos == 0:
        success_style = ParagraphStyle(
            'SuccessStyle',
            parent=styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#38a169'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=20,
            spaceBefore=20
        )
        
        success_box_style = ParagraphStyle(
            'SuccessBoxStyle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#2f855a'),
            alignment=TA_CENTER,
            spaceAfter=30
        )
        
        success_text = Paragraph("🏆 ¡FELICITACIONES! SITUACIÓN ÓPTIMA", success_style)
        elements.append(success_text)
        
        # Mensaje de éxito mejorado con más detalle
        success_message = Paragraph(
            "🎉 <b>EXCELENTE DESEMPEÑO INSTITUCIONAL</b> 🎉<br/><br/>"
            "El Colegio GEM mantiene estándares excepcionales en todas las áreas evaluadas.<br/>"
            "Todos los estudiantes cumplen satisfactoriamente con los criterios establecidos.<br/><br/>"
            "<b>✅ Rendimiento Académico:</b> EXCELENTE - Todos los estudiantes sobre 4.0<br/>"
            "<b>✅ Asistencia Escolar:</b> ÓPTIMA - Todos los estudiantes sobre 85%<br/>"
            "<b>✅ Seguimiento:</b> PREVENTIVO - Monitoreo continuo activo<br/><br/>"
            "<i>Este resultado refleja el compromiso conjunto de estudiantes, familias y equipo educativo.</i>",
            success_box_style
        )
        
        # Caja de éxito con diseño mejorado
        success_table = Table([[success_message]], colWidths=[6.5*inch])
        success_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0fff4')),
            ('BOX', (0, 0), (-1, -1), 3, colors.HexColor('#38a169')),
            ('TOPPADDING', (0, 0), (-1, -1), 25),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 25),
            ('LEFTPADDING', (0, 0), (-1, -1), 25),
            ('RIGHTPADDING', (0, 0), (-1, -1), 25),
        ]))
        
        elements.append(success_table)
        
        # Agregar mensaje de recomendaciones para mantener el buen nivel
        elements.append(Spacer(1, 0.3*inch))
        
        maintenance_title = Paragraph("💡 RECOMENDACIONES PARA MANTENER LA EXCELENCIA", ParagraphStyle(
            'MaintenanceTitle',
            parent=styles['Normal'],
            fontSize=14,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#2d3748'),
            spaceAfter=15
        ))
        elements.append(maintenance_title)
        
        maintenance_recommendations = [
            "• Continuar con el sistema de monitoreo preventivo actual",
            "• Mantener comunicación fluida entre docentes, estudiantes y familias",
            "• Realizar seguimiento trimestral para detectar cambios tempranos",
            "• Fortalecer programas de apoyo académico y socioemocional",
            "• Celebrar y reconocer los logros alcanzados por la comunidad educativa"
        ]
        
        for rec in maintenance_recommendations:
            rec_paragraph = Paragraph(rec, ParagraphStyle(
                'MaintenanceRec',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=5,
                leftIndent=20,
                textColor=colors.HexColor('#2d3748')
            ))
            elements.append(rec_paragraph)
    else:
        # --- Secciones de Riesgo con Diseño Mejorado ---
        
        # Definir estilos comunes para todas las secciones
        criteria_style = ParagraphStyle(
            'CriteriaStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#718096'),
            spaceAfter=20,
            leftIndent=20
        )
        
        critical_style = ParagraphStyle(
            'CriticalStyle',
            parent=styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#c53030'),
            spaceAfter=10
        )
        
        moderate_style = ParagraphStyle(
            'ModerateStyle',
            parent=styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#d69e2e'),
            spaceAfter=10
        )
        
        # Estudiantes en Riesgo Académico
        if riesgo_notas:
            elements.append(PageBreak())  # Nueva página para mejor legibilidad
            
            academic_title_style = ParagraphStyle(
                'AcademicTitleStyle',
                parent=styles['Normal'],
                fontSize=16,
                fontName='Helvetica-Bold',
                textColor=colors.HexColor('#e53e3e'),
                spaceAfter=15,
                spaceBefore=10
            )
            
            academic_title = Paragraph(f"🔴 ESTUDIANTES EN RIESGO ACADÉMICO ({len(riesgo_notas)})", academic_title_style)
            elements.append(academic_title)
            
            # Descripción del criterio
            criteria_text = Paragraph(
                "<b>Criterio:</b> Estudiantes con promedio general inferior a 4.0 (nota mínima de aprobación)<br/>"
                "<b>Acción requerida:</b> Intervención académica inmediata",
                criteria_style
            )
            elements.append(criteria_text)
            
            # Separar por nivel de riesgo
            riesgo_critico = [e for e in riesgo_notas if e['promedio'] < 3.0]
            riesgo_moderado = [e for e in riesgo_notas if e['promedio'] >= 3.0]
            
            if riesgo_critico:
                
                critical_title = Paragraph(f"⚠️ RIESGO CRÍTICO (< 3.0) - {len(riesgo_critico)} estudiantes", critical_style)
                elements.append(critical_title)
                
                # Tabla para riesgo crítico
                critical_headers = ['N°', 'Nombre Completo', 'RUT', 'Curso', 'Promedio', 'Evaluaciones', 'Estado']
                critical_data = [critical_headers]
                
                for i, est in enumerate(riesgo_critico, 1):
                    critical_data.append([
                        str(i),
                        est['nombre'],
                        est['rut'],
                        est['curso'],
                        f"{est['promedio']:.2f}",
                        str(est['total_evaluaciones']),
                        '🚨 URGENTE'
                    ])
                
                critical_table = Table(critical_data, colWidths=[0.3*inch, 2*inch, 0.8*inch, 0.6*inch, 0.6*inch, 0.7*inch, 0.8*inch])
                critical_table.setStyle(TableStyle([
                    # Encabezado
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c53030')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    
                    # Contenido
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                    ('ALIGN', (1, 1), (1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                    
                    # Filas alternadas
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#fed7d7'), colors.white]),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                
                elements.append(critical_table)
                elements.append(Spacer(1, 0.2*inch))
            
            if riesgo_moderado:
                moderate_title = Paragraph(f"⚡ RIESGO MODERADO (3.0 - 3.9) - {len(riesgo_moderado)} estudiantes", moderate_style)
                elements.append(moderate_title)
                
                # Tabla para riesgo moderado
                moderate_headers = ['N°', 'Nombre Completo', 'RUT', 'Curso', 'Promedio', 'Evaluaciones', 'Recomendación']
                moderate_data = [moderate_headers]
                
                for i, est in enumerate(riesgo_moderado, 1):
                    moderate_data.append([
                        str(i),
                        est['nombre'],
                        est['rut'],
                        est['curso'],
                        f"{est['promedio']:.2f}",
                        str(est['total_evaluaciones']),
                        '📚 Refuerzo'
                    ])
                
                moderate_table = Table(moderate_data, colWidths=[0.3*inch, 2*inch, 0.8*inch, 0.6*inch, 0.6*inch, 0.7*inch, 0.8*inch])
                moderate_table.setStyle(TableStyle([
                    # Encabezado
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d69e2e')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    
                    # Contenido
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                    ('ALIGN', (1, 1), (1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                    
                    # Filas alternadas
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#faf089'), colors.white]),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                
                elements.append(moderate_table)
        
        # Estudiantes en Riesgo de Asistencia
        if riesgo_asistencia:
            if riesgo_notas:  # Solo agregar página nueva si ya hay contenido académico
                elements.append(PageBreak())
            
            attendance_title_style = ParagraphStyle(
                'AttendanceTitleStyle',
                parent=styles['Normal'],
                fontSize=16,
                fontName='Helvetica-Bold',
                textColor=colors.HexColor('#d69e2e'),
                spaceAfter=15,
                spaceBefore=10
            )
            
            attendance_title = Paragraph(f"🟡 ESTUDIANTES EN RIESGO DE ASISTENCIA ({len(riesgo_asistencia)})", attendance_title_style)
            elements.append(attendance_title)
            
            # Descripción del criterio
            attendance_criteria_text = Paragraph(
                "<b>Criterio:</b> Estudiantes con porcentaje de asistencia inferior al 85%<br/>"
                "<b>Acción requerida:</b> Contacto inmediato con apoderados",
                criteria_style
            )
            elements.append(attendance_criteria_text)
            
            # Separar por nivel de riesgo de asistencia
            asistencia_critica = [e for e in riesgo_asistencia if e['asistencia'] < 70]
            asistencia_moderada = [e for e in riesgo_asistencia if e['asistencia'] >= 70]
            
            if asistencia_critica:
                critical_attendance_title = Paragraph(f"🚨 ASISTENCIA CRÍTICA (< 70%) - {len(asistencia_critica)} estudiantes", critical_style)
                elements.append(critical_attendance_title)
                
                # Tabla para asistencia crítica
                critical_att_headers = ['N°', 'Nombre Completo', 'RUT', 'Curso', 'Asistencia', 'Registros', 'Prioridad']
                critical_att_data = [critical_att_headers]
                
                for i, est in enumerate(asistencia_critica, 1):
                    critical_att_data.append([
                        str(i),
                        est['nombre'],
                        est['rut'],
                        est['curso'],
                        f"{est['asistencia']:.1f}%",
                        str(est['total_asistencias']),
                        '🔥 ALTA'
                    ])
                
                critical_att_table = Table(critical_att_data, colWidths=[0.3*inch, 2*inch, 0.8*inch, 0.6*inch, 0.7*inch, 0.7*inch, 0.7*inch])
                critical_att_table.setStyle(TableStyle([
                    # Encabezado
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c53030')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    
                    # Contenido
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                    ('ALIGN', (1, 1), (1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                    
                    # Filas alternadas
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#fed7d7'), colors.white]),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                
                elements.append(critical_att_table)
                elements.append(Spacer(1, 0.2*inch))
            
            if asistencia_moderada:
                moderate_att_title = Paragraph(f"⚠️ ASISTENCIA EN RIESGO (70% - 84%) - {len(asistencia_moderada)} estudiantes", moderate_style)
                elements.append(moderate_att_title)
                
                # Tabla para asistencia moderada (mostrar TODOS los estudiantes)
                moderate_att_headers = ['N°', 'Nombre Completo', 'RUT', 'Curso', 'Asistencia', 'Registros', 'Acción']
                moderate_att_data = [moderate_att_headers]
                
                for i, est in enumerate(asistencia_moderada, 1):  # Mostrar TODOS sin limitación
                    moderate_att_data.append([
                        str(i),
                        est['nombre'],
                        est['rut'],
                        est['curso'],
                        f"{est['asistencia']:.1f}%",
                        str(est['total_asistencias']),
                        '👁️ Monitorear'
                    ])
                
                moderate_att_table = Table(moderate_att_data, colWidths=[0.3*inch, 2*inch, 0.8*inch, 0.6*inch, 0.7*inch, 0.7*inch, 0.7*inch])
                moderate_att_table.setStyle(TableStyle([
                    # Encabezado
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d69e2e')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    
                    # Contenido
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                    ('ALIGN', (1, 1), (1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                    
                    # Filas alternadas
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#faf089'), colors.white]),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                
                elements.append(moderate_att_table)
        
        # --- Sección de Recomendaciones Mejorada ---
        elements.append(PageBreak())
        
        recommendations_title_style = ParagraphStyle(
            'RecommendationsTitleStyle',
            parent=styles['Normal'],
            fontSize=16,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#3182ce'),
            spaceAfter=20,
            spaceBefore=10
        )
        
        recommendations_title = Paragraph("💡 PLAN DE ACCIÓN Y RECOMENDACIONES", recommendations_title_style)
        elements.append(recommendations_title)
        
        if riesgo_notas:
            academic_rec_title = Paragraph("🎓 Para Estudiantes en Riesgo Académico:", ParagraphStyle(
                'AcademicRecTitle',
                parent=styles['Normal'],
                fontSize=12,
                fontName='Helvetica-Bold',
                textColor=colors.HexColor('#e53e3e'),
                spaceAfter=10
            ))
            elements.append(academic_rec_title)
            
            academic_recommendations = [
                "• Implementar tutorías personalizadas inmediatas (mínimo 2 horas semanales)",
                "• Establecer plan de reforzamiento en asignaturas con mayor dificultad",
                "• Reunión urgente con apoderados para establecer compromiso familiar",
                "• Seguimiento semanal del progreso académico",
                "• Derivación a psicopedagogo si es necesario",
                "• Evaluación diferenciada según necesidades específicas"
            ]
            
            for rec in academic_recommendations:
                rec_paragraph = Paragraph(rec, ParagraphStyle(
                    'RecParagraph',
                    parent=styles['Normal'],
                    fontSize=10,
                    spaceAfter=5,
                    leftIndent=20
                ))
                elements.append(rec_paragraph)
            
            elements.append(Spacer(1, 0.2*inch))
        
        if riesgo_asistencia:
            attendance_rec_title = Paragraph("📅 Para Estudiantes en Riesgo de Asistencia:", ParagraphStyle(
                'AttendanceRecTitle',
                parent=styles['Normal'],
                fontSize=12,
                fontName='Helvetica-Bold',
                textColor=colors.HexColor('#d69e2e'),
                spaceAfter=10
            ))
            elements.append(attendance_rec_title)
            
            attendance_recommendations = [
                "• Contacto telefónico inmediato con familia para investigar causas",
                "• Entrevista presencial con apoderados en un plazo máximo de 3 días",
                "• Evaluación de situación socioeconómica familiar",
                "• Derivación a asistente social si se detectan problemáticas familiares",
                "• Implementar sistema de seguimiento diario de asistencia",
                "• Establecer compromisos escritos con la familia",
                "• Considerar apoyo de transporte escolar si es necesario"
            ]
            
            for rec in attendance_recommendations:
                rec_paragraph = Paragraph(rec, ParagraphStyle(
                    'RecParagraph',
                    parent=styles['Normal'],
                    fontSize=10,
                    spaceAfter=5,
                    leftIndent=20
                ))
                elements.append(rec_paragraph)
        
        # Cronograma de seguimiento
        elements.append(Spacer(1, 0.3*inch))
        
        timeline_title = Paragraph("📋 CRONOGRAMA DE SEGUIMIENTO", ParagraphStyle(
            'TimelineTitle',
            parent=styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#3182ce'),
            spaceAfter=15
        ))
        elements.append(timeline_title)
        
        timeline_data = [
            ['Plazo', 'Acción', 'Responsable'],
            ['Inmediato (24 hrs)', 'Contacto con familias de casos críticos', 'Inspector General'],
            ['3 días', 'Entrevistas presenciales con apoderados', 'Profesor Jefe'],
            ['1 semana', 'Inicio de tutorías y reforzamiento', 'UTP'],
            ['2 semanas', 'Primera evaluación de progreso', 'Equipo Directivo'],
            ['1 mes', 'Reporte de seguimiento completo', 'Dirección']
        ]
        
        timeline_table = Table(timeline_data, colWidths=[1.5*inch, 3.5*inch, 1.5*inch])
        timeline_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3182ce')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(timeline_table)
    
    # --- Pie de página profesional mejorado ---
    def footer(canvas, doc):
        canvas.saveState()
        
        # Línea decorativa superior más elegante
        canvas.setStrokeColor(colors.HexColor('#4a5568'))
        canvas.setLineWidth(2)
        canvas.line(0.7*inch, 0.6*inch, A4[0] - 0.7*inch, 0.6*inch)
        
        # Línea decorativa inferior más sutil
        canvas.setStrokeColor(colors.HexColor('#e2e8f0'))
        canvas.setLineWidth(0.5)
        canvas.line(0.7*inch, 0.25*inch, A4[0] - 0.7*inch, 0.25*inch)
        
        # Texto del pie principal
        canvas.setFont('Helvetica-Bold', 9)
        canvas.setFillColor(colors.HexColor('#2d3748'))
        footer_main = f"GEM - Gestión Educativa Modular"
        canvas.drawCentredString(A4[0] / 2, 0.45 * inch, footer_main)
        
        # Información adicional
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#718096'))
        footer_info = f"Reporte generado el {fecha_generacion}"
        canvas.drawString(0.7 * inch, 0.35 * inch, footer_info)
        
        # Número de página
        page_info = f"Página {doc.page}"
        canvas.drawRightString(A4[0] - 0.7 * inch, 0.35 * inch, page_info)
        
        # Información de confidencialidad
        canvas.setFont('Helvetica', 7)
        canvas.setFillColor(colors.HexColor('#a0aec0'))
        confidential_text = "Documento confidencial - Uso exclusivo interno"
        canvas.drawCentredString(A4[0] / 2, 0.15 * inch, confidential_text)
        
        canvas.restoreState()
    
    # Construir PDF
    doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    buffer.seek(0)
    
    return buffer 

def generar_pdf_asistencia_estudiante(estudiante_data, periodo_info):
    """Generar PDF con reporte detallado de asistencia de un estudiante específico"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=0.7*inch, leftMargin=0.7*inch,
                          topMargin=1*inch, bottomMargin=0.8*inch)
    
    elements = []
    styles = getSampleStyleSheet()
    fecha_generacion = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    # --- Cabecera profesional ---
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Title'],
        fontSize=22,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1a202c'),
        alignment=1,
        spaceAfter=20,
        spaceBefore=10
    )
    
    header = Paragraph("📊 REPORTE DE ASISTENCIA INDIVIDUAL", header_style)
    elements.append(header)
    
    # Información del estudiante
    estudiante_info = estudiante_data['estudiante']
    student_info_style = ParagraphStyle(
        'StudentInfoStyle',
        parent=styles['Normal'],
        fontSize=14,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#2d3748'),
        alignment=1,
        spaceAfter=15
    )
    
    student_info = Paragraph(f"👤 {estudiante_info['nombre']} | RUT: {estudiante_info['rut']} | Curso: {estudiante_info['curso']}", student_info_style)
    elements.append(student_info)
    
    # Información del período
    period_style = ParagraphStyle(
        'PeriodStyle',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica',
        textColor=colors.HexColor('#718096'),
        alignment=1,
        spaceAfter=20
    )
    
    period_info = Paragraph(f"📅 Período: {periodo_info['fecha_inicio']} - {periodo_info['fecha_fin']}", period_style)
    elements.append(period_info)
    
    # --- Estadísticas generales ---
    stats = estudiante_data['estadisticas']
    
    # Crear tabla de estadísticas
    stats_data = [
        ['📊 Métrica', '📈 Valor', '📋 Detalle'],
        ['Total de Clases', str(stats['total_registros']), 'Clases registradas en el período'],
        ['Clases Presentes', str(stats['presentes']), f"✅ {stats['porcentaje_asistencia']}% de asistencia"],
        ['Clases Ausentes', str(stats['ausentes']), f"❌ {stats['ausentes']} faltas totales"],
        ['Faltas Justificadas', str(stats['justificados']), '📝 Con certificado médico/justificación'],
        ['Faltas Injustificadas', str(stats['injustificados']), '⚠️ Sin justificación válida'],
        ['Estado General', stats['estado'], '📈 Clasificación según porcentaje']
    ]
    
    stats_table = Table(stats_data, colWidths=[2*inch, 1.2*inch, 3*inch])
    stats_table.setStyle(TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a202c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        
        # Contenido
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (2, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1.5, colors.HexColor('#cbd5e0')),
        
        # Filas alternadas
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8fafc'), colors.HexColor('#edf2f7')]),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    elements.append(stats_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # --- Detalle por asignatura ---
    if estudiante_data['asignaturas']:
        asignaturas_title_style = ParagraphStyle(
            'AsignaturasTitle',
            parent=styles['Normal'],
            fontSize=16,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#3182ce'),
            spaceAfter=15
        )
        
        asignaturas_title = Paragraph("📚 DETALLE POR ASIGNATURA", asignaturas_title_style)
        elements.append(asignaturas_title)
        
        asignaturas_data = [['Asignatura', 'Total Clases', 'Presentes', 'Ausentes', 'Justificadas', '% Asistencia']]
        
        for asig in estudiante_data['asignaturas']:
            asignaturas_data.append([
                asig['asignatura'],
                str(asig['total_clases']),
                str(asig['presentes']),
                str(asig['ausentes']),
                str(asig['justificados']),
                f"{asig['porcentaje']}%"
            ])
        
        asignaturas_table = Table(asignaturas_data, colWidths=[2.2*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch])
        asignaturas_table.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3182ce')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Contenido
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            
            # Filas alternadas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(asignaturas_table)
        elements.append(Spacer(1, 0.3*inch))
    
    # --- Historial reciente ---
    if estudiante_data['historial']:
        historial_title = Paragraph("📋 HISTORIAL RECIENTE (Últimas 30 clases)", ParagraphStyle(
            'HistorialTitle',
            parent=styles['Normal'],
            fontSize=16,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#38a169'),
            spaceAfter=15
        ))
        elements.append(historial_title)
        
        historial_data = [['Fecha', 'Asignatura', 'Estado', 'Observaciones']]
        
        for hist in estudiante_data['historial'][:15]:  # Mostrar solo las primeras 15 para que quepa en el PDF
            estado = "✅ Presente" if hist['presente'] else ("📝 Justificado" if hist['justificado'] else "❌ Ausente")
            observaciones = hist['observaciones'][:30] + "..." if len(hist['observaciones']) > 30 else hist['observaciones']
            
            historial_data.append([
                hist['fecha'],
                hist['asignatura'][:20] + "..." if len(hist['asignatura']) > 20 else hist['asignatura'],
                estado,
                observaciones or '-'
            ])
        
        historial_table = Table(historial_data, colWidths=[1*inch, 2*inch, 1.2*inch, 2*inch])
        historial_table.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#38a169')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Contenido
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('ALIGN', (3, 1), (3, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            
            # Filas alternadas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fff4')]),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(historial_table)
    
    # --- Pie de página ---
    def footer(canvas, doc):
        canvas.saveState()
        
        # Línea decorativa
        canvas.setStrokeColor(colors.HexColor('#4a5568'))
        canvas.setLineWidth(2)
        canvas.line(0.7*inch, 0.6*inch, A4[0] - 0.7*inch, 0.6*inch)
        
        # Información principal
        canvas.setFont('Helvetica-Bold', 9)
        canvas.setFillColor(colors.HexColor('#2d3748'))
        footer_main = f"GEM - Reporte Individual de Asistencia"
        canvas.drawCentredString(A4[0] / 2, 0.45 * inch, footer_main)
        
        # Fecha y página
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#718096'))
        canvas.drawString(0.7 * inch, 0.35 * inch, f"Generado: {fecha_generacion}")
        canvas.drawRightString(A4[0] - 0.7 * inch, 0.35 * inch, f"Página {doc.page}")
        
        canvas.restoreState()
    
    doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    buffer.seek(0)
    
    return buffer

def generar_pdf_asistencia_curso(curso_data, periodo_info):
    """Generar PDF con reporte detallado de asistencia de un curso específico"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=0.7*inch, leftMargin=0.7*inch,
                          topMargin=1*inch, bottomMargin=0.8*inch)
    
    elements = []
    styles = getSampleStyleSheet()
    fecha_generacion = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    # --- Cabecera profesional ---
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Title'],
        fontSize=22,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1a202c'),
        alignment=1,
        spaceAfter=20,
        spaceBefore=10
    )
    
    header = Paragraph("📊 REPORTE DE ASISTENCIA POR CURSO", header_style)
    elements.append(header)
    
    # Información del curso
    curso_info = curso_data['curso']
    course_info_style = ParagraphStyle(
        'CourseInfoStyle',
        parent=styles['Normal'],
        fontSize=14,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#2d3748'),
        alignment=1,
        spaceAfter=15
    )
    
    course_info = Paragraph(f"🏫 Curso: {curso_info['nombre']} | 👥 Total Estudiantes: {curso_info['total_estudiantes']}", course_info_style)
    elements.append(course_info)
    
    # Información del período
    period_style = ParagraphStyle(
        'PeriodStyle',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica',
        textColor=colors.HexColor('#718096'),
        alignment=1,
        spaceAfter=20
    )
    
    period_info = Paragraph(f"📅 Período: {periodo_info['fecha_inicio']} - {periodo_info['fecha_fin']}", period_style)
    elements.append(period_info)
    
    # --- Estadísticas generales del curso ---
    stats = curso_data['estadisticas']
    
    stats_data = [
        ['📊 Métrica del Curso', '📈 Valor', '📋 Descripción'],
        ['Total de Registros', str(stats['total_registros']), 'Total de asistencias registradas'],
        ['Promedio de Asistencia', f"{stats['promedio_asistencia']}%", '📈 Promedio general del curso'],
        ['Estudiantes en Estado Crítico', str(stats['estudiantes_criticos']), '🚨 Menos del 70% de asistencia'],
        ['Estudiantes en Riesgo', str(stats['estudiantes_riesgo']), '⚠️ Entre 70% y 84% de asistencia'],
        ['Estudiantes en Buen Estado', str(stats['estudiantes_buenos']), '✅ 85% o más de asistencia']
    ]
    
    stats_table = Table(stats_data, colWidths=[2.2*inch, 1.2*inch, 2.8*inch])
    stats_table.setStyle(TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a202c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        
        # Contenido
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (2, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1.5, colors.HexColor('#cbd5e0')),
        
        # Filas alternadas
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8fafc'), colors.HexColor('#edf2f7')]),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    elements.append(stats_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # --- Detalle por estudiante ---
    if curso_data['estudiantes']:
        estudiantes_title = Paragraph("👥 DETALLE POR ESTUDIANTE", ParagraphStyle(
            'EstudiantesTitle',
            parent=styles['Normal'],
            fontSize=16,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#3182ce'),
            spaceAfter=15
        ))
        elements.append(estudiantes_title)
        
        estudiantes_data = [['Estudiante', 'RUT', 'Total', 'Presentes', 'Ausentes', 'Just.', '% Asist.', 'Estado']]
        
        for est in curso_data['estudiantes']:
            # Determinar color de fondo según estado
            estado_color = colors.HexColor('#fed7d7') if est['estado'] == 'Crítico' else \
                          colors.HexColor('#fef2c7') if est['estado'] == 'En Riesgo' else \
                          colors.HexColor('#d1fae5')
            
            estudiantes_data.append([
                est['nombre'][:25] + "..." if len(est['nombre']) > 25 else est['nombre'],
                est['rut'],
                str(est['total_clases']),
                str(est['presentes']),
                str(est['ausentes']),
                str(est['justificados']),
                f"{est['porcentaje']}%",
                est['estado']
            ])
        
        estudiantes_table = Table(estudiantes_data, colWidths=[2.2*inch, 0.8*inch, 0.5*inch, 0.6*inch, 0.6*inch, 0.5*inch, 0.6*inch, 0.6*inch])
        
        # Crear estilo base
        table_style = [
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3182ce')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Contenido
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]
        
        # Agregar colores por estado
        for i, est in enumerate(curso_data['estudiantes'], 1):
            if est['estado'] == 'Crítico':
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#fed7d7')))
            elif est['estado'] == 'En Riesgo':
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#fef2c7')))
            else:
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#d1fae5')))
        
        estudiantes_table.setStyle(TableStyle(table_style))
        elements.append(estudiantes_table)
        elements.append(Spacer(1, 0.3*inch))
    
    # --- Detalle por asignatura ---
    if curso_data['asignaturas']:
        asignaturas_title = Paragraph("📚 DETALLE POR ASIGNATURA", ParagraphStyle(
            'AsignaturasTitle',
            parent=styles['Normal'],
            fontSize=16,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#38a169'),
            spaceAfter=15
        ))
        elements.append(asignaturas_title)
        
        asignaturas_data = [['Asignatura', 'Total Clases', 'Total Presentes', '% Asistencia General']]
        
        for asig in curso_data['asignaturas']:
            asignaturas_data.append([
                asig['asignatura'],
                str(asig['total_clases']),
                str(asig['total_presentes']),
                f"{asig['porcentaje']}%"
            ])
        
        asignaturas_table = Table(asignaturas_data, colWidths=[3*inch, 1.5*inch, 1.5*inch, 1.2*inch])
        asignaturas_table.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#38a169')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Contenido
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            
            # Filas alternadas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fff4')]),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(asignaturas_table)
    
    # --- Pie de página ---
    def footer(canvas, doc):
        canvas.saveState()
        
        # Línea decorativa
        canvas.setStrokeColor(colors.HexColor('#4a5568'))
        canvas.setLineWidth(2)
        canvas.line(0.7*inch, 0.6*inch, A4[0] - 0.7*inch, 0.6*inch)
        
        # Información principal
        canvas.setFont('Helvetica-Bold', 9)
        canvas.setFillColor(colors.HexColor('#2d3748'))
        footer_main = f"GEM - Reporte de Asistencia por Curso"
        canvas.drawCentredString(A4[0] / 2, 0.45 * inch, footer_main)
        
        # Fecha y página
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#718096'))
        canvas.drawString(0.7 * inch, 0.35 * inch, f"Generado: {fecha_generacion}")
        canvas.drawRightString(A4[0] - 0.7 * inch, 0.35 * inch, f"Página {doc.page}")
        
        canvas.restoreState()
    
    doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    buffer.seek(0)
    
    return buffer

def generar_pdf_promedio_asignaturas_curso(curso_data, periodo_info):
    """
    Genera un PDF del reporte de promedios por asignatura de un curso específico.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # --- Cabecera con Logo y Título ---
    logo_path = os.path.join(settings.BASE_DIR, 'Core', 'static', 'img', 'logo.png')
    logo = Image(logo_path, width=1*inch, height=1*inch)
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#34495e'),
        alignment=TA_CENTER,
        fontName='Helvetica',
        spaceAfter=25
    )
    
    title_text = Paragraph(f"REPORTE DE PROMEDIOS POR ASIGNATURA<br/>CURSO {curso_data['curso']['nombre']}", title_style)
    subtitle_text = Paragraph(f"Colegio GEM - Período: {periodo_info['fecha_inicio']} al {periodo_info['fecha_fin']}", subtitle_style)
    
    # Tabla de cabecera
    header_table = Table([[logo, title_text]], colWidths=[1.5*inch, 6*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (1, 0), (1, 0), 20),
    ]))
    
    elements.append(header_table)
    elements.append(subtitle_text)
    elements.append(Spacer(1, 0.2*inch))
    
    # --- Información del Curso ---
    fecha_generacion = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=20,
        borderBottomWidth=1,
        borderBottomColor=colors.lightgrey,
        borderBottomPadding=10
    )
    
    info_text = f"""
    <b>Fecha de generación:</b> {fecha_generacion}<br/>
    <b>Curso:</b> {curso_data['curso']['nombre']}<br/>
    <b>Total de estudiantes:</b> {curso_data['curso']['total_estudiantes']}<br/>
    <b>Total de asignaturas:</b> {curso_data['curso']['total_asignaturas']}<br/>
    <b>Total de evaluaciones:</b> {curso_data['estadisticas']['total_evaluaciones']:,}<br/>
    <b>Promedio general del curso:</b> {curso_data['estadisticas']['promedio_general']:.2f}
    """
    
    info_paragraph = Paragraph(info_text, info_style)
    elements.append(info_paragraph)
    elements.append(Spacer(1, 0.2*inch))
    
    # --- Tabla Principal de Asignaturas ---
    if curso_data['asignaturas']:
        # Encabezados de la tabla
        headers = [
            'Asignatura', 'Docente', 'Evaluaciones', 'Estudiantes\nEvaluados', 
            'Promedio', 'Aprobados', '% Aprobación', 'Estado'
        ]
        
        data = [headers]
        
        # Datos de las asignaturas
        for asignatura in curso_data['asignaturas']:
            row = [
                asignatura['asignatura'],
                asignatura['docente'],
                str(asignatura['total_evaluaciones']),
                str(asignatura['estudiantes_evaluados']),
                f"{asignatura['promedio']:.2f}",
                str(asignatura['aprobados']),
                f"{asignatura['porcentaje_aprobacion']:.1f}%",
                asignatura['estado']
            ]
            data.append(row)
        
        # Crear tabla
        table = Table(data, colWidths=[1.2*inch, 1.2*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.8*inch])
        
        # Estilos de la tabla
        table_style = [
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Contenido
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),  # Centrar todo excepto asignatura
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),     # Asignatura alineada a la izquierda
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            
            # Alternar colores de filas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]
        
        # Agregar colores específicos para el estado
        for i, asignatura in enumerate(curso_data['asignaturas'], 1):
            estado = asignatura['estado']
            if estado == 'Excelente':
                table_style.append(('BACKGROUND', (7, i), (7, i), colors.HexColor('#27ae60')))
                table_style.append(('TEXTCOLOR', (7, i), (7, i), colors.white))
            elif estado == 'Bueno':
                table_style.append(('BACKGROUND', (7, i), (7, i), colors.HexColor('#2980b9')))
                table_style.append(('TEXTCOLOR', (7, i), (7, i), colors.white))
            elif estado == 'Regular':
                table_style.append(('BACKGROUND', (7, i), (7, i), colors.HexColor('#f39c12')))
                table_style.append(('TEXTCOLOR', (7, i), (7, i), colors.white))
            elif estado == 'Deficiente':
                table_style.append(('BACKGROUND', (7, i), (7, i), colors.HexColor('#e74c3c')))
                table_style.append(('TEXTCOLOR', (7, i), (7, i), colors.white))
        
        table.setStyle(TableStyle(table_style))
        elements.append(table)
        
        # --- Resumen por Estado ---
        elements.append(Spacer(1, 0.3*inch))
        
        resumen_style = ParagraphStyle(
            'ResumenStyle',
            parent=styles['Normal'],
            fontSize=11,
            fontName='Helvetica-Bold',
            spaceAfter=10
        )
        
        resumen_title = Paragraph("RESUMEN POR RENDIMIENTO:", resumen_style)
        elements.append(resumen_title)
        
        # Tabla de resumen
        resumen_data = [
            ['Estado', 'Cantidad', 'Criterio'],
            ['🟢 Excelente', str(curso_data['estadisticas']['asignaturas_excelentes']), 'Promedio ≥ 5.5'],
            ['🔵 Bueno', str(curso_data['estadisticas']['asignaturas_buenas']), 'Promedio ≥ 4.5'],
            ['🟡 Regular', str(curso_data['estadisticas']['asignaturas_regulares']), 'Promedio ≥ 4.0'],
            ['🔴 Deficiente', str(curso_data['estadisticas']['asignaturas_deficientes']), 'Promedio < 4.0']
        ]
        
        resumen_table = Table(resumen_data, colWidths=[1.5*inch, 1*inch, 2*inch])
        resumen_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        
        elements.append(resumen_table)
        
    else:
        # No hay asignaturas con evaluaciones
        no_data_style = ParagraphStyle(
            'NoDataStyle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#e74c3c'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=20
        )
        
        no_data_text = Paragraph("No hay evaluaciones registradas para este curso en el período seleccionado.", no_data_style)
        elements.append(no_data_text)
    
    # --- Pie de página ---
    def footer(canvas, doc):
        canvas.saveState()
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        
        footer_text = f"Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')} - Colegio GEM - Sistema de Gestión Educativa"
        footer_paragraph = Paragraph(footer_text, footer_style)
        
        # Posicionar el pie de página
        w, h = footer_paragraph.wrap(doc.width, doc.bottomMargin)
        footer_paragraph.drawOn(canvas, doc.leftMargin, 0.5*inch)
        
        # Número de página
        page_num = canvas.getPageNumber()
        canvas.drawRightString(doc.width + doc.leftMargin, 0.5*inch, f"Página {page_num}")
        canvas.restoreState()
    
    # Construir el documento
    doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    buffer.seek(0)
    return buffer

def generar_pdf_asistencia_asignaturas_curso(curso_data):
    """
    Genera un PDF del reporte de asistencia por asignaturas de un curso específico
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # --- Cabecera con Logo y Título ---
    logo_path = os.path.join(settings.BASE_DIR, 'Core', 'static', 'img', 'logo.png')
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=0.8*inch, height=0.8*inch)
    else:
        logo = Paragraph("<b>LOGO</b>", styles['Normal'])
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )
    
    header_text = Paragraph(f"Reporte de Asistencia por Asignaturas<br/>Curso {curso_data['curso']}", header_style)
    
    header_table = Table([[logo, header_text]], colWidths=[1*inch, 6.5*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (1, 0), (1, 0), 0),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # --- Información General del Curso ---
    info_style = ParagraphStyle(
        'Info', parent=styles['Normal'], fontSize=11, leading=14,
        spaceAfter=20, borderBottomWidth=1, borderBottomColor=colors.lightgrey,
        borderBottomPadding=10
    )
    
    info_text = f"""
    <b>Curso:</b> {curso_data['curso']}<br/>
    <b>Total de Estudiantes:</b> {curso_data['total_estudiantes']}<br/>
    <b>Total de Asignaturas:</b> {curso_data['total_asignaturas']}<br/>
    <b>Promedio General de Asistencia:</b> {curso_data['promedio_asistencia_curso']}%<br/>
    <b>Fecha de Generación:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}
    """
    info_paragraph = Paragraph(info_text, info_style)
    elements.append(info_paragraph)
    
    # --- Resumen por Estado ---
    if curso_data['asignaturas']:
        estados_count = {'Excelente': 0, 'Bueno': 0, 'Regular': 0, 'Deficiente': 0}
        for asignatura in curso_data['asignaturas']:
            estados_count[asignatura['estado']] += 1
        
        resumen_style = ParagraphStyle(
            'Resumen', parent=styles['Normal'], fontSize=10, leading=12,
            spaceAfter=15, backgroundColor=colors.HexColor('#f8f9fa'),
            borderWidth=1, borderColor=colors.lightgrey, borderPadding=10
        )
        
        resumen_text = f"""
        <b>Resumen por Estado de Asistencia:</b><br/>
        • Excelente (≥85%): {estados_count['Excelente']} asignaturas<br/>
        • Bueno (75-84%): {estados_count['Bueno']} asignaturas<br/>
        • Regular (60-74%): {estados_count['Regular']} asignaturas<br/>
        • Deficiente (<60%): {estados_count['Deficiente']} asignaturas
        """
        resumen_paragraph = Paragraph(resumen_text, resumen_style)
        elements.append(resumen_paragraph)
    
    # --- Tabla Principal ---
    if curso_data['asignaturas']:
        # Encabezados
        data = [[
            Paragraph('<b>Asignatura</b>', styles['Normal']),
            Paragraph('<b>Docente</b>', styles['Normal']),
            Paragraph('<b>Clases</b>', styles['Normal']),
            Paragraph('<b>Est. Evaluados</b>', styles['Normal']),
            Paragraph('<b>Presentes</b>', styles['Normal']),
            Paragraph('<b>Ausentes</b>', styles['Normal']),
            Paragraph('<b>% Asistencia</b>', styles['Normal']),
            Paragraph('<b>Estado</b>', styles['Normal'])
        ]]
        
        # Datos de asignaturas
        for asignatura in curso_data['asignaturas']:
            # Determinar color del estado
            if asignatura['estado'] == 'Excelente':
                estado_color = colors.HexColor('#28a745')
            elif asignatura['estado'] == 'Bueno':
                estado_color = colors.HexColor('#17a2b8')
            elif asignatura['estado'] == 'Regular':
                estado_color = colors.HexColor('#ffc107')
            else:  # Deficiente
                estado_color = colors.HexColor('#dc3545')
            
            estado_paragraph = Paragraph(f'<font color="{estado_color}">{asignatura["estado"]}</font>', styles['Normal'])
            
            data.append([
                Paragraph(asignatura['asignatura'], styles['Normal']),
                Paragraph(asignatura['docente'], styles['Normal']),
                str(asignatura['total_clases']),
                str(asignatura['estudiantes_evaluados']),
                str(asignatura['total_presentes']),
                str(asignatura['total_ausentes']),
                f"{asignatura['porcentaje_asistencia']}%",
                estado_paragraph
            ])
        
        # Crear tabla
        table = Table(data, colWidths=[1.8*inch, 1.5*inch, 0.6*inch, 0.8*inch, 0.7*inch, 0.7*inch, 0.8*inch, 0.8*inch])
        
        # Estilos de la tabla
        table.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4A90E2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            
            # Contenido
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Alternar colores de filas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            
            # Alineación específica
            ('ALIGN', (0, 1), (1, -1), 'LEFT'),  # Asignatura y Docente a la izquierda
            ('ALIGN', (2, 1), (-1, -1), 'CENTER'),  # Números al centro
        ]))
        
        elements.append(table)
        
        # --- Estadísticas Adicionales ---
        elements.append(Spacer(1, 0.3*inch))
        
        # Calcular estadísticas adicionales
        total_registros = sum(a['total_registros'] for a in curso_data['asignaturas'])
        total_presentes = sum(a['total_presentes'] for a in curso_data['asignaturas'])
        
        stats_style = ParagraphStyle(
            'Stats', parent=styles['Normal'], fontSize=10, leading=12,
            backgroundColor=colors.HexColor('#e9ecef'), borderWidth=1,
            borderColor=colors.lightgrey, borderPadding=10
        )
        
        stats_text = f"""
        <b>Estadísticas Generales:</b><br/>
        • Total de registros de asistencia: {total_registros:,}<br/>
        • Total de presencias: {total_presentes:,}<br/>
        • Total de ausencias: {total_registros - total_presentes:,}<br/>
        • Asignatura con mejor asistencia: {curso_data['asignaturas'][0]['asignatura']} ({curso_data['asignaturas'][0]['porcentaje_asistencia']}%)<br/>
        • Asignatura con menor asistencia: {curso_data['asignaturas'][-1]['asignatura']} ({curso_data['asignaturas'][-1]['porcentaje_asistencia']}%)
        """
        stats_paragraph = Paragraph(stats_text, stats_style)
        elements.append(stats_paragraph)
    
    else:
        # Sin datos
        no_data_style = ParagraphStyle(
            'NoData', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER,
            textColor=colors.red, spaceAfter=20
        )
        no_data = Paragraph("No hay datos de asistencia disponibles para este curso.", no_data_style)
        elements.append(no_data)
    
    # --- Pie de página ---
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        
        # Línea divisoria
        canvas.setStrokeColor(colors.lightgrey)
        canvas.line(0.5 * inch, 0.6 * inch, A4[0] - 0.5 * inch, 0.6 * inch)
        
        # Texto del pie
        footer_text = f"GEM - Gestión Educativa Modular | Reporte de Asistencia por Asignaturas"
        canvas.drawCentredString(A4[0] / 2, 0.4 * inch, footer_text)
        
        # Fecha y página
        generation_text = f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        canvas.drawString(0.5 * inch, 0.25 * inch, generation_text)
        
        page_text = f"Página {doc.page}"
        canvas.drawRightString(A4[0] - 0.5 * inch, 0.25 * inch, page_text)
        
        canvas.restoreState()
    
    doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    buffer.seek(0)
    
    return buffer

def generar_pdf_evaluaciones_asignaturas_curso(curso_data):
    """
    Genera un PDF del reporte de evaluaciones por asignaturas de un curso específico
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # --- Cabecera con Logo y Título ---
    logo_path = os.path.join(settings.BASE_DIR, 'Core', 'static', 'img', 'logo.png')
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=0.8*inch, height=0.8*inch)
    else:
        logo = Paragraph("<b>LOGO</b>", styles['Normal'])
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )
    
    header_text = Paragraph(f"Reporte de Evaluaciones por Asignaturas<br/>Curso {curso_data['curso']}", header_style)
    
    header_table = Table([[logo, header_text]], colWidths=[1*inch, 6.5*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (1, 0), (1, 0), 0),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # --- Información General del Curso ---
    info_style = ParagraphStyle(
        'Info', parent=styles['Normal'], fontSize=11, leading=14,
        spaceAfter=20, borderBottomWidth=1, borderBottomColor=colors.lightgrey,
        borderBottomPadding=10
    )
    
    info_text = f"""
    <b>Curso:</b> {curso_data['curso']}<br/>
    <b>Total de Estudiantes:</b> {curso_data['total_estudiantes']}<br/>
    <b>Total de Asignaturas:</b> {curso_data['total_asignaturas']}<br/>
    <b>Total de Evaluaciones:</b> {curso_data['total_evaluaciones']}<br/>
    <b>Total de Notas:</b> {curso_data['total_notas']:,}<br/>
    <b>Promedio General del Curso:</b> {curso_data['promedio_general_curso']}<br/>
    <b>Porcentaje de Aprobación:</b> {curso_data['porcentaje_aprobacion_curso']}%<br/>
    <b>Fecha de Generación:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}
    """
    info_paragraph = Paragraph(info_text, info_style)
    elements.append(info_paragraph)
    
    # --- Resumen por Estado ---
    if curso_data['asignaturas']:
        estados_count = {'Excelente': 0, 'Bueno': 0, 'Regular': 0, 'Deficiente': 0, 'Sin evaluaciones': 0, 'Sin datos': 0}
        for asignatura in curso_data['asignaturas']:
            estado = asignatura['estado']
            if estado in estados_count:
                estados_count[estado] += 1
        
        resumen_style = ParagraphStyle(
            'Resumen', parent=styles['Normal'], fontSize=10, leading=12,
            spaceAfter=15, backgroundColor=colors.HexColor('#f8f9fa'),
            borderWidth=1, borderColor=colors.lightgrey, borderPadding=10
        )
        
        resumen_text = f"""
        <b>Resumen por Estado de Rendimiento:</b><br/>
        • Excelente (≥5.5): {estados_count['Excelente']} asignaturas<br/>
        • Bueno (4.5-5.4): {estados_count['Bueno']} asignaturas<br/>
        • Regular (4.0-4.4): {estados_count['Regular']} asignaturas<br/>
        • Deficiente (<4.0): {estados_count['Deficiente']} asignaturas<br/>
        • Sin evaluaciones: {estados_count['Sin evaluaciones']} asignaturas<br/>
        • Sin datos: {estados_count['Sin datos']} asignaturas
        """
        resumen_paragraph = Paragraph(resumen_text, resumen_style)
        elements.append(resumen_paragraph)
    
    # --- Tabla Principal ---
    if curso_data['asignaturas']:
        # Encabezados
        data = [[
            Paragraph('<b>Asignatura</b>', styles['Normal']),
            Paragraph('<b>Docente</b>', styles['Normal']),
            Paragraph('<b>Evaluaciones</b>', styles['Normal']),
            Paragraph('<b>Est. Evaluados</b>', styles['Normal']),
            Paragraph('<b>Total Notas</b>', styles['Normal']),
            Paragraph('<b>Promedio</b>', styles['Normal']),
            Paragraph('<b>Aprobados</b>', styles['Normal']),
            Paragraph('<b>% Aprobación</b>', styles['Normal']),
            Paragraph('<b>Estado</b>', styles['Normal'])
        ]]
        
        # Datos de asignaturas
        for asignatura in curso_data['asignaturas']:
            # Determinar color del estado
            if asignatura['estado'] == 'Excelente':
                estado_color = colors.HexColor('#28a745')
            elif asignatura['estado'] == 'Bueno':
                estado_color = colors.HexColor('#17a2b8')
            elif asignatura['estado'] == 'Regular':
                estado_color = colors.HexColor('#ffc107')
            elif asignatura['estado'] == 'Deficiente':
                estado_color = colors.HexColor('#dc3545')
            else:  # Sin evaluaciones/Sin datos
                estado_color = colors.HexColor('#6c757d')
            
            estado_paragraph = Paragraph(f'<font color="{estado_color}">{asignatura["estado"]}</font>', styles['Normal'])
            
            data.append([
                Paragraph(asignatura['asignatura'], styles['Normal']),
                Paragraph(asignatura['docente'], styles['Normal']),
                str(asignatura['total_evaluaciones']),
                str(asignatura['estudiantes_evaluados']),
                str(asignatura['total_notas']),
                str(asignatura['promedio_asignatura']),
                str(asignatura['aprobados']),
                f"{asignatura['porcentaje_aprobacion']}%",
                estado_paragraph
            ])
        
        # Crear tabla
        table = Table(data, colWidths=[1.6*inch, 1.3*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.8*inch, 0.8*inch])
        
        # Estilos de la tabla
        table.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4A90E2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            
            # Contenido
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Alternar colores de filas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            
            # Alineación específica
            ('ALIGN', (0, 1), (1, -1), 'LEFT'),  # Asignatura y Docente a la izquierda
            ('ALIGN', (2, 1), (-1, -1), 'CENTER'),  # Números al centro
        ]))
        
        elements.append(table)
        
        # --- Estadísticas Adicionales ---
        elements.append(Spacer(1, 0.3*inch))
        
        # Calcular estadísticas adicionales
        asignaturas_con_datos = [a for a in curso_data['asignaturas'] if a['total_notas'] > 0]
        
        if asignaturas_con_datos:
            mejor_asignatura = max(asignaturas_con_datos, key=lambda x: x['promedio_asignatura'])
            peor_asignatura = min(asignaturas_con_datos, key=lambda x: x['promedio_asignatura'])
            
            stats_style = ParagraphStyle(
                'Stats', parent=styles['Normal'], fontSize=10, leading=12,
                backgroundColor=colors.HexColor('#e9ecef'), borderWidth=1,
                borderColor=colors.lightgrey, borderPadding=10
            )
            
            stats_text = f"""
            <b>Estadísticas Generales:</b><br/>
            • Total de evaluaciones aplicadas: {curso_data['total_evaluaciones']:,}<br/>
            • Total de notas registradas: {curso_data['total_notas']:,}<br/>
            • Asignatura con mejor rendimiento: {mejor_asignatura['asignatura']} ({mejor_asignatura['promedio_asignatura']})<br/>
            • Asignatura con menor rendimiento: {peor_asignatura['asignatura']} ({peor_asignatura['promedio_asignatura']})<br/>
            • Asignaturas con evaluaciones: {len(asignaturas_con_datos)} de {len(curso_data['asignaturas'])}<br/>
            • Promedio general del curso: {curso_data['promedio_general_curso']}<br/>
            • Porcentaje de aprobación general: {curso_data['porcentaje_aprobacion_curso']}%
            """
            stats_paragraph = Paragraph(stats_text, stats_style)
            elements.append(stats_paragraph)
        
    else:
        # Sin datos
        no_data_style = ParagraphStyle(
            'NoData', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER,
            textColor=colors.red, spaceAfter=20
        )
        no_data = Paragraph("No hay datos de evaluaciones disponibles para este curso.", no_data_style)
        elements.append(no_data)
    
    # --- Pie de página ---
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        
        # Línea divisoria
        canvas.setStrokeColor(colors.lightgrey)
        canvas.line(0.5 * inch, 0.6 * inch, A4[0] - 0.5 * inch, 0.6 * inch)
        
        # Texto del pie
        footer_text = f"GEM - Gestión Educativa Modular | Reporte de Evaluaciones por Asignaturas"
        canvas.drawCentredString(A4[0] / 2, 0.4 * inch, footer_text)
        
        # Fecha y página
        generation_text = f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        canvas.drawString(0.5 * inch, 0.25 * inch, generation_text)
        
        page_text = f"Página {doc.page}"
        canvas.drawRightString(A4[0] - 0.5 * inch, 0.25 * inch, page_text)
        
        canvas.restoreState()
    
    doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    buffer.seek(0)
    
    return buffer

def generar_pdf_evaluaciones_estudiante(estudiante_data):
    """
    Genera un PDF detallado de las evaluaciones de un estudiante específico
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.7*inch)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # --- Encabezado con Logo ---
    logo_path = os.path.join(settings.BASE_DIR, 'Core', 'static', 'img', 'logo.png')
    logo = Image(logo_path, width=0.8*inch, height=0.8*inch)
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )
    
    header_text = Paragraph(f"Reporte de Evaluaciones<br/>{estudiante_data['estudiante']['nombre']}", header_style)
    
    header_table = Table([[logo, header_text]], colWidths=[1*inch, 6.5*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (1, 0), (1, 0), 0),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # --- Información del Estudiante ---
    info_style = ParagraphStyle(
        'Info', parent=styles['Normal'], fontSize=11, leading=14,
        spaceAfter=20, borderBottomWidth=1, borderBottomColor=colors.lightgrey,
        borderBottomPadding=10
    )
    
    info_text = f"""
    <b>Estudiante:</b> {estudiante_data['estudiante']['nombre']}<br/>
    <b>RUT:</b> {estudiante_data['estudiante']['rut']}<br/>
    <b>Email:</b> {estudiante_data['estudiante']['email']}<br/>
    <b>Curso:</b> {estudiante_data['estudiante']['curso']}<br/>
    <b>Fecha de Generación:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}
    """
    info_paragraph = Paragraph(info_text, info_style)
    elements.append(info_paragraph)
    
    # --- Estadísticas Generales ---
    stats_style = ParagraphStyle(
        'Stats', parent=styles['Normal'], fontSize=10, leading=12,
        backgroundColor=colors.HexColor('#e8f5e8'), borderWidth=1,
        borderColor=colors.HexColor('#28a745'), borderPadding=12, spaceAfter=15
    )
    
    stats = estudiante_data['estadisticas']
    stats_text = f"""
    <b>Resumen General:</b><br/>
    • Total de Asignaturas: {stats['total_asignaturas']}<br/>
    • Total de Evaluaciones: {stats['total_evaluaciones']}<br/>
    • Promedio General: {stats['promedio_general']}<br/>
    • Mejor Nota: {stats['mejor_nota']}<br/>
    • Peor Nota: {stats['peor_nota']}<br/>
    • Porcentaje de Aprobación: {stats['porcentaje_aprobacion']}%
    """
    stats_paragraph = Paragraph(stats_text, stats_style)
    elements.append(stats_paragraph)
    
    # --- Tabla Resumen por Asignatura ---
    if estudiante_data['asignaturas']:
        elements.append(Paragraph('<b>Resumen por Asignatura</b>', styles['Heading2']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Encabezados de la tabla resumen
        resumen_data = [[
            Paragraph('<b>Asignatura</b>', styles['Normal']),
            Paragraph('<b>Docente</b>', styles['Normal']),
            Paragraph('<b>Evaluaciones</b>', styles['Normal']),
            Paragraph('<b>Promedio</b>', styles['Normal']),
            Paragraph('<b>Nota Máx</b>', styles['Normal']),
            Paragraph('<b>Nota Mín</b>', styles['Normal']),
            Paragraph('<b>Aprobadas</b>', styles['Normal']),
            Paragraph('<b>Estado</b>', styles['Normal'])
        ]]
        
        # Datos de cada asignatura
        for asignatura in estudiante_data['asignaturas']:
            # Determinar color del estado
            if asignatura['estado'] == 'Excelente':
                estado_color = colors.HexColor('#28a745')
            elif asignatura['estado'] == 'Bueno':
                estado_color = colors.HexColor('#17a2b8')
            elif asignatura['estado'] == 'Regular':
                estado_color = colors.HexColor('#ffc107')
            else:  # Deficiente
                estado_color = colors.HexColor('#dc3545')
            
            estado_paragraph = Paragraph(f'<font color="{estado_color}">{asignatura["estado"]}</font>', styles['Normal'])
            
            resumen_data.append([
                Paragraph(asignatura['asignatura'], styles['Normal']),
                Paragraph(asignatura['docente'], styles['Normal']),
                str(asignatura['total_evaluaciones']),
                str(asignatura['promedio']),
                str(asignatura['nota_maxima']),
                str(asignatura['nota_minima']),
                f"{asignatura['aprobadas']}/{asignatura['total_evaluaciones']}",
                estado_paragraph
            ])
        
        # Crear tabla resumen
        resumen_table = Table(resumen_data, colWidths=[1.4*inch, 1.2*inch, 0.7*inch, 0.6*inch, 0.6*inch, 0.6*inch, 0.7*inch, 0.7*inch])
        
        resumen_table.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#28a745')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            
            # Contenido
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Alternar colores de filas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            
            # Alineación específica
            ('ALIGN', (0, 1), (1, -1), 'LEFT'),  # Asignatura y Docente a la izquierda
            ('ALIGN', (2, 1), (-1, -1), 'CENTER'),  # Números al centro
        ]))
        
        elements.append(resumen_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # --- Detalle por Asignatura ---
        elements.append(Paragraph('<b>Detalle de Evaluaciones por Asignatura</b>', styles['Heading2']))
        elements.append(Spacer(1, 0.1*inch))
        
        for asignatura in estudiante_data['asignaturas']:
            # Título de la asignatura
            asignatura_style = ParagraphStyle(
                'AsignaturaTitle', parent=styles['Normal'], fontSize=12, fontName='Helvetica-Bold',
                textColor=colors.HexColor('#2c3e50'), spaceAfter=10, spaceBefore=15
            )
            
            asignatura_title = Paragraph(f"{asignatura['asignatura']} - {asignatura['docente']}", asignatura_style)
            elements.append(asignatura_title)
            
            # Información de la asignatura
            asignatura_info_style = ParagraphStyle(
                'AsignaturaInfo', parent=styles['Normal'], fontSize=9, 
                backgroundColor=colors.HexColor('#f8f9fa'), borderWidth=0.5,
                borderColor=colors.lightgrey, borderPadding=8, spaceAfter=10
            )
            
            asignatura_info_text = f"""
            <b>Evaluaciones:</b> {asignatura['total_evaluaciones']} | 
            <b>Promedio:</b> {asignatura['promedio']} | 
            <b>Aprobadas:</b> {asignatura['aprobadas']} | 
            <b>Reprobadas:</b> {asignatura['reprobadas']} | 
            <b>Estado:</b> {asignatura['estado']}
            """
            asignatura_info = Paragraph(asignatura_info_text, asignatura_info_style)
            elements.append(asignatura_info)
            
            # Tabla de evaluaciones detalladas
            if asignatura['evaluaciones_detalle']:
                eval_data = [[
                    Paragraph('<b>Fecha</b>', styles['Normal']),
                    Paragraph('<b>Tipo</b>', styles['Normal']),
                    Paragraph('<b>Descripción</b>', styles['Normal']),
                    Paragraph('<b>Nota</b>', styles['Normal']),
                    Paragraph('<b>Estado</b>', styles['Normal'])
                ]]
                
                for evaluacion in asignatura['evaluaciones_detalle']:
                    # Color de la nota según aprobación
                    nota_color = colors.HexColor('#28a745') if evaluacion['nota'] >= 4.0 else colors.HexColor('#dc3545')
                    nota_paragraph = Paragraph(f'<font color="{nota_color}"><b>{evaluacion["nota"]}</b></font>', styles['Normal'])
                    
                    # Color del estado
                    estado_color = colors.HexColor('#28a745') if evaluacion['estado'] == 'Aprobada' else colors.HexColor('#dc3545')
                    estado_paragraph = Paragraph(f'<font color="{estado_color}">{evaluacion["estado"]}</font>', styles['Normal'])
                    
                    eval_data.append([
                        evaluacion['fecha'],
                        evaluacion['tipo'],
                        Paragraph(evaluacion['descripcion'], styles['Normal']),
                        nota_paragraph,
                        estado_paragraph
                    ])
                
                eval_table = Table(eval_data, colWidths=[0.8*inch, 0.8*inch, 2.5*inch, 0.6*inch, 0.8*inch])
                
                eval_table.setStyle(TableStyle([
                    # Encabezado
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6c757d')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 8),
                    
                    # Contenido
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    
                    # Alternar colores de filas
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                    
                    # Alineación específica
                    ('ALIGN', (2, 1), (2, -1), 'LEFT'),  # Descripción a la izquierda
                ]))
                
                elements.append(eval_table)
                elements.append(Spacer(1, 0.2*inch))
            else:
                no_eval_paragraph = Paragraph("No hay evaluaciones registradas para esta asignatura.", styles['Normal'])
                elements.append(no_eval_paragraph)
                elements.append(Spacer(1, 0.2*inch))
        
    else:
        # Sin datos
        no_data_style = ParagraphStyle(
            'NoData', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER,
            textColor=colors.red, spaceAfter=20
        )
        no_data = Paragraph("No hay datos de evaluaciones disponibles para este estudiante.", no_data_style)
        elements.append(no_data)
    
    # --- Pie de página ---
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        
        # Línea divisoria
        canvas.setStrokeColor(colors.lightgrey)
        canvas.line(0.5 * inch, 0.6 * inch, A4[0] - 0.5 * inch, 0.6 * inch)
        
        # Texto del pie
        footer_text = f"GEM - Gestión Educativa Modular | Reporte de Evaluaciones del Estudiante"
        canvas.drawCentredString(A4[0] / 2, 0.4 * inch, footer_text)
        
        # Fecha y página
        generation_text = f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        canvas.drawString(0.5 * inch, 0.25 * inch, generation_text)
        
        page_text = f"Página {doc.page}"
        canvas.drawRightString(A4[0] - 0.5 * inch, 0.25 * inch, page_text)
        
        canvas.restoreState()
    
    doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    buffer.seek(0)
    
    return buffer

def generar_pdf_reporte_evaluaciones_general(data):
    """
    Genera un PDF del reporte general de evaluaciones de todos los cursos
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.7*inch)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # --- Encabezado con Logo ---
    logo_path = os.path.join(settings.BASE_DIR, 'Core', 'static', 'img', 'logo.png')
    logo = Image(logo_path, width=0.8*inch, height=0.8*inch)
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=20,
        textColor=colors.HexColor('#2c3e50'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    header_text = Paragraph("Reporte General de Evaluaciones<br/>Todos los Cursos", header_style)
    
    header_table = Table([[logo, header_text]], colWidths=[1*inch, 6.5*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (1, 0), (1, 0), 0),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # --- Información General ---
    info_style = ParagraphStyle(
        'Info', parent=styles['Normal'], fontSize=11, leading=14,
        spaceAfter=20, borderBottomWidth=1, borderBottomColor=colors.lightgrey,
        borderBottomPadding=10
    )
    
    info_text = f"""
    <b>Institución:</b> GEM - Gestión Educativa Modular<br/>
    <b>Fecha de Generación:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/>
    <b>Período:</b> Año Escolar {datetime.now().year}
    """
    info_paragraph = Paragraph(info_text, info_style)
    elements.append(info_paragraph)
    
    # --- Estadísticas Generales ---
    if 'estadisticas_generales' in data:
        stats = data['estadisticas_generales']
        
        stats_style = ParagraphStyle(
            'Stats', parent=styles['Normal'], fontSize=10, leading=12,
            backgroundColor=colors.HexColor('#e8f5e8'), borderWidth=1,
            borderColor=colors.HexColor('#28a745'), borderPadding=12, spaceAfter=15
        )
        
        stats_text = f"""
        <b>Resumen General del Colegio:</b><br/>
        • Total de Cursos: {stats.get('total_cursos', 0)}<br/>
        • Total de Estudiantes: {stats.get('total_estudiantes', 0)}<br/>
        • Total de Evaluaciones: {stats.get('total_evaluaciones', 0):,}<br/>
        • Promedio General: {stats.get('promedio_general', 0)}<br/>
        • Porcentaje de Aprobación: {stats.get('porcentaje_aprobacion_general', 0)}%
        """
        stats_paragraph = Paragraph(stats_text, stats_style)
        elements.append(stats_paragraph)
    
    # --- Tabla Principal por Cursos ---
    if 'cursos' in data and data['cursos']:
        elements.append(Paragraph('<b>Detalle por Curso</b>', styles['Heading2']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Encabezados de la tabla
        curso_data = [[
            Paragraph('<b>Curso</b>', styles['Normal']),
            Paragraph('<b>Estudiantes</b>', styles['Normal']),
            Paragraph('<b>Evaluaciones</b>', styles['Normal']),
            Paragraph('<b>Asignaturas</b>', styles['Normal']),
            Paragraph('<b>Promedio</b>', styles['Normal']),
            Paragraph('<b>Aprobados</b>', styles['Normal']),
            Paragraph('<b>% Aprobación</b>', styles['Normal']),
            Paragraph('<b>Estado</b>', styles['Normal'])
        ]]
        
        # Datos de cada curso
        for curso in data['cursos']:
            # Determinar color del estado
            estado = curso.get('estado', 'Sin datos')
            if estado == 'Excelente':
                estado_color = colors.HexColor('#28a745')
            elif estado == 'Bueno':
                estado_color = colors.HexColor('#17a2b8')
            elif estado == 'Regular':
                estado_color = colors.HexColor('#ffc107')
            elif estado == 'Deficiente':
                estado_color = colors.HexColor('#dc3545')
            else:
                estado_color = colors.HexColor('#6c757d')
            
            estado_paragraph = Paragraph(f'<font color="{estado_color}">{estado}</font>', styles['Normal'])
            
            curso_data.append([
                Paragraph(f'<b>{curso.get("curso", "N/A")}</b>', styles['Normal']),
                str(curso.get('total_estudiantes', 0)),
                str(curso.get('total_evaluaciones', 0)),
                str(curso.get('asignaturas_con_evaluaciones', 0)),
                str(curso.get('promedio_curso', 0)),
                str(curso.get('aprobados', 0)),
                f"{curso.get('porcentaje_aprobacion', 0)}%",
                estado_paragraph
            ])
        
        # Crear tabla de cursos
        curso_table = Table(curso_data, colWidths=[0.8*inch, 0.8*inch, 0.9*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.9*inch, 0.8*inch])
        
        curso_table.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#28a745')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            
            # Contenido
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Alternar colores de filas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        
        elements.append(curso_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # --- Análisis por Estado ---
        if data['cursos']:
            elementos_estados = {'Excelente': 0, 'Bueno': 0, 'Regular': 0, 'Deficiente': 0, 'Sin datos': 0}
            
            for curso in data['cursos']:
                estado = curso.get('estado', 'Sin datos')
                if estado in elementos_estados:
                    elementos_estados[estado] += 1
            
            analisis_style = ParagraphStyle(
                'Analisis', parent=styles['Normal'], fontSize=10, leading=12,
                backgroundColor=colors.HexColor('#f8f9fa'), borderWidth=1,
                borderColor=colors.lightgrey, borderPadding=10, spaceAfter=15
            )
            
            analisis_text = f"""
            <b>Análisis por Estado de Rendimiento:</b><br/>
            • Cursos con rendimiento Excelente (≥5.5): {elementos_estados['Excelente']}<br/>
            • Cursos con rendimiento Bueno (4.5-5.4): {elementos_estados['Bueno']}<br/>
            • Cursos con rendimiento Regular (4.0-4.4): {elementos_estados['Regular']}<br/>
            • Cursos con rendimiento Deficiente (<4.0): {elementos_estados['Deficiente']}<br/>
            • Cursos sin datos: {elementos_estados['Sin datos']}
            """
            analisis_paragraph = Paragraph(analisis_text, analisis_style)
            elements.append(analisis_paragraph)
        
        # --- Mejores y Peores Cursos ---
        cursos_con_datos = [c for c in data['cursos'] if float(c.get('promedio_curso', 0)) > 0]
        
        if cursos_con_datos:
            mejor_curso = max(cursos_con_datos, key=lambda x: float(x.get('promedio_curso', 0)))
            peor_curso = min(cursos_con_datos, key=lambda x: float(x.get('promedio_curso', 0)))
            
            destacados_style = ParagraphStyle(
                'Destacados', parent=styles['Normal'], fontSize=10, leading=12,
                backgroundColor=colors.HexColor('#e9ecef'), borderWidth=1,
                borderColor=colors.lightgrey, borderPadding=10
            )
            
            # Obtener cursos destacados de forma segura
            curso_mas_evaluaciones = max(cursos_con_datos, key=lambda x: int(x.get('total_evaluaciones', 0)))
            curso_mejor_aprobacion = max(cursos_con_datos, key=lambda x: float(x.get('porcentaje_aprobacion', 0)))
            
            destacados_text = f"""
            <b>Cursos Destacados:</b><br/>
            • Mejor rendimiento: {mejor_curso.get('curso', 'N/A')} (Promedio: {mejor_curso.get('promedio_curso', 0)})<br/>
            • Menor rendimiento: {peor_curso.get('curso', 'N/A')} (Promedio: {peor_curso.get('promedio_curso', 0)})<br/>
            • Curso con más evaluaciones: {curso_mas_evaluaciones.get('curso', 'N/A')} ({curso_mas_evaluaciones.get('total_evaluaciones', 0)} evaluaciones)<br/>
            • Mejor porcentaje de aprobación: {curso_mejor_aprobacion.get('curso', 'N/A')} ({curso_mejor_aprobacion.get('porcentaje_aprobacion', 0)}%)
            """
            destacados_paragraph = Paragraph(destacados_text, destacados_style)
            elements.append(destacados_paragraph)
        
    else:
        # Sin datos
        no_data_style = ParagraphStyle(
            'NoData', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER,
            textColor=colors.red, spaceAfter=20
        )
        no_data = Paragraph("No hay datos de evaluaciones disponibles.", no_data_style)
        elements.append(no_data)
    
    # --- Pie de página ---
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        
        # Línea divisoria
        canvas.setStrokeColor(colors.lightgrey)
        canvas.line(0.5 * inch, 0.6 * inch, A4[0] - 0.5 * inch, 0.6 * inch)
        
        # Texto del pie
        footer_text = f"GEM - Gestión Educativa Modular | Reporte General de Evaluaciones"
        canvas.drawCentredString(A4[0] / 2, 0.4 * inch, footer_text)
        
        # Fecha y página
        generation_text = f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        canvas.drawString(0.5 * inch, 0.25 * inch, generation_text)
        
        page_text = f"Página {doc.page}"
        canvas.drawRightString(A4[0] - 0.5 * inch, 0.25 * inch, page_text)
        
        canvas.restoreState()
    
    doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    buffer.seek(0)
    
    return buffer

def generar_pdf_evaluaciones_asignaturas_docente(data):
    """
    Genera un PDF con el reporte de evaluaciones de las asignaturas del docente
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1*inch, bottomMargin=1*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    # Colores
    color_primary = colors.HexColor('#2c3e50')
    color_secondary = colors.HexColor('#3498db')
    color_success = colors.HexColor('#27ae60')
    color_warning = colors.HexColor('#f39c12')
    color_danger = colors.HexColor('#e74c3c')
    
    # --- Encabezado ---
    logo_style = ParagraphStyle(
        'LogoStyle',
        parent=styles['Normal'],
        fontSize=18,
        textColor=color_primary,
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    elements.append(Paragraph("🎓 SISTEMA EDUCATIVO GEM", logo_style))
    
    title_style = ParagraphStyle(
        'TitleStyle', 
        parent=styles['Heading1'],
        fontSize=16,
        textColor=color_primary,
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    elements.append(Paragraph("REPORTE DE EVALUACIONES - MIS ASIGNATURAS", title_style))
    
    # --- Información del Docente ---
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        fontName='Helvetica'
    )
    
    # Información básica
    fecha_actual = datetime.now().strftime("%d de %B de %Y")
    hora_actual = datetime.now().strftime("%H:%M")
    
    info_data = [
        [Paragraph('<b>Docente:</b>', info_style), Paragraph(data['docente'], info_style)],
        [Paragraph('<b>Fecha del reporte:</b>', info_style), Paragraph(f"{fecha_actual} - {hora_actual}", info_style)],
        [Paragraph('<b>Tipo de reporte:</b>', info_style), Paragraph("Evaluaciones de mis asignaturas", info_style)]
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 20))
    
    # --- Estadísticas Generales ---
    stats = data['estadisticas_generales']
    
    stats_style = ParagraphStyle(
        'StatsStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    stats_data = [
        [
            Paragraph(f"{stats['total_asignaturas']}<br/><font size=8>Asignaturas</font>", stats_style),
            Paragraph(f"{stats['total_evaluaciones']}<br/><font size=8>Evaluaciones</font>", stats_style),
            Paragraph(f"{stats['total_notas']}<br/><font size=8>Notas Registradas</font>", stats_style),
            Paragraph(f"{stats['promedio_general']}<br/><font size=8>Promedio General</font>", stats_style),
            Paragraph(f"{stats['porcentaje_aprobacion_general']}%<br/><font size=8>% Aprobación</font>", stats_style)
        ]
    ]
    
    stats_table = Table(stats_data, colWidths=[1.2*inch]*5)
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 2, color_primary),
    ]))
    
    elements.append(stats_table)
    elements.append(Spacer(1, 20))
    
    # --- Tabla Principal ---
    if data['asignaturas']:
        # Encabezados
        table_data = [[
            Paragraph('<b>Asignatura</b>', styles['Normal']),
            Paragraph('<b>Código</b>', styles['Normal']),
            Paragraph('<b>Cursos</b>', styles['Normal']),
            Paragraph('<b>Evaluaciones</b>', styles['Normal']),
            Paragraph('<b>Est. Evaluados</b>', styles['Normal']),
            Paragraph('<b>Promedio</b>', styles['Normal']),
            Paragraph('<b>% Aprobación</b>', styles['Normal']),
            Paragraph('<b>Estado</b>', styles['Normal'])
        ]]
        
        # Datos de asignaturas
        for asignatura in data['asignaturas']:
            # Color según estado
            if asignatura['estado'] == 'Excelente':
                estado_color = color_success
            elif asignatura['estado'] == 'Bueno':
                estado_color = color_secondary
            elif asignatura['estado'] == 'Regular':
                estado_color = color_warning
            else:
                estado_color = color_danger
            
            table_data.append([
                Paragraph(asignatura['asignatura'], styles['Normal']),
                Paragraph(asignatura['codigo'], styles['Normal']),
                Paragraph(asignatura['cursos'], styles['Normal']),
                Paragraph(str(asignatura['total_evaluaciones']), styles['Normal']),
                Paragraph(str(asignatura['estudiantes_evaluados']), styles['Normal']),
                Paragraph(str(asignatura['promedio_asignatura']), styles['Normal']),
                Paragraph(f"{asignatura['porcentaje_aprobacion']}%", styles['Normal']),
                Paragraph(f'<font color="{estado_color}">{asignatura["estado"]}</font>', styles['Normal'])
            ])
        
        # Crear tabla
        table = Table(table_data, colWidths=[1.5*inch, 0.8*inch, 1*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch])
        table.setStyle(TableStyle([
            # Encabezados
            ('BACKGROUND', (0, 0), (-1, 0), color_primary),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Datos
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.white]),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(table)
    else:
        # Mensaje cuando no hay datos
        no_data_style = ParagraphStyle(
            'NoDataStyle',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique',
            textColor=colors.grey
        )
        elements.append(Paragraph("No hay asignaturas asignadas para este docente.", no_data_style))
    
    # --- Pie de página ---
    elements.append(Spacer(1, 30))
    
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.grey
    )
    
    elements.append(Paragraph(f"Reporte generado por Sistema Educativo GEM - {fecha_actual}", footer_style))
    
    # Construir PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def generar_pdf_evaluaciones_curso_jefe(data):
    """
    Genera un PDF con el reporte de evaluaciones del curso donde es profesor jefe
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1*inch, bottomMargin=1*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    # Colores
    color_primary = colors.HexColor('#2c3e50')
    color_secondary = colors.HexColor('#3498db')
    color_success = colors.HexColor('#27ae60')
    color_warning = colors.HexColor('#f39c12')
    color_danger = colors.HexColor('#e74c3c')
    
    # --- Encabezado ---
    logo_style = ParagraphStyle(
        'LogoStyle',
        parent=styles['Normal'],
        fontSize=18,
        textColor=color_primary,
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    elements.append(Paragraph("🎓 SISTEMA EDUCATIVO GEM", logo_style))
    
    title_style = ParagraphStyle(
        'TitleStyle', 
        parent=styles['Heading1'],
        fontSize=16,
        textColor=color_primary,
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    elements.append(Paragraph(f"REPORTE DE EVALUACIONES - CURSO {data['curso']}", title_style))
    
    # --- Información del Reporte ---
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        fontName='Helvetica'
    )
    
    # Información básica
    fecha_actual = datetime.now().strftime("%d de %B de %Y")
    hora_actual = datetime.now().strftime("%H:%M")
    
    info_data = [
        [Paragraph('<b>Profesor Jefe:</b>', info_style), Paragraph(data['docente'], info_style)],
        [Paragraph('<b>Curso:</b>', info_style), Paragraph(data['curso'], info_style)],
        [Paragraph('<b>Fecha del reporte:</b>', info_style), Paragraph(f"{fecha_actual} - {hora_actual}", info_style)],
        [Paragraph('<b>Tipo de reporte:</b>', info_style), Paragraph("Evaluaciones del curso como profesor jefe", info_style)]
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 20))
    
    # --- Estadísticas Generales del Curso ---
    stats = data['estadisticas_generales']
    
    stats_style = ParagraphStyle(
        'StatsStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    stats_data = [
        [
            Paragraph(f"{stats['total_estudiantes']}<br/><font size=8>Estudiantes</font>", stats_style),
            Paragraph(f"{stats['total_asignaturas']}<br/><font size=8>Asignaturas</font>", stats_style),
            Paragraph(f"{stats['total_evaluaciones']}<br/><font size=8>Evaluaciones</font>", stats_style),
            Paragraph(f"{stats['promedio_general_curso']}<br/><font size=8>Promedio Curso</font>", stats_style),
            Paragraph(f"{stats['porcentaje_aprobacion_curso']}%<br/><font size=8>% Aprobación</font>", stats_style)
        ]
    ]
    
    stats_table = Table(stats_data, colWidths=[1.2*inch]*5)
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 2, color_primary),
    ]))
    
    elements.append(stats_table)
    elements.append(Spacer(1, 20))
    
    # --- Tabla Principal ---
    if data['asignaturas']:
        # Encabezados
        table_data = [[
            Paragraph('<b>Asignatura</b>', styles['Normal']),
            Paragraph('<b>Docente</b>', styles['Normal']),
            Paragraph('<b>Evaluaciones</b>', styles['Normal']),
            Paragraph('<b>Est. Evaluados</b>', styles['Normal']),
            Paragraph('<b>Promedio</b>', styles['Normal']),
            Paragraph('<b>% Aprobación</b>', styles['Normal']),
            Paragraph('<b>Estado</b>', styles['Normal'])
        ]]
        
        # Datos de asignaturas
        for asignatura in data['asignaturas']:
            # Color según estado
            if asignatura['estado'] == 'Excelente':
                estado_color = color_success
            elif asignatura['estado'] == 'Bueno':
                estado_color = color_secondary
            elif asignatura['estado'] == 'Regular':
                estado_color = color_warning
            else:
                estado_color = color_danger
            
            table_data.append([
                Paragraph(asignatura['asignatura'], styles['Normal']),
                Paragraph(asignatura['docente'], styles['Normal']),
                Paragraph(str(asignatura['total_evaluaciones']), styles['Normal']),
                Paragraph(str(asignatura['estudiantes_evaluados']), styles['Normal']),
                Paragraph(str(asignatura['promedio_asignatura']), styles['Normal']),
                Paragraph(f"{asignatura['porcentaje_aprobacion']}%", styles['Normal']),
                Paragraph(f'<font color="{estado_color}">{asignatura["estado"]}</font>', styles['Normal'])
            ])
        
        # Crear tabla
        table = Table(table_data, colWidths=[1.5*inch, 1.3*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch])
        table.setStyle(TableStyle([
            # Encabezados
            ('BACKGROUND', (0, 0), (-1, 0), color_primary),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Datos
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.white]),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(table)
    else:
        # Mensaje cuando no hay datos
        no_data_style = ParagraphStyle(
            'NoDataStyle',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique',
            textColor=colors.grey
        )
        elements.append(Paragraph(f"No hay asignaturas con evaluaciones para el curso {data['curso']}.", no_data_style))
    
    # --- Pie de página ---
    elements.append(Spacer(1, 30))
    
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.grey
    )
    
    elements.append(Paragraph(f"Reporte generado por Sistema Educativo GEM - {fecha_actual}", footer_style))
    
    # Construir PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def generar_pdf_asistencia_asignaturas_docente(data):
    """Genera PDF del reporte de asistencia de asignaturas del docente"""
    buffer = io.BytesIO()
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                           rightMargin=72, leftMargin=72, 
                           topMargin=72, bottomMargin=18)
    
    # Contenedor para los elementos del PDF
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilo personalizado para el título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1,  # Centrado
        textColor=colors.darkblue
    )
    
    # Estilo para subtítulos
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.darkblue
    )
    
    # Título del reporte
    titulo = Paragraph("Reporte de Asistencia - Mis Asignaturas", title_style)
    elements.append(titulo)
    
    # Información del docente
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
    info_docente = f"""
    <b>Docente:</b> {data.get('docente', 'No especificado')}<br/>
    <b>Fecha de generación:</b> {fecha_actual}<br/>
    """
    elements.append(Paragraph(info_docente, styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Estadísticas generales
    stats = data.get('estadisticas_generales', {})
    elements.append(Paragraph("Resumen General", subtitle_style))
    
    # Crear tabla de estadísticas generales
    stats_data = [
        ['Métrica', 'Valor'],
        ['Total de Asignaturas', str(stats.get('total_asignaturas', 0))],
        ['Clases Programadas', str(stats.get('total_clases_programadas', 0))],
        ['Registros de Asistencia', str(stats.get('total_registros_asistencia', 0))],
        ['Porcentaje de Asistencia Promedio', f"{stats.get('porcentaje_asistencia_general', 0)}%"],
        ['Estudiantes en Riesgo', str(stats.get('total_estudiantes_riesgo', 0))]
    ]
    
    stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    
    elements.append(stats_table)
    elements.append(Spacer(1, 30))
    
    # Detalle por asignaturas
    elements.append(Paragraph("Detalle por Asignaturas", subtitle_style))
    
    asignaturas = data.get('asignaturas', [])
    if asignaturas:
        # Crear tabla de asignaturas
        table_data = [
            ['Asignatura', 'Código', 'Cursos', 'Clases', 'Registros', 
             '% Asistencia', 'En Riesgo', 'Estado']
        ]
        
        for asignatura in asignaturas:
            table_data.append([
                asignatura.get('asignatura', ''),
                asignatura.get('codigo', ''),
                asignatura.get('cursos', ''),
                str(asignatura.get('total_clases_programadas', 0)),
                str(asignatura.get('total_registros_asistencia', 0)),
                f"{asignatura.get('porcentaje_asistencia', 0)}%",
                str(asignatura.get('estudiantes_en_riesgo', 0)),
                asignatura.get('estado', '')
            ])
        
        # Crear tabla con ancho ajustado
        col_widths = [1.5*inch, 0.8*inch, 1*inch, 0.6*inch, 0.7*inch, 0.8*inch, 0.6*inch, 0.8*inch]
        asignaturas_table = Table(table_data, colWidths=col_widths)
        
        # Aplicar estilos a la tabla
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]
        
        # Agregar colores según el estado de asistencia
        for i, asignatura in enumerate(asignaturas, 1):
            porcentaje = asignatura.get('porcentaje_asistencia', 0)
            if porcentaje >= 90:
                color = colors.lightgreen
            elif porcentaje >= 80:
                color = colors.lightblue
            elif porcentaje >= 70:
                color = colors.lightyellow
            else:
                color = colors.lightcoral
            
            table_style.append(('BACKGROUND', (5, i), (5, i), color))
        
        asignaturas_table.setStyle(TableStyle(table_style))
        elements.append(asignaturas_table)
    else:
        elements.append(Paragraph("No hay datos de asignaturas disponibles.", styles['Normal']))
    
    # Pie de página
    elements.append(Spacer(1, 30))
    pie_pagina = f"Generado el {fecha_actual} - Sistema Educativo GEM"
    elements.append(Paragraph(pie_pagina, styles['Normal']))
    
    # Construir PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generar_pdf_asistencia_curso_jefe(data):
    """Genera PDF del reporte de asistencia del curso jefe"""
    buffer = io.BytesIO()
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                           rightMargin=72, leftMargin=72, 
                           topMargin=72, bottomMargin=18)
    
    # Contenedor para los elementos del PDF
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilo personalizado para el título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1,  # Centrado
        textColor=colors.darkgreen
    )
    
    # Estilo para subtítulos
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.darkgreen
    )
    
    # Título del reporte
    titulo = Paragraph("Reporte de Asistencia - Curso Jefe", title_style)
    elements.append(titulo)
    
    # Información del curso y docente
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
    curso = data.get('curso', 'No especificado')
    docente = data.get('docente', 'No especificado')
    
    info_curso = f"""
    <b>Curso:</b> {curso}<br/>
    <b>Profesor Jefe:</b> {docente}<br/>
    <b>Fecha de generación:</b> {fecha_actual}<br/>
    """
    elements.append(Paragraph(info_curso, styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Estadísticas generales del curso
    stats = data.get('estadisticas_generales', {})
    elements.append(Paragraph("Resumen del Curso", subtitle_style))
    
    # Crear tabla de estadísticas del curso
    stats_data = [
        ['Métrica', 'Valor'],
        ['Total de Estudiantes', str(stats.get('total_estudiantes', 0))],
        ['Total de Asignaturas', str(stats.get('total_asignaturas', 0))],
        ['Clases Programadas', str(stats.get('total_clases_programadas', 0))],
        ['Registros de Asistencia', str(stats.get('total_registros_asistencia', 0))],
        ['Porcentaje de Asistencia del Curso', f"{stats.get('porcentaje_asistencia_curso', 0)}%"],
        ['Estudiantes en Riesgo', str(stats.get('total_estudiantes_riesgo', 0))]
    ]
    
    stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    
    elements.append(stats_table)
    elements.append(Spacer(1, 30))
    
    # Detalle por asignaturas del curso
    elements.append(Paragraph("Asignaturas del Curso", subtitle_style))
    
    asignaturas = data.get('asignaturas', [])
    if asignaturas:
        # Crear tabla de asignaturas del curso
        table_data = [
            ['Asignatura', 'Código', 'Docente', 'Clases', 'Registros', 
             '% Asistencia', 'En Riesgo', 'Estado']
        ]
        
        for asignatura in asignaturas:
            table_data.append([
                asignatura.get('asignatura', ''),
                asignatura.get('codigo', ''),
                asignatura.get('docente', ''),
                str(asignatura.get('total_clases_programadas', 0)),
                str(asignatura.get('total_registros_asistencia', 0)),
                f"{asignatura.get('porcentaje_asistencia', 0)}%",
                str(asignatura.get('estudiantes_en_riesgo', 0)),
                asignatura.get('estado', '')
            ])
        
        # Crear tabla con ancho ajustado
        col_widths = [1.3*inch, 0.7*inch, 1.2*inch, 0.6*inch, 0.7*inch, 0.8*inch, 0.6*inch, 0.8*inch]
        asignaturas_table = Table(table_data, colWidths=col_widths)
        
        # Aplicar estilos a la tabla
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]
        
        # Agregar colores según el estado de asistencia
        for i, asignatura in enumerate(asignaturas, 1):
            porcentaje = asignatura.get('porcentaje_asistencia', 0)
            if porcentaje >= 90:
                color = colors.lightgreen
            elif porcentaje >= 80:
                color = colors.lightblue
            elif porcentaje >= 70:
                color = colors.lightyellow
            else:
                color = colors.lightcoral
            
            table_style.append(('BACKGROUND', (5, i), (5, i), color))
        
        asignaturas_table.setStyle(TableStyle(table_style))
        elements.append(asignaturas_table)
    else:
        elements.append(Paragraph("No hay datos de asignaturas disponibles para este curso.", styles['Normal']))
    
    # Pie de página
    elements.append(Spacer(1, 30))
    pie_pagina = f"Generado el {fecha_actual} - Sistema Educativo GEM"
    elements.append(Paragraph(pie_pagina, styles['Normal']))
    
    # Construir PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer