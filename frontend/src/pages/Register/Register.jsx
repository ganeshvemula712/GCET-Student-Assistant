import { zodResolver } from "@hookform/resolvers/zod";
import { LoaderCircle } from "lucide-react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";

import AuthCard from "@/components/auth/AuthCard";
import AuthField from "@/components/auth/AuthField";
import useRegister from "@/hooks/useRegister";
import { registerSchema } from "@/schema/loginSchema";
import { formatErrorMessage } from "@/utils/error";

export default function Register() {
  const navigate = useNavigate();
  const registerMutation = useRegister();
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(registerSchema),
    defaultValues: { name: "", email: "", password: "", confirmPassword: "" },
  });

  async function onSubmit({ name, email, password }) {
    try {
      await registerMutation.mutateAsync({ name, email, password });
      toast.success("Account created. You can sign in now.");
      navigate("/login");
    } catch (error) {
      toast.error(formatErrorMessage(error, "Unable to create your account. Please try again."));
    }
  }

  return (
    <AuthCard
      title="Create your account"
      description="Start using GCET AI to get focused academic support."
      footer={
        <>
          Already have an account?{" "}
          <Link className="font-semibold text-indigo-400 transition hover:text-indigo-300" to="/login">
            Sign in
          </Link>
        </>
      }
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
        <AuthField label="Full name" placeholder="Your name" autoComplete="name" error={errors.name} {...register("name")} />
        <AuthField label="Email address" type="email" placeholder="you@example.com" autoComplete="email" error={errors.email} {...register("email")} />
        <AuthField label="Password" type="password" placeholder="At least 8 characters" autoComplete="new-password" error={errors.password} {...register("password")} />
        <AuthField label="Confirm password" type="password" placeholder="Repeat your password" autoComplete="new-password" error={errors.confirmPassword} {...register("confirmPassword")} />
        <button
          type="submit"
          disabled={registerMutation.isPending}
          className="flex h-12 w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-indigo-500 via-indigo-600 to-cyan-500 px-4 text-base font-bold text-gray-950 shadow-lg shadow-indigo-500/25 transition-all duration-200 hover:from-indigo-400 hover:to-cyan-400 disabled:cursor-not-allowed disabled:opacity-70 cursor-pointer mt-2"
        >
          {registerMutation.isPending ? <><LoaderCircle className="animate-spin text-gray-950" size={20} /> Creating account</> : "Create account"}
        </button>
      </form>
    </AuthCard>
  );
}
