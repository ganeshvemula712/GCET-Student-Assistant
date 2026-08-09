import gcetLogoImg from "@/assets/gcet-logo.png";

export default function GcetLogo({
  className = "",
  showText = true,
  title = "GCET Student Assistant",
  subtitle = "AI-Powered Academic Workspace",
}) {
  return (
    <div className={`inline-flex items-center gap-3.5 ${className}`}>
      {/* Official Transparent GCET Circular Emblem Logo Asset */}
      <img
        src={gcetLogoImg}
        alt="GCET Logo"
        className="h-11 w-11 shrink-0 drop-shadow-[0_0_12px_rgba(99,102,241,0.35)] object-contain"
      />

      {showText && (
        <div className="flex flex-col leading-tight">
          <span className="text-xl sm:text-2xl font-extrabold tracking-tight text-white">
            {title}
          </span>
          {subtitle && (
            <span className="text-xs font-semibold text-cyan-400 tracking-wide mt-0.5">
              {subtitle}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
