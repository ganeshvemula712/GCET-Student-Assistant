export async function askAI(payload = {}) {
  const {
    conversationId,
    conversation_id,
    question,
    token,
    onChunk,
    onComplete,
    onAbort,
    signal,
  } = payload;

  const conversation = conversationId ?? conversation_id ?? crypto.randomUUID();
  const baseUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

  try {
    const response = await fetch(`${baseUrl}/chat/stream`, {
      method: "POST",
      signal,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token || localStorage.getItem("access_token")}`,
      },
      body: JSON.stringify({
        conversation_id: conversation,
        question,
      }),
    });

    if (!response.ok) {
      const errText = await response.text().catch(() => "");
      throw new Error(`Streaming request failed: ${response.status} ${errText}`);
    }

    if (!response.body) {
      throw new Error("Streaming response body is unavailable.");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    let result = "";
    let buffer = "";
    let metadata = {};

    while (true) {
      const { value, done } = await reader.read();

      if (done) {
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (let rawLine of lines) {
        rawLine = rawLine.trim();
        if (!rawLine) continue;
        if (rawLine.startsWith("data: ")) {
          rawLine = rawLine.slice(6).trim();
        }
        if (!rawLine) continue;

        try {
          const event = JSON.parse(rawLine);
          if (event.type === "token") {
            result += event.content || "";
            onChunk?.(result);
          } else if (event.type === "done") {
            metadata = event;
          } else if (event.type === "error") {
            throw new Error(event.message || "Streaming request failed.");
          }
        } catch (parseErr) {
          if (parseErr.message?.includes("Streaming request failed")) {
            throw parseErr;
          }
          // Ignore incomplete JSON line chunks
        }
      }
    }

    buffer += decoder.decode();
    let finalLine = buffer.trim();
    if (finalLine.startsWith("data: ")) {
      finalLine = finalLine.slice(6).trim();
    }

    if (finalLine) {
      try {
        const event = JSON.parse(finalLine);
        if (event.type === "done") metadata = event;
        if (event.type === "error") throw new Error(event.message || "Streaming request failed.");
      } catch (parseErr) {
        if (parseErr.message?.includes("Streaming request failed")) {
          throw parseErr;
        }
      }
    }

    onComplete?.(result, false, metadata);
    return result;
  } catch (error) {
    if (error?.name === "AbortError") {
      onAbort?.("");
      return "";
    }

    onAbort?.("");
    throw error;
  }
}
