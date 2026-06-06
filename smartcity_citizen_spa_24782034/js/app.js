const API_BASE_URL = "http://127.0.0.1:8000";

let currentTab = "my_reports";
let currentPage = 1;
let allReports = [];
let editingReportId = null;

function getAccessToken() {
    return (
        localStorage.getItem("access_token") ||
        localStorage.getItem("access") ||
        localStorage.getItem("accessToken")
    );
}

function getAuthHeaders() {
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${getAccessToken()}`
    };
}

async function loadDashboardData(tab = currentTab, page = currentPage) {
    currentTab = tab;
    currentPage = page;

    const listContainer = document.getElementById("listContainer");
    const paginationContainer = document.getElementById("paginationContainer");

    if (!listContainer) return;

    listContainer.innerHTML = `
        <div class="text-center text-muted py-5">
            <div class="spinner-border mb-3"></div>
            <p>Sedang memuat data laporan...</p>
        </div>
    `;

    try {
        const response = await fetch(
            `${API_BASE_URL}/api/report/?tab=${currentTab}&page=${currentPage}&page_size=10`,
            {
                method: "GET",
                headers: getAuthHeaders()
            }
        );

        if (!response.ok) {
            throw new Error(`Gagal mengambil data. Status: ${response.status}`);
        }

        const responseData = await response.json();
        allReports = responseData.results || [];

        renderList(allReports);
        renderPagination(responseData.count, currentPage);
        loadSummaryStats();

    } catch (error) {
        console.error(error);

        listContainer.innerHTML = `
            <div class="text-center text-muted py-5">
                <i class="bi bi-exclamation-triangle fs-1"></i>
                <p class="mt-3">Gagal memuat data laporan.</p>
            </div>
        `;

        if (paginationContainer) {
            paginationContainer.innerHTML = "";
        }
    }
}

async function loadSummaryStats() {
    try {
        const response = await fetch(
            `${API_BASE_URL}/api/report/?tab=my_reports&page_size=1000`,
            {
                method: "GET",
                headers: getAuthHeaders()
            }
        );

        if (!response.ok) {
            throw new Error(`Gagal mengambil summary. Status: ${response.status}`);
        }

        const responseData = await response.json();
        const reports = responseData.results || [];

        const totalDraft = reports.filter(r => r.status === "DRAFT").length;
        const totalReported = reports.filter(r => r.status === "REPORTED").length;
        const totalVerified = reports.filter(r => r.status === "VERIFIED").length;
        const totalProgress = reports.filter(r => r.status === "IN_PROGRESS").length;
        const totalResolved = reports.filter(r => r.status === "RESOLVED").length;

        document.getElementById("countDraft").innerText = totalDraft;
        document.getElementById("countReported").innerText = totalReported;
        document.getElementById("countVerified").innerText = totalVerified;
        document.getElementById("countProgress").innerText = totalProgress;
        document.getElementById("countResolved").innerText = totalResolved;

    } catch (error) {
        console.error(error);
    }
}

function renderList(reports) {
    const listContainer = document.getElementById("listContainer");

    if (!reports || reports.length === 0) {
        listContainer.innerHTML = `
            <div class="card border-0 shadow-sm">
                <div class="card-body text-center text-muted py-5">
                    Belum ada laporan di tab ini.
                </div>
            </div>
        `;
        return;
    }

    listContainer.innerHTML = `
        <div class="row g-3">
            ${reports.map(report => `
                <div class="col-12 col-lg-6">
                    <div class="report-card card border-0 shadow-sm h-100">
                        <div class="card-body p-3">

                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <span class="badge rounded-pill ${getStatusBadgeClass(report.status)}">
                                    ${formatStatus(report.status).toUpperCase()}
                                </span>

                                <small class="text-muted">
                                    ${report.category}
                                </small>
                            </div>

                            <h5 class="report-title mb-2">${report.title}</h5>

                            <p class="report-desc text-muted mb-3">
                                ${report.description}
                            </p>

                            <hr class="my-2">

                            <p class="report-meta mb-1">
                                <strong>Lokasi:</strong> ${report.location}
                            </p>

                            <p class="report-meta mb-2">
                                <strong>Oleh:</strong> ${report.reporter}
                            </p>

                            <div class="d-flex justify-content-between align-items-center mb-1">
                                <small class="fw-bold">Progress Laporan:</small>
                                <small class="fw-bold text-primary">
                                    ${formatStatus(report.status)} (${getProgressValue(report.status)}%)
                                </small>
                            </div>

                            <div class="progress report-progress">
                                <div class="progress-bar"
                                     role="progressbar"
                                     style="width: ${getProgressValue(report.status)}%;">
                                </div>
                            </div>

                            <div class="mt-2">
                                ${renderActionButtons(report)}
                            </div>

                        </div>
                    </div>
                </div>
            `).join("")}
        </div>
    `;
}

function renderActionButtons(report) {
    if (report.status === "DRAFT" && report.is_owner) {
        return `
            <button class="btn btn-sm btn-outline-primary"
                    onclick="editDraft(${report.id})">
                <i class="bi bi-pencil-square me-1"></i>
                Edit Draft
            </button>
        `;
    }

    return "";
}

function renderPagination(totalItems, activePage) {
    const paginationContainer = document.getElementById("paginationContainer");

    if (!paginationContainer) return;

    const pageSize = 10;
    const totalPages = Math.ceil(totalItems / pageSize);

    if (totalPages <= 1) {
        paginationContainer.innerHTML = "";
        return;
    }

    let startPage = Math.max(1, activePage - 2);
    let endPage = Math.min(totalPages, startPage + 4);

    if (endPage - startPage < 4) {
        startPage = Math.max(1, endPage - 4);
    }

    let paginationHTML = `
        <nav class="mt-4">
            <ul class="pagination justify-content-center">
                <li class="page-item ${activePage === 1 ? "disabled" : ""}">
                    <button class="page-link"
                            onclick="loadDashboardData('${currentTab}', ${activePage - 1})">
                        Sebelumnya
                    </button>
                </li>
    `;

    for (let page = startPage; page <= endPage; page++) {
        paginationHTML += `
            <li class="page-item ${page === activePage ? "active" : ""}">
                <button class="page-link"
                        onclick="loadDashboardData('${currentTab}', ${page})">
                    ${page}
                </button>
            </li>
        `;
    }

    paginationHTML += `
                <li class="page-item ${activePage === totalPages ? "disabled" : ""}">
                    <button class="page-link"
                            onclick="loadDashboardData('${currentTab}', ${activePage + 1})">
                        Selanjutnya
                    </button>
                </li>
            </ul>
        </nav>
    `;

    paginationContainer.innerHTML = paginationHTML;
}

function getProgressValue(status) {
    const progressMap = {
        "DRAFT": 10,
        "REPORTED": 25,
        "VERIFIED": 50,
        "IN_PROGRESS": 75,
        "RESOLVED": 100
    };

    return progressMap[status] || 0;
}

function getStatusBadgeClass(status) {
    const badgeMap = {
        "DRAFT": "text-bg-secondary",
        "REPORTED": "text-bg-warning",
        "VERIFIED": "text-bg-info",
        "IN_PROGRESS": "text-bg-primary",
        "RESOLVED": "text-bg-success"
    };

    return badgeMap[status] || "text-bg-dark";
}

function formatStatus(status) {
    const statusMap = {
        "DRAFT": "Draft",
        "REPORTED": "Diajukan",
        "VERIFIED": "Terverifikasi",
        "IN_PROGRESS": "Diproses",
        "RESOLVED": "Selesai"
    };

    return statusMap[status] || status;
}

function renderDashboardLayout() {
    const app = document.getElementById("app");

    app.innerHTML = `
        <div class="row g-4">

            <aside class="col-12 col-lg-2">
                <div class="card border-0 shadow-sm rounded-3">
                    <div class="card-body p-3">

                        <button class="btn btn-primary w-100 mb-4 py-3 fw-bold shadow-sm"
                                data-bs-toggle="modal"
                                data-bs-target="#reportModal">
                            <i class="bi bi-plus-circle-fill me-2"></i>
                            Buat Laporan<br>Baru
                        </button>

                        <h6 class="fw-bold text-muted mb-3">
                            <i class="bi bi-activity me-1"></i>
                            STATUS LAPORAN ANDA
                        </h6>

                        <div class="status-row">
                            <span><i class="bi bi-pencil-square me-2"></i>Draf</span>
                            <span class="status-pill bg-secondary" id="countDraft">0</span>
                        </div>

                        <div class="status-row">
                            <span><i class="bi bi-send-fill text-warning me-2"></i>Diajukan</span>
                            <span class="status-pill bg-warning text-dark" id="countReported">0</span>
                        </div>

                        <div class="status-row">
                            <span><i class="bi bi-patch-check-fill text-info me-2"></i>Terverifikasi</span>
                            <span class="status-pill bg-info text-dark" id="countVerified">0</span>
                        </div>

                        <div class="status-row">
                            <span><i class="bi bi-gear-fill text-primary me-2"></i>Diproses</span>
                            <span class="status-pill bg-primary" id="countProgress">0</span>
                        </div>

                        <div class="status-row">
                            <span><i class="bi bi-check-circle-fill text-success me-2"></i>Selesai</span>
                            <span class="status-pill bg-success" id="countResolved">0</span>
                        </div>

                    </div>
                </div>
            </aside>

            <section class="col-12 col-lg-10">

                <ul class="nav nav-tabs mb-4">
                    <li class="nav-item">
                        <button class="nav-link active fw-bold"
                                id="btnMyReports"
                                onclick="switchTab('my_reports')">
                            <i class="bi bi-folder-fill me-2"></i>
                            Laporan Saya
                        </button>
                    </li>

                    <li class="nav-item">
                        <button class="nav-link fw-bold text-dark"
                                id="btnFeed"
                                onclick="switchTab('feed')">
                            <i class="bi bi-globe-americas me-2"></i>
                            Feed Kota (Publik)
                        </button>
                    </li>
                </ul>

                <div id="listContainer"></div>
                <div id="paginationContainer" class="mt-4"></div>

            </section>

        </div>
    `;
}

function switchTab(tab) {
    currentTab = tab;
    currentPage = 1;

    document.getElementById("btnMyReports").classList.toggle("active", tab === "my_reports");
    document.getElementById("btnFeed").classList.toggle("active", tab === "feed");

    document.getElementById("btnMyReports").classList.toggle("text-dark", tab !== "my_reports");
    document.getElementById("btnFeed").classList.toggle("text-dark", tab !== "feed");

    loadDashboardData(tab, 1);
}

async function editDraft(id) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/report/${id}/`, {
            method: "GET",
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            throw new Error(`Gagal mengambil data draft. Status: ${response.status}`);
        }

        const report = await response.json();

        editingReportId = id;

        document.getElementById("reportId").value = report.id;
        document.getElementById("title").value = report.title;
        document.getElementById("category").value = report.category;
        document.getElementById("location").value = report.location;
        document.getElementById("description").value = report.description;

        document.getElementById("reportModalLabel").innerHTML = `
            <i class="bi bi-pencil-square me-2"></i>
            Edit Draft Laporan
        `;

        const modal = new bootstrap.Modal(document.getElementById("reportModal"));
        modal.show();

    } catch (error) {
        console.error(error);
        alert("Gagal membuka data draft.");
    }
}

