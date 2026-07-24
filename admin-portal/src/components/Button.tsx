import type { ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger";
  loading?: boolean;
}

export function Button({ variant = "primary", loading, disabled, className = "", children, ...props }: ButtonProps) {
  const base = "rounded-xl px-4 py-2.5 font-semibold text-sm transition-opacity disabled:opacity-50";
  const variants = {
    primary: "bg-[color:var(--color-primary)] text-white hover:opacity-90",
    secondary: "border border-[color:var(--color-border)] text-[color:var(--color-text-primary)] hover:bg-[color:var(--color-surface)]",
    danger: "bg-[color:var(--color-danger)] text-white hover:opacity-90",
  };

  return (
    <button
      className={`${base} ${variants[variant]} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? "..." : children}
    </button>
  );
}
