import Panel from "../components/Panel";

export default function Home() {
  return (
    <main style={{ padding: 24 }}>
      <div className="panels-grid">
        <Panel title="Refrigerado" refrigerated faults={0} temperature={32.5} />
        <Panel title="Sin Refrigerar" refrigerated={false} faults={1} temperature={32.5} />
      </div>
    </main>
  );
}

