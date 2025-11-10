"""
PDF Report Generation Service
Creates professional PDF reports with charts and data summaries.

HU19: Generate PDF reports with charts.
"""
import io
from typing import Dict, Any, Optional, List
from datetime import datetime
from ..db import get_pool
try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.units import cm, mm
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, 
        Image, PageBreak, Frame, PageTemplate, FrameBreak
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️ reportlab not installed. PDF generation will not work.")

from ..services import chart_manager, analytics_service, storage_controller, efficiency_service


class ReportCanvas(canvas.Canvas):
    """Custom canvas for adding headers and footers to PDF pages."""
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
        
    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()
        
    def save(self):
        page_count = len(self.pages)
        for page_num, page in enumerate(self.pages, 1):
            self.__dict__.update(page)
            self.draw_page_decorations(page_num, page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
        
    def draw_page_decorations(self, page_num, page_count):
        """Draws professional header and footer on each page."""
        # Header
        self.saveState()
        self.setStrokeColor(colors.HexColor('#1f77b4'))
        self.setLineWidth(2)
        self.line(2*cm, 28*cm, 19*cm, 28*cm)
        
        # Footer
        self.setFont('Helvetica', 8)
        self.setFillColor(colors.grey)
        self.drawString(2*cm, 1.5*cm, f"Solar Facades Monitoring System")
        self.drawRightString(19*cm, 1.5*cm, f"Page {page_num} of {page_count}")
        self.line(2*cm, 2*cm, 19*cm, 2*cm)
        
        self.restoreState()


async def generate_facade_report(
    facade_id: str,
    facade_type: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None
) -> bytes:
    """
    Generates a comprehensive professional PDF report for a specific facade.

    HU19: Generate PDF reports with charts.

    Parameters:
    - facade_id (str): ID of the facade. Required.
    - facade_type (Optional[str]): Filter by facade type. Default: None.
    - start (Optional[str]): Start date/time for report period. Default: None.
    - end (Optional[str]): End date/time for report period. Default: None.

    Returns:
    - bytes: PDF file content as bytes.

    Exceptions:
    - RuntimeError: Raised if reportlab is not installed.
    - ValueError: Raised if insufficient data for report generation.
    """
    if not REPORTLAB_AVAILABLE:
        raise RuntimeError("reportlab library is required for PDF generation. Install with: pip install reportlab")
    
    # Create PDF buffer
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        rightMargin=2*cm, 
        leftMargin=2*cm,
        topMargin=3*cm, 
        bottomMargin=3*cm,
        title=f"Facade Report - {facade_id}"
    )
    
    # Container for PDF elements
    elements = []
    
    # Define professional styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=26,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=6*mm,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=30
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#555555'),
        spaceAfter=10*mm,
        alignment=TA_CENTER,
        fontName='Helvetica',
        leading=18
    )
    
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=4*mm,
        spaceBefore=6*mm,
        fontName='Helvetica-Bold',
        leftIndent=0,
        borderWidth=0,
        borderPadding=0,
        backColor=colors.HexColor('#E8F4F8'),
        borderColor=colors.HexColor('#1f77b4'),
        borderRadius=3
    )
    
    subheading_style = ParagraphStyle(
        'Subheading',
        parent=styles['Heading3'],
        fontSize=13,
        textColor=colors.HexColor('#333333'),
        spaceAfter=3*mm,
        spaceBefore=4*mm,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        leading=14,
        alignment=TA_JUSTIFY
    )
    
    # Cover Page
    elements.append(Spacer(1, 4*cm))
    
    title_text = f"SOLAR FACADE MONITORING REPORT"
    elements.append(Paragraph(title_text, title_style))
    
    subtitle_text = f"Facade ID: {facade_id}"
    if facade_type:
        subtitle_text += f" - Type: {facade_type.upper()}"
    elements.append(Paragraph(subtitle_text, subtitle_style))
    
    elements.append(Spacer(1, 2*cm))
    
    # Report metadata box
    report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    period_start = start if start else "N/A"
    period_end = end if end else "N/A"
    
    metadata_data = [
        ["Report Information", ""],
        ["Generated Date:", report_date],
        ["Period Start:", period_start],
        ["Period End:", period_end],
        ["Facade ID:", facade_id],
        ["Facade Type:", facade_type if facade_type else "All Types"]
    ]
    
    metadata_table = Table(metadata_data, colWidths=[6*cm, 8*cm])
    metadata_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 13),
        ('SPAN', (0, 0), (1, 0)),
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#E8F4F8')),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    elements.append(metadata_table)
    elements.append(PageBreak())
    
    # === SECTION 1: Executive Summary ===
    elements.append(Paragraph("1. EXECUTIVE SUMMARY", heading_style))
    elements.append(Spacer(1, 4*mm))
    
    summary_text = """
    This report provides a comprehensive analysis of the solar facade performance for the specified period.
    It includes sensor data analytics, environmental conditions, energy efficiency metrics, and visual
    representations of key performance indicators.
    """
    elements.append(Paragraph(summary_text, normal_style))
    elements.append(Spacer(1, 6*mm))
    
    # Get facade types
    try:
        types = await storage_controller.fetch_facade_types(facade_id)
        types_text = f"<b>Available Configuration Types:</b> {', '.join([t.upper() for t in types])}"
        elements.append(Paragraph(types_text, normal_style))
        elements.append(Spacer(1, 4*mm))
    except:
        pass
    
    # === SECTION 2: Sensor Performance Analysis ===
    elements.append(Paragraph("2. SENSOR PERFORMANCE ANALYSIS", heading_style))
    elements.append(Spacer(1, 4*mm))
    
    try:
        averages = await analytics_service.get_facade_average(facade_id, facade_type=facade_type)
        
        if averages:
            elements.append(Paragraph("2.1 Average Sensor Values", subheading_style))
            
            # Create professional table
            table_data = [["Sensor Name", "Average Value", "Unit", "Facade Type"]]
            for row in averages[:25]:  # Top 25 sensors
                sensor = row.get("sensor_name", "N/A")
                value = row.get('avg_value', 0)
                unit = "°C" if "T_" in sensor or "Temperatura" in sensor else (
                    "W/m²" if "Irradiancia" in sensor else (
                    "m/s" if "Viento" in sensor else (
                    "%" if "Humedad" in sensor else (
                    "bar" if "Presion" in sensor else (
                    "L/min" if "Flujo" in sensor else "")))))
                
                table_data.append([
                    sensor,
                    f"{value:.2f}",
                    unit,
                    row.get("facade_type", "N/A")
                ])
            
            # Professional table styling
            col_widths = [7*cm, 3*cm, 2*cm, 3*cm]
            sensor_table = Table(table_data, colWidths=col_widths, repeatRows=1)
            sensor_table.setStyle(TableStyle([
                # Header
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 0), (-1, 0), 10),
                # Data rows
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
                ('ALIGN', (1, 1), (2, -1), 'CENTER'),
                ('ALIGN', (3, 1), (3, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            elements.append(sensor_table)
            elements.append(Spacer(1, 8*mm))
            
            # Generate bar chart visualization
            elements.append(Paragraph("2.2 Visual Analysis: Top 10 Sensors", subheading_style))
            try:
                data_dict = {row["sensor_name"]: float(row["avg_value"]) 
                            for row in averages[:10] if row.get("avg_value")}
                chart_bytes = chart_manager.generate_bar_chart(
                    data=data_dict,
                    title=f"Top 10 Average Sensor Values - Facade {facade_id}",
                    xlabel="Sensor",
                    ylabel="Average Value"
                )
                
                chart_img = Image(io.BytesIO(chart_bytes), width=16*cm, height=9*cm)
                elements.append(chart_img)
                elements.append(Spacer(1, 6*mm))
            except Exception as e:
                elements.append(Paragraph(f"Chart generation unavailable: {str(e)}", normal_style))
                
    except Exception as e:
        elements.append(Paragraph(f"Sensor data analysis unavailable: {str(e)}", normal_style))
    
    elements.append(PageBreak())
    
    # === SECTION 3: Environmental Conditions ===
    elements.append(Paragraph("3. ENVIRONMENTAL CONDITIONS", heading_style))
    elements.append(Spacer(1, 4*mm))
    
    try:
        env_vars = await analytics_service.get_environmental_variables(facade_id, facade_type=facade_type)
        
        if env_vars:
            env_text = """
            Environmental sensors provide critical context for understanding facade performance.
            Ambient conditions directly impact solar panel efficiency and thermal behavior.
            """
            elements.append(Paragraph(env_text, normal_style))
            elements.append(Spacer(1, 4*mm))
            
            env_table_data = [["Environmental Variable", "Average Value", "Facade Type"]]
            for row in env_vars:
                sensor = row.get("sensor_name", "N/A")
                value = row.get('avg_value', 0)
                
                # Add appropriate units
                if "Irradiancia" in sensor:
                    formatted_value = f"{value:.2f} W/m²"
                elif "Temperatura" in sensor:
                    formatted_value = f"{value:.2f} °C"
                elif "Velocidad_Viento" in sensor:
                    formatted_value = f"{value:.2f} m/s"
                elif "Humedad" in sensor:
                    formatted_value = f"{value:.2f} %"
                else:
                    formatted_value = f"{value:.2f}"
                
                env_table_data.append([
                    sensor.replace("_", " "),
                    formatted_value,
                    row.get("facade_type", "N/A")
                ])
            
            env_table = Table(env_table_data, colWidths=[8*cm, 4*cm, 3*cm])
            env_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ca02c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#E8F8E8')]),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            elements.append(env_table)
            elements.append(Spacer(1, 6*mm))
    except:
        elements.append(Paragraph("Environmental data not available for this period.", normal_style))
    
    # === SECTION 4: Energy Efficiency (if refrigerated) ===
    if facade_type == "refrigerada" or facade_type is None:
        elements.append(PageBreak())
        elements.append(Paragraph("4. ENERGY EFFICIENCY METRICS", heading_style))
        elements.append(Spacer(1, 4*mm))
        
        try:
            cop_data = await efficiency_service.calculate_cop(facade_id, start, end)
            
            efficiency_text = """
            The Coefficient of Performance (COP) measures refrigeration system efficiency.
            Higher COP values indicate better energy performance.
            """
            elements.append(Paragraph(efficiency_text, normal_style))
            elements.append(Spacer(1, 4*mm))
            
            cop_table_data = [
                ["Metric", "Value"],
                ["Average COP", f"{cop_data.get('cop_average', 0):.2f}"],
                ["Cooling Capacity", f"{cop_data.get('cooling_capacity_avg_w', 0):.2f} W"],
                ["Estimated Power Input", f"{cop_data.get('estimated_power_input_w', 0):.2f} W"],
                ["Water Temperature Delta", f"{cop_data.get('water_temp_delta_avg', 0):.2f} °C"],
                ["Water Flow Rate", f"{cop_data.get('water_flow_avg_lpm', 0):.2f} L/min"],
            ]
            
            cop_table = Table(cop_table_data, colWidths=[10*cm, 5*cm])
            cop_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff7f0e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#FFF4E6')),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('ALIGN', (1, 1), (1, -1), 'CENTER'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FFF8F0')]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            elements.append(cop_table)
            elements.append(Spacer(1, 4*mm))
            
            note = Paragraph(
                f"<i>Note: {cop_data.get('note', 'Power estimates are calculated values.')}</i>",
                ParagraphStyle('Note', parent=normal_style, fontSize=8, textColor=colors.grey)
            )
            elements.append(note)
            
        except ValueError as e:
            elements.append(Paragraph(f"Efficiency metrics unavailable: {str(e)}", normal_style))
        except Exception as e:
            elements.append(Paragraph(f"Error calculating efficiency: {str(e)}", normal_style))
    
    # === SECTION 5: Conclusions ===
    elements.append(PageBreak())
    elements.append(Paragraph("5. CONCLUSIONS & RECOMMENDATIONS", heading_style))
    elements.append(Spacer(1, 4*mm))
    
    conclusion_text = """
    <b>Summary:</b><br/>
    This report presents a comprehensive analysis of the solar facade monitoring data for the specified period.
    The data indicates system performance across multiple sensors and environmental conditions.<br/><br/>
    
    <b>Recommendations:</b><br/>
    • Continue monitoring all sensors for anomalies or performance degradation<br/>
    • Review efficiency metrics regularly to optimize refrigeration system performance<br/>
    • Compare refrigerated vs. non-refrigerated performance to validate system benefits<br/>
    • Schedule maintenance based on temperature and pressure trends<br/><br/>
    
    <b>Data Quality:</b><br/>
    All measurements are stored in TimescaleDB with high temporal resolution.
    Real-time data is cached in Redis for immediate access.
    """
    elements.append(Paragraph(conclusion_text, normal_style))
    
    # Final footer
    elements.append(Spacer(1, 3*cm))
    final_footer = Paragraph(
        f"<i>Report generated by Solar Facades Monitoring System on {report_date}</i>",
        ParagraphStyle(
            'FinalFooter',
            parent=normal_style,
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
    )
    elements.append(final_footer)
    
    # Build PDF with custom canvas for headers/footers
    doc.build(elements, canvasmaker=ReportCanvas)
    
    # Get PDF bytes
    buffer.seek(0)
    return buffer.getvalue()


async def generate_comparison_report(
    facade_id: str,
    sensor_name: str,
    start: Optional[str] = None,
    end: Optional[str] = None
) -> bytes:
    """
    Generates a professional PDF comparison report between refrigerated and non-refrigerated facades.

    HU19: Generate PDF reports with charts.
    HU17: Compare performance with and without refrigeration.

    Parameters:
    - facade_id (str): ID of the facade. Required.
    - sensor_name (str): Sensor to compare. Required.
    - start (Optional[str]): Start date/time for report period. Default: None.
    - end (Optional[str]): End date/time for report period. Default: None.

    Returns:
    - bytes: PDF file content as bytes.

    Exceptions:
    - RuntimeError: Raised if reportlab is not installed.
    - ValueError: Raised if insufficient data for report generation.
    """
    if not REPORTLAB_AVAILABLE:
        raise RuntimeError("reportlab library is required for PDF generation")
    
    # Create PDF buffer
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        rightMargin=2*cm, 
        leftMargin=2*cm,
        topMargin=3*cm, 
        bottomMargin=3*cm,
        title=f"Comparison Report - {sensor_name}"
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Professional styles
    title_style = ParagraphStyle(
        'ComparisonTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=6*mm,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'ComparisonSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#555555'),
        spaceAfter=10*mm,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'ComparisonHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=4*mm,
        spaceBefore=6*mm,
        fontName='Helvetica-Bold',
        backColor=colors.HexColor('#E8F4F8')
    )
    
    normal_style = ParagraphStyle(
        'ComparisonNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY
    )
    
    # Cover Page
    elements.append(Spacer(1, 4*cm))
    title_text = "FACADE PERFORMANCE COMPARISON REPORT"
    elements.append(Paragraph(title_text, title_style))
    
    subtitle_text = f"Sensor: {sensor_name} - Facade ID: {facade_id}"
    elements.append(Paragraph(subtitle_text, subtitle_style))
    
    elements.append(Spacer(1, 2*cm))
    
    # Report metadata
    report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    metadata_data = [
        ["Comparison Report Information", ""],
        ["Generated Date:", report_date],
        ["Facade ID:", facade_id],
        ["Sensor:", sensor_name],
        ["Period Start:", start if start else "N/A"],
        ["Period End:", end if end else "N/A"],
        ["Comparison:", "Refrigerated vs. Non-Refrigerated"]
    ]
    
    metadata_table = Table(metadata_data, colWidths=[7*cm, 7*cm])
    metadata_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 13),
        ('SPAN', (0, 0), (1, 0)),
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#E8F4F8')),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(metadata_table)
    elements.append(PageBreak())
    
    # === SECTION 1: Comparison Overview ===
    elements.append(Paragraph("1. COMPARISON OVERVIEW", heading_style))
    elements.append(Spacer(1, 4*mm))
    
    intro_text = f"""
    This report compares the performance of <b>{sensor_name}</b> between refrigerated and non-refrigerated
    facade configurations for Facade ID {facade_id}. The analysis includes statistical summaries,
    visual representations, and performance insights to validate the impact of the refrigeration system.
    """
    elements.append(Paragraph(intro_text, normal_style))
    elements.append(Spacer(1, 6*mm))
    
    # Get comparison data
    try:
        comparison = await storage_controller.compare_facade_types(
            facade_id=facade_id,
            sensor=sensor_name,
            start=start,
            end=end,
            limit=1000
        )
        
        refrigerada_data = comparison.get("refrigerada", [])
        no_refrigerada_data = comparison.get("no_refrigerada", [])
        
        if not refrigerada_data and not no_refrigerada_data:
            raise ValueError("No comparison data available")
        
        # === SECTION 2: Statistical Analysis ===
        elements.append(Paragraph("2. STATISTICAL ANALYSIS", heading_style))
        elements.append(Spacer(1, 4*mm))
        
        # Calculate statistics
        ref_values = [float(r["value"]) for r in refrigerada_data if r.get("value") is not None]
        no_ref_values = [float(r["value"]) for r in no_refrigerada_data if r.get("value") is not None]
        
        ref_avg = sum(ref_values) / len(ref_values) if ref_values else 0
        ref_min = min(ref_values) if ref_values else 0
        ref_max = max(ref_values) if ref_values else 0
        ref_count = len(ref_values)
        
        no_ref_avg = sum(no_ref_values) / len(no_ref_values) if no_ref_values else 0
        no_ref_min = min(no_ref_values) if no_ref_values else 0
        no_ref_max = max(no_ref_values) if no_ref_values else 0
        no_ref_count = len(no_ref_values)
        
        difference = abs(ref_avg - no_ref_avg)
        improvement_pct = ((no_ref_avg - ref_avg) / no_ref_avg * 100) if no_ref_avg != 0 else 0
        
        # Statistics table
        stats_data = [
            ["Metric", "Refrigerated", "Non-Refrigerated", "Difference"],
            ["Average", f"{ref_avg:.2f}", f"{no_ref_avg:.2f}", f"{difference:.2f}"],
            ["Minimum", f"{ref_min:.2f}", f"{no_ref_min:.2f}", f"{abs(ref_min - no_ref_min):.2f}"],
            ["Maximum", f"{ref_max:.2f}", f"{no_ref_max:.2f}", f"{abs(ref_max - no_ref_max):.2f}"],
            ["Data Points", str(ref_count), str(no_ref_count), "-"],
            ["Temperature Reduction", "-", "-", f"{improvement_pct:.2f}%"]
        ]
        
        stats_table = Table(stats_data, colWidths=[5*cm, 3.5*cm, 3.5*cm, 3*cm])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff7f0e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#FFF4E6')),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('ROWBACKGROUNDS', (1, 1), (-1, -1), [colors.white, colors.HexColor('#FFF8F0')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            # Highlight the last row (improvement)
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#90EE90')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        
        elements.append(stats_table)
        elements.append(Spacer(1, 8*mm))
        
        # === SECTION 3: Visual Comparison ===
        elements.append(PageBreak())
        elements.append(Paragraph("3. VISUAL COMPARISON", heading_style))
        elements.append(Spacer(1, 4*mm))
        
        visual_text = """
        The following chart overlays measurements from both facade types over the analysis period.
        This visualization highlights performance differences and the impact of refrigeration on temperature control.
        """
        elements.append(Paragraph(visual_text, normal_style))
        elements.append(Spacer(1, 4*mm))
        
        # Generate comparison chart
        try:
            chart_bytes = chart_manager.generate_comparison_chart(
                data1=refrigerada_data,
                data2=no_refrigerada_data,
                label1="Refrigerated Facade",
                label2="Non-Refrigerated Facade",
                title=f"{sensor_name} Comparison - Facade {facade_id}",
                ylabel=sensor_name
            )
            
            chart_img = Image(io.BytesIO(chart_bytes), width=16*cm, height=10*cm)
            elements.append(chart_img)
            elements.append(Spacer(1, 6*mm))
            
        except Exception as e:
            elements.append(Paragraph(f"Chart generation error: {str(e)}", normal_style))
        
        # === SECTION 4: Key Findings ===
        elements.append(PageBreak())
        elements.append(Paragraph("4. KEY FINDINGS & INSIGHTS", heading_style))
        elements.append(Spacer(1, 4*mm))
        
        findings_text = f"""
        <b>Performance Summary:</b><br/>
        • The refrigerated facade shows an average {sensor_name} value of {ref_avg:.2f}<br/>
        • The non-refrigerated facade shows an average {sensor_name} value of {no_ref_avg:.2f}<br/>
        • The difference between configurations is {difference:.2f} units<br/>
        • Refrigeration achieves approximately {abs(improvement_pct):.2f}% temperature reduction<br/><br/>
        
        <b>Data Quality:</b><br/>
        • Refrigerated facade: {ref_count} measurements analyzed<br/>
        • Non-refrigerated facade: {no_ref_count} measurements analyzed<br/>
        • Data completeness: {"Excellent" if min(ref_count, no_ref_count) > 500 else "Good" if min(ref_count, no_ref_count) > 100 else "Limited"}<br/><br/>
        
        <b>Interpretation:</b><br/>
        {'The refrigerated system demonstrates significant cooling performance, maintaining lower panel temperatures.' if improvement_pct > 5 else 'Both systems show similar thermal behavior in the analyzed period.'}<br/>
        Temperature control is critical for photovoltaic efficiency, as every degree of temperature reduction
        can improve electrical output by approximately 0.4-0.5%.<br/><br/>
        
        <b>Recommendations:</b><br/>
        • Continue monitoring to establish long-term performance trends<br/>
        • Analyze energy consumption vs. cooling benefit for ROI calculation<br/>
        • Consider seasonal variations in refrigeration effectiveness<br/>
        • Validate electrical power output improvement from cooling<br/>
        """
        
        elements.append(Paragraph(findings_text, normal_style))
        
    except Exception as e:
        error_text = f"""
        <b>Data Retrieval Error:</b><br/>
        Unable to generate comparison analysis: {str(e)}<br/><br/>
        
        <b>Possible Causes:</b><br/>
        • Insufficient data in the specified time period<br/>
        • Missing sensor measurements for one or both facade types<br/>
        • Database connectivity issues<br/><br/>
        
        Please verify data availability and try generating the report again.
        """
        elements.append(Paragraph(error_text, normal_style))
    
    # Final footer
    elements.append(Spacer(1, 3*cm))
    final_footer = Paragraph(
        f"<i>Comparison report generated by Solar Facades Monitoring System on {report_date}</i>",
        ParagraphStyle(
            'FinalFooter',
            parent=normal_style,
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
    )
    elements.append(final_footer)
    
    # Build PDF with custom canvas
    doc.build(elements, canvasmaker=ReportCanvas)
    buffer.seek(0)
    return buffer.getvalue()


async def generate_multi_facade_comparison_report(
    sensor_name: str,
    start: Optional[str] = None,
    end: Optional[str] = None
) -> bytes:
    """
    Generates a PDF comparison report comparing a sensor ACROSS ALL facades in the system.
    
    Automatically detects all facades and compares the sensor values between them,
    identifying which facades are refrigerated vs non-refrigerated.

    HU19: Generate PDF reports with charts.
    HU17: Compare performance with and without refrigeration.

    Parameters:
    - sensor_name (str): Sensor to compare across facades. Required.
    - start (Optional[str]): Start date/time for report period. Default: None.
    - end (Optional[str]): End date/time for report period. Default: None.

    Returns:
    - bytes: PDF file content as bytes.

    Exceptions:
    - RuntimeError: Raised if reportlab is not installed.
    - ValueError: Raised if insufficient data for report generation.
    """
    if not REPORTLAB_AVAILABLE:
        raise RuntimeError("reportlab library is required for PDF generation")
    
    # Get all facades
    pool = get_pool()
    if not pool:
        raise RuntimeError("Database connection pool not initialized")
    
    try:
        async with pool.acquire() as conn:
            facades_query = """
                SELECT DISTINCT facade_id, facade_type
                FROM measurements
                WHERE sensor_name = $1
                ORDER BY facade_id
            """
            facades = await conn.fetch(facades_query, sensor_name)
            
            if not facades or len(facades) < 2:
                raise ValueError(f"Need at least 2 facades for comparison. Found: {len(facades) if facades else 0}")
            
            # Get data for each facade
            facade_data = {}
            for facade in facades:
                fid = facade['facade_id']
                ftype = facade['facade_type']
                
                data_query = """
                    SELECT ts, value
                    FROM measurements
                    WHERE facade_id = $1 
                    AND sensor_name = $2
                """
                params = [fid, sensor_name]
                idx = 3
                
                if start:
                    data_query += f" AND ts >= ${idx}"
                    params.append(start)
                    idx += 1
                
                if end:
                    data_query += f" AND ts <= ${idx}"
                    params.append(end)
                
                data_query += " ORDER BY ts DESC LIMIT 1000"
                
                rows = await conn.fetch(data_query, *params)
                
                facade_data[fid] = {
                    'type': ftype,
                    'data': [(row['ts'], row['value']) for row in rows]
                }
    
    except Exception as e:
        print(f"❌ Error fetching multi-facade data: {e}")
        raise ValueError(f"Error retrieving facade data: {str(e)}")
    
    # Create PDF buffer
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        rightMargin=2*cm, 
        leftMargin=2*cm,
        topMargin=3*cm, 
        bottomMargin=3*cm,
        title=f"Multi-Facade Comparison - {sensor_name}"
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Professional styles
    title_style = ParagraphStyle(
        'ComparisonTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=6*mm,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'ComparisonSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#555555'),
        spaceAfter=10*mm,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'ComparisonHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=4*mm,
        spaceBefore=6*mm,
        fontName='Helvetica-Bold',
        backColor=colors.HexColor('#E8F4F8')
    )
    
    normal_style = ParagraphStyle(
        'ComparisonNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY
    )
    
    # Cover Page
    elements.append(Spacer(1, 4*cm))
    title_text = "MULTI-FACADE COMPARISON REPORT"
    elements.append(Paragraph(title_text, title_style))
    
    subtitle_text = f"Sensor: {sensor_name}"
    elements.append(Paragraph(subtitle_text, subtitle_style))
    
    elements.append(Spacer(1, 2*cm))
    
    # Report metadata
    report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    facades_list = ", ".join([f"Facade {fid} ({facade_data[fid]['type']})" for fid in facade_data.keys()])
    
    metadata_data = [
        ["Multi-Facade Comparison Information", ""],
        ["Generated Date:", report_date],
        ["Sensor:", sensor_name],
        ["Facades Compared:", facades_list],
        ["Period Start:", start if start else "N/A"],
        ["Period End:", end if end else "N/A"],
    ]
    
    metadata_table = Table(metadata_data, colWidths=[7*cm, 7*cm])
    metadata_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 13),
        ('SPAN', (0, 0), (1, 0)),
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#E8F4F8')),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(metadata_table)
    elements.append(PageBreak())
    
    # === SECTION 1: Statistical Summary ===
    elements.append(Paragraph("1. STATISTICAL SUMMARY", heading_style))
    elements.append(Spacer(1, 4*mm))
    
    intro_text = f"""
    This report compares <b>{sensor_name}</b> across all available facades in the system.
    The analysis provides statistical insights and visual comparisons to evaluate performance
    differences between refrigerated and non-refrigerated configurations.
    """
    elements.append(Paragraph(intro_text, normal_style))
    elements.append(Spacer(1, 6*mm))
    
    # Calculate statistics for each facade
    stats_data = [["Facade ID", "Type", "Avg Value", "Min Value", "Max Value", "Std Dev", "Samples"]]
    
    for fid in sorted(facade_data.keys()):
        fdata = facade_data[fid]
        values = [v for _, v in fdata['data']]
        
        if values:
            avg_val = sum(values) / len(values)
            min_val = min(values)
            max_val = max(values)
            std_dev = (sum((x - avg_val) ** 2 for x in values) / len(values)) ** 0.5
            
            stats_data.append([
                f"Facade {fid}",
                fdata['type'].capitalize(),
                f"{avg_val:.2f}",
                f"{min_val:.2f}",
                f"{max_val:.2f}",
                f"{std_dev:.2f}",
                str(len(values))
            ])
    
    stats_table = Table(stats_data, colWidths=[2*cm, 2.5*cm, 2*cm, 2*cm, 2*cm, 2*cm, 1.5*cm])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    elements.append(stats_table)
    elements.append(Spacer(1, 8*mm))
    
    # === SECTION 2: Comparison Chart ===
    elements.append(Paragraph("2. VISUAL COMPARISON", heading_style))
    elements.append(Spacer(1, 4*mm))
    
    chart_text = """
    The following chart shows the time-series comparison of the sensor values across all facades.
    This allows for direct visual assessment of performance differences.
    """
    elements.append(Paragraph(chart_text, normal_style))
    elements.append(Spacer(1, 6*mm))
    
    # Generate comparison chart
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        colors_map = {
            'refrigerada': '#1f77b4',
            'no_refrigerada': '#ff7f0e'
        }
        
        for fid in sorted(facade_data.keys()):
            fdata = facade_data[fid]
            if fdata['data']:
                timestamps = [ts for ts, _ in fdata['data']]
                values = [v for _, v in fdata['data']]
                
                color = colors_map.get(fdata['type'], '#2ca02c')
                label = f"Facade {fid} ({fdata['type']})"
                
                ax.plot(timestamps, values, label=label, color=color, linewidth=2, alpha=0.7)
        
        ax.set_xlabel('Time', fontsize=12, fontweight='bold')
        ax.set_ylabel(f'{sensor_name}', fontsize=12, fontweight='bold')
        ax.set_title(f'{sensor_name} - Multi-Facade Comparison', fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save chart to buffer
        chart_buffer = io.BytesIO()
        plt.savefig(chart_buffer, format='png', dpi=150, bbox_inches='tight')
        chart_buffer.seek(0)
        plt.close()
        
        # Add chart to PDF
        img = Image(chart_buffer, width=16*cm, height=8*cm)
        elements.append(img)
        
    except Exception as e:
        print(f"⚠️  Could not generate chart: {e}")
        elements.append(Paragraph(f"[Chart generation failed: {str(e)}]", normal_style))
    
    elements.append(Spacer(1, 8*mm))
    
    # === SECTION 3: Conclusions ===
    elements.append(Paragraph("3. CONCLUSIONS", heading_style))
    elements.append(Spacer(1, 4*mm))
    
    # Calculate differences between refrigerated and non-refrigerated
    refrig_facades = {fid: fdata for fid, fdata in facade_data.items() if fdata['type'] == 'refrigerada'}
    no_refrig_facades = {fid: fdata for fid, fdata in facade_data.items() if fdata['type'] == 'no_refrigerada'}
    
    if refrig_facades and no_refrig_facades:
        # Get averages
        refrig_values = []
        for fdata in refrig_facades.values():
            refrig_values.extend([v for _, v in fdata['data']])
        
        no_refrig_values = []
        for fdata in no_refrig_facades.values():
            no_refrig_values.extend([v for _, v in fdata['data']])
        
        if refrig_values and no_refrig_values:
            avg_refrig = sum(refrig_values) / len(refrig_values)
            avg_no_refrig = sum(no_refrig_values) / len(no_refrig_values)
            difference = avg_no_refrig - avg_refrig
            percent_diff = (difference / avg_no_refrig * 100) if avg_no_refrig != 0 else 0
            
            conclusion_text = f"""
            <b>Key Findings:</b><br/>
            • Average {sensor_name} (Refrigerated): {avg_refrig:.2f}<br/>
            • Average {sensor_name} (Non-Refrigerated): {avg_no_refrig:.2f}<br/>
            • Difference: {difference:.2f} ({abs(percent_diff):.1f}%)<br/>
            <br/>
            <b>Interpretation:</b><br/>
            The refrigeration system shows a {"reduction" if difference > 0 else "increase"} of 
            {abs(difference):.2f} units ({abs(percent_diff):.1f}%) compared to the non-refrigerated configuration.
            This demonstrates {"effective" if difference > 0 and "Temperature" in sensor_name else "the"} 
            thermal management impact of the active cooling system.
            """
            elements.append(Paragraph(conclusion_text, normal_style))
    else:
        elements.append(Paragraph("Insufficient data to calculate comparative conclusions.", normal_style))
    
    # Final footer
    elements.append(Spacer(1, 2*cm))
    final_footer = Paragraph(
        "Report generated by BICPV Monitoring System",
        ParagraphStyle(
            'FinalFooter',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
    )
    elements.append(final_footer)
    
    # Build PDF
    doc.build(elements, canvasmaker=ReportCanvas)
    buffer.seek(0)
    return buffer.getvalue()
