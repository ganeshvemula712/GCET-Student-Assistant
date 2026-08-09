import { Sparkles, GraduationCap, BookOpen, Briefcase, Cpu, Brain, ArrowRight } from "lucide-react";
import { motion } from "framer-motion";

const promptSuggestions = [
  {
    icon: GraduationCap,
    title: "Attendance Requirements",
    prompt: "What are the mandatory attendance requirements at GCET?",
    color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
    category: "GCET RAG",
  },
  {
    icon: Briefcase,
    title: "Placement Criteria",
    prompt: "What are the eligibility criteria for campus placements at GCET?",
    color: "text-cyan-400 bg-cyan-500/10 border-cyan-500/20",
    category: "GCET RAG",
  },
  {
    icon: BookOpen,
    title: "R22 Regulations",
    prompt: "What are the important R22 academic regulations?",
    color: "text-purple-400 bg-purple-500/10 border-purple-500/20",
    category: "GCET RAG",
  },
  {
    icon: Cpu,
    title: "RAG Concepts",
    prompt: "What is Retrieval-Augmented Generation?",
    color: "text-amber-400 bg-amber-500/10 border-amber-500/20",
    category: "General AI",
  },
  {
    icon: Brain,
    title: "LLM Fundamentals",
    prompt: "How does a Large Language Model work?",
    color: "text-pink-400 bg-pink-500/10 border-pink-500/20",
    category: "General AI",
  },
];

export default function WelcomeScreen({ onSelectPrompt }) {
  return (
    <div className="flex h-full flex-col items-center justify-center px-4 py-10 text-center">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        className="max-w-3xl"
      >
        <div className="mx-auto flex size-16 items-center justify-center rounded-3xl bg-gradient-to-br from-emerald-500 to-cyan-500 text-gray-950 shadow-xl">
          <Sparkles size={32} />
        </div>
        <h1 className="mt-5 text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
          Welcome to GCET AI Assistant
        </h1>
        <p className="mt-2.5 text-sm text-gray-400 leading-relaxed max-w-xl mx-auto">
          Your personal academic companion powered by Retrieval-Augmented Generation (RAG). Ask anything about college regulations, attendance, placements, or general AI concepts.
        </p>

        <div className="mt-8 grid gap-3.5 sm:grid-cols-2 lg:grid-cols-3 text-left">
          {promptSuggestions.map((item, idx) => {
            const Icon = item.icon;
            return (
              <motion.button
                key={item.title}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.25, delay: idx * 0.04 }}
                type="button"
                onClick={() => onSelectPrompt?.(item.prompt)}
                className="group relative flex flex-col justify-between rounded-2xl border border-gray-800 bg-[#111827] p-4 shadow-lg transition-all duration-200 hover:-translate-y-0.5 hover:border-emerald-500/40 hover:bg-[#151e30] cursor-pointer"
              >
                <div>
                  <div className="flex items-center justify-between">
                    <div className={`flex size-8 items-center justify-center rounded-xl border ${item.color}`}>
                      <Icon size={16} />
                    </div>
                    <span className="rounded-full bg-white/5 px-2 py-0.5 text-[10px] font-semibold text-gray-400">
                      {item.category}
                    </span>
                  </div>
                  <h3 className="mt-3 text-xs font-bold text-white group-hover:text-emerald-400">
                    {item.title}
                  </h3>
                  <p className="mt-1 text-[11px] text-gray-400 line-clamp-2 leading-snug">
                    "{item.prompt}"
                  </p>
                </div>
                <div className="mt-3 flex items-center justify-end">
                  <ArrowRight size={13} className="text-gray-600 transition-transform duration-200 group-hover:translate-x-1 group-hover:text-emerald-400" />
                </div>
              </motion.button>
            );
          })}
        </div>
      </motion.div>
    </div>
  );
}