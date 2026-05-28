import { useState } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "@/components/layout/Sidebar";
import TopNavbar from "@/components/layout/TopNavbar";

export default function AppLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="fixed inset-0 -z-10 ops-grid opacity-60" />
      <div className="fixed inset-x-0 top-0 -z-10 h-64 bg-[radial-gradient(circle_at_top_right,rgba(249,115,22,0.16),transparent_34%),radial-gradient(circle_at_top_left,rgba(34,211,238,0.11),transparent_30%)]" />

      <Sidebar mobileOpen={mobileOpen} setMobileOpen={setMobileOpen} />

      <div className="min-h-screen lg:pl-72">
        <TopNavbar onMenuClick={() => setMobileOpen(true)} />
        <main className="px-4 py-6 sm:px-6 lg:px-8">
          <div className="mx-auto flex w-full max-w-7xl flex-col gap-6">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
