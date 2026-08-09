export function isAuthenticated() {
  const token = localStorage.getItem("access_token");

  return !!token;
}

export function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}