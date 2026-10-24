
import { useState } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import './App.css'

const sampleReadings = [
  { time_seconds: 0, coolant_temp_c: 88, rpm: 900, engine_load_pct: 20 },
  { time_seconds: 60, coolant_temp_c: 96, rpm: 1400, engine_load_pct: 35 },
  { time_seconds: 120, coolant_temp_c: 106, rpm: 1800, engine_load_pct: 55 },
  { time_seconds: 180, coolant_temp_c: 112, rpm: 2200, engine_load_pct: 55 },
]

type Reading = {
  time_seconds: number
  coolant_temp_c: number
  rpm: number
  engine_load_pct: number
}

type Diagnosis = {
  temperature_analysis: {
    starting_temperature_c: number
    highest_temperature_c: number
    temperature_rise_c: number
    temperature_rise_c_per_minute: number
    status: string
  }
  diagnostic_analysis: {
    hypotheses: {
      name: string
      score: number
      score_breakdown: {
        points: number
        rule: string
      }[]
      evidence: string[]
      next_test: string
      supporting_readings: Reading[]
    }[]
    sensor_anomaly: boolean
  }
  disclaimer: string
}

function App() {
  const [readings, setReadings] = useState<Reading[]>(sampleReadings)
  const [diagnosis, setDiagnosis] = useState<Diagnosis | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [fileName, setFileName] = useState('Sample vehicle trace')

  async function analyseTrace(data: Reading[]) {
    setLoading(true)
    setError('')
    setDiagnosis(null)

    try {
      const response = await fetch('http://127.0.0.1:8000/diagnose', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ readings: data }),
      })

      const result = await response.json()

      if (!response.ok) {
        throw new Error(
          typeof result.detail === 'string'
            ? result.detail
            : 'The API rejected this trace. Check its values and format.',
        )
      }

      setReadings(data)
      setDiagnosis(result)
    } catch (err) {
      setError(
        err instanceof Error
          ? `${err.message}. Make sure the TorqueTrace API is running.`
          : 'Could not connect to the TorqueTrace API.',
      )
    } finally {
      setLoading(false)
    }
  }

  function handleFileUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    if (!file) return

    setError('')
    setDiagnosis(null)

    const reader = new FileReader()

    reader.onload = () => {
      try {
        const text = String(reader.result)
        const lines = text.trim().split(/\r?\n/)
        const headers = lines[0].split(',').map((header) => header.trim())

        const required = [
          'time_seconds',
          'coolant_temp_c',
          'rpm',
          'engine_load_pct',
        ]

        const missing = required.filter((field) => !headers.includes(field))
        if (missing.length) {
          throw new Error(`CSV is missing columns: ${missing.join(', ')}`)
        }

        const data = lines.slice(1).filter(Boolean).map((line, index) => {
          const values = line.split(',')
          const record: Record<string, number> = {}

          headers.forEach((header, column) => {
            record[header] = Number(values[column])
          })

          const reading = {
            time_seconds: record.time_seconds,
            coolant_temp_c: record.coolant_temp_c,
            rpm: record.rpm,
            engine_load_pct: record.engine_load_pct,
          }

          if (Object.values(reading).some((value) => !Number.isFinite(value))) {
            throw new Error(`Invalid numeric value on CSV data row ${index + 2}.`)
          }

          return reading
        })

        if (data.length === 0) {
          throw new Error('The CSV contains no data rows.')
        }

        setFileName(file.name)
        void analyseTrace(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Could not read this CSV.')
      }
    }

    reader.onerror = () => setError('Could not read this file.')
    reader.readAsText(file)
    event.target.value = ''
  }

  const chartData = readings.map((reading) => ({
    ...reading,
    timeLabel: `${reading.time_seconds}s`,
  }))

  const temperature = diagnosis?.temperature_analysis
  const hypotheses = diagnosis?.diagnostic_analysis.hypotheses ?? []

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#">
          <span className="brand-icon">T</span>
          <span>
            <strong>TorqueTrace</strong>
            <small>VEHICLE INTELLIGENCE</small>
          </span>
        </a>

        <div className="nav-label">WORKSPACE</div>
        <div className="nav-item active">
          <span>◫</span> Diagnostic overview
        </div>
        <div className="nav-item">
          <span>⌁</span> Sensor traces
        </div>
        <div className="nav-item">
          <span>◎</span> Fault hypotheses
        </div>

        <div className="sidebar-bottom">
          <div className="status-dot" />
          <div>
            <strong>Diagnostic engine</strong>
            <small>Connects to local API</small>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb">Workspace / <strong>Overview</strong></div>
          <div className="live-indicator"><span /> LOCAL ENVIRONMENT</div>
        </header>

        <section className="page-heading">
          <div>
            <p className="eyebrow">VEHICLE DIAGNOSTICS / 01</p>
            <h1>Diagnostic overview</h1>
            <p className="subtitle">
              Turn raw sensor readings into evidence-led investigations.
            </p>
          </div>

          <label className="upload-button">
            <span>↑</span> Upload CSV
            <input
              type="file"
              accept=".csv,text/csv"
              onChange={handleFileUpload}
              hidden
            />
          </label>
        </section>

        <section className="trace-banner">
          <div className="trace-symbol">⌁</div>
          <div className="trace-info">
            <span className="eyebrow">CURRENT TRACE</span>
            <strong>{fileName}</strong>
            <small>{readings.length} sensor readings · Coolant temperature analysis</small>
          </div>
          <button
            className="analyse-button"
            disabled={loading}
            onClick={() => void analyseTrace(readings)}
          >
            {loading ? 'Analysing...' : 'Run analysis ↗'}
          </button>
        </section>

        {error && <div className="error-banner">{error}</div>}

        <section className="metric-grid">
          <article className="metric-card">
            <span className="metric-label">PEAK COOLANT TEMP.</span>
            <strong className="metric-value">
              {temperature ? `${temperature.highest_temperature_c}°C` : '––'}
            </strong>
            <span className="metric-note">Highest recorded reading</span>
          </article>
          <article className="metric-card">
            <span className="metric-label">TEMPERATURE RISE</span>
            <strong className="metric-value">
              {temperature ? `+${temperature.temperature_rise_c}°C` : '––'}
            </strong>
            <span className="metric-note">From initial reading to peak</span>
          </article>
          <article className="metric-card">
            <span className="metric-label">RISE RATE</span>
            <strong className="metric-value">
              {temperature ? `${temperature.temperature_rise_c_per_minute}°` : '––'}
              {temperature && <small> C/min</small>}
            </strong>
            <span className="metric-note">Average rise per minute</span>
          </article>
          <article className="metric-card">
            <span className="metric-label">SENSOR ANOMALY</span>
            <strong className="metric-value anomaly-value">
              {diagnosis
                ? diagnosis.diagnostic_analysis.sensor_anomaly ? 'Detected' : 'None'
                : '––'}
            </strong>
            <span className="metric-note">Abrupt temperature spike check</span>
          </article>
        </section>

        <section className="content-grid">
          <article className="panel chart-panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">TELEMETRY</p>
                <h2>Coolant temperature</h2>
              </div>
              <span className="unit-tag">°C</span>
            </div>

            <div className="chart-container">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 12, right: 12, left: -18, bottom: 4 }}>
                  <CartesianGrid stroke="#26303d" strokeDasharray="3 5" vertical={false} />
                  <XAxis
                    dataKey="timeLabel"
                    stroke="#8994a5"
                    tickLine={false}
                    axisLine={false}
                    tick={{ fontSize: 11 }}
                  />
                  <YAxis
                    domain={['auto', 'auto']}
                    stroke="#8994a5"
                    tickLine={false}
                    axisLine={false}
                    tick={{ fontSize: 11 }}
                  />
                  <Tooltip
                    contentStyle={{
                      background: '#111923',
                      border: '1px solid #344253',
                      borderRadius: 8,
                      color: '#f2f5f9',
                    }}
                    formatter={(value) => [`${value}°C`, 'Coolant temperature']}
                    labelFormatter={(label) => `Time: ${label}`}
                  />
                  <Line
                    type="monotone"
                    dataKey="coolant_temp_c"
                    stroke="#42e8b4"
                    strokeWidth={2.5}
                    dot={{ r: 4, fill: '#42e8b4', stroke: '#101820', strokeWidth: 2 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="chart-legend"><span /> Coolant temperature</div>
          </article>

          <article className="panel health-panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">SCREENING RESULT</p>
                <h2>Temperature status</h2>
              </div>
              <span className="health-icon">⌁</span>
            </div>

            <div className="health-result">
              <div className="health-ring">
                <span>{temperature ? `${temperature.highest_temperature_c}°` : '––'}</span>
              </div>
              <strong className="health-status">
                {temperature?.status ?? 'Awaiting analysis'}
              </strong>
              <p>
                {temperature
                  ? 'The highest recorded coolant temperature is shown above.'
                  : 'Run the analysis to evaluate this trace.'}
              </p>
            </div>

            <div className="health-footnote">
              <span className="status-dot" />
              <span>Rule-based preliminary screening</span>
            </div>
          </article>
        </section>

        <section className="panel hypotheses-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">DECISION SUPPORT</p>
              <h2>Ranked fault hypotheses</h2>
            </div>
            <span className="count-tag">{hypotheses.length} findings</span>
          </div>

          {!diagnosis && (
            <div className="empty-state">
              <div className="empty-icon">⌕</div>
              <strong>No analysis results yet</strong>
              <p>Run the sample trace or upload a CSV to see evidence and suggested next tests.</p>
            </div>
          )}

          {hypotheses.map((hypothesis, index) => (
            <div className="hypothesis-row" key={hypothesis.name}>
              <div className="rank-number">{String(index + 1).padStart(2, '0')}</div>
              <div className="hypothesis-main">
                
                <strong>{hypothesis.name}</strong>
                <span>{hypothesis.evidence.join(' ')}</span>

                <div className="score-breakdown">
                  <strong>Why this score?</strong>
                  {hypothesis.score_breakdown.map((item, itemIndex) => (
                    <div key={`${item.rule}-${itemIndex}`}>
                      +{item.points} · {item.rule}
                    </div>
                  ))}
                </div>

                {hypothesis.supporting_readings.length > 0 && (
                  <div className="supporting-readings">
                    <strong>Supporting readings</strong>
                    <div className="evidence-table-wrapper">
                      <table className="evidence-table">
                        <thead>
                          <tr>
                            <th>Time (s)</th>
                            <th>Coolant (°C)</th>
                            <th>RPM</th>
                            <th>Load (%)</th>
                          </tr>
                        </thead>
                        <tbody>
                          {hypothesis.supporting_readings.map((reading) => (
                            <tr key={reading.time_seconds}>
                              <td>{reading.time_seconds}</td>
                              <td>{reading.coolant_temp_c}</td>
                              <td>{reading.rpm}</td>
                              <td>{reading.engine_load_pct}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                <div className="next-test">
                  <span>↳ NEXT TEST</span> {hypothesis.next_test}
                </div>

              </div>
              <div className="score-block">
                <strong>{hypothesis.score}</strong>
                <span>priority score</span>
              </div>
            </div>
          ))}
        </section>

        <footer className="disclaimer">
          <span>ⓘ</span>
          {diagnosis?.disclaimer ??
            'Preliminary decision support only. Diagnostic hypotheses are not confirmed faults.'}
          <span className="footer-version">TORQUETRACE / 0.1.0</span>
        </footer>
      </main>
    </div>
  )
}

export default App
