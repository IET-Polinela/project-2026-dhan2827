const routes = {
    "#login": `
        <div class="row justify-content-center align-items-center mt-5">
            <div class="col-12 col-md-5 col-lg-4">
                <div class="card hero-card p-4">
                    <div class="text-center mb-4">
                        <span class="icon-box mb-3">
                            <i class="bi bi-person-circle fs-4"></i>
                        </span>
                        <h4 class="fw-bold">Login Citizen</h4>
                        <p class="text-muted mb-0">Masuk ke Smart City Portal</p>
                    </div>

                    <form id="loginForm">
                        <input type="text" id="loginUsername" class="form-control mb-3" placeholder="Username" required>
                        <input type="password" id="loginPassword" class="form-control mb-3" placeholder="Password" required>

                        <button type="submit" class="btn btn-primary w-100 fw-semibold">
                            <i class="bi bi-box-arrow-in-right me-1"></i>
                            Login
                        </button>
                    </form>
                </div>
            </div>
        </div>
    `
};

function getStoredAccessToken() {
    return (
        localStorage.getItem("access_token") ||
        localStorage.getItem("access") ||
        localStorage.getItem("accessToken")
    );
}

function handleRouting() {
    const token = getStoredAccessToken();
    const hash = window.location.hash || "#login";

    if (!token && hash === "#dashboard") {
        window.location.hash = "#login";
        return;
    }

    if (token && (hash === "#login" || hash === "#register")) {
        window.location.hash = "#dashboard";
        return;
    }

    updateNavbar();

    if (hash === "#dashboard") {
        if (typeof renderDashboardLayout === "function") {
            renderDashboardLayout();
        }

        if (typeof loadDashboardData === "function") {
            loadDashboardData("my_reports", 1);
        }

        return;
    }

    document.getElementById("app").innerHTML =
        routes[hash] || routes["#login"];

    if (hash === "#login" && typeof setupLoginForm === "function") {
        setupLoginForm();
    }
}

function updateNavbar() {
    const navMenus = document.getElementById("nav-menus");
    const token = getStoredAccessToken();
    const username = localStorage.getItem("username") || "Warga";

    if (!navMenus) return;

    if (token) {
        navMenus.innerHTML = `
            <div class="d-flex align-items-center gap-3 text-white">
                <span class="fw-semibold">
                    <i class="bi bi-person-circle me-1"></i>
                    Halo, ${username}!
                </span>

                <button class="btn btn-light btn-sm text-primary fw-semibold"
                        onclick="logoutUser()">
                    <i class="bi bi-box-arrow-right me-1"></i>
                    Keluar
                </button>
            </div>
        `;
    } else {
        navMenus.innerHTML = `
            <a href="#login" class="btn btn-light btn-sm text-primary fw-semibold">
                <i class="bi bi-box-arrow-in-right me-1"></i>
                Login
            </a>
        `;
    }
}

function logoutUser() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("username");

    window.location.hash = "#login";
    updateNavbar();
}

window.addEventListener("hashchange", handleRouting);
window.addEventListener("DOMContentLoaded", handleRouting);
