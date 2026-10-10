import React from "react";
import type { DailyBriefing } from "../../types/news";
import { formatDate } from "../../lib/utils";

interface DailyBriefingHeroProps {
  briefing: DailyBriefing;
}

export const DailyBriefingHero: React.FC<DailyBriefingHeroProps> = ({ briefing }) => {
  return (
    <div className="brutal-panel relative mb-10 overflow-hidden bg-surface p-6 sm:p-10">
      {/* Decorative background element */}
      <div className="pointer-events-none absolute -right-12 -top-12 h-44 w-44 rotate-12 border-2 border-border bg-yellow-300" />
      
      <div className="relative z-10 flex flex-col sm:flex-row sm:items-end justify-between gap-4 border-b border-border/50 pb-6 mb-6">
        <div>
          <span className="mb-2 inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[0.2em] text-accent">
            <span className="h-3 w-3 border-2 border-border bg-accent" />
            Daily Briefing
          </span>
          <h2 className="font-serif text-4xl font-bold leading-none text-foreground sm:text-6xl">
            Today's world, at a glance.
          </h2>
        </div>
        <div className="brutal-panel-sm bg-yellow-300 px-3 py-1.5 text-sm font-bold text-foreground">
          {formatDate(briefing.date)}
        </div>
      </div>

      <div className="relative z-10 max-w-4xl">
        <p className="max-w-3xl font-serif text-xl leading-relaxed text-foreground sm:text-2xl">
          {briefing.headline_summary}
        </p>
        
        {briefing.market_pulse && (
          <div className="mt-6 border-2 border-border bg-[#b8efcf] p-4 text-foreground">
            <span className="mb-1 block text-xs font-bold uppercase tracking-wider">Market Pulse</span>
            <p className="text-sm text-foreground-muted">{briefing.market_pulse}</p>
          </div>
        )}
      </div>
    </div>
  );
};
