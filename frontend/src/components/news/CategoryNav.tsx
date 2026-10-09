import React from "react";
import type { NewsCategory } from "../../types/news";

interface CategoryNavProps {
  categories: NewsCategory[];
  activeCategory: NewsCategory | "all";
  onSelect: (category: NewsCategory | "all") => void;
}

export const CategoryNav: React.FC<CategoryNavProps> = ({
  categories,
  activeCategory,
  onSelect,
}) => {
  const tabs = ["all", ...categories];

  return (
    <div className="w-full overflow-x-auto no-scrollbar border-b border-border mb-6">
      <div className="flex space-x-8 px-2 min-w-max">
        {tabs.map((tab) => {
          const isActive = activeCategory === tab;
          return (
            <button
              key={tab}
              onClick={() => onSelect(tab as NewsCategory | "all")}
              className={`pb-4 text-sm font-medium uppercase tracking-wider transition-colors relative whitespace-nowrap ${
                isActive ? "text-accent" : "text-foreground-muted hover:text-foreground"
              }`}
            >
              {tab}
              {isActive && (
                <span className="absolute bottom-0 left-0 w-full h-0.5 bg-accent rounded-t-full" />
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};
