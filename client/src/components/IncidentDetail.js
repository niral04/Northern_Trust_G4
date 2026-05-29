import { useState, useEffect } from "react"

export default function IncidentDetail({ incident, onClose, onAction }) {
  const [timeline,   setTimeline]   = useState([])
  const [postmortem, setPostmortem] = useState(null)
  const [tab,        setTab]        = useState("timeline")

  useEffect(() => {
    if (!incident) return

    // Fetch timeline
    fetch(`http://localhost:8000/api/incidents/${incident.incident_id}/timeline`)
      .then(r => r.json())
      .then(setTimeline)
      .catch(console.error)

    // Fetch postmortem if resolved
    if (incident.status === "RESOLVED") {
      fetch(`http://localhost:8000/api/incidents/${incident.incident_id}/postmortem`)
        .then(r => r.json())
        .then(setPostmortem)
        .catch(console.error)
    }
  }, [incident, incident.status])

  const eventColor = {
    CREATED:               "bg-blue-500",
    CLASSIFIED:            "bg-purple-500",
    NOTIFIED:              "bg-yellow-500",
    ACKNOWLEDGED:          "bg-blue-400",
    ESCALATED:             "bg-orange-500",
    RESOLVED:              "bg-green-500",
    POSTMORTEM_GENERATED:  "bg-teal-500",
    REMEDIATION_STARTED:   "bg-indigo-500",
    REMEDIATION_SUCCESS:   "bg-green-400",
    REMEDIATION_FAILED:    "bg-red-500"
  }

  const severityColor = {
    critical: "text-red-400",
    high:     "text-orange-400",
    medium:   "text-yellow-400",
    low:      "text-green-400"
  }

  return (
    <div className="bg-gray-900 border border-gray-800
                    rounded-xl overflow-hidden h-fit sticky top-6">

      {/* Header */}
      <div className="flex items-center justify-between
                      px-4 py-3 border-b border-gray-800 bg-gray-950">
        <span className="font-mono font-bold text-blue-400">
          {incident.incident_id}
        </span>
        <button
          onClick={onClose}
          className="text-gray-500 hover:text-white text-lg
                     transition-colors"
        >✕</button>
      </div>

      {/* Info Grid */}
      <div className="p-4 border-b border-gray-800">
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <p className="text-gray-500 text-xs mb-1">Source</p>
            <p className="font-medium">{incident.source}</p>
          </div>
          <div>
            <p className="text-gray-500 text-xs mb-1">Type</p>
            <p className="capitalize">{incident.alert_type}</p>
          </div>
          <div>
            <p className="text-gray-500 text-xs mb-1">Severity</p>
            <p className={`font-bold capitalize
                           ${severityColor[incident.severity]}`}>
              {incident.severity}
            </p>
          </div>
          <div>
            <p className="text-gray-500 text-xs mb-1">Status</p>
            <p className="font-semibold">{incident.status}</p>
          </div>
          <div className="col-span-2">
            <p className="text-gray-500 text-xs mb-1">Assignee</p>
            <p className="text-xs">{incident.assignee}</p>
          </div>
          {incident.mttr_minutes != null && (
            <div className="col-span-2">
              <p className="text-gray-500 text-xs mb-1">MTTR</p>
              <p className="text-green-400 font-bold">
                {incident.mttr_minutes} minutes
              </p>
            </div>
          )}
        </div>

        {/* Message */}
        <div className="mt-3">
          <p className="text-gray-500 text-xs mb-1">Message</p>
          <p className="text-xs bg-gray-800 p-2 rounded
                        text-gray-300 leading-relaxed">
            {incident.message}
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-800">
        {["timeline", "postmortem"].map(t => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`flex-1 py-2 text-xs font-medium
                        capitalize transition-colors
                        ${tab === t
                          ? "text-blue-400 border-b-2 border-blue-400 bg-gray-800"
                          : "text-gray-500 hover:text-gray-300"}`}
          >
            {t === "timeline" ? "📋 Timeline" : "📄 Post-Mortem"}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="p-4 max-h-64 overflow-y-auto">

        {/* Timeline Tab */}
        {tab === "timeline" && (
          <div className="space-y-3">
            {timeline.map((event, i) => (
              <div key={i} className="flex gap-3 items-start">
                <div className={`w-2 h-2 rounded-full mt-1.5
                                flex-shrink-0
                                ${eventColor[event.event_type]
                                  || "bg-gray-500"}`}
                />
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-gray-300 leading-relaxed">
                    {event.description}
                  </p>
                  <p className="text-gray-600 text-xs mt-0.5">
                    {event.created_at
                      ? new Date(event.created_at).toLocaleTimeString()
                      : ""}
                  </p>
                </div>
              </div>
            ))}
            {timeline.length === 0 && (
              <p className="text-gray-600 text-xs text-center py-4">
                No events yet
              </p>
            )}
          </div>
        )}

        {/* Post-Mortem Tab */}
        {tab === "postmortem" && (
          <div>
            {postmortem ? (
              <div className="space-y-3 text-xs">
                <div className="grid grid-cols-2 gap-2">
                  {[
                    ["Date",       postmortem.date],
                    ["Source",     postmortem.source],
                    ["Severity",   postmortem.severity],
                    ["Type",       postmortem.type],
                    ["MTTR",       `${postmortem.mttr_minutes} mins`],
                    ["SLA",        postmortem.sla_status]
                  ].map(([label, val]) => (
                    <div key={label}
                         className="bg-gray-800 p-2 rounded">
                      <p className="text-gray-500 text-xs">{label}</p>
                      <p className="text-gray-200 font-medium">{val}</p>
                    </div>
                  ))}
                </div>

                <div className="bg-gray-800 p-2 rounded">
                  <p className="text-gray-500 text-xs mb-1">Root Cause</p>
                  <p className="text-gray-300">{postmortem.root_cause}</p>
                </div>

                <div className="bg-gray-800 p-2 rounded">
                  <p className="text-gray-500 text-xs mb-1">Resolution</p>
                  <p className="text-gray-300">{postmortem.resolution}</p>
                </div>

                <div>
                  <p className="text-gray-500 text-xs mb-2">Timeline</p>
                  {postmortem.timeline?.map((e, i) => (
                    <div key={i}
                         className="flex gap-2 text-xs mb-1">
                      <span className="text-gray-500 flex-shrink-0">
                        {e.time}
                      </span>
                      <span className="text-gray-300">
                        {e.description}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <p className="text-gray-600 text-xs text-center py-4">
                {incident.status === "RESOLVED"
                  ? "Loading post-mortem..."
                  : "Post-mortem available after resolution"}
              </p>
            )}
          </div>
        )}
      </div>

      {/* Action Buttons */}
      {incident.status !== "RESOLVED" && (
        <div className="p-4 border-t border-gray-800
                        flex gap-2">
          {incident.status === "OPEN" && (
            <button
              onClick={() => onAction(
                incident.incident_id, "acknowledge",
                { engineer: "On-Call Engineer" }
              )}
              className="flex-1 py-2 bg-blue-700
                         hover:bg-blue-600 rounded
                         text-sm font-medium transition-colors"
            >
              👀 Acknowledge
            </button>
          )}
          <button
            onClick={() => onAction(incident.incident_id, "escalate")}
            className="flex-1 py-2 bg-orange-700
                       hover:bg-orange-600 rounded
                       text-sm font-medium transition-colors"
          >
            🔺 Escalate
          </button>
          <button
            onClick={() => onAction(
              incident.incident_id, "resolve",
              { notes: "Issue resolved" }
            )}
            className="flex-1 py-2 bg-green-700
                       hover:bg-green-600 rounded
                       text-sm font-medium transition-colors"
          >
            ✅ Resolve
          </button>
        </div>
      )}
    </div>
  )
}