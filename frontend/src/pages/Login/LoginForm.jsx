import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import {
  Mail,
  Lock,
  Eye,
  EyeOff,
  ArrowRight,
  LoaderCircle,
  ShieldCheck,
} from "lucide-react";

import gcetLogoImg from "@/assets/gcet-logo.png";
import useLogin from "@/hooks/useLogin";
import { loginWithGoogle } from "@/services/authService";
import api from "@/services/api";
import { saveTokens } from "@/utils/token";
import { useAuth } from "@/context/AuthContext";
import { loginSchema } from "@/schema/loginSchema";
import { formatErrorMessage } from "@/utils/error";

export default function LoginForm() {
  const navigate = useNavigate();
  const { login: loginContext } = useAuth();
  const loginMutation = useLogin();
  const [googleLoading, setGoogleLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
  });

  useEffect(() => {
    if (document.getElementById("google-gsi-script")) return;
    const script = document.createElement("script");
    script.id = "google-gsi-script";
    script.src = "https://accounts.google.com/gsi/client";
    script.async = true;
    script.defer = true;
    document.body.appendChild(script);
  }, []);

  async function onSubmit({ email, password }) {
    try {
      const data = await loginMutation.mutateAsync({ email, password });
      saveTokens(data.access_token, data.refresh_token);
      if (rememberMe) {
        localStorage.setItem("gcet_remember_email", email);
      }
      loginContext();
      toast.success("Welcome back to GCET AI.");
      navigate("/dashboard");
    } catch (err) {
      toast.error(formatErrorMessage(err, "Unable to sign in. Check your details and try again."));
    }
  }

  async function handleGoogleSignIn() {
    setGoogleLoading(true);
    try {
      const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || "";
      const savedEmail = localStorage.getItem("gcet_last_google_email") || undefined;

      if (clientId && window.google?.accounts?.id) {
        window.google.accounts.id.initialize({
          client_id: clientId,
          auto_select: false, // Ensure standard Google account chooser appears when requested
          use_fedcm_for_prompt: true,
          login_hint: savedEmail,
          callback: async (response) => {
            try {
              if (response.credential) {
                const data = await loginWithGoogle({ credential: response.credential });
                saveTokens(data.access_token, data.refresh_token);
                if (data.user?.email) {
                  localStorage.setItem("gcet_last_google_email", data.user.email);
                }
                loginContext();
                toast.success("Signed in with Google successfully.");
                navigate("/dashboard");
              }
            } catch (err) {
              console.error(err);
              toast.error(formatErrorMessage(err, "Google authentication failed. Please try again."));
            } finally {
              setGoogleLoading(false);
            }
          },
        });

        window.google.accounts.id.prompt((notification) => {
          if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
            triggerOAuthRedirect();
          }
        });
        return;
      }

      await triggerOAuthRedirect();
    } catch (err) {
      console.error(err);
      toast.error(formatErrorMessage(err, "Google authentication failed. Please try again."));
      setGoogleLoading(false);
    }
  }

  async function triggerOAuthRedirect() {
    try {
      const response = await api.get("/auth/google/url");
      if (response.data?.auth_url && response.data?.configured) {
        const savedEmail = localStorage.getItem("gcet_last_google_email");
        let targetUrl = response.data.auth_url;
        if (savedEmail && !targetUrl.includes("login_hint")) {
          targetUrl += `&login_hint=${encodeURIComponent(savedEmail)}`;
        }
        window.location.href = targetUrl;
        return;
      }
    } catch {
      // Fallback for dev environments without client ID
    }

    const userEmail = prompt("Enter your GCET Google email address (@gcet.edu.in):");
    if (!userEmail) {
      setGoogleLoading(false);
      return;
    }

    const data = await loginWithGoogle({
      email: userEmail.trim(),
      name: userEmail.split("@")[0],
    });

    saveTokens(data.access_token, data.refresh_token);
    localStorage.setItem("gcet_last_google_email", userEmail.trim());
    loginContext();
    toast.success(`Signed in as ${userEmail.trim()}`);
    navigate("/dashboard");
  }

  return (
    <div className="w-full max-w-[420px] rounded-3xl border border-gray-800/80 bg-[#0A1022]/95 p-6 sm:p-8 shadow-2xl backdrop-blur-2xl relative min-w-0">
      {/* GCET Golden Circular Crest / Emblem Lockup (Exact Reference Image) */}
      <div className="mb-6 flex flex-col items-center justify-center text-center">
        <div className="relative flex size-24 items-center justify-center rounded-full bg-gradient-to-br from-amber-500/20 via-[#0B1124] to-indigo-900/40 p-2 shadow-2xl border-2 border-amber-400/40 mb-3.5 group">
          <div className="absolute inset-0 rounded-full bg-amber-400/10 blur-md pointer-events-none" />
          <img
            src={gcetLogoImg}
            alt="GCET Crest"
            className="size-14 object-contain filter drop-shadow-[0_0_14px_rgba(245,158,11,0.5)] relative z-10"
          />
        </div>

        <h2 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
          GCET Student Assistant
        </h2>
        <p className="mt-1 text-xs font-semibold text-gray-400">
          AI Powered. Student Focused. GCET Proud.
        </p>
        <div className="mt-2.5 h-0.5 w-16 bg-gradient-to-r from-amber-400 to-amber-500 rounded-full" />
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
        {/* Email Address Field */}
        <div>
          <label className="mb-1.5 block text-xs font-bold text-gray-300">
            Email Address
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 flex w-11 items-center justify-center text-gray-400 pointer-events-none">
              <Mail size={18} />
            </div>
            <input
              type="email"
              placeholder="Enter your email"
              autoComplete="email"
              aria-invalid={Boolean(errors.email)}
              className="h-12 w-full rounded-2xl border border-gray-800 bg-[#060A16] pl-11 pr-4 text-sm text-white outline-none transition duration-200 placeholder:text-gray-500 focus:border-indigo-500/70 focus:ring-2 focus:ring-indigo-500/20 aria-invalid:border-rose-500/60"
              {...register("email")}
            />
          </div>
          {errors.email && (
            <span className="mt-1 block text-xs font-medium text-rose-400">
              {errors.email.message}
            </span>
          )}
        </div>

        {/* Password Field */}
        <div>
          <label className="mb-1.5 block text-xs font-bold text-gray-300">
            Password
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 flex w-11 items-center justify-center text-gray-400 pointer-events-none">
              <Lock size={18} />
            </div>
            <input
              type={showPassword ? "text" : "password"}
              placeholder="Enter your password"
              autoComplete="current-password"
              aria-invalid={Boolean(errors.password)}
              className="h-12 w-full rounded-2xl border border-gray-800 bg-[#060A16] pl-11 pr-11 text-sm text-white outline-none transition duration-200 placeholder:text-gray-500 focus:border-indigo-500/70 focus:ring-2 focus:ring-indigo-500/20 aria-invalid:border-rose-500/60"
              {...register("password")}
            />
            <button
              type="button"
              onClick={() => setShowPassword((prev) => !prev)}
              aria-label={showPassword ? "Hide password" : "Show password"}
              className="absolute inset-y-0 right-0 flex w-11 items-center justify-center text-gray-400 hover:text-white transition"
            >
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>
          {errors.password && (
            <span className="mt-1 block text-xs font-medium text-rose-400">
              {errors.password.message}
            </span>
          )}
        </div>

        {/* Remember Me Checkbox & Forgot Password Link */}
        <div className="flex items-center justify-between pt-0.5">
          <label className="flex items-center gap-2 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={rememberMe}
              onChange={(e) => setRememberMe(e.target.checked)}
              className="size-4 rounded border-gray-800 bg-[#060A16] text-indigo-600 focus:ring-indigo-500/20 accent-indigo-600"
            />
            <span className="text-xs font-medium text-gray-300">Remember me</span>
          </label>

          <Link
            to="/forgot-password"
            className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition"
          >
            Forgot Password?
          </Link>
        </div>

        {/* Primary Submit Button */}
        <button
          type="submit"
          disabled={loginMutation.isPending || googleLoading}
          className="flex h-12 w-full items-center justify-center gap-2 rounded-2xl bg-indigo-600 px-4 text-sm font-extrabold text-white shadow-lg shadow-indigo-600/30 transition-all duration-200 hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-70 cursor-pointer mt-3"
        >
          {loginMutation.isPending ? (
            <>
              <LoaderCircle className="animate-spin text-white" size={18} />
              <span>Logging in...</span>
            </>
          ) : (
            <>
              <span>Login</span>
              <ArrowRight size={18} />
            </>
          )}
        </button>

        {/* Divider */}
        <div className="relative my-4 flex items-center justify-center">
          <div className="w-full border-t border-gray-800/80" />
          <span className="absolute bg-[#0A1022] px-3 text-[11px] font-bold uppercase tracking-wider text-gray-400">
            or continue with
          </span>
        </div>

        {/* Google Sign In Button */}
        <button
          type="button"
          disabled={loginMutation.isPending || googleLoading}
          onClick={handleGoogleSignIn}
          className="flex h-11 w-full items-center justify-center gap-2.5 rounded-2xl border border-gray-800 bg-gray-900/60 text-xs font-bold text-gray-200 transition hover:bg-gray-800 hover:text-white disabled:opacity-50 cursor-pointer shadow-sm"
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
          <span>{googleLoading ? "Authenticating..." : "Sign in with Google"}</span>
        </button>
      </form>

      {/* Registration Footer Link */}
      <div className="mt-6 text-center text-xs text-gray-400 font-medium">
        New to GCET Assistant?{" "}
        <Link
          to="/register"
          className="font-bold text-indigo-400 hover:text-indigo-300 transition"
        >
          Create an Account
        </Link>
      </div>
    </div>
  );
}
