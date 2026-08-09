import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { ShieldCheck, Eye, EyeOff, KeyRound, LoaderCircle } from "lucide-react";

import useChangePassword from "@/hooks/useChangePassword";
import { changePasswordSchema } from "@/schema/profileSchema";

export default function ChangePasswordForm() {
  const mutation = useChangePassword();
  const [showCurrent, setShowCurrent] = useState(false);
  const [showNew, setShowNew] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(changePasswordSchema),
  });

  async function onSubmit(values) {
    try {
      await mutation.mutateAsync({
        current_password: values.current_password,
        new_password: values.new_password,
      });

      toast.success("Password changed successfully.");
      reset();
    } catch (error) {
      toast.error(
        error?.response?.data?.detail ?? "Unable to change password."
      );
    }
  }

  return (
    <div className="rounded-3xl border border-gray-800 bg-[#111827] p-6 shadow-xl sm:p-8">
      <div className="mb-6 flex items-center justify-between border-b border-gray-800/80 pb-4">
        <div>
          <h3 className="text-base font-bold text-white">Security & Password</h3>
          <p className="mt-0.5 text-xs text-gray-400">Update your account password to maintain security.</p>
        </div>
        <div className="flex size-8 items-center justify-center rounded-xl bg-purple-500/10 text-purple-400">
          <KeyRound size={16} />
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5" noValidate>
        <div>
          <label className="mb-2 block text-xs font-semibold text-gray-300">
            Current Password
          </label>
          <div className="relative">
            <input
              type={showCurrent ? "text" : "password"}
              {...register("current_password")}
              className="h-11 w-full rounded-2xl border border-gray-800 bg-[#0b1020] pl-4 pr-11 text-xs text-white outline-none transition focus:border-indigo-500/60 focus:ring-2 focus:ring-indigo-500/20"
              placeholder="Enter current password"
            />
            <button
              type="button"
              onClick={() => setShowCurrent((prev) => !prev)}
              className="absolute right-3 top-3 text-gray-500 hover:text-white"
            >
              {showCurrent ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
          {errors.current_password && (
            <p className="mt-1.5 text-xs font-medium text-rose-400">
              {errors.current_password.message}
            </p>
          )}
        </div>

        <div>
          <label className="mb-2 block text-xs font-semibold text-gray-300">
            New Password
          </label>
          <div className="relative">
            <input
              type={showNew ? "text" : "password"}
              {...register("new_password")}
              className="h-11 w-full rounded-2xl border border-gray-800 bg-[#0b1020] pl-4 pr-11 text-xs text-white outline-none transition focus:border-indigo-500/60 focus:ring-2 focus:ring-indigo-500/20"
              placeholder="Enter new password (min 6 chars)"
            />
            <button
              type="button"
              onClick={() => setShowNew((prev) => !prev)}
              className="absolute right-3 top-3 text-gray-500 hover:text-white"
            >
              {showNew ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
          {errors.new_password && (
            <p className="mt-1.5 text-xs font-medium text-rose-400">
              {errors.new_password.message}
            </p>
          )}
        </div>

        <div>
          <label className="mb-2 block text-xs font-semibold text-gray-300">
            Confirm New Password
          </label>
          <input
            type="password"
            {...register("confirm_password")}
            className="h-11 w-full rounded-2xl border border-gray-800 bg-[#0b1020] px-4 text-xs text-white outline-none transition focus:border-indigo-500/60 focus:ring-2 focus:ring-indigo-500/20"
            placeholder="Confirm new password"
          />
          {errors.confirm_password && (
            <p className="mt-1.5 text-xs font-medium text-rose-400">
              {errors.confirm_password.message}
            </p>
          )}
        </div>

        <div className="pt-2">
          <button
            type="submit"
            disabled={mutation.isPending}
            className="inline-flex items-center justify-center gap-2 rounded-2xl bg-purple-600 px-6 py-2.5 text-xs font-bold text-white shadow-lg shadow-purple-600/20 transition hover:bg-purple-500 disabled:opacity-50"
          >
            {mutation.isPending ? (
              <>
                <LoaderCircle size={15} className="animate-spin text-white" />
                <span>Updating Password...</span>
              </>
            ) : (
              <>
                <ShieldCheck size={15} />
                <span>Update Password</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}