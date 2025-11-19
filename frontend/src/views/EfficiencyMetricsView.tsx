import React, { useState, useEffect } from 'react';
import '../styles/EfficiencyMetricsView.css';

// ✅ INTERFACES ACTUALIZADAS según el JSON real del backend
interface EfficiencyData {
  facade_id: string;
  analysis_period: {
    start: string;
    end: string;
  };
  thermal_analysis: {
    refrigerada?: {
      facade_type: string;
      avg_panel_temperature: number;
      avg_ambient_temperature: number;
      temperature_difference: number;
      estimated_thermal_gain_w: number;
      panel_area_m2: number;
      measurements_count: number;
      interpretation: string;
    };
    no_refrigerada?: {
      facade_type: string;
      avg_panel_temperature: number;
      avg_ambient_temperature: number;
      temperature_difference: number;
      estimated_thermal_gain_w: number;
      panel_area_m2: number;
      measurements_count: number;
      interpretation: string;
    };
  };
  temperature_comparison: {
    refrigerated_facade?: {
      avg_temperature_celsius: number;
      min_temperature_celsius: number;
      max_temperature_celsius: number;
      stddev_celsius: number;
      temperature_range_celsius: number;
      sample_count: number;
    };
    non_refrigerated_facade?: {
      avg_temperature_celsius: number;
      min_temperature_celsius: number;
      max_temperature_celsius: number;
      stddev_celsius: number;
      temperature_range_celsius: number;
      sample_count: number;
    };
    note: string;
  };
  cop_metrics: {
    cop_available: boolean;
    cop_average?: number;
    efficiency_rating?: string;
    cooling_capacity_avg_w?: number;
    estimated_power_input_w?: number;
    water_temp_delta_avg_celsius?: number;
    water_flow_avg_lpm?: number;
    measurements_count?: number;
    note: string;
  };
}

