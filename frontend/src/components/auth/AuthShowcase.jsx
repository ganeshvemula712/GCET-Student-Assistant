import {
  Bot,
  FolderKanban,
  BookOpen,
  BarChart3,
  ShieldCheck,
  Bell,
  Target,
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
    <section className="hidden w-full flex-col justify-center space-y-5 lg:flex pr-2 xl:pr-4">
      {/* 1. GCET Branding Header */}
      <div>
        <GcetLogo showText={true} />
      </div>

      {/* 2. Main Hero Heading & Concise Description */}
      <div className="space-y-2.5">
        <h1 className="text-3xl font-extrabold tracking-tight sm:text-4xl lg:text-4xl xl:text-5xl leading-[1.15] bg-gradient-to-r from-white via-indigo-100 to-cyan-200 bg-clip-text text-transparent">
          Your Intelligent Academic Companion
        </h1>
        <p className="text-sm leading-relaxed text-gray-300 max-w-xl">
          GCET Student Assistant is an AI-powered platform designed to help you learn smarter, stay organized, and achieve more. Get instant answers, access verified academic resources, and manage your studies — all in one secure workspace.
        </p>
      </div>

      {/* 3. 6 Compact Feature Cards (3 columns x 2 rows on desktop) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 pt-1">
        {features.map(({ icon: Icon, title }) => (
          <div
            key={title}
            className="group rounded-2xl border border-gray-800/80 bg-[#111827]/80 p-3 backdrop-blur-md transition-all duration-200 hover:border-indigo-500/40 hover:bg-[#151e32] flex items-center gap-2.5"
          >
            <div className="flex size-8 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500/20 to-cyan-500/20 text-cyan-300 border border-cyan-500/20 group-hover:scale-105 transition-transform shrink-0">
              <Icon size={16} />
            </div>
            <h3 className="text-xs font-bold text-white leading-snug">{title}</h3>
          </div>
        ))}
      </div>

      {/* 4. Compact Our Aim Panel */}
      <div className="rounded-2xl border border-indigo-500/20 bg-indigo-500/10 p-3.5 shadow-lg backdrop-blur-md">
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
