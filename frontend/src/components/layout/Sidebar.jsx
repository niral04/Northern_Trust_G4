import { NavLink } from "react-router-dom";
import {
  Activity,
  BarChart3,
  BellRing,
  Gauge,
  LayoutDashboard,
  LogIn,
  RadioTower,
  ShieldAlert,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";

const navItems = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Analytics", href: "/analytics", icon: BarChart3 },
  { label: "Login", href: "/login", icon: LogIn },
];

const systemItems = [
  { label: "Event Bus", value: "1.2k/min", icon: RadioTower, tone: "text-cyan-300" },
  { label: "Classifier", value: "94.8%", icon: Activity, tone: "text-emerald-300" },
  { label: "Escalation", value: "Armed", icon: BellRing, tone: "text-orange-300" },
];

function SidebarContent({ setMobileOpen }) {
  return (
    <div className="flex h-full flex-col">
      <div className="flex h-16 items-center justify-between px-5">
        <NavLink to="/dashboard" className="flex min-w-0 items-center gap-3" onClick={() => setMobileOpen?.(false)}>
          <div className="relative grid size-10 place-items-center rounded-lg border border-orange-500/30 bg-orange-500/10 text-orange-300 shadow-alert">
            <ShieldAlert className="size-5" />
            <span className="absolute -right-1 -top-1 size-2.5 rounded-full bg-red-500" />
          </div>
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-foreground">Incident Command</p>
            <p className="truncate text-xs text-muted-foreground">Event-driven ops</p>
          </div>
        </NavLink>
        <Button
          variant="ghost"
          size="icon"
          className="lg:hidden"
          onClick={() => setMobileOpen?.(false)}
          aria-label="Close navigation"
        >
          <X className="size-5" />
        </Button>
      </div>

      <Separator />

      <nav className="flex-1 space-y-1 px-3 py-4">
        {navItems.map((item) => (
          <NavLink
            key={item.href}
            to={item.href}
            onClick={() => setMobileOpen?.(false)}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground",
                isActive && "bg-primary/10 text-primary ring-1 ring-primary/20",
              )
            }
          >
            <item.icon className="size-4" />
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="px-4 pb-5">
        <div className="rounded-lg border border-border bg-muted/40 p-4">
          <div className="mb-3 flex items-center justify-between">
            <p className="text-xs font-semibold uppercase text-muted-foreground">Signal Mesh</p>
            <Gauge className="size-4 text-primary" />
          </div>
          <div className="space-y-3">
            {systemItems.map((item) => (
              <div key={item.label} className="flex items-center justify-between gap-3">
                <div className="flex min-w-0 items-center gap-2">
                  <item.icon className={cn("size-4 shrink-0", item.tone)} />
                  <span className="truncate text-sm text-muted-foreground">{item.label}</span>
                </div>
                <span className="font-mono text-xs text-foreground">{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Sidebar({ mobileOpen, setMobileOpen }) {
  return (
    <>
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-72 border-r border-border bg-background/88 backdrop-blur-xl lg:block">
        <SidebarContent />
      </aside>

      {mobileOpen ? (
        <div className="fixed inset-0 z-50 lg:hidden">
          <button
            className="absolute inset-0 bg-background/80 backdrop-blur-sm"
            onClick={() => setMobileOpen(false)}
            aria-label="Close navigation overlay"
          />
          <aside className="relative h-full w-[min(21rem,86vw)] border-r border-border bg-background shadow-glow">
            <SidebarContent setMobileOpen={setMobileOpen} />
          </aside>
        </div>
      ) : null}
    </>
  );
}
