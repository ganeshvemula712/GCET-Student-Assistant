import { Eye, EyeOff } from "lucide-react";
import { useId, useState } from "react";

export default function AuthField({
  label,
  error,
  type = "text",
  className = "",
  id: customId,
  ...props
}) {
  const [visible, setVisible] = useState(false);
  const autoId = useId();
  const fieldId = customId || props.name || autoId;
  const errorId = `${fieldId}-error`;
  const isPassword = type === "password";
  const inputType = isPassword && visible ? "text" : type;

  return (
    <div className={`block ${className}`}>
      {label && (
        <label htmlFor={fieldId} className="mb-2 block text-sm font-semibold text-gray-200">
          {label}
        </label>
      )}
      <span className="relative block">
        <input
          id={fieldId}
          type={inputType}
          aria-invalid={Boolean(error)}
          aria-describedby={error ? errorId : undefined}
          className="h-12 w-full rounded-2xl border border-gray-800 bg-[#0b1020]/95 px-4.5 text-base text-white outline-none transition duration-200 placeholder:text-gray-400 focus:border-indigo-500/70 focus:ring-2 focus:ring-indigo-500/25 aria-invalid:border-rose-500/60 aria-invalid:ring-rose-500/20"
          {...props}
        />
        {isPassword && (
          <button
            type="button"
            aria-label={visible ? "Hide password" : "Show password"}
            onClick={() => setVisible((current) => !current)}
            className="absolute inset-y-0 right-0 flex w-12 items-center justify-center text-gray-400 transition hover:text-white"
          >
            {visible ? <EyeOff size={19} /> : <Eye size={19} />}
          </button>
        )}
      </span>
      {error && (
        <span id={errorId} className="mt-1.5 block text-xs font-medium text-rose-400">
          {error.message}
        </span>
      )}
    </div>
  );
}
