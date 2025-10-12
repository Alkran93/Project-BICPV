import api from "../services/api";

export default function ExportCSV({ facadeId = 1 }: { facadeId?: number }) {
  const handleExport = async (type: "facade" | "compare") => {
    const res = await api.get(`/exports/csv/${type}/${facadeId}`, {
      responseType: "blob",
    });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `${type}_data.csv`);
    document.body.appendChild(link);
    link.click();
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Exportar Datos CSV</h2>
      <button
        onClick={() => handleExport("facade")}
        className="bg-blue-600 text-white px-4 py-2 rounded mr-3"
      >
        Exportar Fachada
      </button>
      <button
        onClick={() => handleExport("compare")}
        className="bg-green-600 text-white px-4 py-2 rounded"
      >
        Exportar Comparación
      </button>
    </div>
  );
}
