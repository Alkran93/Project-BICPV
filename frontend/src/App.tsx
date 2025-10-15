import { useState } from "react";
import Sidebar from "./components/Sidebar";
import Home from "./pages/Home";
import PanelDetail from "./components/PanelDetail";
import SystemAnalysis from "./components/SystemAnalysis";
import ComparisonChart from "./components/ComparisonChart";

// Nuevas vistas
import AlertsHistory from "./views/AlertsHistory";
import TemperatureComparison from "./views/TemperatureComparison";
import RefrigerantCycle from "./views/RefrigerantCycle";
import AlertNotifications from "./views/AlertNotifications";
import WaterTemperatures from "./views/WaterTemperatures";
import ExportCSV from "./views/ExportCSV";

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

  // ✅ Nuevos estados para las HU
  const [showAlertsHistory, setShowAlertsHistory] = useState(false);
  const [showRealtimeAlerts, setShowRealtimeAlerts] = useState(false);
  const [showCSVExport, setShowCSVExport] = useState(false);
  const [showTempComparison, setShowTempComparison] = useState(false);
  const [showRefrigerantCycle, setShowRefrigerantCycle] = useState(false);
  const [showWaterTemps, setShowWaterTemps] = useState(false);

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
  const resetViews = () => {
    setShowSystemAnalysis(false);
    setShowComparison(false);
    setShowAlertsHistory(false);
    setShowRealtimeAlerts(false);
    setShowCSVExport(false);
    setShowTempComparison(false);
    setShowRefrigerantCycle(false);
    setShowWaterTemps(false);
  };

  const handlePanelClick = (panel: PanelData) => {
    resetViews();
    setSelectedPanel(panel);
  };

  const handleBackToOverview = () => {
    setSelectedPanel(null);
    resetViews();
  };

  const handleSystemAnalysisClick = () => {
    resetViews();
    setShowSystemAnalysis(true);
  };

  const handleBackToPanelDetail = () => {
    setShowSystemAnalysis(false);
  };

  const handleComparisonClick = () => {
    resetViews();
    setShowComparison(true);
    setSelectedPanel(null);
  };

  // ✅ Nuevos handlers
  const handleAlertsClick = () => {
    resetViews();
    setShowAlertsHistory(true);
  };

  const handleRealtimeAlertsClick = () => {
    resetViews();
    setShowRealtimeAlerts(true);
  };

  const handleCSVExportClick = () => {
    resetViews();
    setShowCSVExport(true);
  };

  const handleTempComparisonClick = () => {
    resetViews();
    setShowTempComparison(true);
  };

  const handleRefrigerantCycleClick = () => {
    resetViews();
    setShowRefrigerantCycle(true);
  };

  const handleWaterTempsClick = () => {
    resetViews();
    setShowWaterTemps(true);
  };


  return (
    <div className="app-root">
      {/* Sidebar siempre visible */}
      <Sidebar
        onComparisonClick={handleComparisonClick}
        onAlertsClick={handleAlertsClick}
        onRealtimeAlertsClick={handleRealtimeAlertsClick}
        onCSVExportClick={handleCSVExportClick}
        onTempComparisonClick={handleTempComparisonClick}
        onRefrigerantCycleClick={handleRefrigerantCycleClick}
        onWaterTempsClick={handleWaterTempsClick}
      />

      <div className="content">
        {/* ✅ HU21 - Historial de alertas */}
        {showAlertsHistory && <AlertsHistory />}

        {/* ✅ HU15 - Alertas automáticas */}
        {showRealtimeAlerts && <AlertNotifications />}

        {/* ✅ HU18 - Exportar CSV */}
        {showCSVExport && <ExportCSV />}

        {/* ✅ HU13 - Comparativa de temperaturas */}
        {showTempComparison && <TemperatureComparison />}

        {/* ✅ HU10 - Temperatura del refrigerante en el ciclo */}
        {showRefrigerantCycle && <RefrigerantCycle />}

        {/* ✅ HU12 - Temperatura del agua en el intercambiador */}
        {showWaterTemps && <WaterTemperatures />}

        {/* Comparación térmica general existente */}
        {showComparison && <ComparisonChart onBack={handleBackToOverview} id="1" />}

        {/* Análisis del sistema */}
        {showSystemAnalysis && selectedPanel && (
          <SystemAnalysis
            title={selectedPanel.title}
            refrigerated={selectedPanel.refrigerated}
            sensors={selectedPanel.sensors}
            refrigeratedData={panelsData.find((p) => p.refrigerated)!}
            nonRefrigeratedData={panelsData.find((p) => !p.refrigerated)!}
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

        {/* Vista principal */}
        {!selectedPanel &&
          !showSystemAnalysis &&
          !showComparison &&
          !showAlertsHistory &&
          !showRealtimeAlerts &&
          !showCSVExport &&
          !showTempComparison &&
          !showRefrigerantCycle &&
          !showWaterTemps && (
            <Home panelsData={panelsData} onPanelClick={handlePanelClick} />
          )}
      </div>
    </div>
  );
}
