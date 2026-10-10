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
    styleClasses = "bg-yellow-300 text-foreground border-border";
  } else if (variant === "sentiment") {
    if (sentiment === "positive") {
      styleClasses = "bg-[#b8efcf] text-foreground border-border";
    } else if (sentiment === "negative") {
      styleClasses = "bg-[#ffc3b5] text-foreground border-border";
    } else {
      styleClasses = "bg-surface-elevated text-foreground border-border";
    }
  } else if (variant === "importance") {
    if (importance === "high") {
      styleClasses = "bg-accent text-white border-border font-semibold";
    } else {
      styleClasses = "bg-surface-elevated text-foreground-muted border-border";
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
