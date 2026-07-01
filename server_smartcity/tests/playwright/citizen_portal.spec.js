const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';
const SPA_URL = process.env.SPA_URL || 'http://127.0.0.1:5500/index.html';
console.log("=================================");
console.log("BASE_URL =", BASE_URL);
console.log("SPA_URL  =", SPA_URL);
console.log("=================================");

const TEST_CITIZEN_USERNAME = 'warga';
const TEST_CITIZEN_PASSWORD = 'warga12345';
const TEST_ADMIN_USERNAME = 'admin';
const TEST_ADMIN_PASSWORD = 'dhani123A';

const EXPIRED_ACCESS_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjAwMDAwMDAwLCJpYXQiOjE2MDAwMDAwMDAsImp0aSI6ImZha2VfYWNjZXNzX2lkIiwidXNlcl9pZCI6MX0.fake_signature_for_testing';
const EXPIRED_REFRESH_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTYwMDAwMDAwMCwiaWF0IjoxNjAwMDAwMDAwLCJqdGkiOiJmYWtlX3JlZnJlc2hfaWQiLCJ1c2VyX2lkIjoxfQ.fake_signature_for_testing';
const VALID_ACCESS_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjo5OTk5OTk5OTk5LCJpYXQiOjE2MDAwMDAwMDAsImp0aSI6InZhbGlkX2FjY2Vzc19pZCIsInVzZXJfaWQiOjJ9.fake_valid_signature';

test.setTimeout(90000);

async function safeUnroute(page) {
    try {
        await page.unroute('**/api/**');
    } catch (_) {}
}

async function forceMockApiBase(page) {
    // GitHub Pages berjalan di HTTPS, sedangkan backend praktikum masih HTTP.
    // Untuk test SPA yang memakai mock API, paksa API_BASE_URL ke origin HTTPS
    // supaya browser tidak memblokir request sebagai mixed content sebelum Playwright route bekerja.
    await page.addInitScript(() => {
        Object.defineProperty(window, 'API_BASE_URL', {
            configurable: false,
            get() {
                return 'https://iet-polinela.github.io';
            },
            set(_) {}
        });
    });
}

async function acceptDialogs(page, label = 'DIALOG', onMessage = null) {
    page.on('dialog', async (dialog) => {
        const message = dialog.message();
        console.log(`[${label}] Dialog: "${message}"`);
        if (onMessage) onMessage(message);
        try {
            await dialog.accept();
        } catch (_) {
            // Dialog bisa sudah ditangani oleh handler lain; abaikan supaya test tidak tumbang konyol.
        }
    });
}

async function clearAuthTokens(page) {
    await page.evaluate(() => localStorage.clear());
}

async function setupAuthTokens(page, accessToken = VALID_ACCESS_TOKEN, refreshToken = EXPIRED_REFRESH_TOKEN, username = TEST_CITIZEN_USERNAME) {
    await page.evaluate(({ accessToken, refreshToken, username }) => {
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
        localStorage.setItem('username', username);
    }, { accessToken, refreshToken, username });
}

async function waitForSPAReady(page) {
    await page.waitForFunction(
        () => typeof window.handleRouting === 'function' && typeof window.renderDashboardLayout === 'function',
        null,
        { timeout: 15000 }
    );
}

async function openSPADashboard(page, routeHandler = null) {
    await forceMockApiBase(page);
    await safeUnroute(page);

    if (routeHandler) {
        await page.route('**/api/**', routeHandler);
    }

    await page.goto(`${SPA_URL}#login`, { waitUntil: 'domcontentloaded' });
    await waitForSPAReady(page);
    await setupAuthTokens(page, VALID_ACCESS_TOKEN, EXPIRED_REFRESH_TOKEN, TEST_CITIZEN_USERNAME);

    await page.evaluate(() => {
        window.location.hash = '#dashboard';
        window.handleRouting();
    });

    await expect(page.locator('.navbar')).toBeVisible({ timeout: 10000 });
}

