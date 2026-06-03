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
                        <input type="text" id="username" class="form-control mb-3" placeholder="Username" required>
                        <input type="password" id="password" class="form-control mb-3" placeholder="Password" required>

                        <button type="submit" class="btn btn-primary w-100 fw-semibold">
                            <i class="bi bi-box-arrow-in-right me-1"></i>
                            Login
                        </button>
                    </form>
                </div>
            </div>
        </div>
    `,

    "#dashboard": `
    <div class="row g-4">

        <aside class="col-12 col-lg-3">
            <div class="card hero-card p-3">
                <h5><i class="bi bi-file-earmark-text me-2"></i>Laporan</h5>
                <h2 class="text-primary">12</h2>
                <small>Total laporan masuk</small>
            </div>
        </aside>

        <section class="col-12 col-lg-6">
            <div class="card hero-card p-4 text-center">
                <i class="bi bi-buildings-fill fs-1 text-primary"></i>
                <h2 class="mt-3">Dashboard Smart City</h2>
                <p class="text-muted">
                    Sistem monitoring laporan masyarakat berbasis SPA dan JWT Authentication.
                </p>
            </div>
        </section>

        <aside class="col-12 col-lg-3">
            <div class="card hero-card p-3">
                <h5><i class="bi bi-person-check me-2"></i>Status</h5>
                <h2 class="text-success">Aktif</h2>
                <small>Login berhasil</small>
            </div>
        </aside>

    </div>
    `
};

function handleRouting() {
    const hash = window.location.hash || "#login";

    document.getElementById("app").innerHTML =
        routes[hash] || routes["#login"];

    if (hash === "#login" && typeof setupLoginForm === "function") {
        setupLoginForm();
    }
}

window.addEventListener("hashchange", handleRouting);
window.addEventListener("DOMContentLoaded", handleRouting);