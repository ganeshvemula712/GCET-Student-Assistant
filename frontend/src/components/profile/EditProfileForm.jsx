import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { User, Mail, BookOpen, Save, LoaderCircle } from "lucide-react";

import useUpdateProfile from "@/hooks/useUpdateProfile";
import { updateProfileSchema } from "@/schema/profileSchema";

export default function EditProfileForm({ profile }) {
  const mutation = useUpdateProfile();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(updateProfileSchema),
  });

  useEffect(() => {
    if (profile) {
      reset({
        name: profile.name || "",
      });
    }
  }, [profile, reset]);

  async function onSubmit(values) {
    try {
      await mutation.mutateAsync(values);
      toast.success("Personal information updated successfully.");
    } catch (error) {
      toast.error(
        error?.response?.data?.detail ?? "Unable to update profile settings."
      );
    }
  }

  return (
    <div className="rounded-3xl border border-gray-800 bg-[#111827] p-6 shadow-xl sm:p-8">
      <div className="mb-6 flex items-center justify-between border-b border-gray-800/80 pb-4">
        <div>
          <h3 className="text-base font-bold text-white">Personal Information</h3>
          <p className="mt-0.5 text-xs text-gray-400">Update your student name and contact preferences.</p>
        </div>
        <div className="flex size-8 items-center justify-center rounded-xl bg-indigo-500/10 text-indigo-400">
          <User size={16} />
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5" noValidate>
        <div>
          <label className="mb-2 block text-xs font-semibold text-gray-300">
            Full Name
          </label>
          <input
            type="text"
            {...register("name")}
            className="h-11 w-full rounded-2xl border border-gray-800 bg-[#0b1020] px-4 text-xs text-white outline-none transition focus:border-indigo-500/60 focus:ring-2 focus:ring-indigo-500/20"
            placeholder="Your full student name"
          />
          {errors.name && (
            <p className="mt-1.5 text-xs font-medium text-rose-400">
              {errors.name.message}
            </p>
          )}
        </div>

        <div>
          <label className="mb-2 block text-xs font-semibold text-gray-300">
            Email Address (Read-only)
          </label>
          <div className="relative">
            <input
              type="email"
              value={profile?.email || ""}
              disabled
              className="h-11 w-full cursor-not-allowed rounded-2xl border border-gray-800 bg-gray-900/80 px-4 text-xs text-gray-400"
            />
            <Mail size={16} className="absolute right-4 top-3.5 text-gray-600" />
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-2 block text-xs font-semibold text-gray-300">
              Department
            </label>
            <div className="relative">
              <input
                type="text"
                value="Computer Science & Engineering"
                disabled
                className="h-11 w-full cursor-not-allowed rounded-2xl border border-gray-800 bg-gray-900/80 px-4 text-xs text-gray-400"
              />
              <BookOpen size={16} className="absolute right-4 top-3.5 text-gray-600" />
            </div>
          </div>

          <div>
            <label className="mb-2 block text-xs font-semibold text-gray-300">
              Academic Regulation
            </label>
            <input
              type="text"
              value="R22 Academic Regulation"
              disabled
              className="h-11 w-full cursor-not-allowed rounded-2xl border border-gray-800 bg-gray-900/80 px-4 text-xs text-gray-400"
            />
          </div>
        </div>

        <div className="pt-2">
          <button
            type="submit"
            disabled={mutation.isPending}
            className="inline-flex items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-indigo-500 to-cyan-500 px-6 py-2.5 text-xs font-bold text-gray-950 shadow-lg shadow-indigo-500/20 transition-all duration-200 hover:from-indigo-400 hover:to-cyan-400 disabled:opacity-50"
          >
            {mutation.isPending ? (
              <>
                <LoaderCircle size={15} className="animate-spin text-gray-950" />
                <span>Saving Changes...</span>
              </>
            ) : (
              <>
                <Save size={15} />
                <span>Save Personal Info</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}