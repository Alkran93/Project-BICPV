import { Settings, Power, BarChart3 } from "lucide-react";

type SidebarProps = {
  onComparisonClick?: () => void;
};

export default function Sidebar({ onComparisonClick }: SidebarProps) {
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
          <a href="#">Panel</a>
          <a href="#">Dashboard</a>
          <a href="#">Histórico</a>
          <a
            href="#"
            onClick={e => {
              e.preventDefault();
              onComparisonClick?.();
            }}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              color: "#ffffffff",
              fontWeight: "500",
            }}
          >
            <BarChart3 size={16} />
            Comparación Térmica
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
