import { useEffect, useState } from "react";
import api from "../services/api";

interface Alert {
  timestamp: string;
  type: string;
  message: string;
  sensor: string;
}

export default function AlertsHistory() {
  const [alerts, setAlerts] = useState<Alert[]>([]);

  useEffect(() => {
    api.get("/alerts/history").then((res) => setAlerts(res.data));
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Historial de Alertas</h2>
      {alerts.length === 0 ? (
        <p>No se han registrado alertas.</p>
      ) : (
        <table className="w-full border-collapse border border-gray-300">
          <thead>
            <tr className="bg-gray-100">
              <th className="border p-2">Fecha</th>
              <th className="border p-2">Tipo</th>
              <th className="border p-2">Mensaje</th>
              <th className="border p-2">Sensor</th>
            </tr>
          </thead>
          <tbody>
            {alerts.map((a, i) => (
              <tr key={i}>
                <td className="border p-2">{a.timestamp}</td>
                <td className="border p-2">{a.type}</td>
                <td className="border p-2">{a.message}</td>
                <td className="border p-2">{a.sensor}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
