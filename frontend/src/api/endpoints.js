const API_ENDPOINTS = {

    AUTH: {
        LOGIN: "/auth/login",
        REGISTER: "/auth/register",
        REFRESH: "/auth/refresh",
    },

    USER: {
        ME: "/users/me",
        CHANGE_PASSWORD: "/users/change-password",
    },

    CHAT: {
        ASK: "/chat/stream",
    },

    CONVERSATIONS: {
        LIST: "/conversations",
        SEARCH: "/conversations/search",
    },

    DOCUMENTS: {
        LIST: "/documents",
        UPLOAD: "/documents/upload",
    },

};

export default API_ENDPOINTS;