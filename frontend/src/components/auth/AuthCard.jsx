import { ShieldCheck } from "lucide-react";
import { motion } from "framer-motion";

export default function AuthCard({ title, description, children, footer }) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.28, ease: "easeOut" }}
      className="w-full max-w-[460px] rounded-3xl border border-gray-800 bg-[#111827]/95 p-7 shadow-2xl backdrop-blur-xl sm:p-9 lg:ml-auto"
    >
      <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-indigo-500/20 bg-indigo-500/10 px-3.5 py-1.5 text-xs font-semibold text-indigo-300">
        <ShieldCheck size={15} className="text-cyan-400" /> Secure Student Workspace
      </div>
      <h1 className="text-2xl font-extrabold tracking-tight text-white sm:text-3xl">{title}</h1>
      <p className="mt-2 text-sm leading-relaxed text-gray-400">{description}</p>
      <div className="mt-7">{children}</div>
      {footer && <div className="mt-6 text-center text-sm text-gray-400">{footer}</div>}
    </motion.section>
  );
}
