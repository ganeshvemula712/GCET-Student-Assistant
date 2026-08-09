import { useState } from "react";
import { Search, Shield, User, ChevronLeft, ChevronRight, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";

import useAdminUsers from "@/hooks/useAdminUsers";
import useUpdateUserRole from "@/hooks/useUpdateUserRole";

export default function UserTable() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("");

  const { data, isLoading, isError } = useAdminUsers({
    page,
    limit: 8,
    search,
    role: roleFilter,
  });

  const updateRoleMutation = useUpdateUserRole();

  const handleRoleToggle = async (userId, currentRole) => {
    const newRole = currentRole === "admin" ? "student" : "admin";
    try {
      await updateRoleMutation.mutateAsync({ userId, role: newRole });
      toast.success(`User role updated to ${newRole.toUpperCase()}`);
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Unable to change user role.");
    }
  };

  const users = data?.items || [];
  const totalPages = data?.total_pages || 1;

  return (
    <div className="space-y-4 rounded-3xl border border-gray-800 bg-[#111827] p-6 shadow-xl">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="text-base font-bold text-white">Registered Users ({data?.total || 0})</h3>
          <p className="text-xs text-gray-400">Manage student access permissions and administrator privileges.</p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Search bar */}
          <div className="relative">
            <Search size={15} className="absolute left-3 top-3 text-gray-500" />
            <input
              type="text"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              placeholder="Search by name or email..."
              className="h-10 rounded-2xl border border-gray-800 bg-[#0b1020] pl-9 pr-4 text-xs text-white outline-none transition focus:border-indigo-500/60"
            />
          </div>

          {/* Role Filter */}
          <select
            value={roleFilter}
            onChange={(e) => {
              setRoleFilter(e.target.value);
              setPage(1);
            }}
            className="h-10 rounded-2xl border border-gray-800 bg-[#0b1020] px-3 text-xs text-white outline-none"
          >
            <option value="">All Roles</option>
            <option value="student">Students Only</option>
            <option value="admin">Admins Only</option>
          </select>
        </div>
      </div>

      {isLoading ? (
        <div className="py-12 text-center text-xs text-gray-400 animate-pulse">Loading users list...</div>
      ) : isError ? (
        <div className="py-8 text-center text-xs text-rose-400">Failed to load user accounts.</div>
      ) : users.length === 0 ? (
        <div className="py-12 text-center text-xs text-gray-400">No users found matching filter criteria.</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-gray-800 text-gray-400">
              <tr>
                <th className="pb-3 pt-2 font-semibold">User Details</th>
                <th className="pb-3 pt-2 font-semibold">Role</th>
                <th className="pb-3 pt-2 font-semibold">Department</th>
                <th className="pb-3 pt-2 font-semibold">Status</th>
                <th className="pb-3 pt-2 font-semibold">Joined Date</th>
                <th className="pb-3 pt-2 text-right font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60">
              {users.map((user) => {
                const isAdmin = user.role === "admin";
                const initials = user.name?.charAt(0)?.toUpperCase() || "U";
                const joinedDate = user.created_at
                  ? new Date(user.created_at).toLocaleDateString([], { month: "short", day: "numeric", year: "numeric" })
                  : "N/A";

                return (
                  <tr key={user.id} className="hover:bg-gray-900/40">
                    <td className="py-3">
                      <div className="flex items-center gap-3">
                        <div className="flex size-9 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 to-cyan-500 text-xs font-bold text-gray-950">
                          {initials}
                        </div>
                        <div>
                          <p className="font-semibold text-white">{user.name}</p>
                          <p className="text-[11px] text-gray-400">{user.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-3">
                      <span
                        className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[10px] font-bold ${
                          isAdmin
                            ? "bg-purple-500/10 text-purple-300 border border-purple-500/20"
                            : "bg-indigo-500/10 text-indigo-300 border border-indigo-500/20"
                        }`}
                      >
                        {isAdmin ? <Shield size={11} /> : <User size={11} />}
                        {user.role?.toUpperCase() || "STUDENT"}
                      </span>
                    </td>
                    <td className="py-3 text-gray-300">CSE • R22</td>
                    <td className="py-3">
                      <span className="inline-flex items-center gap-1 text-emerald-400 font-semibold text-[11px]">
                        <CheckCircle2 size={12} /> Active
                      </span>
                    </td>
                    <td className="py-3 text-gray-400">{joinedDate}</td>
                    <td className="py-3 text-right">
                      <button
                        onClick={() => handleRoleToggle(user.id, user.role)}
                        disabled={updateRoleMutation.isPending}
                        className="rounded-xl border border-gray-800 bg-gray-900 px-3 py-1.5 text-[11px] font-semibold text-gray-300 transition hover:border-indigo-500 hover:text-white disabled:opacity-50"
                      >
                        {isAdmin ? "Make Student" : "Promote Admin"}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination Footer */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between border-t border-gray-800 pt-4 text-xs text-gray-400">
          <span>Page {page} of {totalPages}</span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="flex size-8 items-center justify-center rounded-xl border border-gray-800 bg-gray-900 text-gray-300 hover:bg-gray-800 disabled:opacity-40"
            >
              <ChevronLeft size={16} />
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="flex size-8 items-center justify-center rounded-xl border border-gray-800 bg-gray-900 text-gray-300 hover:bg-gray-800 disabled:opacity-40"
            >
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
