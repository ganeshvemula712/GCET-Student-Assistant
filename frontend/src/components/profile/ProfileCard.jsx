import { Mail, GraduationCap, Calendar } from "lucide-react";

export default function ProfileCard({ profile }) {
  const name = profile?.name || "Student User";
  const email = profile?.email || "student@gcet.edu.in";
  const role = (profile?.role || "Student").toUpperCase();
  const initials = name.charAt(0).toUpperCase();

  const memberSince = profile?.created_at
    ? new Date(profile.created_at).toLocaleDateString([], { month: "short", year: "numeric" })
    : "Aug 2026";

  return (
    <div className="relative overflow-hidden rounded-3xl border border-gray-800 bg-[#111827] p-6 shadow-xl backdrop-blur-xl sm:p-8">
      {/* Background Subtle Radial Glow */}
      <div className="absolute -right-16 -top-16 size-64 rounded-full bg-indigo-500/10 blur-3xl" />

      <div className="relative z-10 flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-5">
          {/* Avatar Icon */}
          <div className="relative flex size-20 shrink-0 items-center justify-center rounded-3xl bg-gradient-to-br from-indigo-500 via-teal-500 to-cyan-500 text-3xl font-extrabold text-gray-950 shadow-xl shadow-indigo-500/20">
            {initials}
            <span className="absolute -bottom-1 -right-1 size-4 rounded-full border-2 border-[#111827] bg-emerald-400" />
          </div>

          <div>
            <div className="flex items-center gap-2.5">
              <h2 className="text-2xl font-bold tracking-tight text-white">{name}</h2>
              <span className="rounded-full bg-indigo-500/10 border border-indigo-500/20 px-2.5 py-0.5 text-[10px] font-bold text-indigo-400">
                {role}
              </span>
            </div>
            <div className="mt-1 flex items-center gap-1.5 text-xs text-gray-400">
              <Mail size={13} className="text-cyan-400" />
              <span>{email}</span>
            </div>
          </div>
        </div>

        {/* Member metadata badges */}
        <div className="flex flex-wrap items-center gap-3 sm:justify-end">
          <div className="flex items-center gap-2 rounded-2xl border border-gray-800 bg-gray-900/60 px-3.5 py-2 text-xs">
            <GraduationCap size={15} className="text-indigo-400" />
            <div>
              <p className="text-[10px] text-gray-500">Department</p>
              <p className="font-semibold text-white">CSE • R22</p>
            </div>
          </div>

          <div className="flex items-center gap-2 rounded-2xl border border-gray-800 bg-gray-900/60 px-3.5 py-2 text-xs">
            <Calendar size={15} className="text-cyan-400" />
            <div>
              <p className="text-[10px] text-gray-500">Joined</p>
              <p className="font-semibold text-white">{memberSince}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}