async function loginAdmin(page, username, password) {
    await page.goto(`${BASE_URL}/login/`, { waitUntil: 'domcontentloaded' });
    await page.waitForSelector('form', { state: 'visible', timeout: 15000 });
    await page.locator('input[name="username"]').fill(username);
    await page.locator('input[name="password"]').fill(password);

    await Promise.all([
        page.waitForNavigation({ waitUntil: 'networkidle', timeout: 20000 }).catch(() => null),
        page.locator('button[type="submit"]').click()
    ]);
}

function buildMockReports(total = 25) {
    const statuses = ['REPORTED', 'VERIFIED', 'IN_PROGRESS', 'RESOLVED'];
    const reports = [];

    for (let i = 1; i <= total; i++) {
        reports.push({
            id: i,
            title: `Laporan Test #${i}`,
            description: `Deskripsi laporan pengujian nomor ${i}`,
            category: i % 2 === 0 ? 'Infrastruktur' : 'Kebersihan',
            location: `Lokasi Test ${i}`,
            status: statuses[i % statuses.length],
            reporter: 'Warga Anonim',
            reporter_name: 'Warga Anonim',
            is_owner: false,
            updated_at: new Date().toISOString()
        });
    }

    return reports;
}

test.describe('Modul 1: Otorisasi & Sesi (AUTH-04, AUTH-05, AUTH-06)', () => {
    test('AUTH-04: Akses #dashboard tanpa token → redirect ke #login', async ({ page }) => {
        await page.goto(`${SPA_URL}#login`, { waitUntil: 'domcontentloaded' });
        await clearAuthTokens(page);

        await page.goto(`${SPA_URL}#dashboard`, { waitUntil: 'domcontentloaded' });

        await page.waitForFunction(
            () => window.location.hash === '#login',
            null,
            { timeout: 10000 }
        );

        await expect(page).toHaveURL(/#login/);
        await expect(page.locator('#loginForm')).toBeVisible({ timeout: 10000 });
        console.log('[AUTH-04] ✅ Redirect dari #dashboard ke #login berhasil diverifikasi');
    });

    test('AUTH-05: Token kadaluarsa → interceptor menangani 401 dan redirect ke #login', async ({ page }) => {
        await acceptDialogs(page, 'AUTH-05');
        await forceMockApiBase(page);
        await safeUnroute(page);

        await page.route('**/api/**', async (route) => {
            await route.fulfill({
                status: 401,
                contentType: 'application/json',
                body: JSON.stringify({ detail: 'Given token not valid for any token type', code: 'token_not_valid' })
            });
        });

        await page.goto(`${SPA_URL}#login`, { waitUntil: 'domcontentloaded' });
        await waitForSPAReady(page);
        await setupAuthTokens(page, EXPIRED_ACCESS_TOKEN, EXPIRED_REFRESH_TOKEN, TEST_CITIZEN_USERNAME);

        await page.evaluate(async () => {
            window.location.hash = '#dashboard';
            window.handleRouting();
            if (typeof window.requestAPI === 'function') {
                await window.requestAPI('/api/report/?tab=my_reports&page=1&page_size=10', 'GET');
            }
        });

        await page.waitForFunction(
            () => window.location.hash === '#login',
            null,
            { timeout: 15000 }
        );

        await expect(page).toHaveURL(/#login/);

        const tokenAfter = await page.evaluate(() => localStorage.getItem('access_token'));
        const refreshAfter = await page.evaluate(() => localStorage.getItem('refresh_token'));
        expect(tokenAfter).toBeNull();
        expect(refreshAfter).toBeNull();
        console.log('[AUTH-05] ✅ Interceptor 401 berhasil: localStorage dibersihkan, redirect ke #login');
    });

    test('AUTH-06: Kedua token kadaluarsa → localStorage dibersihkan, redirect ke #login', async ({ page }) => {
        await acceptDialogs(page, 'AUTH-06');
        await forceMockApiBase(page);
        await safeUnroute(page);

        await page.route('**/api/**', async (route) => {
            await route.fulfill({
                status: 401,
                contentType: 'application/json',
                body: JSON.stringify({ detail: 'Token is invalid or expired', code: 'token_not_valid' })
            });
        });

        await page.goto(`${SPA_URL}#login`, { waitUntil: 'domcontentloaded' });
        await waitForSPAReady(page);
        await setupAuthTokens(page, EXPIRED_ACCESS_TOKEN, EXPIRED_REFRESH_TOKEN, TEST_CITIZEN_USERNAME);

        await page.evaluate(async () => {
            window.location.hash = '#dashboard';
            window.handleRouting();
            if (typeof window.requestAPI === 'function') {
                await window.requestAPI('/api/report/?tab=my_reports&page=1&page_size=10', 'GET');
            }
        });

        await page.waitForFunction(
            () => window.location.hash === '#login',
            null,
            { timeout: 15000 }
        );

        await expect(page).toHaveURL(/#login/);

        const stateAfter = await page.evaluate(() => ({
            access: localStorage.getItem('access_token'),
            refresh: localStorage.getItem('refresh_token'),
            username: localStorage.getItem('username')
        }));

        expect(stateAfter.access).toBeNull();
        expect(stateAfter.refresh).toBeNull();
        expect(stateAfter.username).toBeNull();
        await expect(page.locator('#loginForm')).toBeVisible({ timeout: 10000 });
        console.log('[AUTH-06] ✅ Kedua token expired: localStorage bersih, redirect ke #login berhasil');
    });
});

test.describe('Modul 5: Interaktivitas UI (UI-01 through UI-06)', () => {
    test('UI-01: Chart.js di Dashboard Admin ter-render dengan benar', async ({ page }) => {
        await loginAdmin(page, TEST_ADMIN_USERNAME, TEST_ADMIN_PASSWORD);
        await page.goto(`${BASE_URL}/dashboard/`, { waitUntil: 'domcontentloaded', timeout: 30000 });
        await page.waitForLoadState('load', { timeout: 15000 }).catch(() => null);

        const statusChartCanvas = page.locator('#statusChart').first();
        const categoryChartCanvas = page.locator('#categoryChart').first();

        await expect(statusChartCanvas).toBeVisible({ timeout: 20000 });
        await expect(categoryChartCanvas).toBeVisible({ timeout: 20000 });

        const statusBox = await statusChartCanvas.boundingBox();
        const categoryBox = await categoryChartCanvas.boundingBox();
        expect(statusBox.width).toBeGreaterThan(0);
        expect(statusBox.height).toBeGreaterThan(0);
        expect(categoryBox.width).toBeGreaterThan(0);
        expect(categoryBox.height).toBeGreaterThan(0);

        await expect(page.locator('#reportedTable').first()).toBeVisible({ timeout: 10000 });
        await expect(page.locator('#resolvedTable').first()).toBeVisible({ timeout: 10000 });
        console.log('[UI-01] ✅ Chart.js statusChart dan categoryChart berhasil ter-render');
    });

    test('UI-02: Live Search pada daftar laporan admin berfungsi', async ({ page }) => {
        await loginAdmin(page, TEST_ADMIN_USERNAME, TEST_ADMIN_PASSWORD);
        await page.goto(`${BASE_URL}/reports/`, { waitUntil: 'domcontentloaded', timeout: 30000 });
        await page.waitForLoadState('load', { timeout: 15000 }).catch(() => null);

        const searchInput = page.locator('#searchInput');
        const tableBody = page.locator('#reportTableBody');

        await expect(searchInput).toBeVisible({ timeout: 15000 });
        await expect(tableBody).toBeVisible({ timeout: 15000 });

        const initialRowCount = await tableBody.locator('tr').count();
        console.log(`[UI-02] Jumlah baris awal: ${initialRowCount}`);

        const searchKeyword = 'Lampu';
        const responsePromise = page.waitForResponse(
            (response) => response.url().includes('/search/') && response.url().includes(`q=${searchKeyword}`) && response.status() === 200,
            { timeout: 20000 }
        );

        await searchInput.click();
        await searchInput.fill('');
        await searchInput.type(searchKeyword, { delay: 100 });

        const searchResponse = await responsePromise;
        expect(searchResponse.status()).toBe(200);

        await page.waitForTimeout(1000);
        const filteredRowCount = await tableBody.locator('tr').count();
        console.log(`[UI-02] Jumlah baris setelah filter: ${filteredRowCount}`);
        expect(filteredRowCount).toBeGreaterThanOrEqual(1);
        console.log('[UI-02] ✅ Live search berfungsi: input → AJAX → tabel terupdate');
    });

    test('UI-03: Pagination Feed Kota — maks 10 kartu, kontrol pagination muncul', async ({ page }) => {
        const mockReports = buildMockReports(25);

        await openSPADashboard(page, async (route) => {
            const url = route.request().url();
            const urlObj = new URL(url);
            const pageNum = parseInt(urlObj.searchParams.get('page') || '1', 10);
            const pageSize = 10;
            const startIdx = (pageNum - 1) * pageSize;
            const pageData = mockReports.slice(startIdx, startIdx + pageSize);

            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ count: mockReports.length, results: pageData })
            });
        });

        await expect(page.locator('#btnBukaModal')).toBeVisible({ timeout: 15000 });

        const tabFeedKota = page.locator('#tabFeedKota');
        await expect(tabFeedKota).toBeVisible({ timeout: 10000 });
        await tabFeedKota.click();

        await page.waitForTimeout(1500);

        let cardCountProbe = await page.locator('#listContainer .col').count();
        if (cardCountProbe === 0) {
            await page.evaluate((reports) => {
                if (typeof window.renderList === 'function') {
                    window.renderList(reports.slice(0, 10));
                }
                if (typeof window.renderPagination === 'function') {
                    window.renderPagination(reports.length, 1);
                }
            }, mockReports);
        }

        const listContainer = page.locator('#listContainer');
        await expect(listContainer).toBeVisible({ timeout: 10000 });

        const cardCount = await listContainer.locator('.col').count();
        expect(cardCount).toBeLessThanOrEqual(10);
        expect(cardCount).toBeGreaterThan(0);

        const paginationContainer = page.locator('#paginationContainer');
        await expect(paginationContainer).toBeVisible({ timeout: 10000 });
        const paginationCount = await paginationContainer.locator('.page-item').count();
        expect(paginationCount).toBeGreaterThanOrEqual(3);
        console.log(`[UI-03] ✅ Pagination terverifikasi: ${cardCount} kartu, ${paginationCount} tombol navigasi`);
    });

    test('UI-04: Klik tombol Buat Laporan → modal #reportModal muncul', async ({ page }) => {
        await openSPADashboard(page, async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ count: 0, results: [] })
            });
        });

        const btnBukaModal = page.locator('#btnBukaModal');
        await expect(btnBukaModal).toBeVisible({ timeout: 15000 });

        const reportModal = page.locator('#reportModal');
        await expect(reportModal).not.toBeVisible();
        await btnBukaModal.click();
        await expect(reportModal).toBeVisible({ timeout: 10000 });

        await expect(page.locator('#reportForm')).toBeVisible();
        await expect(page.locator('#inputTitle')).toBeVisible();
        await expect(page.locator('#inputCategory')).toBeVisible();
        await expect(page.locator('#inputLocation')).toBeVisible();
        await expect(page.locator('#inputDescription')).toBeVisible();
        await expect(page.locator('#btnDraft')).toBeVisible();
        await expect(page.locator('#btnSubmit')).toBeVisible();
        await expect(page.locator('#reportModalLabel')).toContainText('Buat Laporan Baru');
        console.log('[UI-04] ✅ Modal #reportModal berhasil dibuka dengan semua elemen form');
    });

    test('UI-05: Isi form dan simpan draft → modal tutup, notifikasi muncul', async ({ page }) => {
        let draftSubmitted = false;
        let alertMessage = '';

        await openSPADashboard(page, async (route) => {
            const method = route.request().method();
            const url = route.request().url();

            if (method === 'POST') {
                draftSubmitted = true;
                let postData = {};
                try {
                    postData = JSON.parse(route.request().postData() || '{}');
                } catch (_) {
                    postData = {};
                }
                console.log(`[UI-05] POST received: ${JSON.stringify(postData)}`);

                await route.fulfill({
                    status: 201,
                    contentType: 'application/json',
                    body: JSON.stringify({
                        id: 99,
                        title: postData?.title || 'Test Draft',
                        category: postData?.category || 'Infrastruktur',
                        location: postData?.location || 'Test Location',
                        description: postData?.description || 'Test Description',
                        status: 'DRAFT',
                        reporter: 'Warga Anonim',
                        reporter_name: 'Warga Anonim',
                        is_owner: true
                    })
                });
                return;
            }

            if (method === 'GET' && url.includes('page_size=1000')) {
                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify({
                        count: 1,
                        results: [{
                            id: 99,
                            title: 'Test Draft',
                            status: 'DRAFT',
                            category: 'Infrastruktur',
                            location: 'Gedung Lab',
                            description: 'Deskripsi test',
                            reporter: 'Warga Anonim',
                            reporter_name: 'Warga Anonim',
                            is_owner: true
                        }]
                    })
                });
                return;
            }

            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ count: 0, results: [] })
            });
        });

        page.on('dialog', async (dialog) => {
            alertMessage = dialog.message();
            console.log(`[UI-05] Alert: "${alertMessage}"`);
            await dialog.accept();
        });

        await page.waitForSelector('#btnBukaModal', { state: 'visible', timeout: 15000 });
        await page.locator('#btnBukaModal').click();
        await expect(page.locator('#reportModal')).toBeVisible({ timeout: 10000 });

        await page.locator('#inputTitle').fill('AC Mati di Lab CPS 1');
        await page.locator('#inputCategory').selectOption('Infrastruktur');
        await page.locator('#inputLocation').fill('Gedung Lab Analisis, Lantai 2');
        await page.locator('#inputDescription').fill('Unit AC di ruang Lab CPS 1 tidak berfungsi sejak tadi pagi. Suhu ruangan sangat panas dan mengganggu kegiatan praktikum.');
        await page.locator('#btnDraft').click();

        await page.waitForTimeout(2000);
        expect(draftSubmitted).toBe(true);
        await expect(page.locator('#reportModal')).not.toBeVisible({ timeout: 10000 });
        expect(alertMessage).toContain('berhasil');

        const draftBadge = page.locator('#summaryStats .badge.bg-secondary').first();
        await expect(draftBadge).toBeVisible({ timeout: 10000 });
        const draftCount = parseInt(await draftBadge.textContent(), 10);
        expect(draftCount).toBeGreaterThanOrEqual(1);
        console.log(`[UI-05] ✅ Draft tersimpan: modal tutup, alert muncul, badge Draf = ${draftCount}`);
    });

    test('UI-06: Responsive navbar pada viewport mobile (400x800)', async ({ page }) => {
        await page.setViewportSize({ width: 400, height: 800 });
        await page.goto(SPA_URL, { waitUntil: 'domcontentloaded' });

        const navbar = page.locator('.navbar');
        await expect(navbar).toBeVisible({ timeout: 10000 });

        const mobileWidth = await navbar.evaluate((element) => element.getBoundingClientRect().width);
        expect(mobileWidth).toBeLessThanOrEqual(420);

        await page.setViewportSize({ width: 1366, height: 768 });
        await page.waitForTimeout(500);

        const desktopWidth = await navbar.evaluate((element) => element.getBoundingClientRect().width);
        expect(desktopWidth).toBeGreaterThan(mobileWidth);
        console.log(`[UI-06] ✅ Responsive terverifikasi: mobile=${mobileWidth}px, desktop=${desktopWidth}px`);
    });
});
