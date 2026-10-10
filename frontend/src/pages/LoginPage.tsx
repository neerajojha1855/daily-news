import { useState } from "react";
import type { FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { authApi } from "../services/api/auth";

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsLoading(true);
    setError(null);
    try {
      const response = await authApi.login(email, password);
      localStorage.setItem("daily_news_token", response.access_token);
      localStorage.setItem("daily_news_refresh_token", response.refresh_token);
      const destination = (location.state as { from?: string } | null)?.from || "/for-you";
      navigate(destination, { replace: true });
    } catch (requestError) {
      setError((requestError as { message?: string }).message || "Unable to sign in with those credentials.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mx-auto grid min-h-[calc(100vh-9rem)] max-w-6xl items-center gap-12 px-4 py-12 lg:grid-cols-[1fr_420px] lg:px-8">
      <div className="hidden lg:block">
        <p className="text-sm font-semibold uppercase tracking-[0.18em] text-accent">Welcome back</p>
        <h1 className="mt-4 max-w-xl font-serif text-6xl font-bold leading-tight text-foreground">A sharper way to stay informed.</h1>
        <p className="mt-6 max-w-lg text-lg leading-relaxed text-foreground-muted">Save the stories you care about and get a feed tuned to your interests.</p>
      </div>
      <form onSubmit={handleSubmit} className="rounded-3xl border border-border bg-surface p-6 shadow-xl shadow-slate-950/5 sm:p-8">
        <p className="text-sm font-semibold uppercase tracking-[0.18em] text-accent">Daily News</p>
        <h2 className="mt-3 font-serif text-3xl font-bold text-foreground">Sign in</h2>
        <p className="mt-2 text-sm text-foreground-muted">Continue to your personalized news desk.</p>
        {error && <p role="alert" className="mt-5 rounded-lg bg-red-50 p-3 text-sm text-red-800 dark:bg-red-950/40 dark:text-red-100">{error}</p>}
        <div className="mt-7 space-y-5">
          <Input label="Email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required autoComplete="email" />
          <Input label="Password" isPassword value={password} onChange={(event) => setPassword(event.target.value)} required autoComplete="current-password" />
        </div>
        <Button type="submit" className="mt-7 w-full" isLoading={isLoading}>Sign in</Button>
        <p className="mt-6 text-center text-sm text-foreground-muted">New here? <Link className="font-semibold text-accent hover:underline" to="/signup">Create an account</Link></p>
      </form>
    </div>
  );
}
