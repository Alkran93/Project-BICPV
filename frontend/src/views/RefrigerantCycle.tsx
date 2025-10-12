import { useEffect, useState } from "react";
import { Bar } from "react-chartjs-2";
import api from "../services/api";

interface CyclePoint {
  point: string;
  temperature: number;
}

export default function RefrigerantCycle({ facadeId = 1 }: { facadeId?: number }) {
  const [cycle, setCycle] = useState<CyclePoint[]>([]);

  useEffect(() => {
    api.get(`/temperatures/refrigerant-cycle/${facadeId}`).then((res) => setCycle(res.data));
  }, [facadeId]);

  const chartData = {
    labels: cycle.map((c) => c.point),
    datasets: [
      {
        label: "Temperatura (°C)",
        data: cycle.map((c) => c.temperature),
        backgroundColor: "rgba(75,192,192,0.6)",
      },
    ],
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Temperaturas del Ciclo de Refrigeración</h2>
      <Bar data={chartData} />
    </div>
  );
}
