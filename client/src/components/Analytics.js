import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, LineChart, Line, CartesianGrid
} from "recharts"

export default function Analytics({ incidents, stats }) {

  // Incidents by service
  const byService = incidents.reduce((acc, inc) => {
    acc[inc.source] = (acc[inc.source] || 0) + 1
    return acc
  }, {})

  const serviceData = Object.entries(byService)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 8)

  // Incidents by severity
  const bySeverity = incidents.reduce((acc, inc) => {
    acc[inc.severity] = (acc[inc.severity] || 0) + 1
    return acc
  }, {})

  const severityData = Object.entries(bySeverity)
    .map(([name, count]) => ({ name: name.toUpperCase(), count }))

  // Incidents by type
  const infraCount = incidents.filter(
    i => i.alert_type === "infrastructure"
  ).length
  const appCount = incidents.filter(
    i => i.alert_type === "application"
  ).length

  // MTTR data
  const resolved = incidents.filter(
    i => i.status === "RESOLVED" && i.mttr_minutes != null
  )

  return (
    <div className="space-y-6">

      {/* Top Stats */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Total Incidents",   value: incidents.length,  color: "text-white" },
          { label: "Infrastructure",    value: infraCount,         color: "text-red-400" },
          { label: "Application",       value: appCount,           color: "text-yellow-400" },
          { label: "Avg MTTR (mins)",   value: stats.avg_mttr || "N/A", color: "text-blue-400" }
        ].map(item => (
          <div key={item.label}
               className="bg-gray-900 border border-gray-800
                          rounded-xl p-4 text-center">
            <div className={`text-3xl font-bold ${item.color}`}>
              {item.value}
            </div>
            <div className="text-gray-500 text-xs mt-1">
              {item.label}
            </div>
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-2 gap-6">

        {/* Incidents by Service */}
        <div className="bg-gray-900 border border-gray-800
                        rounded-xl p-4">
          <h3 className="text-gray-300 font-medium mb-4 text-sm">
            📊 Incidents by Service
          </h3>
          {serviceData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={serviceData}>
                <CartesianGrid strokeDasharray="3 3"
                               stroke="#374151" />
                <XAxis dataKey="name" stroke="#9CA3AF"
                       tick={{ fontSize: 10 }} />
                <YAxis stroke="#9CA3AF"
                       tick={{ fontSize: 10 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#1F2937",
                    border: "1px solid #374151",
                    borderRadius: "8px"
                  }}
                />
                <Bar dataKey="count" fill="#3B82F6"
                     radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-48 flex items-center
                            justify-center text-gray-600 text-sm">
              No data yet
            </div>
          )}
        </div>

        {/* Incidents by Severity */}
        <div className="bg-gray-900 border border-gray-800
                        rounded-xl p-4">
          <h3 className="text-gray-300 font-medium mb-4 text-sm">
            🔥 Incidents by Severity
          </h3>
          {severityData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={severityData}>
                <CartesianGrid strokeDasharray="3 3"
                               stroke="#374151" />
                <XAxis dataKey="name" stroke="#9CA3AF"
                       tick={{ fontSize: 10 }} />
                <YAxis stroke="#9CA3AF"
                       tick={{ fontSize: 10 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#1F2937",
                    border: "1px solid #374151",
                    borderRadius: "8px"
                  }}
                />
                <Bar dataKey="count" fill="#EF4444"
                     radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-48 flex items-center
                            justify-center text-gray-600 text-sm">
              No data yet
            </div>
          )}
        </div>
      </div>

      {/* MTTR Table */}
      {resolved.length > 0 && (
        <div className="bg-gray-900 border border-gray-800
                        rounded-xl p-4">
          <h3 className="text-gray-300 font-medium mb-4 text-sm">
            ⏱️ Resolution Times
          </h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-gray-500 text-left
                             border-b border-gray-800">
                <th className="pb-2">Incident</th>
                <th className="pb-2">Source</th>
                <th className="pb-2">Severity</th>
                <th className="pb-2">MTTR</th>
              </tr>
            </thead>
            <tbody>
              {resolved.map(inc => (
                <tr key={inc.incident_id}
                    className="border-b border-gray-800">
                  <td className="py-2 font-mono text-blue-400 text-xs">
                    {inc.incident_id}
                  </td>
                  <td className="py-2 text-gray-300">{inc.source}</td>
                  <td className="py-2 capitalize text-gray-400">
                    {inc.severity}
                  </td>
                  <td className="py-2 text-green-400 font-bold">
                    {inc.mttr_minutes} mins
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

    </div>
  )
}