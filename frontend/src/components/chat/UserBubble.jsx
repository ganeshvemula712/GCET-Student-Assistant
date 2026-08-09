import { UserCircle } from "lucide-react";

export default function UserBubble({ message }) {
  return (
    <div className="mb-8 flex justify-end">

      <div className="flex max-w-2xl gap-3">

        <div className="rounded-2xl bg-blue-600 px-5 py-4 text-white">
          {message}
        </div>

        <UserCircle
          size={36}
          className="text-slate-400"
        />

      </div>

    </div>
  );
}