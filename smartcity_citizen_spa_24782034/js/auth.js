function setupLoginForm() {
    const form = document.getElementById("loginForm");

    if (!form) return;

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const usernameInput =
            document.getElementById("loginUsername") ||
            document.getElementById("username");

        const passwordInput =
            document.getElementById("loginPassword") ||
            document.getElementById("password");

        const username = usernameInput.value;
        const password = passwordInput.value;

        const result = await requestAPI("/api/token/", "POST", {
            username: username,
            password: password
        });

        if (result.status === 200) {
            localStorage.setItem("access_token", result.data.access);
            localStorage.setItem("refresh_token", result.data.refresh);
            localStorage.setItem("username", username);

            alert("Login berhasil!");
            window.location.hash = "#dashboard";
        } else {
            alert("Login gagal. Cek username dan password.");
        }
    });
}


function getRegisterErrorMessage(data) {
    if (!data || typeof data !== "object") {
        return "";
    }

    const messages = [];

    Object.entries(data).forEach(([field, value]) => {
        if (Array.isArray(value)) {
            messages.push(`${field}: ${value.join(", ")}`);
        } else if (typeof value === "string") {
            messages.push(`${field}: ${value}`);
        } else if (value && typeof value === "object") {
            messages.push(`${field}: ${JSON.stringify(value)}`);
        }
    });

    return messages.join("\n");
}

async function registerCitizen(username, email, password) {
    let result = await requestAPI("/api/register/", "POST", {
        username: username,
        email: email,
        password: password
    });

    const errorText = JSON.stringify(result.data || {}).toLowerCase();

    if (
        result.status !== 200 &&
        result.status !== 201 &&
        errorText.includes("password2")
    ) {
        result = await requestAPI("/api/register/", "POST", {
            username: username,
            email: email,
            password: password,
            password2: password
        });
    }

    return result;
}

function handleAuthFailure() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("username");

    window.location.hash = "#login";

    if (typeof handleRouting === "function") {
        handleRouting();
    }
}

function setupRegisterForm() {
    const form = document.getElementById("registerForm");

    if (!form) return;

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const username = document.getElementById("registerUsername").value.trim();
        const email = document.getElementById("registerEmail").value.trim();
        const password = document.getElementById("registerPassword").value;
        const passwordConfirm = document.getElementById("registerPasswordConfirm").value;

        if (!username || !email || !password || !passwordConfirm) {
            alert("Username, email, password, dan konfirmasi password wajib diisi.");
            return;
        }

        if (password !== passwordConfirm) {
            alert("Password dan konfirmasi password harus sama.");
            return;
        }

        const result = await registerCitizen(username, email, password);

        if (result.status === 200 || result.status === 201) {
            alert("Registrasi berhasil. Silakan login.");
            window.location.hash = "#login";
            return;
        }

        const detail = getRegisterErrorMessage(result.data);
        alert(
            "Registrasi gagal. Periksa kembali data yang diisi." +
            (detail ? "\n\nDetail:\n" + detail : "")
        );
    });
}
