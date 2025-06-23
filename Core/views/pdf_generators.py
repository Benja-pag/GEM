from django.http import HttpResponse
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
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