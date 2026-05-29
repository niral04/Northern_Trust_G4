import StatsBar        from "./StatsBar"
import IncidentTable   from "./IncidentTable"
import IncidentDetail  from "./IncidentDetail"
import Analytics       from "./Analytics"
import { useState }    from "react"

export default function Dashboard({
  incidents, stats, selected, onSelect, onAction, connected
}) {
  const [showAnalytics, setShowAnalytics] = useState(false)

  return (
    <div className="min-h-screen bg-gray-950 text-white">

      {/* ── HEADER ─────────────────────────────── */}
      <div className="bg-gray-900 border-b border-gray-800 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🚨</span>
            <div>
              <h1 className="text-xl font-bold text-white">
                Incident Management System
              </h1>
              <p className="text-gray-500 text-xs">
                Real-time DevOps Incident Response Platform
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={() => setShowAnalytics(!showAnalytics)}
              className="px-4 py-2 bg-gray-800 hover:bg-gray-700
                         rounded-lg text-sm text-gray-300"
            >
              {showAnalytics ? "📋 Incidents" : "📊 Analytics"}
            </button>
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${
                connected
                  ? "bg-green-400 animate-pulse"
                  : "bg-red-400"
              }`}/>
              <span className={`text-sm font-medium ${
                connected ? "text-green-400" : "text-red-400"
              }`}>
                {connected ? "LIVE" : "RECONNECTING..."}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="p-6">

        {/* ── STATS ──────────────────────────────── */}
        <StatsBar stats={stats} />

        {/* ── MAIN CONTENT ───────────────────────── */}
        {showAnalytics ? (
          <div className="mt-6">
            <Analytics incidents={incidents} stats={stats} />
          </div>
        ) : (
          <div className="flex gap-6 mt-6">

            {/* Incident Table */}
            <div className="flex-1 min-w-0">
              <IncidentTable
                incidents={incidents}
                onSelect={onSelect}
                onAction={onAction}
                selected={selected}
              />
            </div>

            {/* Detail Panel */}
            {selected && (
              <div className="w-96 flex-shrink-0">
                <IncidentDetail
                  incident={selected}
                  onClose={() => onSelect(null)}
                  onAction={onAction}
                />
              </div>
            )}

          </div>
        )}
      </div>
    </div>
  )
}