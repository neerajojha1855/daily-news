import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { DailyBriefingHero } from "../components/news/DailyBriefingHero";
import { CategoryNav } from "../components/news/CategoryNav";
import { ArticleCard } from "../components/news/ArticleCard";
import { TrendingSidebar } from "../components/news/TrendingSidebar";
import { ArticleDetailModal } from "../components/news/ArticleDetailModal";
import type { NewsCategory, NewsArticle, DailyBriefing } from "../types/news";

// MOCK DATA (Temporary for UI validation)
const MOCK_BRIEFING: DailyBriefing = {
  date: new Date().toISOString(),
  headline_summary: "Global markets rally as AI advancements outpace expectations, while new environmental regulations take effect across Europe.",
  market_pulse: "S&P 500 up 1.2%, NASDAQ rallies on tech earnings. Crypto markets remain volatile.",
  top_stories: []
};

const MOCK_ARTICLE: NewsArticle = {
  id: 1,
  title: "Next-Gen AI Models Show Unprecedented Reasoning Capabilities",
  source: "TechInsider",
  url: "https://example.com",
  image_url: "https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&q=80&w=800",
  summary: "Researchers have published new benchmarks demonstrating that recent large language models can perform complex multi-step reasoning previously thought to require human intuition.",
  key_points: ["Benchmarks show 40% improvement in logic tasks", "New architecture reduces hallucination rates", "Industry leaders call for updated safety frameworks"],
  category: "technology",
  sentiment: "positive",
  sentiment_score: 0.85,
  importance: "high",
  created_at: new Date().toISOString()
};

const CATEGORIES: NewsCategory[] = ["technology", "business", "politics", "health", "science", "world", "general", "sports", "entertainment"];

export const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const [activeCategory, setActiveCategory] = useState<NewsCategory | "all">("all");
  const [selectedArticle, setSelectedArticle] = useState<NewsArticle | null>(null);

  const handleCategorySelect = (category: NewsCategory | "all") => {
    setActiveCategory(category);
    if (category !== "all") {
      navigate(`/category/${category}`);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <DailyBriefingHero briefing={MOCK_BRIEFING} />
      
      <CategoryNav 
        categories={CATEGORIES} 
        activeCategory={activeCategory} 
        onSelect={handleCategorySelect} 
      />

      <div className="flex flex-col lg:flex-row gap-8">
        <div className="lg:w-2/3">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="md:col-span-2">
               <ArticleCard article={MOCK_ARTICLE} featured onClick={setSelectedArticle} />
            </div>
            <ArticleCard article={{...MOCK_ARTICLE, id: 2, importance: "medium", image_url: null}} onClick={setSelectedArticle} />
            <ArticleCard article={{...MOCK_ARTICLE, id: 3, category: "business", sentiment: "neutral"}} onClick={setSelectedArticle} />
          </div>
        </div>
        
        <aside className="lg:w-1/3">
          <TrendingSidebar 
            articles={[MOCK_ARTICLE, {...MOCK_ARTICLE, id: 2, title: "Central Banks Signal Rate Cuts"} ]} 
            onClick={setSelectedArticle} 
          />
        </aside>
      </div>

      <ArticleDetailModal 
        article={selectedArticle} 
        isOpen={!!selectedArticle} 
        onClose={() => setSelectedArticle(null)} 
      />
    </div>
  );
};
