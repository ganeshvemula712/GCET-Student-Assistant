const ACCESS_TOKEN = "access_token";
const REFRESH_TOKEN = "refresh_token";

export function getAccessToken() {
    return localStorage.getItem(ACCESS_TOKEN);
}

export function getRefreshToken() {
    return localStorage.getItem(REFRESH_TOKEN);
}

export function saveTokens(tokens) {

    localStorage.setItem(
        ACCESS_TOKEN,
        tokens.access_token
    );

    localStorage.setItem(
        REFRESH_TOKEN,
        tokens.refresh_token
    );
}

export function updateAccessToken(token) {

    localStorage.setItem(
        ACCESS_TOKEN,
        token
    );

}

export function clearTokens() {

    localStorage.removeItem(
        ACCESS_TOKEN
    );

    localStorage.removeItem(
        REFRESH_TOKEN
    );

}