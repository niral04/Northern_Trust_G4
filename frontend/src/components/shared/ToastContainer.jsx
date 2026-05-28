import { useToast } from "@/context/ToastContext";
import { cn } from "@/lib/utils";

const toneStyles = {
  info: "border-zinc-700 bg-zinc-900 text-zinc-100",
  success: "border-emerald-500/40 bg-emerald-500/10 text-emerald-100",
  warning: "border-orange-500/40 bg-orange-500/10 text-orange-100",
  danger: "border-red-500/40 bg-red-500/10 text-red-100",
};

export default function ToastContainer() {
  const { toasts, dismissToast } = useToast();

  return (
    <div className="pointer-events-none fixed bottom-4 right-4 z-[100] flex w-full max-w-sm flex-col gap-2">
      {toasts.map((toast) => (
        <button
          key={toast.id}
          type="button"
          onClick={() => dismissToast(toast.id)}
          className={cn(
            "pointer-events-auto rounded-lg border px-4 py-3 text-left text-sm shadow-lg backdrop-blur transition-all animate-in slide-in-from-right",
            toneStyles[toast.tone] ?? toneStyles.info,
          )}
        >
          {toast.message}
        </button>
      ))}
    </div>
  );
}
