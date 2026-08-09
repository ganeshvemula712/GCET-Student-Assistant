import api from "./api";

export async function login(email, password) {
  const body = new URLSearchParams();

  body.append("username", email);
  body.append("password", password);

  const response = await api.post("/auth/login", body, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });

  return response.data;
}

export async function loginWithGoogle(payload = {}) {
  const response = await api.post("/auth/google", payload);
  return response.data;
}

export async function refreshToken(refresh_token) {
  const response = await api.post("/auth/refresh", {
    refresh_token,
  });

  return response.data;
}

export async function logout() {
  return true;
}

export async function register({ name, email, password }) {
  const response = await api.post("/auth/register", {
    name,
    email,
    password,
  });

  return response.data;
}
