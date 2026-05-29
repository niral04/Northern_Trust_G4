export default function StatsBar({ stats }) {
  const cards = [
    {
      label: "Total",
      value: stats.total || 0,
      bg: "bg-gray-800",
      border: "border-gray-700",
      text: "text-white"
    },
    {
      label: "Open",
      value: stats.open || 0,
      bg: "bg-yellow-950",
      border: "border-yellow-800",
      text: "text-yellow-400"
    },
    {
      label: "Escalated",
      value: stats.escalated || 0,
      bg: "bg-orange-950",
      border: "border-orange-800",
      text: "text-orange-400"
    },
    {
      label: "Critical",
      value: stats.critical || 0,
      bg: "bg-red-950",
      border: "border-red-800",
      text: "text-red-400"
    },
    {
      label: "Resolved",
      value: stats.resolved || 0,
      bg: "bg-green-950",
      border: "border-green-800",
      text: "text-green-400"
    },
    {
      label: "Avg MTTR",
      value: stats.avg_mttr ? `${stats.avg_mttr}m` : "1",
      bg: "bg-blue-950",
      border: "border-blue-800",
      text: "text-blue-400"
    }
  ]

  return (
    <div className="grid grid-cols-6 gap-4">
      {cards.map(card => (
        <div
          key={card.label}
          className={`${card.bg} border ${card.border}
                      rounded-xl p-4 text-center`}
        >
          <div className={`text-3xl font-bold ${card.text}`}>
            {card.value}
          </div>
          <div className="text-gray-400 text-xs mt-1">
            {card.label}
          </div>
        </div>
      ))}
    </div>
  )
}