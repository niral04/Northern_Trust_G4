export default function IncidentTable({
  incidents, onSelect, onAction, selected
}) {

  const severityStyle = {
    critical: "text-red-400 bg-red-950 border border-red-800",
    high:     "text-orange-400 bg-orange-950 border border-orange-800",
    medium:   "text-yellow-400 bg-yellow-950 border border-yellow-800",
    low:      "text-green-400 bg-green-950 border border-green-800"
  }

  const statusStyle = {
    OPEN:         "text-yellow-400",
    ACKNOWLEDGED: "text-blue-400",
    ESCALATED:    "text-orange-400 font-bold",
    RESOLVED:     "text-green-400"
  }

  const statusEmoji = {
    OPEN:         "🟡",
    ACKNOWLEDGED: "🔵",
    ESCALATED:    "🔺",
    RESOLVED:     "✅"
  }

  const severityEmoji = {
    critical: "🔴",
    high:     "🟠",
    medium:   "🟡",
    low:      "🟢"
  }

  const typeEmoji = {
    infrastructure: "🖥️",
    application:    "📱"
  }

  const active   = incidents.filter(i => i.status !== "RESOLVED")
  const resolved = incidents.filter(i => i.status === "RESOLVED")
  const sorted   = [...active, ...resolved]

  return (
    <div className="bg-gray-900 rounded-xl overflow-hidden
                    border border-gray-800">

      {/* Table Header */}
      <div className="px-4 py-3 border-b border-gray-800
                      flex items-center justify-between">
        <h2 className="font-semibold text-gray-200">
          Active Incidents
        </h2>
        <span className="text-gray-500 text-sm">
          {active.length} active / {resolved.length} resolved
        </span>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-gray-500 text-left
                           border-b border-gray-800 bg-gray-950">
              <th className="px-4 py-3">ID</th>
              <th className="px-4 py-3">Type</th>
              <th className="px-4 py-3">Source</th>
              <th className="px-4 py-3">Severity</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Assignee</th>
              <th className="px-4 py-3">Time</th>
              <th className="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map(inc => (
              <tr
                key={inc.incident_id}
                onClick={() => onSelect(inc)}
                className={`
                  border-b border-gray-800 cursor-pointer
                  transition-colors duration-150
                  ${selected?.incident_id === inc.incident_id
                    ? "bg-gray-800"
                    : "hover:bg-gray-800/50"}
                  ${inc.status === "ESCALATED"
                    ? "border-l-2 border-l-orange-500"
                    : inc.severity === "critical" && inc.status !== "RESOLVED"
                    ? "border-l-2 border-l-red-500"
                    : ""}
                `}
              >
                {/* ID */}
                <td className="px-4 py-3 font-mono text-blue-400
                               text-xs font-bold">
                  {inc.incident_id}
                </td>

                {/* Type */}
                <td className="px-4 py-3 text-gray-400 text-xs capitalize">
                  {typeEmoji[inc.alert_type]} {inc.alert_type}
                </td>

                {/* Source */}
                <td className="px-4 py-3 text-gray-200 font-medium">
                  {inc.source}
                </td>

                {/* Severity */}
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded text-xs
                                   font-bold ${severityStyle[inc.severity]}`}>
                    {severityEmoji[inc.severity]} {inc.severity?.toUpperCase()}
                  </span>
                </td>

                {/* Status */}
                <td className={`px-4 py-3 font-semibold text-xs
                                ${statusStyle[inc.status]}`}>
                  {statusEmoji[inc.status]} {inc.status}
                </td>

                {/* Assignee */}
                <td className="px-4 py-3 text-gray-400 text-xs max-w-32 truncate">
                  {inc.assignee}
                </td>

                {/* Time */}
                <td className="px-4 py-3 text-gray-500 text-xs">
                  {inc.created_at
                    ? new Date(inc.created_at).toLocaleTimeString()
                    : "—"}
                </td>

                {/* Actions */}
                <td className="px-4 py-3">
                  <div className="flex gap-1"
                       onClick={e => e.stopPropagation()}>

                    {inc.status === "OPEN" && (
                      <button
                        onClick={() => onAction(
                          inc.incident_id, "acknowledge",
                          { engineer: "On-Call Engineer" }
                        )}
                        className="px-2 py-1 bg-blue-700
                                   hover:bg-blue-600 rounded
                                   text-xs font-medium transition-colors"
                        title="Acknowledge"
                      >ACK</button>
                    )}

                    {inc.status !== "RESOLVED" && (
                      <>
                        <button
                          onClick={() => onAction(
                            inc.incident_id, "escalate"
                          )}
                          className="px-2 py-1 bg-orange-700
                                     hover:bg-orange-600 rounded
                                     text-xs font-medium transition-colors"
                          title="Escalate"
                        >ESC</button>

                        <button
                          onClick={() => onAction(
                            inc.incident_id, "resolve",
                            { notes: "Issue resolved" }
                          )}
                          className="px-2 py-1 bg-green-700
                                     hover:bg-green-600 rounded
                                     text-xs font-medium transition-colors"
                          title="Resolve"
                        >RES</button>
                      </>
                    )}

                    {inc.status === "RESOLVED" && (
                      <span className="text-green-500 text-xs">
                        ✅ Done
                      </span>
                    )}
                  </div>
                </td>
              </tr>
            ))}

            {incidents.length === 0 && (
              <tr>
                <td colSpan="8"
                    className="px-4 py-16 text-center text-gray-600">
                  <div className="text-4xl mb-2">🟢</div>
                  <div className="text-sm">No incidents</div>
                  <div className="text-xs mt-1">
                    Run the simulator to generate alerts
                  </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}