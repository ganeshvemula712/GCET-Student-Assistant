import axios from "axios";

import {
    getRefreshToken,
} from "./auth";

const BASE_URL =
    "http://127.0.0.1:8000";

export async function refreshAccessToken() {

    const response =
        await axios.post(

            `${BASE_URL}/auth/refresh`,

            {
                refresh_token:
                    getRefreshToken(),
            }

        );

    return response.data;

}