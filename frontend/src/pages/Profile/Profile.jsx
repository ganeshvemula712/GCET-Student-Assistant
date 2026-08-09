import ProfileHeader from "@/components/profile/ProfileHeader";
import ProfileCard from "@/components/profile/ProfileCard";
import EditProfileForm from "@/components/profile/EditProfileForm";
import ChangePasswordForm from "@/components/profile/ChangePasswordForm";
import PreferenceCard from "@/components/profile/PreferenceCard";
import ProfileSkeleton from "@/components/profile/ProfileSkeleton";

import useProfile from "@/hooks/useProfile";
import { AlertCircle } from "lucide-react";

export default function Profile() {
  const { data: profile, isLoading, isError, refetch } = useProfile();

  if (isLoading) {
    return <ProfileSkeleton />;
  }

  if (isError) {
    return (
      <div className="mx-auto max-w-2xl rounded-3xl border border-rose-500/30 bg-rose-500/10 p-8 text-center text-sm font-semibold text-rose-400 shadow-xl">
        <AlertCircle size={32} className="mx-auto mb-2 text-rose-400" />
        Failed to load student profile information. Please verify your connection and try again.
        <div className="mt-4">
          <button
            onClick={() => refetch()}
            className="rounded-2xl bg-rose-500 px-5 py-2 text-xs font-bold text-white shadow-md hover:bg-rose-400"
          >
            Retry Sync
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-7xl mx-auto space-y-8 pb-12">
      <ProfileHeader />

      <ProfileCard profile={profile} />

      <div className="grid gap-8 lg:grid-cols-2">
        <EditProfileForm profile={profile} />
        <ChangePasswordForm />
      </div>

      <PreferenceCard />
    </div>
  );
}