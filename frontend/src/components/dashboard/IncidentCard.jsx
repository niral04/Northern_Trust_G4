export default function IncidentCard({ incident }) {
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-6 hover:border-orange-500 transition-all cursor-pointer">
      <div className="flex items-center gap-3 mb-4">
        <span className="text-sm text-zinc-400">
          INC-{incident.id}
        </span>

        <span className="rounded-md bg-red-500/20 px-2 py-1 text-xs text-red-300">
          {incident.severity}
        </span>

        <span className="rounded-md bg-yellow-500/20 px-2 py-1 text-xs text-yellow-300">
          {incident.status}
        </span>
      </div>

      <h2 className="text-2xl font-semibold text-white mb-2">
        {incident.title}
      </h2>

      <p className="text-zinc-400">
        Service: {incident.service}
      </p>
    </div>
  );
}
