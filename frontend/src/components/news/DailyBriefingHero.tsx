import React from "react";
import type { DailyBriefing } from "../../types/news";
import { formatDate } from "../../lib/utils";

interface DailyBriefingHeroProps {
  briefing: DailyBriefing;
}

export const DailyBriefingHero: React.FC<DailyBriefingHeroProps> = ({ briefing }) => {
  return (
    <div className="bg-surface-elevated rounded-2xl p-6 sm:p-10 border border-border shadow-sm mb-10 relative overflow-hidden">
      {/* Decorative background element */}
      <div className="absolute top-0 right-0 -mr-20 -mt-20 w-64 h-64 bg-accent opacity-5 rounded-full blur-3xl pointer-events-none" />
      
      <div className="relative z-10 flex flex-col sm:flex-row sm:items-end justify-between gap-4 border-b border-border/50 pb-6 mb-6">
        <div>
          <span className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-accent mb-2">
            <span className="w-2 h-2 rounded-full bg-accent animate-pulse" />
            Daily Briefing
          </span>
          <h2 className="text-3xl sm:text-4xl font-serif font-bold text-foreground">
            Today's world, at a glance.
          </h2>
        </div>
        <div className="text-sm font-medium text-foreground-muted bg-surface px-3 py-1.5 rounded-lg border border-border/50">
          {formatDate(briefing.date)}
        </div>
      </div>

      <div className="relative z-10 max-w-4xl">
        <p className="text-lg sm:text-xl text-foreground-muted leading-relaxed font-serif">
          {briefing.headline_summary}
        </p>
        
        {briefing.market_pulse && (
          <div className="mt-6 p-4 bg-indigo-50/50 dark:bg-indigo-950/20 border border-indigo-100 dark:border-indigo-900/30 rounded-xl">
            <span className="text-xs font-bold uppercase tracking-wider text-indigo-600 dark:text-indigo-400 block mb-1">Market Pulse</span>
            <p className="text-sm text-foreground-muted">{briefing.market_pulse}</p>
          </div>
        )}
      </div>
    </div>
  );
};
