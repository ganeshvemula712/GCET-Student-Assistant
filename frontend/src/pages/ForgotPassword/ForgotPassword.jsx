import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowLeft, Mail } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";
import { toast } from "sonner";

import AuthCard from "@/components/auth/AuthCard";
import AuthField from "@/components/auth/AuthField";
import { emailSchema } from "@/schema/loginSchema";

export default function ForgotPassword() {
  const [submitted, setSubmitted] = useState(false);
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(emailSchema),
    defaultValues: { email: "" },
  });

  function onSubmit() {
    setSubmitted(true);
    toast.info("Password recovery is not available yet. Please contact your administrator.");
  }

  return (
    <AuthCard title="Reset your password" description="Enter the email address associated with your account." footer={<Link className="inline-flex items-center gap-1 font-medium text-emerald-300 hover:text-emerald-200" to="/login"><ArrowLeft size={15} /> Back to sign in</Link>}>
      {submitted ? (
        <div className="rounded-2xl border border-emerald-300/15 bg-emerald-300/10 p-5 text-sm leading-6 text-emerald-50/80"><Mail className="mb-3 text-emerald-300" size={20} />Password recovery is ready for a future backend endpoint. For now, contact your administrator for account help.</div>
      ) : (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5" noValidate>
          <AuthField label="Email address" type="email" placeholder="you@example.com" autoComplete="email" error={errors.email} {...register("email")} />
          <button type="submit" className="h-12 w-full rounded-xl bg-emerald-400 px-4 text-sm font-semibold text-[#032018] shadow-lg shadow-emerald-900/30 transition hover:bg-emerald-300">Send recovery instructions</button>
        </form>
      )}
    </AuthCard>
  );
}
