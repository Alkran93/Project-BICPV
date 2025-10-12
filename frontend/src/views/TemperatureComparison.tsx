import { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import api from "../services/api";

interface TempData {
  timestamp: string;
  refrigerant_temp: number;
  water_temp: number;
}

export default function TemperatureComparison({ facadeId = 1 }: { facadeId?: number }) {
  const [data, setData] = useState<TempData[]>([]);

  useEffect(() => {
    api.get(`/temperatures/exchanger/${facadeId}`).then((res) => setData(res.data));
  }, [facadeId]);

  const chartData = {
    labels: data.map((d) => d.timestamp),
    datasets: [
      {
        label: "Temperatura Refrigerante (°C)",
        data: data.map((d) => d.refrigerant_temp),
        borderColor: "rgb(255, 99, 132)",
        tension: 0.3,
      },
      {
        label: "Temperatura Agua (°C)",
        data: data.map((d) => d.water_temp),
        borderColor: "rgb(54, 162, 235)",
        tension: 0.3,
      },
    ],
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Comparativa de Temperaturas — Intercambiador</h2>
      <Line data={chartData} />
    </div>
  );
}
