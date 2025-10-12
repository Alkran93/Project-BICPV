import { useEffect, useState } from "react";
import api from "../services/api";

interface Anomaly {
  sensor: string;
  type: string;
  message: string;
}

export default function AlertNotifications() {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);

  useEffect(() => {
    const fetchAlerts = async () => {
      const res = await api.get("/alerts/anomalies");
      setAnomalies(res.data);
    };

    fetchAlerts();
    const interval = setInterval(fetchAlerts, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Alertas en Tiempo Real</h2>
      {anomalies.length === 0 ? (
        <p>No se han detectado anomalías.</p>
      ) : (
        anomalies.map((a, i) => (
          <div key={i} className="p-3 bg-red-100 border-l-4 border-red-500 mb-2">
            <p><strong>Sensor:</strong> {a.sensor}</p>
            <p><strong>Tipo:</strong> {a.type}</p>
            <p><strong>Mensaje:</strong> {a.message}</p>
          </div>
        ))
      )}
    </div>
  );
}