const EfficiencyMetricsView: React.FC = () => {
  const [facadeId, setFacadeId] = useState<string>('2');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [efficiencyData, setEfficiencyData] = useState<EfficiencyData | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  // ✅ Cambiar a localhost si es necesario
  const API_BASE_URL = "http://136.115.180.156:8000";

  // Función para obtener el análisis completo de eficiencia
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
      const url = `${API_BASE_URL}/efficiency/${facadeId}${queryString ? `?${queryString}` : ''}`;
      
      console.log(`📊 Fetching efficiency data from: ${url}`);

      const response = await fetch(url);
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('No hay datos de eficiencia disponibles para esta fachada');
        }
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const data: EfficiencyData = await response.json();
      console.log('📊 Efficiency data received:', data);
      setEfficiencyData(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido al obtener los datos';
      setError(errorMessage);
      setEfficiencyData(null);
    } finally {
      setLoading(false);
    }
  };

  // ✅ Cargar datos cuando cambie facadeId
  useEffect(() => {
    if (facadeId) {
      fetchEfficiencyAnalysis();
    }
  }, [facadeId]);

  const handleSearch = () => {
    fetchEfficiencyAnalysis();
  };

  const formatTemperature = (temp: number): string => {
    return `${temp?.toFixed(1) || '0.0'}°C`;
  };

  const formatPower = (power: number): string => {
    return `${(power / 1000)?.toFixed(1) || '0.0'} kW`;
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
          {/* ✅ COMPARACIÓN DE TEMPERATURAS - ACTUALIZADO */}
          <div className="metric-card">
            <h3>Comparación de Temperaturas</h3>
            <div className="metric-comparison">
              {efficiencyData.temperature_comparison.refrigerated_facade && (
                <div className="metric-item">
                  <span className="metric-label">Fachada Refrigerada:</span>
                  <span className="metric-value refrigerated">
                    {formatTemperature(efficiencyData.temperature_comparison.refrigerated_facade.avg_temperature_celsius)}
                  </span>
                  <div className="metric-subtext">
                    Rango: {formatTemperature(efficiencyData.temperature_comparison.refrigerated_facade.min_temperature_celsius)} - {formatTemperature(efficiencyData.temperature_comparison.refrigerated_facade.max_temperature_celsius)}
                  </div>
                </div>
              )}
              {efficiencyData.temperature_comparison.non_refrigerated_facade && (
                <div className="metric-item">
                  <span className="metric-label">Fachada No Refrigerada:</span>
                  <span className="metric-value non-refrigerated">
                    {formatTemperature(efficiencyData.temperature_comparison.non_refrigerated_facade.avg_temperature_celsius)}
                  </span>
                  <div className="metric-subtext">
                    Rango: {formatTemperature(efficiencyData.temperature_comparison.non_refrigerated_facade.min_temperature_celsius)} - {formatTemperature(efficiencyData.temperature_comparison.non_refrigerated_facade.max_temperature_celsius)}
                  </div>
                </div>
              )}
            </div>
            {efficiencyData.temperature_comparison.note && (
              <div className="metric-note">
                {efficiencyData.temperature_comparison.note}
              </div>
            )}
          </div>

          {/* ✅ ANÁLISIS TÉRMICO - ACTUALIZADO */}
          <div className="metric-card">
            <h3>Análisis Térmico</h3>
            <div className="metric-comparison">
              {efficiencyData.thermal_analysis.refrigerada && (
                <div className="metric-item">
                  <span className="metric-label">Fachada Refrigerada:</span>
                  <div className="metric-details">
                    <div>Temp. Panel: {formatTemperature(efficiencyData.thermal_analysis.refrigerada.avg_panel_temperature)}</div>
                    <div>Temp. Ambiente: {formatTemperature(efficiencyData.thermal_analysis.refrigerada.avg_ambient_temperature)}</div>
                    <div>Diferencia: {formatTemperature(efficiencyData.thermal_analysis.refrigerada.temperature_difference)}</div>
                    <div>Ganancia Térmica: {formatPower(efficiencyData.thermal_analysis.refrigerada.estimated_thermal_gain_w)}</div>
                    <div className="interpretation">
                      {efficiencyData.thermal_analysis.refrigerada.interpretation}
                    </div>
                  </div>
                </div>
              )}
              {efficiencyData.thermal_analysis.no_refrigerada && (
                <div className="metric-item">
                  <span className="metric-label">Fachada No Refrigerada:</span>
                  <div className="metric-details">
                    <div>Temp. Panel: {formatTemperature(efficiencyData.thermal_analysis.no_refrigerada.avg_panel_temperature)}</div>
                    <div>Temp. Ambiente: {formatTemperature(efficiencyData.thermal_analysis.no_refrigerada.avg_ambient_temperature)}</div>
                    <div>Diferencia: {formatTemperature(efficiencyData.thermal_analysis.no_refrigerada.temperature_difference)}</div>
                    <div>Ganancia Térmica: {formatPower(efficiencyData.thermal_analysis.no_refrigerada.estimated_thermal_gain_w)}</div>
                    <div className="interpretation">
                      {efficiencyData.thermal_analysis.no_refrigerada.interpretation}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* ✅ COP METRICS - ACTUALIZADO */}
          <div className="metric-card">
            <h3>Coeficiente de Rendimiento (COP)</h3>
            <div className="metric-single">
              {efficiencyData.cop_metrics.cop_available ? (
                <>
                  <div className="metric-item">
                    <span className="metric-label">Valor COP:</span>
                    <span className="metric-value cop-value">
                      {efficiencyData.cop_metrics.cop_average?.toFixed(2) || 'N/A'}
                    </span>
                  </div>
                  <div className="metric-details">
                    <div>Capacidad de Enfriamiento: {formatPower(efficiencyData.cop_metrics.cooling_capacity_avg_w || 0)}</div>
                    <div>Consumo Eléctrico: {formatPower(efficiencyData.cop_metrics.estimated_power_input_w || 0)}</div>
                    <div>Delta Temp. Agua: {formatTemperature(efficiencyData.cop_metrics.water_temp_delta_avg_celsius || 0)}</div>
                    <div>Flujo Agua: {efficiencyData.cop_metrics.water_flow_avg_lpm?.toFixed(1) || '0.0'} LPM</div>
                    <div className="efficiency-rating">
                      Eficiencia: {efficiencyData.cop_metrics.efficiency_rating}
                    </div>
                  </div>
                </>
              ) : (
                <div className="metric-unavailable">
                  <span className="metric-label">Sistema no disponible:</span>
                  <span className="metric-value">{efficiencyData.cop_metrics.note || 'Datos de COP no disponibles'}</span>
                </div>
              )}
              {efficiencyData.cop_metrics.note && (
                <div className="metric-note">
                  {efficiencyData.cop_metrics.note}
                </div>
              )}
            </div>
          </div>

          {/* ✅ INFORMACIÓN GENERAL */}
          <div className="metric-card highlight">
            <h3>Información General</h3>
            <div className="metric-single">
              <div className="metric-item">
                <span className="metric-label">ID Fachada:</span>
                <span className="metric-value">{efficiencyData.facade_id}</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Período de Análisis:</span>
                <span className="metric-value">
                  {efficiencyData.analysis_period.start === "Not specified" ? 
                    "No especificado" : efficiencyData.analysis_period.start} - 
                  {efficiencyData.analysis_period.end === "Not specified" ? 
                    "No especificado" : efficiencyData.analysis_period.end}
                </span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Total Mediciones:</span>
                <span className="metric-value">
                  {(
                    (efficiencyData.thermal_analysis.refrigerada?.measurements_count || 0) +
                    (efficiencyData.thermal_analysis.no_refrigerada?.measurements_count || 0)
                  ).toLocaleString()}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {!efficiencyData && !loading && !error && (
        <div className="no-data">
          <p>Ingrese un ID de fachada para ver las métricas de eficiencia</p>
          <p><strong>Sugerencia:</strong> Prueba con el ID "1" (no refrigerada) o "2" (refrigerada)</p>
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