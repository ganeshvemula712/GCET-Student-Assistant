import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowLeft, Info } from "lucide-react";
import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";
import { toast } from "sonner";

import AuthCard from "@/components/auth/AuthCard";
import AuthField from "@/components/auth/AuthField";
import { resetPasswordSchema } from "@/schema/loginSchema";

export default function ResetPassword() {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: { password: "", confirmPassword: "" },
  });

  function onSubmit() {
    toast.info("Password recovery is not enabled by the backend yet. Please contact your administrator.");
  }

  return (
    <AuthCard title="Choose a new password" description="Use a strong password you do not use elsewhere." footer={<Link className="inline-flex items-center gap-1 font-medium text-emerald-300 hover:text-emerald-200" to="/login"><ArrowLeft size={15} /> Back to sign in</Link>}>
      <div className="mb-5 flex gap-3 rounded-xl border border-amber-300/15 bg-amber-300/10 p-3 text-xs leading-5 text-amber-100/80"><Info className="mt-0.5 shrink-0 text-amber-300" size={16} />This screen is ready for a future recovery-token API. Password reset is not yet available.</div>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
        <AuthField label="New password" type="password" placeholder="At least 8 characters" autoComplete="new-password" error={errors.password} {...register("password")} />
        <AuthField label="Confirm new password" type="password" placeholder="Repeat your new password" autoComplete="new-password" error={errors.confirmPassword} {...register("confirmPassword")} />
        <button type="submit" className="h-12 w-full rounded-xl bg-emerald-400 px-4 text-sm font-semibold text-[#032018] shadow-lg shadow-emerald-900/30 transition hover:bg-emerald-300">Reset password</button>
      </form>
    </AuthCard>
  );
}
