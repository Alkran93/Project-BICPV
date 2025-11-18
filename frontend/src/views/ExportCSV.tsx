import { useState } from "react";

export default function ExportCSV({ facadeId = 1 }: { facadeId?: number }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  // Puedes cambiar este sensor si quieres exportar otro tipo
  const sensor = "temperature";

  const handleExport = async (type: "facade" | "compare") => {
    setLoading(true);
    setError(null);
    setMessage(null);

    try {
      let url = "";

      if (type === "facade") {
        // Export normal
        url = `http://34.135.241.88:8000/exports/csv/facade/${facadeId}`;
      } else {
        // Export comparativo: requiere facade_id + sensor
        fetch (`http://34.135.241.88:8000/exports/csv/compare?facade_id=${facadeId}&sensor=${sensor}`);
      }

      console.log(`⬇️ Exporting CSV from: ${url}`);

      const response = await fetch(url);

      if (!response.ok) {
        if (response.status === 404)
          throw new Error("No hay datos disponibles para exportar.");
        if (response.status === 422)
          throw new Error("Faltan parámetros requeridos (facade_id o sensor).");
        if (response.status === 500)
          throw new Error("Error interno del servidor al generar el CSV.");
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.setAttribute(
        "download",
        `${type}_data_fachada_${facadeId}_${sensor}.csv`
      );
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(downloadUrl);

      setMessage(`✅ Archivo CSV de tipo "${type}" exportado correctamente.`);
    } catch (err) {
      console.error("💥 Error al exportar CSV:", err);
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        padding: "2rem",
        backgroundColor: "#f8f9fa",
        minHeight: "100vh",
      }}
    >
      <h2
        style={{
          fontSize: "1.75rem",
          fontWeight: "bold",
          color: "#214B4E",
          marginBottom: "1.5rem",
        }}
      >
        📦 Exportar Datos CSV
      </h2>

      <div style={{ display: "flex", gap: "1rem", marginBottom: "1rem" }}>
        <button
          onClick={() => handleExport("facade")}
          disabled={loading}
          style={{
            backgroundColor: "#007bff",
            color: "white",
            padding: "0.75rem 1.5rem",
            border: "none",
            borderRadius: "8px",
            cursor: loading ? "not-allowed" : "pointer",
            fontWeight: "600",
          }}
        >
          {loading ? "Exportando..." : "Exportar Fachada"}
        </button>

        <button
          onClick={() => handleExport("compare")}
          disabled={loading}
          style={{
            backgroundColor: "#28a745",
            color: "white",
            padding: "0.75rem 1.5rem",
            border: "none",
            borderRadius: "8px",
            cursor: loading ? "not-allowed" : "pointer",
            fontWeight: "600",
          }}
        >
          {loading ? "Exportando..." : "Exportar Comparación"}
        </button>
      </div>

      {error && (
        <div
          style={{
            backgroundColor: "#f8d7da",
            border: "1px solid #f5c6cb",
            color: "#721c24",
            padding: "1rem",
            borderRadius: "8px",
          }}
        >
          <strong>Error:</strong> {error}
        </div>
      )}

      {message && (
        <div
          style={{
            backgroundColor: "#d4edda",
            border: "1px solid #c3e6cb",
            color: "#155724",
            padding: "1rem",
            borderRadius: "8px",
          }}
        >
          {message}
        </div>
      )}
    </div>
  );
}
