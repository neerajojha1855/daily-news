import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "./context/ThemeContext";
import { ToastProvider } from "./context/ToastContext";
import { Navbar } from "./components/layout/Navbar";
import { Footer } from "./components/layout/Footer";
import { HomePage } from "./pages/HomePage";

export default function App() {
  return (
    <ThemeProvider>
      <ToastProvider>
        <Router>
          <div className="flex flex-col min-h-screen bg-background text-foreground">
            <Navbar />
            <main className="flex-grow">
              <Routes>
                <Route path="/" element={<HomePage />} />
                {/* Future routes (Phase 8 API integration) */}
                <Route path="/category/:slug" element={<HomePage />} />
                <Route path="/for-you" element={<HomePage />} />
                <Route path="/bookmarks" element={<HomePage />} />
              </Routes>
            </main>
            <Footer />
          </div>
        </Router>
      </ToastProvider>
    </ThemeProvider>
  );
}
