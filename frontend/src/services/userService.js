import api from "./api";

export async function getProfile() {
  const { data } = await api.get("/users/me");
  return data;
}

export async function updateProfile(payload) {
  const { data } = await api.patch("/users/me", payload);

  return data;
}

export async function changePassword(payload) {
  const { data } = await api.patch(
    "/users/change-password",
    payload
  );

  return data;
}