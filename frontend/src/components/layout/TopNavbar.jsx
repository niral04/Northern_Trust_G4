import { Bell, Menu, Moon, RefreshCw, Search, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useTheme } from "@/context/ThemeContext";

export default function TopNavbar({ onMenuClick }) {
  const { isDark, toggleTheme } = useTheme();

  return (
    <header className="sticky top-0 z-30 border-b border-border bg-background/76 backdrop-blur-xl">
      <div className="flex h-16 items-center gap-3 px-4 sm:px-6 lg:px-8">
        <Button variant="ghost" size="icon" className="lg:hidden" onClick={onMenuClick} aria-label="Open navigation">
          <Menu className="size-5" />
        </Button>

        <div className="relative hidden w-full max-w-md sm:block">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="search"
            placeholder="Search incidents, services, owners"
            className="h-10 w-full rounded-md border border-border bg-muted/40 pl-9 pr-3 text-sm outline-none transition focus:border-primary/60 focus:ring-2 focus:ring-primary/20"
          />
        </div>

        <div className="ml-auto flex items-center gap-2">
          <Badge variant="outline" className="hidden gap-2 border-emerald-500/30 bg-emerald-500/10 text-emerald-200 sm:inline-flex">
            <span className="relative flex size-2">
              <span className="absolute inline-flex size-full animate-ping rounded-full bg-emerald-400 opacity-70" />
              <span className="relative inline-flex size-2 rounded-full bg-emerald-400" />
            </span>
            Live
          </Badge>
          <Button variant="ghost" size="icon" aria-label="Refresh dashboard" title="Refresh dashboard">
            <RefreshCw className="size-4" />
          </Button>
          <Button variant="ghost" size="icon" aria-label="Notifications" title="Notifications">
            <Bell className="size-4" />
          </Button>
          <Button variant="outline" size="icon" onClick={toggleTheme} aria-label="Toggle theme" title="Toggle theme">
            {isDark ? <Sun className="size-4" /> : <Moon className="size-4" />}
          </Button>
        </div>
      </div>
    </header>
  );
}
