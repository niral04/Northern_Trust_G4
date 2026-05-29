import { useState, useEffect, useCallback } from "react"
import Dashboard from "./components/Dashboard"

export default function App() {
  const [incidents, setIncidents] = useState([])
  const [stats, setStats]         = useState({
    total: 0, open: 0, escalated: 0,
    resolved: 0, critical: 0
  })
  const [selected, setSelected]   = useState(null)
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    let ws
    let reconnectTimer

    function connect() {
      ws = new WebSocket("ws://localhost:8000/ws")

      ws.onopen = () => {
        setConnected(true)
        console.log("WebSocket connected")
      }

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        if (data.type === "update") {
          setIncidents(data.incidents || [])
          setStats(data.stats || {})
        }
      }

      ws.onclose = () => {
        setConnected(false)
        reconnectTimer = setTimeout(connect, 3000)
      }

      ws.onerror = () => {
        ws.close()
      }
    }

    connect()

    return () => {
      clearTimeout(reconnectTimer)
      if (ws) ws.close()
    }
  }, [])

  const handleAction = useCallback(async (incidentId, action, body = {}) => {
    try {
      await fetch(
        `http://localhost:8000/api/incidents/${incidentId}/${action}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body)
        }
      )
    } catch (e) {
      console.error("Action failed:", e)
    }
  }, [])

  return (
    <Dashboard
      incidents={incidents}
      stats={stats}
      selected={selected}
      onSelect={setSelected}
      onAction={handleAction}
      connected={connected}
    />
  )
}