import { useState, useEffect } from "react";

type HeaderProps = {
  viewMode: "Fachada" | "Temperatura";
  setViewMode: (mode: "Fachada" | "Temperatura") => void;
};

export default function Header({ viewMode, setViewMode }: HeaderProps) {
  const [now, setNow] = useState(() => new Date());

  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  return (
    <header className="app-header" role="banner">
      <div className="header-left">
        {" "}
        {now.toLocaleDateString(undefined, {
          weekday: "long",
          day: "numeric",
          month: "long",
          year: "numeric",
        })}{" "}
        - {now.toLocaleTimeString()}
      </div>

      <div className="header-right">
        {/* Botón toggle estilo moderno */}
        <div
          className={`toggle-switch ${viewMode}`}
          onClick={() =>
            setViewMode(viewMode === "Fachada" ? "Temperatura" : "Fachada")
          }
        >
          <div className="toggle-slider">{viewMode}</div>
        </div>

        <div className="status-dot" aria-hidden></div>
        <div className="subtle">Status</div>
      </div>
    </header>
  );
}
