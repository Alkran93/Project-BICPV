// EfficiencyMetricsView.tsx
import React, { useState, useEffect } from 'react';
import '../styles/EfficiencyMetricsView.css';

interface EfficiencyData {
  temperatureComparison?: {
    refrigerated: number;
    nonRefrigerated: number;
  };
  thermalGain?: {
    refrigerated: number;
    nonRefrigerated: number;
  };
  cop?: {
    value: number;
    coolingCapacity: number;
    powerInput: number;
  };
  temperatureReduction?: {
    reduction: number;
    efficiencyImprovement: number;
  };
  efficiencyImprovement?: number;
  pvPerformanceImpact?: number;
}

const EfficiencyMetricsView: React.FC = () => {
  const [facadeId, setFacadeId] = useState<string>('2'); // ✅ Valor por defecto
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [efficiencyData, setEfficiencyData] = useState<EfficiencyData | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  // ✅ CONSTANTE CON LA URL CORRECTA
  const API_BASE_URL = "http://localhost:8000";

  // Función para obtener el análisis completo de eficiencia usando endpoints reales
  const fetchEfficiencyAnalysis = async () => {
    if (!facadeId) {
      setError('Por favor, ingrese un ID de fachada');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const params = new URLSearchParams();
      if (startDate) params.append('start', startDate);
      if (endDate) params.append('end', endDate);

      const queryString = params.toString();

      // Obtener promedios de ambas fachadas para comparación
      const refUrl = `${API_BASE_URL}/facades/${facadeId}/average?facade_type=refrigerada${queryString ? `&${queryString}` : ''}`;
      const nonRefUrl = `${API_BASE_URL}/facades/${facadeId}/average?facade_type=no_refrigerada${queryString ? `&${queryString}` : ''}`;
      
      console.log(`📊 Fetching efficiency data from:`, refUrl, nonRefUrl);

      const [refResponse, nonRefResponse] = await Promise.all([
        fetch(refUrl),
        fetch(nonRefUrl)
      ]);
      
      if (!refResponse.ok && !nonRefResponse.ok) {
        throw new Error('No hay datos disponibles para ninguna fachada');
      }

      const refData = refResponse.ok ? await refResponse.json() : null;
      const nonRefData = nonRefResponse.ok ? await nonRefResponse.json() : null;
      
      console.log('📊 Efficiency data received:', { refData, nonRefData });

      // Calcular métricas basadas en los promedios
      const refAvg = refData?.averages?.[0] || {};
      const nonRefAvg = nonRefData?.averages?.[0] || {};

      const refTemp = refAvg.avg_temperature || refAvg.avg_value || 0;
      const nonRefTemp = nonRefAvg.avg_temperature || nonRefAvg.avg_value || 0;

      setEfficiencyData({
        temperatureComparison: {
          refrigerated: refTemp,
          nonRefrigerated: nonRefTemp
        },
        temperatureReduction: {
          reduction: nonRefTemp - refTemp,
          efficiencyImprovement: ((nonRefTemp - refTemp) / nonRefTemp) * 100
        },
        efficiencyImprovement: ((nonRefTemp - refTemp) / nonRefTemp) * 100
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido al obtener los datos';
      setError(errorMessage);
      setEfficiencyData(null);
    } finally {
      setLoading(false);
    }
  };

  // Cargar datos cuando cambie facadeId y actualizar cada 10 segundos
  useEffect(() => {
    if (facadeId) {
      fetchEfficiencyAnalysis();
      
      // Actualización automática cada 10 segundos
      const interval = setInterval(() => {
        fetchEfficiencyAnalysis();
      }, 10000);
      
      return () => clearInterval(interval);
    }
  }, [facadeId, startDate, endDate]);

  const handleSearch = () => {
    fetchEfficiencyAnalysis();
  };

  const formatTemperature = (temp: number): string => {
    return `${temp?.toFixed(1) || '0.0'}°C`;
  };

  const formatPercentage = (value: number): string => {
    return `${value?.toFixed(1) || '0.0'}%`;
  };

  return (
    <div className="efficiency-metrics-container">
      <h1>Métricas de Eficiencia Energética</h1>
      
      {/* Filtros */}
      <div className="filters-section">
        <div className="filter-group">
          <label htmlFor="facadeId">ID de Fachada:</label>
          <input
            id="facadeId"
            type="text"
            value={facadeId}
            onChange={(e) => setFacadeId(e.target.value)}
            placeholder="Ingrese el ID de la fachada"
          />
        </div>
        
        <div className="filter-group">
          <label htmlFor="startDate">Fecha Inicio:</label>
          <input
            id="startDate"
            type="datetime-local"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />
        </div>
        
        <div className="filter-group">
          <label htmlFor="endDate">Fecha Fin:</label>
          <input
            id="endDate"
            type="datetime-local"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
        </div>
        
        <button 
          onClick={handleSearch}
          disabled={loading || !facadeId}
          className="search-button"
        >
          {loading ? 'Cargando...' : 'Buscar Métricas'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* Métricas de Eficiencia */}
      {efficiencyData && (
        <div className="metrics-grid">
          {/* Comparación de Temperaturas */}
          {efficiencyData.temperatureComparison && (
            <div className="metric-card">
              <h3>Comparación de Temperaturas</h3>
              <div className="metric-comparison">
                <div className="metric-item">
                  <span className="metric-label">Con Refrigeración:</span>
                  <span className="metric-value refrigerated">
                    {formatTemperature(efficiencyData.temperatureComparison.refrigerated)}
                  </span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Sin Refrigeración:</span>
                  <span className="metric-value non-refrigerated">
                    {formatTemperature(efficiencyData.temperatureComparison.nonRefrigerated)}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Ganancia Térmica */}
          {efficiencyData.thermalGain && (
            <div className="metric-card">
              <h3>Ganancia Térmica</h3>
              <div className="metric-comparison">
                <div className="metric-item">
                  <span className="metric-label">Con Refrigeración:</span>
                  <span className="metric-value">
                    {formatTemperature(efficiencyData.thermalGain.refrigerated)}
                  </span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Sin Refrigeración:</span>
                  <span className="metric-value">
                    {formatTemperature(efficiencyData.thermalGain.nonRefrigerated)}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* COP (Coefficient of Performance) */}
          {efficiencyData.cop && (
            <div className="metric-card">
              <h3>Coeficiente de Rendimiento (COP)</h3>
              <div className="metric-single">
                <div className="metric-item">
                  <span className="metric-label">Valor COP:</span>
                  <span className="metric-value cop-value">
                    {efficiencyData.cop.value?.toFixed(2) || '0.00'}
                  </span>
                </div>
                <div className="metric-details">
                  <div>Capacidad de Enfriamiento: {efficiencyData.cop.coolingCapacity?.toFixed(1) || '0.0'} kW</div>
                  <div>Consumo Eléctrico: {efficiencyData.cop.powerInput?.toFixed(1) || '0.0'} kW</div>
                </div>
              </div>
            </div>
          )}

          {/* Reducción de Temperatura */}
          {efficiencyData.temperatureReduction && (
            <div className="metric-card">
              <h3>Reducción de Temperatura</h3>
              <div className="metric-single">
                <div className="metric-item">
                  <span className="metric-label">Reducción Absoluta:</span>
                  <span className="metric-value reduction">
                    {formatTemperature(efficiencyData.temperatureReduction.reduction)}
                  </span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Mejora en Eficiencia PV:</span>
                  <span className="metric-value improvement">
                    {formatPercentage(efficiencyData.temperatureReduction.efficiencyImprovement)}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Mejora General de Eficiencia */}
          {efficiencyData.efficiencyImprovement && (
            <div className="metric-card highlight">
              <h3>Mejora General de Eficiencia</h3>
              <div className="metric-single">
                <div className="metric-item">
                  <span className="metric-label">Incremento en Eficiencia:</span>
                  <span className="metric-value highlight-value">
                    {formatPercentage(efficiencyData.efficiencyImprovement)}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Impacto en Rendimiento PV */}
          {efficiencyData.pvPerformanceImpact && (
            <div className="metric-card">
              <h3>Impacto en Rendimiento Fotovoltaico</h3>
              <div className="metric-single">
                <div className="metric-item">
                  <span className="metric-label">Impacto Estimado:</span>
                  <span className="metric-value pv-impact">
                    {formatPercentage(efficiencyData.pvPerformanceImpact)}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {!efficiencyData && !loading && !error && (
        <div className="no-data">
          <p>Ingrese un ID de fachada para ver las métricas de eficiencia</p>
          <p><strong>Sugerencia:</strong> Prueba con el ID "2" para fachada refrigerada</p>
        </div>
      )}

      {/* Loading state */}
      {loading && (
        <div className="loading-state">
          <p>Cargando métricas de eficiencia...</p>
        </div>
      )}
    </div>
  );
};

export default EfficiencyMetricsView;