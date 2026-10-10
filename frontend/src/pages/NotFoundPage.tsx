import { Link } from "react-router-dom";
import { Button } from "../components/ui/Button";

export function NotFoundPage() {
  return (
    <div className="mx-auto max-w-xl px-4 py-28 text-center">
      <p className="text-6xl font-serif font-bold text-accent">404</p>
      <h1 className="mt-4 font-serif text-3xl font-bold text-foreground">This page took a wrong turn.</h1>
      <p className="mt-3 text-foreground-muted">The story or page you requested does not exist.</p>
      <Link to="/"><Button className="mt-7">Back to top stories</Button></Link>
    </div>
  );
}
