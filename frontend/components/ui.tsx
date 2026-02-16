interface CardProps {
  children: React.ReactNode;
  className?: string;
}

export function Card({ children, className = "" }: CardProps) {
  return (
    <div
      className={`p-6 border rounded ${className}`}
      style={{
        borderColor: "var(--border-green)",
        backgroundColor: "rgba(0, 255, 0, 0.02)",
      }}
    >
      {children}
    </div>
  );
}

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger";
  loading?: boolean;
  size?: "sm" | "md" | "lg";
}

export function Button({
  variant = "primary",
  loading = false,
  size = "md",
  children,
  disabled,
  ...props
}: ButtonProps) {
  const sizeClasses = {
    sm: "px-2 py-1 text-xs",
    md: "px-4 py-2 text-sm",
    lg: "px-6 py-3 text-base",
  };

  const baseStyle = {
    fontFamily: "monospace",
    border: `1px solid`,
    borderRadius: "0.375rem",
    cursor: "pointer",
    transition: "all 0.2s ease",
  };

  const variants = {
    primary: {
      color: "var(--bg-dark)",
      backgroundColor: "var(--text-green)",
      borderColor: "var(--text-green)",
    },
    secondary: {
      color: "var(--text-green)",
      backgroundColor: "transparent",
      borderColor: "var(--text-green)",
    },
    danger: {
      color: "var(--bg-dark)",
      backgroundColor: "var(--accent-cyan)",
      borderColor: "var(--accent-cyan)",
    },
  };

  return (
    <button
      {...props}
      disabled={loading || disabled}
      className={`${sizeClasses[size]} ${props.className || ""}`}
      style={{
        ...baseStyle,
        ...variants[variant],
        opacity: loading || disabled ? 0.5 : 1,
      }}
    >
      {loading ? "..." : children}
    </button>
  );
}

interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export function Input({ label, error, ...props }: InputProps) {
  return (
    <div className="space-y-1">
      {label && (
        <label
          className="block text-sm"
          style={{ color: "var(--text-green)" }}
        >
          {label}:
        </label>
      )}
      <input
        {...props}
        className="w-full px-3 py-2 border rounded text-sm font-mono"
        style={{
          borderColor: error ? "var(--accent-cyan)" : "var(--text-green-subtle)",
          backgroundColor: "var(--bg-darker)",
          color: "var(--text-green)",
        }}
      />
      {error && (
        <p
          className="text-xs"
          style={{ color: "var(--accent-cyan)" }}
        >
          error: {error}
        </p>
      )}
    </div>
  );
}
