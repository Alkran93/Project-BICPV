import Header from "../components/Header";
import Panel from "../components/Panel";

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

export default function Home({
  panelsData,
  onPanelClick,
}: {
  panelsData: PanelData[];
  onPanelClick: (panel: PanelData) => void;
}) {
  return (
    <div className="content">
      <Header viewMode="Temperatura" setViewMode={() => {}} />

      <main className="container">
        <h1 className="page-title">Estado de Fachadas Solares Fotovoltaicas</h1>
        <p className="subtle" style={{ marginBottom: 18 }}>
          Vista general en tiempo real de los paneles refrigerado y sin refrigerar.
          <span className="click-hint">
            {" "}
            Haz clic en cualquier panel para ver detalles.
          </span>
        </p>

        <section className="panels-grid" aria-live="polite">
          {panelsData.map(panel => (
            <Panel
              key={panel.id}
              id={panel.id}
              title={panel.title}
              refrigerated={panel.refrigerated}
              faults={panel.faults}
              temperature={getAverageTemperature(panel.sensors)}
              viewMode="Temperatura"
              sensors={panel.sensors}
              onClick={() => onPanelClick(panel)}
            />
          ))}
        </section>
      </main>
    </div>
  );
}
