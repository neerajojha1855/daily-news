import { forwardRef, useState } from "react";
import type { InputHTMLAttributes } from "react";
import { cn } from "../../lib/utils";

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  isPassword?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, isPassword, className, type = "text", id, ...props }, ref) => {
    const [showPassword, setShowPassword] = useState(false);
    const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, "-") : undefined);
    const inputType = isPassword ? (showPassword ? "text" : "password") : type;

    return (
      <div className="w-full flex flex-col gap-1.5 text-left">
        {label && (
          <label htmlFor={inputId} className="text-xs font-semibold text-foreground-muted tracking-wide uppercase">
            {label}
          </label>
        )}
        <div className="relative flex items-center">
          <input
            id={inputId}
            ref={ref}
            type={inputType}
            className={cn(
              "w-full px-3.5 py-2 text-sm rounded-lg bg-surface border transition-colors",
              "text-foreground placeholder:text-foreground-muted/60",
              "focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent",
              error ? "border-red-500 focus:ring-red-400" : "border-border",
              isPassword ? "pr-10" : "",
              className
            )}
            {...props}
          />
          {isPassword && (
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 text-foreground-muted hover:text-foreground text-xs font-medium focus:outline-none"
              tabIndex={-1}
            >
              {showPassword ? "Hide" : "Show"}
            </button>
          )}
        </div>
        {error && <span className="text-xs text-red-500 font-medium">{error}</span>}
        {!error && helperText && <span className="text-xs text-foreground-muted">{helperText}</span>}
      </div>
    );
  }
);

Input.displayName = "Input";
