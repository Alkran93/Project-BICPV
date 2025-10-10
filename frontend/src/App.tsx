import { useState } from "react";
import Sidebar from "./components/Sidebar";
import Home from "./pages/Home";
import PanelDetail from "./components/PanelDetail";
import SystemAnalysis from "./components/SystemAnalysis";
import ComparisonChart from "./components/ComparisonChart";

type PanelData = {
  id: string;
  title: string;
  refrigerated: boolean;
  faults: number;
  sensors: number[];
};

function getAverageTemperature(sensors: number[]) {
  if (!sensors.length) return 0;
  return sensors.reduce((sum, t) => sum + t, 0) / sensors.length;
}

export default function App() {
  const [selectedPanel, setSelectedPanel] = useState<PanelData | null>(null);
  const [showSystemAnalysis, setShowSystemAnalysis] = useState(false);
  const [showComparison, setShowComparison] = useState(false);

  // Datos de prueba (puedes moverlos a un contexto o fetch real)
  const panelsData: PanelData[] = [
    {
      id: "refrigerated",
      title: "Refrigerado",
      refrigerated: true,
      faults: 0,
      sensors: [18, 25, 30, 28, 22, 35, 30, 29, 28, 30, 24, 26, 31, 32, 27],
    },
    {
      id: "non-refrigerated",
      title: "Sin Refrigerar",
      refrigerated: false,
      faults: 1,
      sensors: [42, 36, 29, 31, 28, 26, 18, 37, 37, 20, 28, 38, 35, 33, 29],
    },
  ];

  // Handlers de navegación
  const handlePanelClick = (panel: PanelData) => {
    setSelectedPanel(panel);
    setShowSystemAnalysis(false);
    setShowComparison(false);
  };

  const handleBackToOverview = () => {
    setSelectedPanel(null);
    setShowSystemAnalysis(false);
    setShowComparison(false);
  };

  const handleSystemAnalysisClick = () => {
    setShowSystemAnalysis(true);
  };

  const handleBackToPanelDetail = () => {
    setShowSystemAnalysis(false);
  };

  const handleComparisonClick = () => {
    setShowComparison(true);
    setSelectedPanel(null);
    setShowSystemAnalysis(false);
  };

  const handleBackFromComparison = () => {
    setShowComparison(false);
  };

  return (
    <div className="app-root">
      {/* Sidebar siempre visible */}
      <Sidebar onComparisonClick={handleComparisonClick} />

      <div className="content">
        {/* Comparación */}
        {showComparison && <ComparisonChart onBack={handleBackFromComparison} id="1" />}

        {/* Análisis del sistema */}
        {showSystemAnalysis && selectedPanel && (
          <SystemAnalysis
            title={selectedPanel.title}
            refrigerated={selectedPanel.refrigerated}
            sensors={selectedPanel.sensors}
            refrigeratedData={panelsData.find(p => p.refrigerated)!}
            nonRefrigeratedData={panelsData.find(p => !p.refrigerated)!}
            onBack={handleBackToPanelDetail}
          />
        )}

        {/* Detalle de un panel */}
        {!showSystemAnalysis && selectedPanel && !showComparison && (
          <PanelDetail
            title={selectedPanel.title}
            refrigerated={selectedPanel.refrigerated}
            faults={selectedPanel.faults}
            temperature={getAverageTemperature(selectedPanel.sensors)}
            sensors={selectedPanel.sensors}
            onBack={handleBackToOverview}
            onSystemTempClick={handleSystemAnalysisClick}
          />
        )}

        {/* Vista principal (Home dashboard) */}
        {!selectedPanel && !showComparison && !showSystemAnalysis && (
          <Home panelsData={panelsData} onPanelClick={handlePanelClick} />
        )}
      </div>
    </div>
  );
}
