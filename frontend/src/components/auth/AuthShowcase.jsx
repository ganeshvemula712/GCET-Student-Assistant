import {
  BookOpen,
  Zap,
  ShieldCheck,
  BarChart3,
  FileText,
  MessageSquareText,
  Target,
  Sparkles,
} from "lucide-react";
import GcetLogo from "@/components/common/GcetLogo";

const features = [
  {
    icon: BookOpen,
    title: "Academic Support",
    description: "Get clear answers about courses, regulations, syllabus, examinations, attendance, and academic procedures.",
    color: "bg-indigo-600/20 text-indigo-400 border-indigo-500/30",
  },
  {
    icon: Zap,
    title: "Smart & Reliable",
    description: "AI-powered responses grounded in the GCET knowledge base and official academic documents.",
    color: "bg-amber-500/20 text-amber-400 border-amber-500/30",
  },
  {
    icon: ShieldCheck,
    title: "Secure & Private",
    description: "Student information and conversations are handled through a secure authenticated workspace.",
    color: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
  },
  {
    icon: BarChart3,
    title: "Campus Information",
    description: "Access relevant information about placements, notices, campus resources, and student activities.",
    color: "bg-blue-500/20 text-blue-400 border-blue-500/30",
  },
  {
    icon: FileText,
    title: "Document Insights",
    description: "Understand important academic documents and institutional resources through AI-powered assistance.",
    color: "bg-pink-500/20 text-pink-400 border-pink-500/30",
  },
  {
    icon: MessageSquareText,
    title: "Smart Assistance",
    description: "Ask questions naturally and receive useful, context-aware answers from the available GCET knowledge base.",
    color: "bg-purple-500/20 text-purple-400 border-purple-500/30",
  },
];

export default function AuthShowcase() {
  return (
    <section className="hidden w-full flex-col justify-center space-y-6 lg:flex pr-2 xl:pr-4 min-w-0">
      {/* GCET Branding Header */}
      <div>
        <GcetLogo showText={true} />
      </div>

      {/* Main Hero Heading & Description */}
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 rounded-full border border-indigo-500/30 bg-indigo-500/10 px-3.5 py-1.5 text-xs font-bold text-indigo-300">
          <Sparkles size={14} className="text-cyan-400 shrink-0" />
          <span>Official Academic AI Platform</span>
        </div>
        <h1 className="text-3xl font-black tracking-tight sm:text-4xl lg:text-4xl xl:text-5xl leading-[1.15] text-white">
          Your College. <br />
          <span className="bg-gradient-to-r from-indigo-400 via-cyan-400 to-teal-300 bg-clip-text text-transparent">
            Your Questions.
          </span> <br />
          <span className="bg-gradient-to-r from-cyan-400 via-indigo-300 to-purple-400 bg-clip-text text-transparent">
            Smarter Answers.
          </span>
        </h1>
        <p className="text-xs sm:text-sm leading-relaxed text-gray-300 max-w-xl">
          GCET AI Assistant is an AI-powered academic companion designed to help GCET students access trusted information, understand academic resources, and get answers from verified institutional knowledge.
        </p>
      </div>

      {/* 6 Feature Cards (3 columns x 2 rows on desktop) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {features.map(({ icon: Icon, title, description, color }) => (
          <div
            key={title}
            className="group rounded-2xl border border-gray-800/80 bg-[#0B1120]/80 p-3.5 backdrop-blur-md transition-all duration-200 hover:border-indigo-500/40 hover:bg-[#111827] flex flex-col justify-between min-w-0"
          >
            <div className={`flex size-9 items-center justify-center rounded-xl border ${color} mb-2.5 group-hover:scale-105 transition-transform shrink-0`}>
              <Icon size={18} />
            </div>
            <div>
              <h3 className="text-xs font-bold text-white leading-snug">{title}</h3>
              <p className="text-[11px] text-gray-400 mt-1 leading-tight line-clamp-3">{description}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Our Aim Panel */}
      <div className="rounded-2xl border border-gray-800/80 bg-[#0B1120]/80 p-4 backdrop-blur-md">
        <div className="flex items-center gap-2 text-xs font-bold text-indigo-400">
          <Target size={16} className="text-cyan-400 shrink-0" />
          <span>Our Aim</span>
        </div>
        <p className="mt-1.5 text-xs leading-relaxed text-gray-300 font-medium">
          To provide GCET students with a reliable AI-powered academic assistant that simplifies access to institutional knowledge, improves learning, and supports informed academic decisions.
        </p>
      </div>
    </section>
  );
}
