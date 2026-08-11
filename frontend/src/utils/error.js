/**
 * Utility to format API/Axios/FastAPI error responses safely into plain strings.
 * Guarantees that the returned value is ALWAYS a string, preventing React Minified Error #31
 * ("Objects are not valid as a React child").
 */

export function formatErrorMessage(
  err,
  fallback = "An unexpected error occurred. Please try again."
) {
  if (!err) {
    return fallback;
  }

  // If err is already a primitive string
  if (typeof err === "string") {
    return err;
  }

  // Extract error detail/message payload from Axios or standard Error object
  const data = err?.response?.data;
  const rawDetail = data?.detail ?? data?.message ?? err?.message;

  // Case 1: String detail
  if (typeof rawDetail === "string" && rawDetail.trim()) {
    return rawDetail;
  }

  // Case 2: Array of validation errors (e.g. FastAPI 422 Unprocessable Entity)
  if (Array.isArray(rawDetail)) {
    const formattedMsgs = rawDetail
      .map((item) => {
        if (typeof item === "string") return item;
        if (item && typeof item === "object") {
          return item.msg || item.message || JSON.stringify(item);
        }
        return String(item);
      })
      .filter(Boolean);

    if (formattedMsgs.length > 0) {
      return formattedMsgs.join(", ");
    }
  }

  // Case 3: Object detail (e.g. { message: "...", detail: "..." })
  if (typeof rawDetail === "object" && rawDetail !== null) {
    if (typeof rawDetail.message === "string") return rawDetail.message;
    if (typeof rawDetail.detail === "string") return rawDetail.detail;
    if (typeof rawDetail.msg === "string") return rawDetail.msg;
    return JSON.stringify(rawDetail);
  }

  // Case 4: Network error or missing response
  if (err?.code === "ERR_NETWORK" || !err?.response) {
    return "Unable to connect to backend server. Please check your network connection.";
  }

  return fallback;
}
