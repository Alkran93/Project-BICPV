import React from "react";
import type { PanelProps } from "../types/Panel";
import "../styles/index.css"; // usa tu css global existente

export default function Panel({
  title,
  refrigerated = false,
  faults = 0,
  temperature = 0,
  icon,
}: PanelProps) {
  const stateClass = refrigerated ? "panel-ok" : "panel-alert";

  return (
    <article className={`panel ${stateClass}`} role="region" aria-label={title}>
      <div className="panel-visual" aria-hidden="true">
        {/* SVG simple estilizado: rack con 6 estantes */}
        <svg viewBox="0 0 200 360" width="220" height="396" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="g1" x1="0" x2="1">
              <stop offset="0" stopColor="#e6e9ee"/>
              <stop offset="1" stopColor="#cfd6df"/>
            </linearGradient>
            <linearGradient id="g2" x1="0" x2="1">
              <stop offset="0" stopColor="#2b3948"/>
              <stop offset="1" stopColor="#0f1721"/>
            </linearGradient>
          </defs>

          {/* estructura lateral */}
          <rect x="30" y="10" width="20" height="340" rx="2" fill="url(#g1)"/>
          <rect x="150" y="10" width="20" height="340" rx="2" fill="url(#g1)"/>
          {/* estantes (repetidos) */}
          {Array.from({length:6}).map((_, i) => {
            const y = 20 + i * 50;
            return (
              <g key={i}>
                <rect x="55" y={y} width="90" height="8" rx="1" fill="#9aa7b6" />
                <rect x="55" y={y+10} width="90" height="28" rx="2" fill="url(#g2)" opacity="0.95" />
                {/* divisiones internas del estante */}
                {Array.from({length:6}).map((__, j) => (
                  <rect key={j} x={62 + j*14} y={y+12} width="12" height="24" rx="1" fill="#0b1a22" opacity="0.35" />
                ))}
              </g>
            );
          })}
        </svg>
      </div>

      <div className="panel-info">
        <div className="panel-header">
          <h3 className="panel-title">{title}</h3>
          <div className="panel-status" title={refrigerated ? "Refrigerado" : "Sin refrigerar"}>
            {refrigerated ? (
              /* check icon */
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
                <path d="M20 6L9 17l-5-5" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            ) : (
              /* exclamation icon */
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
                <path d="M12 9v4" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M12 17h.01" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            )}
          </div>
        </div>

        <div className="panel-cards">
          <div className="info-card">
            <div className="info-value">{faults}</div>
            <div className="info-label">Fallos Detectados</div>
          </div>

          <div className="info-card">
            <div className="info-value">{Number(temperature).toFixed(1)}°C</div>
            <div className="info-label">Temperatura General</div>
          </div>
        </div>
      </div>
    </article>
  );
}
