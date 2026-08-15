import gcetLogoImg from "@/assets/gcet-logo.png";

export default function GcetLogo({
  className = "",
  showText = true,
  title = "GCET AI",
  subtitle = "Assistant",
}) {
  return (
    <div className={`inline-flex items-center gap-3.5 ${className}`}>
      {/* Official GCET Circular Emblem Logo Asset */}
      <img
        src={gcetLogoImg}
        alt="GCET Logo"
        className="h-10 w-10 sm:h-11 sm:w-11 shrink-0 drop-shadow-[0_0_14px_rgba(99,102,241,0.4)] object-contain"
      />

      {showText && (
        <div className="flex flex-col leading-tight">
          <span className="text-xl sm:text-2xl font-black tracking-tight text-white">
            {title}
          </span>
          {subtitle && (
            <span className="text-xs sm:text-sm font-extrabold text-indigo-400 tracking-wider">
              {subtitle}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
