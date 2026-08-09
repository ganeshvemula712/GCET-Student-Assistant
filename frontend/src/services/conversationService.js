import api from "./api";

export async function getConversations() {
  const { data } = await api.get("/conversations");
  return data;
}

export async function getConversation(id) {
  const { data } = await api.get(`/conversations/${id}`);
  return data;
}

export async function createConversation(title) {
  const { data } = await api.post("/conversations", {
    title,
  });

  return data;
}

export async function renameConversation(id, title) {
  const { data } = await api.patch(`/conversations/${id}`, {
    title,
  });

  return data;
}

export async function deleteConversation(id) {
  const { data } = await api.delete(`/conversations/${id}`);

  return data;
}