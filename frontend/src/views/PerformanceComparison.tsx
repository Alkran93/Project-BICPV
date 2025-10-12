import { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import api from "../services/api";

interface PerfData {
  timestamp: string;
  with_refrigeration: number;
  without_refrigeration: number;
}

export default function PerformanceComparison({ facadeId = 1 }: { facadeId?: number }) {
  const [compare, setCompare] = useState<PerfData[]>([]);

  useEffect(() => {
    api.get(`/analytics/compare/${facadeId}`).then((res) => setCompare(res.data));
  }, [facadeId]);

  const chartData = {
    labels: compare.map((c) => c.timestamp),
    datasets: [
      {
        label: "Con Refrigeración",
        data: compare.map((c) => c.with_refrigeration),
        borderColor: "rgb(75, 192, 192)",
        tension: 0.3,
      },
      {
        label: "Sin Refrigeración",
        data: compare.map((c) => c.without_refrigeration),
        borderColor: "rgb(255, 159, 64)",
        tension: 0.3,
      },
    ],
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">
        Comparación de Rendimiento — Con vs Sin Refrigeración
      </h2>
      <Line data={chartData} />
    </div>
  );
}
