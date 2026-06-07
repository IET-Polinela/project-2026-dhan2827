function setupLoginForm() {
    const form = document.getElementById("loginForm");

    if (!form) return;

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

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