async function submitReport(statusValue) {
    const reportForm = document.getElementById("reportForm");

    const payload = {
        title: document.getElementById("title").value,
        category: document.getElementById("category").value,
        location: document.getElementById("location").value,
        description: document.getElementById("description").value,
        status: statusValue
    };

    const url = editingReportId === null
        ? `${API_BASE_URL}/api/report/`
        : `${API_BASE_URL}/api/report/${editingReportId}/`;

    const method = editingReportId === null ? "POST" : "PUT";

    try {
        const response = await fetch(url, {
            method: method,
            headers: getAuthHeaders(),
            body: JSON.stringify(payload)
        });

        if (response.status === 201 || response.status === 200) {
            const modalElement = document.getElementById("reportModal");
            const modalInstance = bootstrap.Modal.getInstance(modalElement);

            if (modalInstance) {
                modalInstance.hide();
            }

            reportForm.reset();
            editingReportId = null;

            document.getElementById("reportId").value = "";
            document.getElementById("reportModalLabel").innerHTML = `
                <i class="bi bi-pencil-square me-2"></i>
                Buat Laporan Baru
            `;

            loadDashboardData(currentTab, currentPage);
            alert("Laporan berhasil disimpan.");

        } else {
            const errorData = await response.json();
            console.error(errorData);
            alert("Gagal menyimpan laporan. Cek data form.");
        }

    } catch (error) {
        console.error(error);
        alert("Terjadi kesalahan saat mengirim laporan.");
    }
}

function setupReportFormEvents() {
    const btnDraft = document.getElementById("btnDraft");
    const btnSubmit = document.getElementById("btnSubmit");
    const reportModal = document.getElementById("reportModal");

    if (btnDraft) {
        btnDraft.addEventListener("click", function () {
            submitReport("DRAFT");
        });
    }

    if (btnSubmit) {
        btnSubmit.addEventListener("click", function () {
            submitReport("REPORTED");
        });
    }

    if (reportModal) {
        reportModal.addEventListener("hidden.bs.modal", function () {
            document.getElementById("reportForm").reset();
            document.getElementById("reportId").value = "";
            editingReportId = null;

            document.getElementById("reportModalLabel").innerHTML = `
                <i class="bi bi-pencil-square me-2"></i>
                Buat Laporan Baru
            `;
        });
    }
}

window.addEventListener("DOMContentLoaded", () => {
    setupReportFormEvents();
});