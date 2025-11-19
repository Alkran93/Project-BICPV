import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./styles/index.css";
import App from "./App.tsx";
import { RealtimeDataProvider } from "../contexts/RealtimeDataContext.tsx";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <RealtimeDataProvider>
      <App />
    </RealtimeDataProvider>
  </StrictMode>
);
