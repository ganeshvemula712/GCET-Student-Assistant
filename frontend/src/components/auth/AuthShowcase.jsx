import { BookOpen, Zap, ShieldCheck, Quote, Sparkles } from "lucide-react";

export default function AuthShowcase() {
  const cards = [
    {
      icon: BookOpen,
      title: "Academic Guidance",
      description: "Instant answers on syllabus, rules, and course regulations.",
      color: "bg-indigo-600/30 text-indigo-400 border-indigo-500/30",
    },
    {
      icon: Zap,
      title: "Smart & Reliable",
      description: "Verified AI responses grounded in official GCET resources.",
      color: "bg-amber-500/30 text-amber-400 border-amber-500/30",
    },
    {
      icon: ShieldCheck,
      title: "Secure & Confidential",
      description: "Student data privacy and protected academic workspace.",
      color: "bg-emerald-500/30 text-emerald-400 border-emerald-500/30",
    },
  ];

  return (
    <section className="flex w-full flex-col justify-center space-y-6 min-w-0 relative z-10">
      {/* Sleek Professional Hero Container without background image */}
      <div className="relative min-h-[300px] lg:min-h-[340px] flex flex-col justify-between overflow-hidden rounded-3xl border border-indigo-500/25 bg-gradient-to-br from-[#080E22] via-[#0C1530] to-[#080E22] p-6 lg:p-8 shadow-2xl">
        {/* Ambient Decorative Tech Glows & Grid Accent */}
        <div className="absolute -top-20 -right-20 size-72 bg-indigo-600/15 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-20 -left-20 size-72 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />

        {/* Background Dot Pattern Overlay */}
        <div className="absolute top-6 right-6 opacity-20 pointer-events-none">
          <div className="grid grid-cols-6 gap-2">
            {Array.from({ length: 36 }).map((_, i) => (
              <div key={i} className="size-1 rounded-full bg-indigo-300" />
            ))}
          </div>
        </div>

        {/* Top Badge */}
        <div className="relative z-10 inline-flex items-center gap-2 rounded-full border border-indigo-500/35 bg-indigo-500/10 px-3.5 py-1.5 text-xs font-bold text-indigo-300 backdrop-blur-md w-fit">
          <Sparkles size={14} className="text-amber-400 shrink-0" />
          <span>Official AI Academic Assistant</span>
        </div>

        {/* Hero Text Content */}
        <div className="relative z-10 max-w-xl space-y-3.5 my-auto pt-2">
          <h1 className="text-3xl font-black tracking-tight sm:text-4xl lg:text-4xl xl:text-5xl leading-[1.15] text-white">
            Your College. <br />
            Your Questions. <br />
            <span className="text-amber-400 drop-shadow-[0_2px_10px_rgba(245,158,11,0.3)]">
              Smarter Answers.
            </span>
          </h1>

          <p className="text-xs sm:text-sm leading-relaxed text-gray-300 font-medium max-w-lg">
            GCET Student Assistant is your official AI companion for academic guidance, course syllabus, exam regulations, and campus insights — powered by verified institutional knowledge.
          </p>
        </div>
      </div>

      {/* 3 Support Feature Cards in a Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {cards.map(({ icon: Icon, title, description, color }) => (
          <div
            key={title}
            className="rounded-2xl border border-gray-800/70 bg-[#0A1022]/90 p-4 shadow-lg backdrop-blur-md transition-all duration-200 hover:border-indigo-500/40 flex flex-col justify-between min-w-0"
          >
            <div className={`flex size-10 items-center justify-center rounded-2xl border ${color} mb-3 shadow-inner`}>
              <Icon size={20} />
            </div>
            <div>
              <h3 className="text-xs font-bold text-white leading-snug">{title}</h3>
              <p className="text-[11px] text-gray-400 mt-1 leading-tight">{description}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Bottom Quote Panel */}
      <div className="relative overflow-hidden rounded-2xl border border-indigo-500/30 bg-gradient-to-r from-indigo-950/40 via-[#0B1124] to-[#0A1022] p-4.5 shadow-lg backdrop-blur-md flex items-center justify-between">
        <div className="flex items-center gap-3 relative z-10">
          <div className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-amber-500/20 text-amber-400 border border-amber-500/30">
            <Quote size={18} />
          </div>
          <p className="text-xs font-semibold italic text-gray-300 leading-snug">
            "Empowering GCET engineering students with intelligent academic guidance."
          </p>
        </div>

        {/* Right Dot Grid Decorative Pattern */}
        <div className="hidden sm:flex opacity-20 gap-1.5 shrink-0 pl-4">
          <div className="grid grid-cols-4 gap-1.5">
            {Array.from({ length: 16 }).map((_, i) => (
              <div key={i} className="size-1 rounded-full bg-indigo-400" />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
