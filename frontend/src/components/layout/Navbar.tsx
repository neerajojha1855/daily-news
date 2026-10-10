import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useTheme } from "../../context/ThemeContext";
import { Button } from "../ui/Button";

export const Navbar: React.FC = () => {
  const { theme, setTheme } = useTheme();
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark");
  };

  const navLinks = [
    { name: "Top Stories", path: "/" },
    { name: "For You", path: "/for-you" },
    { name: "Bookmarks", path: "/bookmarks" },
  ];

  return (
    <nav className="sticky top-0 z-40 w-full bg-surface/80 backdrop-blur-lg border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center gap-8">
            <Link to="/" className="flex items-center gap-2">
              <span className="w-8 h-8 rounded-lg bg-accent flex items-center justify-center text-white font-serif font-bold text-xl">D</span>
              <span className="font-serif font-bold text-xl text-foreground hidden sm:block tracking-tight">Daily News</span>
            </Link>
            
            <div className="hidden md:flex items-center space-x-1">
              {navLinks.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    location.pathname === link.path
                      ? "bg-surface-elevated text-accent"
                      : "text-foreground-muted hover:text-foreground hover:bg-surface-elevated"
                  }`}
                >
                  {link.name}
                </Link>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-full text-foreground-muted hover:text-foreground hover:bg-surface-elevated transition-colors"
              aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
            >
              {theme === "dark" ? "☀️" : "🌙"}
            </button>
            {localStorage.getItem("daily_news_token") ? (
              <Button
                variant="ghost"
                size="sm"
                className="hidden sm:inline-flex"
                onClick={() => {
                  localStorage.removeItem("daily_news_token");
                  localStorage.removeItem("daily_news_refresh_token");
                  navigate("/");
                }}
              >
                Sign out
              </Button>
            ) : (
              <Button variant="primary" size="sm" className="hidden sm:inline-flex" onClick={() => navigate("/login")}>Sign In</Button>
            )}
            
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-md text-foreground-muted hover:text-foreground hover:bg-surface-elevated"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d={mobileMenuOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"} />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {mobileMenuOpen && (
        <div className="md:hidden border-t border-border bg-surface">
          <div className="px-2 pt-2 pb-3 space-y-1">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                onClick={() => setMobileMenuOpen(false)}
                className={`block px-3 py-2 rounded-md text-base font-medium ${
                  location.pathname === link.path
                    ? "bg-surface-elevated text-accent"
                    : "text-foreground-muted hover:text-foreground hover:bg-surface-elevated"
                }`}
              >
                {link.name}
              </Link>
            ))}
            <div className="pt-2 px-3">
              {localStorage.getItem("daily_news_token") ? (
                <Button
                  variant="ghost"
                  className="w-full"
                  onClick={() => {
                    localStorage.removeItem("daily_news_token");
                    localStorage.removeItem("daily_news_refresh_token");
                    setMobileMenuOpen(false);
                    navigate("/");
                  }}
                >
                  Sign out
                </Button>
              ) : (
                <Button variant="primary" className="w-full" onClick={() => { setMobileMenuOpen(false); navigate("/login"); }}>Sign In</Button>
              )}
            </div>
          </div>
        </div>
      )}
    </nav>
  );
};