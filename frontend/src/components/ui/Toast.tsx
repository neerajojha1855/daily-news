import React from "react";
import { useToast } from "../../context/ToastContext";
import { cn } from "../../lib/utils";

export const ToastContainer: React.FC = () => {
  const { toasts, removeToast } = useToast();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none">
      {toasts.map((toast) => {
        let borderAndBg = "bg-surface border-border text-foreground";
        if (toast.type === "success") {
          borderAndBg = "bg-emerald-50 dark:bg-emerald-950/80 border-emerald-300 dark:border-emerald-800 text-emerald-900 dark:text-emerald-100";
        } else if (toast.type === "error") {
          borderAndBg = "bg-red-50 dark:bg-red-950/80 border-red-300 dark:border-red-800 text-red-900 dark:text-red-100";
        }

        return (
          <div
            key={toast.id}
            className={cn(
              "pointer-events-auto flex items-center justify-between p-4 rounded-xl border shadow-lg transition-all animate-bounce-in",
              borderAndBg
            )}
          >
            <span className="text-sm font-medium">{toast.message}</span>
            <button
              onClick={() => removeToast(toast.id)}
              className="ml-3 text-xs opacity-70 hover:opacity-100"
            >
              ✕
            </button>
          </div>
        );
      })}
    </div>
  );
};
