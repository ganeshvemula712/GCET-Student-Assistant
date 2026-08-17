/**
 * Utility to format API/Axios/FastAPI error responses safely into plain strings.
 * Guarantees that the returned value is ALWAYS a string, preventing React Minified Error #31
 * ("Objects are not valid as a React child").
 */

function stringifyPayload(payload) {
  if (!payload) return null;
  if (typeof payload === "string" && payload.trim()) {
    return payload.trim();
  }
  if (Array.isArray(payload)) {
    const msgs = payload
      .map((item) => {
        if (typeof item === "string") return item.trim();
        if (item && typeof item === "object") {
          return item.msg || item.message || item.detail || JSON.stringify(item);
        }
        return String(item);
      })
      .filter(Boolean);
    if (msgs.length > 0) return msgs.join(", ");
  }
  if (typeof payload === "object") {
    if (typeof payload.message === "string" && payload.message.trim()) return payload.message.trim();
    if (typeof payload.detail === "string" && payload.detail.trim()) return payload.detail.trim();
    if (typeof payload.msg === "string" && payload.msg.trim()) return payload.msg.trim();
  }
  return null;
}

export function formatErrorMessage(
  err,
  fallback = "An unexpected error occurred. Please try again."
) {
  if (!err) {
    return fallback;
  }

  if (typeof err === "string" && err.trim()) {
    return err.trim();
  }

  const response = err?.response;
  const data = response?.data;

  if (response) {
    // 1. Try response.data.message
    const msgPayload = stringifyPayload(data?.message);
    if (msgPayload) return msgPayload;

    // 2. Try response.data.detail
    const detailPayload = stringifyPayload(data?.detail);
    if (detailPayload) return detailPayload;

    // 3. Try response.data.error
    const errorPayload = stringifyPayload(data?.error);
    if (errorPayload) return errorPayload;

    // 4. Status-specific default messages
    const status = response.status;
    if (status === 401) {
      return "Authentication required. Please log in again.";
    }
    if (status === 403) {
      return "You do not have permission to perform this action.";
    }
    if (status === 429) {
      return "Rate limit or quota exceeded. Please try again later.";
    }
    if (status >= 500) {
      return "Server error. Please try again later.";
    }
  }

  // 5. Genuine network error (no response or ERR_NETWORK)
  if (err?.code === "ERR_NETWORK" || !response) {
    return "Unable to reach the server. Please check your connection and try again.";
  }

  // 6. Generic err.message if not Axios generic string
  if (typeof err?.message === "string" && err.message.trim()) {
    const m = err.message.trim();
    if (m !== "Network Error" && !m.startsWith("Request failed with status code")) {
      return m;
    }
  }

  // 7. Generic fallback
  return fallback;
}
