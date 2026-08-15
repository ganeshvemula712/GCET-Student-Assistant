import {
  BookOpen,
  Zap,
  ShieldCheck,
  BarChart3,
  FileText,
  Bell,
  Target,
  Sparkles,
} from "lucide-react";
import GcetLogo from "@/components/common/GcetLogo";

const features = [
  {
    icon: BookOpen,
    title: "Academic Support",
    description: "Get instant answers about courses, rules, syllabus, and more.",
    color: "bg-indigo-600/30 text-indigo-300 border-indigo-500/30",
  },
  {
    icon: Zap,
    title: "Smart & Reliable",
    description: "AI-powered responses based on official college resources.",
    color: "bg-amber-500/30 text-amber-300 border-amber-500/30",
  },
  {
    icon: ShieldCheck,
    title: "Secure & Private",
    description: "Your data is safe and confidential. Always.",
    color: "bg-emerald-500/30 text-emerald-300 border-emerald-500/30",
  },
  {
    icon: BarChart3,
    title: "Campus Information",
    description: "Access placements, events, notices, and important announcements.",
    color: "bg-blue-500/30 text-blue-300 border-blue-500/30",
  },
  {
    icon: FileText,
    title: "Document Insights",
    description: "Explore and understand official documents with AI.",
    color: "bg-pink-500/30 text-pink-300 border-pink-500/30",
  },
  {
    icon: Bell,
    title: "Smart Notifications",
    description: "Never miss important updates and deadlines.",
    color: "bg-orange-500/30 text-orange-300 border-orange-500/30",
  },
];

export default function AuthShowcase() {
  return (
    <section className="hidden w-full flex-col justify-center space-y-5 lg:flex pr-2 xl:pr-4 min-w-0 relative z-10">
      {/* 1. GCET Branding Header */}
      <div>
        <GcetLogo showText={true} />
      </div>

      {/* 2. Main Hero Heading & Description */}
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 rounded-full border border-indigo-500/40 bg-[#0B1120]/80 px-3.5 py-1.5 text-xs font-bold text-indigo-300 backdrop-blur-md shadow-md">
          <Sparkles size={14} className="text-cyan-400 shrink-0" />
          <span>Official Academic AI Platform</span>
        </div>
        <h1 className="text-3xl font-black tracking-tight sm:text-4xl lg:text-4xl xl:text-5xl leading-[1.15] text-white drop-shadow-[0_2px_10px_rgba(0,0,0,0.9)]">
          Your College. <br />
          <span className="bg-gradient-to-r from-indigo-300 via-cyan-300 to-teal-200 bg-clip-text text-transparent">
            Your Questions.
          </span> <br />
          <span className="bg-gradient-to-r from-cyan-300 via-indigo-200 to-purple-300 bg-clip-text text-transparent">
            Smarter Answers.
          </span>
        </h1>
        <p className="text-xs sm:text-sm leading-relaxed text-gray-200 max-w-xl font-medium drop-shadow-[0_1px_4px_rgba(0,0,0,0.9)]">
          GCET AI Assistant is your AI-powered companion for academics, resources, and campus information. Get instant answers, access verified knowledge, and manage your studies — all in one secure workspace.
        </p>
      </div>

      {/* 3. 6 Feature Cards (3 columns x 2 rows on desktop) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 pt-1">
        {features.map(({ icon: Icon, title, description, color }) => (
          <div
            key={title}
            className="group rounded-2xl border border-gray-800/80 bg-[#0B1120]/80 p-3 backdrop-blur-md transition-all duration-200 hover:border-indigo-500/50 hover:bg-[#111827]/90 flex items-start gap-3 min-w-0"
          >
            <div className={`flex size-9 items-center justify-center rounded-2xl border ${color} group-hover:scale-105 transition-transform shrink-0 shadow-inner`}>
              <Icon size={18} />
            </div>
            <div className="min-w-0">
              <h3 className="text-xs font-bold text-white leading-snug truncate">{title}</h3>
              <p className="text-[11px] text-gray-400 mt-0.5 leading-tight line-clamp-2">{description}</p>
            </div>
          </div>
        ))}
      </div>

      {/* 4. Compact Our Aim Panel */}
      <div className="rounded-2xl border border-indigo-500/30 bg-[#0D1527]/85 p-3.5 shadow-lg backdrop-blur-md">
        <div className="flex items-center gap-2 text-xs font-bold text-indigo-300">
          <div className="flex size-6 items-center justify-center rounded-lg bg-indigo-500/20 text-cyan-400 border border-indigo-500/30">
            <Target size={14} className="shrink-0" />
          </div>
          <span>Our Aim</span>
        </div>
        <p className="mt-1.5 text-xs leading-relaxed text-indigo-100/90 font-medium">
          To empower GCET students with an AI-driven platform that simplifies access to academic information, enhances learning, and supports success throughout their engineering journey.
        </p>
      </div>
    </section>
  );
}
