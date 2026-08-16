import {
  BookOpen,
  Zap,
  ShieldCheck,
  BarChart3,
  FileText,
  Sparkles,
  Lock,
  GraduationCap,
  Users,
} from "lucide-react";
import GcetLogo from "@/components/common/GcetLogo";

const cards = [
  {
    icon: BookOpen,
    title: "Academic Help",
    description: "Get answers about courses, syllabus, regulations, examinations, attendance, and more.",
    color: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  },
  {
    icon: FileText,
    title: "Document Insights",
    description: "Find information from official documents, timetables, notices, circulars, and academic resources.",
    color: "bg-purple-500/10 text-purple-400 border-purple-500/20",
  },
  {
    icon: BarChart3,
    title: "Smart Assistance",
    description: "Ask questions in natural language and receive accurate, easy-to-understand answers.",
    color: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  },
  {
    icon: GraduationCap,
    title: "Campus Information",
    description: "Access placement updates, events, announcements, and important student information.",
    color: "bg-teal-500/10 text-teal-400 border-teal-500/20",
  },
  {
    icon: Users,
    title: "Admin Managed",
    description: "All content is managed by the administration to ensure accuracy and reliability.",
    color: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  },
  {
    icon: Sparkles,
    title: "AI-Powered",
    description: "Advanced retrieval-augmented AI (RAG) ensures answers with sources you can trust.",
    color: "bg-indigo-500/10 text-indigo-400 border-indigo-500/20",
  },
];

export default function AuthShowcase() {
  return (
    <section className="hidden w-full flex-col justify-center space-y-5 lg:flex pr-2 xl:pr-4 min-w-0">
      {/* GCET Branding Header */}
      <div>
        <GcetLogo showText={true} />
      </div>

      {/* Main Hero Heading & Description */}
      <div className="space-y-2.5">
        <div className="inline-flex items-center gap-2 rounded-full border border-indigo-500/30 bg-indigo-500/10 px-3.5 py-1 text-xs font-semibold text-indigo-300">
          <Sparkles size={14} className="text-cyan-400 shrink-0" />
          <span>Official Academic AI Platform</span>
        </div>
        <h1 className="text-3xl font-black tracking-tight sm:text-4xl lg:text-4xl xl:text-5xl leading-[1.15] text-white">
          Empowering GCET Students with{" "}
          <span className="bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
            Knowledge, Clarity
          </span>{" "}
          <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-fuchsia-400 bg-clip-text text-transparent">
            and Confidence.
          </span>
        </h1>
        <p className="text-xs sm:text-sm leading-relaxed text-gray-300 max-w-xl">
          GCET AI Assistant is an AI-powered academic companion that helps students access verified institutional information, explore academic resources, and get accurate answers with sources you can trust.
        </p>
      </div>

      {/* 3 Feature Highlights (Pills) */}
      <div className="grid grid-cols-3 gap-3 border-y border-gray-800/80 py-3">
        <div className="flex items-start gap-2.5">
          <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-400">
            <ShieldCheck size={16} />
          </div>
          <div>
            <h4 className="text-xs font-bold text-white">Verified & Trusted</h4>
            <p className="text-[10px] text-gray-400 leading-tight mt-0.5">Answers grounded in official academic documents.</p>
          </div>
        </div>

        <div className="flex items-start gap-2.5">
          <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
            <Zap size={16} />
          </div>
          <div>
            <h4 className="text-xs font-bold text-white">Smart & Intuitive</h4>
            <p className="text-[10px] text-gray-400 leading-tight mt-0.5">Ask naturally. Get context-aware, relevant answers.</p>
          </div>
        </div>

        <div className="flex items-start gap-2.5">
          <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-purple-500/10 border border-purple-500/20 text-purple-400">
            <Lock size={16} />
          </div>
          <div>
            <h4 className="text-xs font-bold text-white">Secure & Private</h4>
            <p className="text-[10px] text-gray-400 leading-tight mt-0.5">Your data and conversations are always protected.</p>
          </div>
        </div>
      </div>

      {/* Section Title: What You Can Do */}
      <div className="flex items-center gap-1.5 text-xs font-bold text-white">
        <span>What You Can Do</span>
        <Sparkles size={14} className="text-purple-400" />
      </div>

      {/* 6 Feature Cards Grid (3 columns x 2 rows) */}
      <div className="grid grid-cols-3 gap-3">
        {cards.map(({ icon: Icon, title, description, color }) => (
          <div
            key={title}
            className="group rounded-2xl border border-gray-800/80 bg-[#0B1120]/80 p-3.5 backdrop-blur-md transition-all duration-200 hover:border-indigo-500/40 hover:bg-[#111827] flex flex-col justify-between min-w-0"
          >
            <div className={`flex size-8 items-center justify-center rounded-xl border ${color} mb-2.5 group-hover:scale-105 transition-transform shrink-0`}>
              <Icon size={16} />
            </div>
            <div>
              <h3 className="text-xs font-bold text-white leading-snug">{title}</h3>
              <p className="text-[11px] text-gray-400 mt-1 leading-normal">{description}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
