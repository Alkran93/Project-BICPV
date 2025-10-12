import { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import api from "../services/api";

interface TempData {
  timestamp: string;
  inlet_temp: number;
  outlet_temp: number;
}

export default function WaterTemperatures({ facadeId = 1 }: { facadeId?: number }) {
  const [temps, setTemps] = useState<TempData[]>([]);

  useEffect(() => {
    api.get(`/temperatures/exchanger/${facadeId}`).then((res) => setTemps(res.data));
  }, [facadeId]);

  const chartData = {
    labels: temps.map((t) => t.timestamp),
    datasets: [
      {
        label: "Agua - Entrada (°C)",
        data: temps.map((t) => t.inlet_temp),
        borderColor: "rgb(54, 162, 235)",
        tension: 0.3,
      },
      {
        label: "Agua - Salida (°C)",
        data: temps.map((t) => t.outlet_temp),
        borderColor: "rgb(255, 205, 86)",
        tension: 0.3,
      },
    ],
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Temperaturas del Agua — Intercambiador</h2>
      <Line data={chartData} />
    </div>
  );
}
