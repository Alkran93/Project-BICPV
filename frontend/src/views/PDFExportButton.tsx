import { useState } from 'react';
import { FileDown, Loader } from 'lucide-react';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

interface PDFExportButtonProps {
  title: string;
  elementId: string;
  filename?: string;
  includeTimestamp?: boolean;
}

export default function PDFExportButton({
  title,
  elementId,
  filename = 'reporte',
  includeTimestamp = true
}: PDFExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false);

  const exportToPDF = async () => {
    setIsExporting(true);

    try {
      // Obtener el elemento a exportar
      const element = document.getElementById(elementId);
      
      if (!element) {
        throw new Error(`Elemento con ID "${elementId}" no encontrado`);
      }

      console.log('📄 Generando PDF...');

      // Capturar el elemento como imagen
      const canvas = await html2canvas(element, {
        scale: 2, // Mayor calidad
        useCORS: true,
        logging: false,
        backgroundColor: '#ffffff'
      });

      const imgData = canvas.toDataURL('image/png');
      
      // Crear PDF
      const pdf = new jsPDF({
        orientation: canvas.width > canvas.height ? 'landscape' : 'portrait',
        unit: 'mm',
        format: 'a4'
      });

      // Calcular dimensiones para ajustar la imagen al PDF
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = pdf.internal.pageSize.getHeight();
      const imgWidth = canvas.width;
      const imgHeight = canvas.height;
      const ratio = Math.min(pdfWidth / imgWidth, pdfHeight / imgHeight);
      
      const imgX = (pdfWidth - imgWidth * ratio) / 2;
      const imgY = 15;

      // Agregar título
      pdf.setFontSize(16);
      pdf.setFont('helvetica', 'bold');
      pdf.text(title, pdfWidth / 2, 10, { align: 'center' });

      // Agregar timestamp si se solicita
      if (includeTimestamp) {
        pdf.setFontSize(9);
        pdf.setFont('helvetica', 'normal');
        pdf.setTextColor(128, 128, 128);
        pdf.text(
          `Generado: ${new Date().toLocaleString('es-ES')}`,
          pdfWidth / 2,
          pdfHeight - 5,
          { align: 'center' }
        );
      }

      // Agregar imagen
      pdf.addImage(
        imgData,
        'PNG',
        imgX,
        imgY,
        imgWidth * ratio,
        imgHeight * ratio
      );

      // Generar nombre de archivo
      const timestamp = includeTimestamp 
        ? `_${new Date().toISOString().split('T')[0]}`
        : '';
      const finalFilename = `${filename}${timestamp}.pdf`;

      // Descargar
      pdf.save(finalFilename);

      console.log('✅ PDF generado exitosamente:', finalFilename);
    } catch (error) {
      console.error('❌ Error al generar PDF:', error);
      alert('Error al generar el PDF. Por favor, intenta de nuevo.');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <button
      onClick={exportToPDF}
      disabled={isExporting}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem',
        padding: '0.75rem 1.5rem',
        backgroundColor: isExporting ? '#6c757d' : '#dc3545',
        color: 'white',
        border: 'none',
        borderRadius: '8px',
        cursor: isExporting ? 'not-allowed' : 'pointer',
        fontSize: '14px',
        fontWeight: '600',
        transition: 'background-color 0.2s'
      }}
      onMouseEnter={(e) => {
        if (!isExporting) {
          e.currentTarget.style.backgroundColor = '#c82333';
        }
      }}
      onMouseLeave={(e) => {
        if (!isExporting) {
          e.currentTarget.style.backgroundColor = '#dc3545';
        }
      }}
    >
      {isExporting ? (
        <>
          <Loader size={18} style={{ animation: 'spin 1s linear infinite' }} />
          Generando PDF...
        </>
      ) : (
        <>
          <FileDown size={18} />
          Exportar a PDF
        </>
      )}
    </button>
  );
}