import { Link } from "react-router-dom";
import { ArrowRight, LockKeyhole, ShieldAlert } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function Login() {
  return (
    <main className="grid min-h-screen place-items-center bg-background px-4 text-foreground">
      <div className="fixed inset-0 -z-10 ops-grid opacity-60" />
      <div className="w-full max-w-md">
        <div className="mb-8 flex items-center justify-center gap-3">
          <div className="grid size-11 place-items-center rounded-lg border border-orange-500/30 bg-orange-500/10 text-orange-300 shadow-alert">
            <ShieldAlert className="size-6" />
          </div>
          <div>
            <p className="font-semibold">Incident Command</p>
            <p className="text-sm text-muted-foreground">Secure operations console</p>
          </div>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Sign in</CardTitle>
            <p className="text-sm text-muted-foreground">Use your team identity provider to continue.</p>
          </CardHeader>
          <CardContent className="space-y-4">
            <label className="block space-y-2">
              <span className="text-sm text-muted-foreground">Email</span>
              <input
                type="email"
                placeholder="oncall@company.com"
                className="h-11 w-full rounded-md border border-border bg-muted/40 px-3 text-sm outline-none transition focus:border-primary/60 focus:ring-2 focus:ring-primary/20"
              />
            </label>
            <label className="block space-y-2">
              <span className="text-sm text-muted-foreground">Password</span>
              <input
                type="password"
                placeholder="Password"
                className="h-11 w-full rounded-md border border-border bg-muted/40 px-3 text-sm outline-none transition focus:border-primary/60 focus:ring-2 focus:ring-primary/20"
              />
            </label>
            <Button className="w-full" asChild>
              <Link to="/dashboard">
                <LockKeyhole className="size-4" />
                Enter console
                <ArrowRight className="size-4" />
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
