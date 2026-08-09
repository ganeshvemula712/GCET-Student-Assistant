import api from "./api";

export async function submitFeedback(messageId, feedback) {
  const { data } = await api.post("/feedback", null, {
    params: {
      message_id: messageId,
      feedback,
    },
  });

  return data;
}
