import React from "react";
import { cn } from "../../lib/utils";

export const Skeleton: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <div
      className={cn(
        "animate-pulse rounded bg-slate-200 dark:bg-slate-800",
        className
      )}
    />
  );
};

export const ArticleCardSkeleton: React.FC = () => {
  return (
    <div className="rounded-xl border border-border bg-surface p-5 flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <Skeleton className="h-5 w-20 rounded-full" />
        <Skeleton className="h-4 w-16" />
      </div>
      <Skeleton className="h-6 w-3/4" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-5/6" />
      <div className="pt-2 flex items-center justify-between border-t border-border mt-auto">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-8 w-8 rounded-full" />
      </div>
    </div>
  );
};

export const DailyBriefingSkeleton: React.FC = () => {
  return (
    <div className="rounded-2xl border border-border bg-surface-elevated p-8 flex flex-col gap-6">
      <div className="flex items-center gap-3">
        <Skeleton className="h-6 w-28 rounded-full" />
        <Skeleton className="h-4 w-32" />
      </div>
      <Skeleton className="h-10 w-4/5" />
      <div className="flex flex-col gap-2">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-11/12" />
        <Skeleton className="h-4 w-3/4" />
      </div>
    </div>
  );
};
