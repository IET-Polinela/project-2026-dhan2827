/// <reference path="auth.js" />
function getBaseURL() {
    return window.API_BASE_URL || "http://localhost:8000";
}

async function requestAPI(endpoint, method = "GET", bodyData = null) {
    const token = localStorage.getItem("access_token");

    const options = {
        method: method,
        headers: {
            "Content-Type": "application/json",
        },
    };

    if (token) {
        options.headers["Authorization"] = `Bearer ${token}`;
    }

    if (bodyData) {
        options.body = JSON.stringify(bodyData);
    }

    const response = await fetch(getBaseURL() + endpoint, options);

    let data = null;
    try {
        data = await response.json();
    } catch (error) {
        data = {};
    }

    if (response.status === 401) {
        handleAuthFailure();

        return {
            status: response.status,
            data: data
        };
    }
    return {
        status: response.status,
        data: data
    };
}
