import { ReactNode } from "react";

export interface PanelProps {
  title: string;
  children?: ReactNode;
  refrigerated?: boolean; // true = refrigerado (ok), false = sin refrigerar (alert)
  faults?: number;
  temperature?: number;
  icon?: ReactNode;
}
