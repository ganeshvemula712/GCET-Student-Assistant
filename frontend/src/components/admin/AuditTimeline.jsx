import { LogIn, FileUp, Trash2, Shield } from "lucide-react";

export default function AuditTimeline() {
  const auditLogs = [
    {
      id: 1,
      action: "Admin User Role Granted",
      description: "User 'admin@gcet.edu.in' promoted student account permissions.",
      timestamp: "10 minutes ago",
      icon: Shield,
      color: "text-purple-400 bg-purple-500/10 border-purple-500/20",
    },
    {
      id: 2,
      action: "Document Vector Ingestion",
      description: "Uploaded file 'R22_Attendance_Policy.pdf' (48 chunks indexed in ChromaDB).",
      timestamp: "1 hour ago",
      icon: FileUp,
      color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
    },
    {
      id: 3,
      action: "Student Session Login",
      description: "Successful JWT bearer authentication for user 'student@gcet.edu.in'.",
      timestamp: "2 hours ago",
      icon: LogIn,
      color: "text-cyan-400 bg-cyan-500/10 border-cyan-500/20",
    },
    {
      id: 4,
      action: "Conversation Archived",
      description: "User cleared thread session history ID #94102.",
      timestamp: "Yesterday at 16:42",
      icon: Trash2,
      color: "text-amber-400 bg-amber-500/10 border-amber-500/20",
    },
  ];

  return (
    <div className="rounded-3xl border border-gray-800 bg-[#111827] p-6 shadow-xl space-y-6">
      <div className="flex items-center justify-between border-b border-gray-800 pb-4">
        <div>
          <h3 className="text-base font-bold text-white">System Audit & Security Logs</h3>
          <p className="text-xs text-gray-400">Chronological trail of administrative actions, user logins, and database events.</p>
        </div>
        <span className="text-xs text-gray-500">Real-time Stream</span>
      </div>

      <div className="relative border-l border-gray-800 ml-4 space-y-6">
        {auditLogs.map((log) => {
          const Icon = log.icon;
          return (
            <div key={log.id} className="relative pl-6">
              {/* Dot Icon */}
              <div className={`absolute -left-4 top-0.5 flex size-8 items-center justify-center rounded-xl border ${log.color}`}>
                <Icon size={14} />
              </div>

              <div>
                <div className="flex items-center gap-2">
                  <p className="text-xs font-bold text-white">{log.action}</p>
                  <span className="text-[10px] text-gray-500">• {log.timestamp}</span>
                </div>
                <p className="mt-1 text-xs text-gray-400">{log.description}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
