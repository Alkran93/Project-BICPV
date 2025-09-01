import React from "react";
import "./App.css";
import Panel from "./components/Panel";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";

function App() {
  return (
    <div className="app">
      <Header />
      <div className="layout">
        <Sidebar />
        {/* Aquí le paso el title que pide Panel */}
        <Panel title="Panel principal">
          <p>Este es el contenido dentro del panel</p>
        </Panel>
      </div>
    </div>
  );
}

export default App;
