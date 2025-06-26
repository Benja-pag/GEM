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