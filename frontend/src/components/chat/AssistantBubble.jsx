import { Bot } from "lucide-react";
import MarkdownRenderer from "./MarkdownRenderer";

export default function AssistantBubble({ message }) {
  return (
    <div className="mb-8 flex gap-4">

      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 to-violet-600">
        <Bot className="text-white" size={20} />
      </div>

      <div className="flex-1 rounded-2xl border border-slate-800 bg-[#141B2D] p-5">

        <MarkdownRenderer
          content={message}
        />

      </div>

    </div>
  );
}