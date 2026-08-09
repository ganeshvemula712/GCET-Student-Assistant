import api from "./api";

// --------------------------------------------------
// Update User Message
// --------------------------------------------------
export async function updateMessage(
  messageId,
  content,
) {
  const { data } = await api.patch(
    `/messages/${messageId}`,
    {
      content,
    }
  );

  return data;
}

// --------------------------------------------------
// Delete Message
// --------------------------------------------------
export async function deleteMessage(
  messageId,
) {
  const { data } = await api.delete(
    `/messages/${messageId}`
  );

  return data;
}

// --------------------------------------------------
// Regenerate Assistant
// --------------------------------------------------
export async function regenerateMessage(
  messageId,
) {
  const { data } = await api.post(
    `/messages/${messageId}/regenerate`
  );

  return data;
}