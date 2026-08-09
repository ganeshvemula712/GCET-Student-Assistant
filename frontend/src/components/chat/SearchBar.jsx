import { Search, X } from "lucide-react";
import { useEffect, useRef } from "react";

export default function SearchBar({ value, onChange, onFocus }) {
  const inputRef = useRef(null);

  useEffect(() => {
    function handleKeyDown(e) {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        inputRef.current?.focus();
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <div className="relative w-full">
      <Search size={16} className="absolute left-3 top-3 text-gray-400" />
      <input
        ref={inputRef}
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onFocus={onFocus}
        placeholder="Search chats (Ctrl+K)..."
        aria-label="Search conversations"
        className="w-full rounded-xl border border-gray-800 bg-[#0f172a] py-2.5 pl-9 pr-14 text-xs text-white placeholder-gray-500 outline-none transition duration-200 focus:border-emerald-500/40 focus:ring-1 focus:ring-emerald-500/30"
      />
      {value ? (
        <button
          type="button"
          onClick={() => onChange("")}
          className="absolute right-3 top-2.5 rounded-lg p-0.5 text-gray-400 hover:text-white"
        >
          <X size={14} />
        </button>
      ) : (
        <span className="absolute right-3 top-2.5 rounded border border-gray-800 bg-gray-900 px-1.5 py-0.5 font-mono text-[10px] text-gray-400">
          ⌘K
        </span>
      )}
    </div>
  );
}