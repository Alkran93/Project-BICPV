import {
  Settings,
  Power,
  BarChart3,
  Bell,
  FileDown,
  Thermometer,
  Activity,
  AlertTriangle,
} from "lucide-react";

type SidebarProps = {
  onComparisonClick?: () => void;
  onAlertsClick?: () => void;
  onRealtimeAlertsClick?: () => void;
  onCSVExportClick?: () => void;
  onTempComparisonClick?: () => void;
  onRefrigerantCycleClick?: () => void;
  onWaterTempsClick?: () => void;
};

export default function Sidebar({
  onComparisonClick,
  onAlertsClick,
  onRealtimeAlertsClick,
  onCSVExportClick,
  onTempComparisonClick,
  onRefrigerantCycleClick,
  onWaterTempsClick,
}: SidebarProps) {
  return (
    <aside className="sidebar" aria-label="Sidebar navigation">
      <div>
        <div className="brand">
          <div className="brand-mark">⚡</div>
          <div>
            <div className="brand-title">BICPV</div>
            <div className="subtle" style={{ fontSize: 12 }}>
              Monitor de estado
            </div>
          </div>
        </div>

        <nav className="nav" aria-label="Main">
          {/* Panel principal */}
          <a href="#">Inicio</a>

          {/* === SECCIÓN ALERTAS === */}
          <a
            href="#"
            onClick={(e) => {
              e.preventDefault();
              onAlertsClick?.();
            }}
          >
            <AlertTriangle size={16} /> Historial de Alertas
          </a>

          <a
            href="#"
            onClick={(e) => {
              e.preventDefault();
              onRealtimeAlertsClick?.();
            }}
          >
            <Bell size={16} /> Alertas Automáticas
          </a>

          {/* === SECCIÓN ANÁLISIS TÉRMICO === */}
          <a
            href="#"
            onClick={(e) => {
              e.preventDefault();
              onTempComparisonClick?.();
            }}
          >
            <Thermometer size={16} /> Comparativa de Temperaturas
          </a>

          <a
            href="#"
            onClick={(e) => {
              e.preventDefault();
              onRefrigerantCycleClick?.();
            }}
          >
            <Activity size={16} /> Ciclo de Refrigerante
          </a>

          <a
            href="#"
            onClick={(e) => {
              e.preventDefault();
              onWaterTempsClick?.();
            }}
          >
            <Thermometer size={16} /> Agua In/Out Intercambiador
          </a>
          
          <a
            href="#"
            onClick={(e) => {
              e.preventDefault();
              onComparisonClick?.();
            }}
          >
            <BarChart3 size={16} /> Comparación Térmica
          </a>

          {/* === EXPORTAR === */}
          <a
            href="#"
            onClick={(e) => {
              e.preventDefault();
              onCSVExportClick?.();
            }}
          >
            <FileDown size={16} /> Exportar CSV
          </a>
        </nav>
      </div>

      <div className="sidebar-foot">
        <div className="icon-btn" title="Ajustes">
          <Settings size={20} strokeWidth={2} />
        </div>
        <div className="icon-btn" title="Cerrar sesión">
          <Power size={20} strokeWidth={2} />
        </div>
      </div>
    </aside>
  );
}
