import { useMemo } from "react";

export default function useConversationMemory(messages = []) {
  return useMemo(() => {
    const recentMessages = messages.slice(-8);
    return recentMessages
      .filter((message) => message?.content)
      .map((message) => `${message.role === "user" ? "User" : "Assistant"}: ${message.content}`)
      .join("\n");
  }, [messages]);
}
