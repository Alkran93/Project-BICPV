// contexts/RealtimeDataContext.tsx
import React, { createContext, useContext, useEffect, useState } from 'react';

interface RealtimeData {
  [facadeId: string]: {
    [sensorName: string]: {
      value: number;
      ts: string;
      device_id: string;
      facade_type: string;
    };
  };
}

interface RealtimeContextType {
  data: RealtimeData;
  loading: boolean;
  error: string | null;
  lastUpdate: string;
  refreshData: () => void;
}

const RealtimeDataContext = createContext<RealtimeContextType | undefined>(undefined);

export const RealtimeDataProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [data, setData] = useState<RealtimeData>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<string>('');

  const fetchAllRealtimeData = async () => {
    setLoading(true);
    setError(null);

    try {
      const url = `http://136.115.180.156:8000/realtime/facades`;
      console.log(`🚀 Fetching ALL realtime data from: ${url}`);

      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const responseData = await response.json();
      console.log(`✅ ALL Realtime data:`, responseData);

      // La estructura es: { data: { "1": { unknown: {...} }, "2": { unknown: {...} } } }
      const allFacadesData = responseData.data || {};
      
      // Extraer solo la parte "unknown" de cada fachada
      const processedData: RealtimeData = {};
      Object.entries(allFacadesData).forEach(([facadeId, facadeData]: [string, any]) => {
        processedData[facadeId] = facadeData.unknown || {};
      });

      setData(processedData);
      setLastUpdate(new Date().toLocaleString());
      console.log(`✅ Processed realtime data for facades:`, Object.keys(processedData));

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      console.error(`💥 Error fetching ALL realtime data:`, err);
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllRealtimeData();
    
    // Auto-refresh cada 5 segundos
    const interval = setInterval(fetchAllRealtimeData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <RealtimeDataContext.Provider value={{
      data,
      loading,
      error,
      lastUpdate,
      refreshData: fetchAllRealtimeData
    }}>
      {children}
    </RealtimeDataContext.Provider>
  );
};

export const useRealtimeData = () => {
  const context = useContext(RealtimeDataContext);
  if (context === undefined) {
    throw new Error('useRealtimeData must be used within a RealtimeDataProvider');
  }
  return context;
};