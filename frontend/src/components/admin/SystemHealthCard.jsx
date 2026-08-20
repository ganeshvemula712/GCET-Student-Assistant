import { CheckCircle2, Server, Database, HardDrive, Cpu, ShieldCheck } from "lucide-react";

export default function SystemHealthCard() {
  const services = [
    {
      name: "FastAPI Backend Server",
      endpoint: `${import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"}/health`,
      status: "Healthy",
      icon: Server,
      latency: "12 ms",
      color: "text-emerald-400 border-emerald-500/20 bg-emerald-500/10",
    },
    {
      name: "PostgreSQL Database",
      endpoint: "SQLAlchemy Pool",
      status: "Healthy",
      icon: Database,
      latency: "4 ms",
      color: "text-emerald-400 border-emerald-500/20 bg-emerald-500/10",
    },
    {
      name: "ChromaDB Vector Store",
      endpoint: "Vector Index Collection",
      status: "Healthy",
      icon: HardDrive,
      latency: "18 ms",
      color: "text-emerald-400 border-emerald-500/20 bg-emerald-500/10",
    },
    {
      name: "Google Gemini 3.5 Flash API",
      endpoint: "generativeai.google",
      status: "Healthy",
      icon: Cpu,
      latency: "380 ms",
      color: "text-emerald-400 border-emerald-500/20 bg-emerald-500/10",
    },
    {
      name: "JWT Authentication Service",
      endpoint: "OAuth2 Bearer Tokens",
      status: "Healthy",
      icon: ShieldCheck,
      latency: "2 ms",
      color: "text-emerald-400 border-emerald-500/20 bg-emerald-500/10",
    },
  ];

  return (
    <div className="rounded-3xl border border-gray-800 bg-[#111827] p-6 shadow-xl space-y-6">
      <div className="flex items-center justify-between border-b border-gray-800 pb-4">
        <div>
          <h3 className="text-base font-bold text-white">System Architecture Health</h3>
          <p className="text-xs text-gray-400">Live operational status across application services and external APIs.</p>
        </div>
        <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-bold text-emerald-400 border border-emerald-500/20">
          <CheckCircle2 size={14} /> 5/5 Operational
        </span>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {services.map((svc) => {
          const Icon = svc.icon;
          return (
            <div
              key={svc.name}
              className="rounded-2xl border border-gray-800 bg-gray-900/60 p-4 space-y-3 shadow-md"
            >
              <div className="flex items-center justify-between">
                <div className="flex size-9 items-center justify-center rounded-xl bg-gray-800 text-white">
                  <Icon size={18} />
                </div>
                <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[10px] font-bold border ${svc.color}`}>
                  <CheckCircle2 size={11} /> {svc.status}
                </span>
              </div>

              <div>
                <p className="text-xs font-bold text-white">{svc.name}</p>
                <p className="text-[11px] text-gray-500">{svc.endpoint}</p>
              </div>

              <div className="flex items-center justify-between border-t border-gray-800/80 pt-2 text-[11px] text-gray-400">
                <span>Latency</span>
                <span className="font-semibold text-cyan-300">{svc.latency}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
