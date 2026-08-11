import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useNavigate } from "react-router-dom";

import { toast } from "sonner";
import { ArrowRight, LoaderCircle } from "lucide-react";

import useLogin from "@/hooks/useLogin";
import { loginWithGoogle } from "@/services/authService";
import { saveTokens } from "@/utils/token";
import { useAuth } from "@/context/AuthContext";
import { loginSchema } from "@/schema/loginSchema";
import { formatErrorMessage } from "@/utils/error";
import AuthCard from "@/components/auth/AuthCard";
import AuthField from "@/components/auth/AuthField";

export default function LoginForm() {
  const navigate = useNavigate();
  const { login: loginContext } = useAuth();
  const loginMutation = useLogin();
  const [googleLoading, setGoogleLoading] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
  });

  async function onSubmit({ email, password }) {
    try {
      const data = await loginMutation.mutateAsync({
        email,
        password,
      });

      saveTokens(data.access_token, data.refresh_token);
      loginContext();
      toast.success("Welcome back to GCET AI Assistant.");

      navigate("/dashboard");
    } catch (err) {
      toast.error(formatErrorMessage(err, "Unable to sign in. Check your details and try again."));
    }
  }

  async function handleGoogleSignIn() {
    setGoogleLoading(true);
    try {
      const data = await loginWithGoogle({
        email: "student@gcet.edu.in",
        name: "GCET Student",
      });

      saveTokens(data.access_token, data.refresh_token);
      loginContext();
      toast.success("Signed in with Google (@gcet.edu.in) successfully.");
      navigate("/dashboard");
    } catch (err) {
      console.error(err);
      toast.error(formatErrorMessage(err, "Google authentication failed. Please try again."));
    } finally {
      setGoogleLoading(false);
    }
  }

  return (
    <AuthCard
      title="Welcome back"
      description="Sign in to continue your academic workspace."
      footer={
        <>
          New to GCET AI?{" "}
          <Link className="font-semibold text-indigo-400 transition hover:text-indigo-300" to="/register">
            Create an account
          </Link>
        </>
      }
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
        <AuthField
          label="Email address"
          type="email"
          placeholder="you@example.com"
          autoComplete="email"
          error={errors.email}
          {...register("email")}
        />
        <div>
          <div className="mb-2 flex items-center justify-between">
            <span className="text-sm font-semibold text-gray-200">Password</span>
            <Link to="/forgot-password" className="text-sm font-semibold text-indigo-400 transition hover:text-indigo-300">
              Forgot password?
            </Link>
          </div>
          <AuthField
            label=""
            type="password"
            placeholder="Enter your password"
            autoComplete="current-password"
            error={errors.password}
            {...register("password")}
          />
        </div>

        <button
          type="submit"
          disabled={loginMutation.isPending || googleLoading}
          className="flex h-12 w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-indigo-500 via-indigo-600 to-cyan-500 px-4 text-base font-bold text-gray-950 shadow-lg shadow-indigo-500/25 transition-all duration-200 hover:from-indigo-400 hover:to-cyan-400 disabled:cursor-not-allowed disabled:opacity-70 cursor-pointer"
        >
          {loginMutation.isPending ? (
            <>
              <LoaderCircle className="animate-spin text-gray-950" size={20} />
              <span>Signing in...</span>
            </>
          ) : (
            <>
              <span>Sign in</span>
              <ArrowRight size={18} />
            </>
          )}
        </button>

        <div className="relative my-4 flex items-center justify-center">
          <div className="w-full border-t border-gray-800" />
          <span className="absolute bg-[#111827] px-3 text-xs font-semibold uppercase tracking-wider text-gray-500">
            or
          </span>
        </div>

        <button
          type="button"
          disabled={loginMutation.isPending || googleLoading}
          onClick={handleGoogleSignIn}
          className="flex h-11 w-full items-center justify-center gap-2.5 rounded-2xl border border-gray-800 bg-gray-900/60 text-sm font-semibold text-gray-200 transition hover:bg-gray-800 hover:text-white disabled:opacity-50 cursor-pointer"
        >
          {googleLoading ? (
            <LoaderCircle className="animate-spin text-indigo-400" size={18} />
          ) : (
            <svg className="size-4" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
              />
            </svg>
          )}
          <span>{googleLoading ? "Authenticating..." : "Continue with Google"}</span>
        </button>
      </form>
    </AuthCard>
  );
}
