import React from "react";
import { cn } from "../../lib/utils";
import type { SentimentType, ImportanceType } from "../../types/news";

export interface BadgeProps {
  children: React.ReactNode;
  variant?: "category" | "sentiment" | "importance" | "neutral";
  sentiment?: SentimentType;
  importance?: ImportanceType;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = "neutral",
  sentiment,
  importance,
  className,
}) => {
  let styleClasses = "bg-surface-elevated text-foreground-muted border-border";

  if (variant === "category") {
    styleClasses = "bg-indigo-50 text-indigo-700 border-indigo-200 dark:bg-indigo-950/40 dark:text-indigo-300 dark:border-indigo-800";
  } else if (variant === "sentiment") {
    if (sentiment === "positive") {
      styleClasses = "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800";
    } else if (sentiment === "negative") {
      styleClasses = "bg-red-50 text-red-700 border-red-200 dark:bg-red-950/40 dark:text-red-300 dark:border-red-800";
    } else {
      styleClasses = "bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-800/40 dark:text-slate-300 dark:border-slate-700";
    }
  } else if (variant === "importance") {
    if (importance === "high") {
      styleClasses = "bg-amber-50 text-amber-800 border-amber-300 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800 font-semibold";
    } else {
      styleClasses = "bg-slate-100 text-slate-600 border-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700";
    }
  }

  return (
    <span
      className={cn(
        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border uppercase tracking-wider",
        styleClasses,
        className
      )}
    >
      {children}
    </span>
  );
};
