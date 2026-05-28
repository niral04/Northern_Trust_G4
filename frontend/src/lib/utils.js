import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export function formatCompactNumber(value) {
  return new Intl.NumberFormat("en", {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value);
}

export function formatPercent(value) {
  return `${Number(value).toFixed(1)}%`;
}

export function severityColor(severity) {
  const colors = {
    Critical: "text-severity-critical bg-severity-critical/10 border-severity-critical/30",
    High: "text-severity-high bg-severity-high/10 border-severity-high/30",
    Medium: "text-severity-medium bg-severity-medium/10 border-severity-medium/30",
    Low: "text-severity-low bg-severity-low/10 border-severity-low/30",
    Info: "text-severity-info bg-severity-info/10 border-severity-info/30",
  };

  return colors[severity] ?? colors.Info;
}
