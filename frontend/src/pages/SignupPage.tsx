import { useState } from "react";
import type { FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { authApi } from "../services/api/auth";

function getApiMessage(error: unknown, fallback: string): string {
  if (typeof error === "object" && error !== null && "message" in error) {
    const message = (error as { message?: unknown }).message;
    if (typeof message === "string" && message.length > 0) return message;
  }
  return fallback;
}

export function SignupPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);

    const normalizedUsername = username.trim().toLowerCase();
    if (!/^[a-zA-Z0-9._]{3,30}$/.test(normalizedUsername)) {
      setError("Username must be 3–30 characters and use only letters, numbers, dots, or underscores.");
      return;
    }
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setIsLoading(true);
    try {
      const response = await authApi.register(normalizedUsername, email.trim(), password, confirmPassword);
      localStorage.setItem("daily_news_token", response.access_token);
      localStorage.setItem("daily_news_refresh_token", response.refresh_token);
      const destination = (location.state as { from?: string } | null)?.from || "/for-you";
      navigate(destination, { replace: true });
    } catch (requestError) {
      setError(getApiMessage(requestError, "We couldn't create your account. Please try again."));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mx-auto grid min-h-[calc(100vh-9rem)] max-w-6xl items-center gap-12 px-4 py-12 lg:grid-cols-[1fr_420px] lg:px-8">
      <div className="hidden lg:block">
        <p className="text-sm font-semibold uppercase tracking-[0.18em] text-accent">Join Daily News</p>
        <h1 className="mt-4 max-w-xl font-serif text-6xl font-bold leading-tight text-foreground">Build a news habit that respects your time.</h1>
        <p className="mt-6 max-w-lg text-lg leading-relaxed text-foreground-muted">Create an account to save stories and make your For You feed more relevant.</p>
      </div>
      <form onSubmit={handleSubmit} className="rounded-3xl border border-border bg-surface p-6 shadow-xl shadow-slate-950/5 sm:p-8">
        <p className="text-sm font-semibold uppercase tracking-[0.18em] text-accent">Daily News</p>
        <h2 className="mt-3 font-serif text-3xl font-bold text-foreground">Create your account</h2>
        <p className="mt-2 text-sm text-foreground-muted">Start building your personalized reading list.</p>
        {error && <p role="alert" className="mt-5 rounded-lg bg-red-50 p-3 text-sm text-red-800 dark:bg-red-950/40 dark:text-red-100">{error}</p>}
        <div className="mt-7 space-y-5">
          <Input
            label="Username"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            required
            autoComplete="username"
            minLength={3}
            maxLength={30}
            pattern="[A-Za-z0-9._]{3,30}"
            helperText="3–30 letters, numbers, dots, or underscores."
          />
          <Input label="Email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required autoComplete="email" />
          <Input label="Password" isPassword value={password} onChange={(event) => setPassword(event.target.value)} required autoComplete="new-password" minLength={8} helperText="Use at least 8 characters." />
          <Input label="Confirm password" isPassword value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} required autoComplete="new-password" minLength={8} />
        </div>
        <Button type="submit" className="mt-7 w-full" isLoading={isLoading}>Create account</Button>
        <p className="mt-6 text-center text-sm text-foreground-muted">Already have an account? <Link className="font-semibold text-accent hover:underline" to="/login">Sign in</Link></p>
      </form>
    </div>
  );
}
