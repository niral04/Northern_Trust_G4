import { useEffect, useRef } from "react";
import { useToast } from "@/context/ToastContext";

const WS_URL = import.meta.env.VITE_WS_URL
  ?? `${(import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000").replace(/^http/, "ws")}/ws`;

const TOAST_MESSAGES = {
  incident_created: (payload) => ({
    message:
      payload.severity === "Critical" || payload.severity === "critical"
        ? "🚨 Critical Incident Created"
        : `Incident ${payload.incident_id} created`,
    tone: "danger",
  }),
  incident_escalated: () => ({
    message: "⚠ Incident Auto Escalated",
    tone: "warning",
  }),
  incident_resolved: () => ({
    message: "✅ Incident Resolved",
    tone: "success",
  }),
  incident_acknowledged: (payload) => ({
    message: `${payload.incident_id} acknowledged`,
    tone: "info",
  }),
  invalid_transition_attempt: (payload) => ({
    message: `Invalid transition: ${payload.current_state} → ${payload.target_state}`,
    tone: "warning",
  }),
};

export function useIncidentWebSocket({
  enabled = true,
  onDashboardUpdate,
  onIncidentPatch,
  onTimelineEvent,
}) {
  const { pushToast } = useToast();
  const callbacksRef = useRef({
    onDashboardUpdate,
    onIncidentPatch,
    onTimelineEvent,
  });

  useEffect(() => {
    callbacksRef.current = {
      onDashboardUpdate,
      onIncidentPatch,
      onTimelineEvent,
    };
  }, [onDashboardUpdate, onIncidentPatch, onTimelineEvent]);

  useEffect(() => {
    if (!enabled || !import.meta.env.VITE_API_BASE_URL) {
      return undefined;
    }

    const socket = new WebSocket(WS_URL);

    socket.onmessage = (message) => {
      let payload;
      try {
        payload = JSON.parse(message.data);
      } catch {
        return;
      }

      const eventName = payload.event ?? payload.type;

      if (eventName && TOAST_MESSAGES[eventName]) {
        const toast = TOAST_MESSAGES[eventName](payload);
        pushToast(toast.message, toast.tone);
      }

      if (eventName === "countdown_updated") {
        callbacksRef.current.onIncidentPatch?.(payload.incident_id, {
          remaining_seconds: payload.remaining_seconds,
          escalation_level: payload.escalation_level,
        });
        return;
      }

      if (
        eventName === "dashboard_stats_updated"
        || eventName === "update"
        || payload.incidents
      ) {
        callbacksRef.current.onDashboardUpdate?.(payload);
        return;
      }

      if (eventName === "timeline_updated") {
        callbacksRef.current.onTimelineEvent?.(payload);
        return;
      }

      if (
        [
          "incident_created",
          "incident_acknowledged",
          "incident_escalated",
          "incident_resolved",
        ].includes(eventName)
      ) {
        callbacksRef.current.onIncidentPatch?.(payload.incident_id, payload);
      }
    };

    socket.onerror = () => {
      console.warn("WebSocket connection error");
    };

    return () => socket.close();
  }, [enabled, pushToast]);
}
