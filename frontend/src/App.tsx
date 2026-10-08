import React, { useState } from "react";
import { ThemeProvider, useTheme } from "./context/ThemeContext";
import { ToastProvider, useToast } from "./context/ToastContext";
import { Button } from "./components/ui/Button";
import { Input } from "./components/ui/Input";
import { Badge } from "./components/ui/Badge";
import { ArticleCardSkeleton, DailyBriefingSkeleton } from "./components/ui/SkeletonLoader";
import { Modal } from "./components/ui/Modal";
import { ToastContainer } from "./components/ui/Toast";

const DesignSystemGallery: React.FC = () => {
  const { theme, setTheme, effectiveTheme } = useTheme();
  const { showToast } = useToast();
  const [modalOpen, setModalOpen] = useState(false);
  const [buttonLoading, setButtonLoading] = useState(false);

  return (
    <div className="min-h-screen bg-background text-foreground transition-colors p-6 sm:p-12 max-w-6xl mx-auto space-y-12">
      <header className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-6 border-b border-border gap-4">
        <div>
          <span className="text-xs uppercase tracking-widest font-semibold text-accent">Phase 5 Design System</span>
          <h1 className="text-3xl sm:text-4xl font-bold font-serif text-foreground mt-1">Daily News UI Foundation</h1>
          <p className="text-foreground-muted text-sm mt-1">Editorial aesthetics, zero-flash theming, and atomic components.</p>
        </div>

        <div className="flex items-center gap-2 bg-surface-elevated p-1.5 rounded-xl border border-border">
          <Button
            size="sm"
            variant={theme === "light" ? "primary" : "ghost"}
            onClick={() => setTheme("light")}
          >
            ☀️ Light
          </Button>
          <Button
            size="sm"
            variant={theme === "dark" ? "primary" : "ghost"}
            onClick={() => setTheme("dark")}
          >
            🌙 Dark
          </Button>
          <Button
            size="sm"
            variant={theme === "system" ? "primary" : "ghost"}
            onClick={() => setTheme("system")}
          >
            💻 System ({effectiveTheme})
          </Button>
        </div>
      </header>

      <section className="space-y-4">
        <h2 className="text-xl font-bold font-serif border-b border-border pb-2">Editorial Typography</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 bg-surface p-6 rounded-2xl border border-border">
          <div>
            <span className="text-xs font-semibold text-foreground-muted uppercase tracking-wider">Serif Headline (Merriweather)</span>
            <h3 className="text-2xl font-serif font-bold text-foreground mt-2 leading-tight">
              Global Markets Shift as AI Ingestion Pipelines Redefine Modern Newsrooms
            </h3>
          </div>
          <div>
            <span className="text-xs font-semibold text-foreground-muted uppercase tracking-wider">Sans Body (Inter)</span>
            <p className="text-foreground-muted text-sm mt-2 leading-relaxed">
              Every story processed by our platform undergoes structured synthesis by Google Gemini, extracting concise takeaways, importance rankings, and multi-point sentiment.
            </p>
          </div>
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-bold font-serif border-b border-border pb-2">Button Primitives</h2>
        <div className="flex flex-wrap items-center gap-4 bg-surface p-6 rounded-2xl border border-border">
          <Button variant="primary">Primary Button</Button>
          <Button variant="secondary">Secondary Button</Button>
          <Button variant="outline">Outline</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="danger">Danger</Button>
          <Button
            variant="primary"
            isLoading={buttonLoading}
            onClick={() => {
              setButtonLoading(true);
              setTimeout(() => setButtonLoading(false), 2000);
            }}
          >
            {buttonLoading ? "Loading..." : "Test Spinner"}
          </Button>
          <Button variant="primary" disabled>Disabled</Button>
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-bold font-serif border-b border-border pb-2">Form Controls</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 bg-surface p-6 rounded-2xl border border-border">
          <Input label="Email Address" placeholder="editor@dailynews.com" helperText="We will never share your email." />
          <Input label="Password" placeholder="••••••••" isPassword helperText="Must be 8+ characters." />
          <Input label="Search Query" placeholder="AI, Semiconductors, Climate..." error="Please enter a valid search term" />
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-bold font-serif border-b border-border pb-2">Semantic Badges</h2>
        <div className="flex flex-wrap items-center gap-3 bg-surface p-6 rounded-2xl border border-border">
          <Badge variant="category">Technology</Badge>
          <Badge variant="category">Finance</Badge>
          <Badge variant="category">World</Badge>
          <Badge variant="sentiment" sentiment="positive">Positive (+0.84)</Badge>
          <Badge variant="sentiment" sentiment="negative">Negative (-0.61)</Badge>
          <Badge variant="sentiment" sentiment="neutral">Neutral (0.02)</Badge>
          <Badge variant="importance" importance="high">High Importance</Badge>
          <Badge variant="importance" importance="medium">Standard Priority</Badge>
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-bold font-serif border-b border-border pb-2">Loading Skeletons</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <DailyBriefingSkeleton />
          <ArticleCardSkeleton />
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-bold font-serif border-b border-border pb-2">Feedback & Dialogs</h2>
        <div className="flex flex-wrap items-center gap-4 bg-surface p-6 rounded-2xl border border-border">
          <Button variant="secondary" onClick={() => setModalOpen(true)}>
            Open Article Preview Modal
          </Button>
          <Button
            variant="outline"
            onClick={() => showToast("Article saved to bookmarks!", "success")}
          >
            Trigger Success Toast
          </Button>
          <Button
            variant="outline"
            onClick={() => showToast("Failed to refresh feed. Rate limit reached.", "error")}
          >
            Trigger Error Toast
          </Button>
        </div>
      </section>

      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title="AI Article Analysis Preview"
      >
        <div className="space-y-4 text-left">
          <div className="flex items-center gap-2">
            <Badge variant="category">Technology</Badge>
            <Badge variant="sentiment" sentiment="positive">Positive</Badge>
          </div>
          <p className="text-sm text-foreground-muted leading-relaxed">
            This modal illustrates the zero-layout-shift accessible dialog primitive. It supports keyboard ESC dismissal, backdrop blur, and scroll lock.
          </p>
          <div className="flex justify-end gap-3 pt-4 border-t border-border">
            <Button variant="outline" size="sm" onClick={() => setModalOpen(false)}>
              Close
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={() => {
                setModalOpen(false);
                showToast("Action confirmed in modal", "info");
              }}
            >
              Confirm
            </Button>
          </div>
        </div>
      </Modal>

      <ToastContainer />
    </div>
  );
};

export default function App() {
  return (
    <ThemeProvider>
      <ToastProvider>
        <DesignSystemGallery />
      </ToastProvider>
    </ThemeProvider>
  );
}
