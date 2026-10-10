import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { profileApi } from "../services/api/profile";
import { useToast } from "../context/ToastContext";
import type { UserPreferences, UserProfile } from "../types/user";
import type { NewsCategory } from "../types/news";

const CATEGORIES: Array<{ value: NewsCategory; label: string }> = [
  { value: "technology", label: "Technology" },
  { value: "business", label: "Business" },
  { value: "politics", label: "Politics" },
  { value: "science", label: "Science" },
  { value: "health", label: "Health" },
  { value: "sports", label: "Sports" },
  { value: "entertainment", label: "Entertainment" },
  { value: "world", label: "World" },
  { value: "india", label: "India" },
  { value: "education", label: "Education" },
  { value: "environment", label: "Environment" },
  { value: "other", label: "Other" },
];

const DEFAULT_PREFERENCES: UserPreferences = {
  preferred_categories: [],
  preferred_sources: [],
  preferred_language: "en",
};

function errorMessage(error: unknown, fallback: string) {
  if (typeof error === "object" && error !== null && "message" in error) {
    const message = (error as { message?: unknown }).message;
    if (typeof message === "string" && message) return message;
  }
  return fallback;
}

export function ProfilePage() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [preferences, setPreferences] = useState<UserPreferences>(DEFAULT_PREFERENCES);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [sources, setSources] = useState("");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSavingProfile, setIsSavingProfile] = useState(false);
  const [isSavingPreferences, setIsSavingPreferences] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!localStorage.getItem("daily_news_token")) {
      navigate("/login", { replace: true, state: { from: "/profile" } });
      return;
    }

    Promise.all([profileApi.getProfile(), profileApi.getPreferences()])
      .then(([user, userPreferences]) => {
        setProfile(user);
        setUsername(user.username);
        setEmail(user.email);
        setPreferences(userPreferences);
        setSources(userPreferences.preferred_sources.join(", "));
      })
      .catch((requestError) => setError(errorMessage(requestError, "Unable to load your profile.")))
      .finally(() => setIsLoading(false));
  }, [navigate]);

  const toggleCategory = (category: NewsCategory) => {
    setPreferences((current) => ({
      ...current,
      preferred_categories: current.preferred_categories.includes(category)
        ? current.preferred_categories.filter((item) => item !== category)
        : [...current.preferred_categories, category],
    }));
  };

  const saveProfile = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSavingProfile(true);
    try {
      const updated = await profileApi.updateProfile({ username: username.trim(), email: email.trim() });
      setProfile((current) => current ? { ...current, ...updated } : current);
      setUsername(updated.username);
      setEmail(updated.email);
      showToast("Profile details updated.", "success");
    } catch (requestError) {
      showToast(errorMessage(requestError, "Unable to update profile details."), "error");
    } finally {
      setIsSavingProfile(false);
    }
  };

  const savePreferences = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSavingPreferences(true);
    try {
      const updated = await profileApi.updatePreferences({
        ...preferences,
        preferred_sources: sources.split(",").map((source) => source.trim()).filter(Boolean),
      });
      setPreferences(updated);
      setSources(updated.preferred_sources.join(", "));
      showToast("Your feed preferences were updated.", "success");
    } catch (requestError) {
      showToast(errorMessage(requestError, "Unable to update feed preferences."), "error");
    } finally {
      setIsSavingPreferences(false);
    }
  };

  const changePassword = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (newPassword.length < 8) {
      showToast("Your new password must be at least 8 characters.", "error");
      return;
    }
    if (newPassword !== confirmPassword) {
      showToast("New passwords do not match.", "error");
      return;
    }
    setIsChangingPassword(true);
    try {
      await profileApi.changePassword(currentPassword, newPassword);
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      showToast("Password changed successfully.", "success");
    } catch (requestError) {
      showToast(errorMessage(requestError, "Unable to change your password."), "error");
    } finally {
      setIsChangingPassword(false);
    }
  };

  if (!localStorage.getItem("daily_news_token")) return null;

  if (isLoading) {
    return <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:px-8"><div className="h-96 animate-pulse rounded-3xl bg-surface-elevated" /></div>;
  }

  if (error || !profile) {
    return (
      <div className="mx-auto max-w-xl px-4 py-24 text-center">
        <h1 className="font-serif text-3xl font-bold text-foreground">Profile unavailable</h1>
        <p className="mt-3 text-foreground-muted">{error || "We couldn't load your profile."}</p>
        <Button className="mt-6" onClick={() => window.location.reload()}>Try again</Button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="mb-10 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-accent">Account settings</p>
          <h1 className="mt-2 font-serif text-4xl font-bold text-foreground">Your profile</h1>
          <p className="mt-2 text-foreground-muted">Shape your feed and keep your account details up to date.</p>
        </div>
        <div className="clay-panel rounded-3xl bg-surface-elevated px-5 py-4 text-sm">
          <span className="block text-2xl font-bold text-accent">{profile.stats.total_bookmarks}</span>
          <span className="text-foreground-muted">saved stories</span>
        </div>
      </div>

      <div className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="space-y-8">
          <form onSubmit={saveProfile} className="clay-panel rounded-3xl bg-surface p-6 sm:p-8">
            <h2 className="font-serif text-2xl font-bold text-foreground">Account details</h2>
            <p className="mt-1 text-sm text-foreground-muted">These details identify your Daily News account.</p>
            <div className="mt-6 grid gap-5 sm:grid-cols-2">
              <Input label="Username" value={username} onChange={(event) => setUsername(event.target.value)} minLength={3} maxLength={30} pattern="[A-Za-z0-9._]{3,30}" required />
              <Input label="Email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
            </div>
            <Button type="submit" className="mt-6" isLoading={isSavingProfile}>Save details</Button>
          </form>

          <form onSubmit={changePassword} className="clay-panel rounded-3xl bg-surface p-6 sm:p-8">
            <h2 className="font-serif text-2xl font-bold text-foreground">Change password</h2>
            <div className="mt-6 space-y-5">
              <Input label="Current password" isPassword value={currentPassword} onChange={(event) => setCurrentPassword(event.target.value)} required />
              <div className="grid gap-5 sm:grid-cols-2">
                <Input label="New password" isPassword value={newPassword} onChange={(event) => setNewPassword(event.target.value)} minLength={8} required />
                <Input label="Confirm new password" isPassword value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} minLength={8} required />
              </div>
            </div>
            <Button type="submit" variant="outline" className="mt-6" isLoading={isChangingPassword}>Change password</Button>
          </form>
        </div>

        <form onSubmit={savePreferences} className="clay-panel h-fit rounded-3xl bg-surface p-6 sm:p-8">
          <h2 className="font-serif text-2xl font-bold text-foreground">Personalize your feed</h2>
          <p className="mt-1 text-sm text-foreground-muted">Choose the topics you want to see more often in For You.</p>
          <fieldset className="mt-6">
            <legend className="text-xs font-semibold uppercase tracking-wide text-foreground-muted">Preferred topics</legend>
            <div className="mt-3 flex flex-wrap gap-2">
              {CATEGORIES.map((category) => {
                const selected = preferences.preferred_categories.includes(category.value);
                return (
                  <button
                    key={category.value}
                    type="button"
                    aria-pressed={selected}
                    onClick={() => toggleCategory(category.value)}
                    className={`rounded-full border px-3 py-2 text-sm font-bold transition-all ${selected ? "border-accent bg-accent text-white shadow-[3px_3px_0_#171717]" : "border-border bg-surface-elevated text-foreground-muted shadow-[inset_2px_2px_5px_rgba(0,0,0,0.08)] hover:border-accent hover:text-accent"}`}
                  >
                    {category.label}
                  </button>
                );
              })}
            </div>
          </fieldset>
          <div className="mt-7 space-y-5">
            <Input label="Preferred sources" value={sources} onChange={(event) => setSources(event.target.value)} placeholder="BBC, Reuters, The Hindu" helperText="Separate source names with commas." />
            <label className="flex flex-col gap-1.5 text-left">
              <span className="text-xs font-semibold uppercase tracking-wide text-foreground-muted">Language</span>
              <select value={preferences.preferred_language} onChange={(event) => setPreferences((current) => ({ ...current, preferred_language: event.target.value }))} className="rounded-lg border border-border bg-surface px-3.5 py-2 text-sm text-foreground focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/40">
                <option value="en">English</option>
                <option value="hi">Hindi</option>
              </select>
            </label>
          </div>
          <Button type="submit" className="mt-6 w-full" isLoading={isSavingPreferences}>Save feed preferences</Button>
        </form>
      </div>
    </div>
  );
}
