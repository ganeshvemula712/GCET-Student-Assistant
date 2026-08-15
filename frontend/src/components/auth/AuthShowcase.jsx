import {
  Bot,
  FolderKanban,
  BookOpen,
  BarChart3,
  ShieldCheck,
  Bell,
  Target,
  Sparkles,
} from "lucide-react";
import GcetLogo from "@/components/common/GcetLogo";

const features = [
  {
    icon: Bot,
    title: "AI Study Companion",
  },
  {
    icon: FolderKanban,
    title: "Document Management",
  },
  {
    icon: BookOpen,
    title: "Knowledge Base",
  },
  {
    icon: BarChart3,
    title: "Academic Analytics",
  },
  {
    icon: ShieldCheck,
    title: "Secure & Private",
  },
  {
    icon: Bell,
    title: "Smart Notifications",
  },
];

export default function AuthShowcase() {
  return (
    <section className="hidden w-full flex-col justify-center space-y-6 lg:flex pr-2 xl:pr-4 min-w-0">
      {/* 1. GCET Branding Header */}
      <div>
        <GcetLogo showText={true} />
      </div>

      {/* 2. Main Hero Heading & Concise Description */}
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 rounded-full border border-indigo-500/30 bg-indigo-500/10 px-3.5 py-1.5 text-xs font-bold text-indigo-300 backdrop-blur-md">
          <Sparkles size={14} className="text-cyan-400" />
          <span>Official Academic AI Platform</span>
        </div>
        <h1 className="text-3xl font-black tracking-tight sm:text-4xl lg:text-4xl xl:text-5xl leading-[1.15] text-white">
          Your College. <br />
          <span className="bg-gradient-to-r from-indigo-400 via-cyan-400 to-teal-300 bg-clip-text text-transparent">
            Your Questions.
          </span> <br />
          Smarter Answers.
        </h1>
        <p className="text-sm leading-relaxed text-gray-300 max-w-xl">
          GCET AI Assistant is an AI-powered platform designed to help you learn smarter, stay organized, and achieve more. Get instant answers, access verified academic resources, and manage your studies — all in one secure workspace.
        </p>
      </div>

      {/* 3. 6 Compact Feature Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 pt-1">
        {features.map(({ icon: Icon, title }) => (
          <div
            key={title}
            className="group rounded-2xl border border-gray-800/80 bg-[#111827]/80 p-3 backdrop-blur-md transition-all duration-200 hover:border-indigo-500/40 hover:bg-[#151e32] flex items-center gap-2.5 min-w-0"
          >
            <div className="flex size-8 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500/20 to-cyan-500/20 text-cyan-300 border border-cyan-500/20 group-hover:scale-105 transition-transform shrink-0">
              <Icon size={16} />
            </div>
            <h3 className="text-xs font-bold text-white leading-snug truncate">{title}</h3>
          </div>
        ))}
      </div>

      {/* 4. Compact Our Aim Panel */}
      <div className="rounded-2xl border border-indigo-500/20 bg-indigo-500/10 p-4 shadow-lg backdrop-blur-md">
        <div className="flex items-center gap-2 text-xs font-bold text-indigo-300">
          <Target size={15} className="text-cyan-400 shrink-0" />
          <span>Our Aim</span>
        </div>
        <p className="mt-1 text-xs leading-relaxed text-indigo-100/90">
          To empower GCET students with an AI-driven platform that simplifies access to academic information, enhances learning, and supports success throughout their engineering journey.
        </p>
      </div>
    </section>
  );
}
