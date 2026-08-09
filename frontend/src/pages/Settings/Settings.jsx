import SettingsHeader from "@/components/settings/SettingsHeader";
import PreferenceCard from "@/components/profile/PreferenceCard";
import ChangePasswordForm from "@/components/profile/ChangePasswordForm";
import AccountUsageCard from "@/components/settings/AccountUsageCard";

export default function Settings() {
  return (
    <div className="w-full max-w-7xl mx-auto space-y-8 pb-12">
      <SettingsHeader />
      <div className="grid gap-8 lg:grid-cols-2">
        <PreferenceCard />
        <ChangePasswordForm />
      </div>
      <AccountUsageCard />
    </div>
  );
}
