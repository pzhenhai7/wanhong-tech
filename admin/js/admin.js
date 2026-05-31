/* ===== 涓囨硴绉戞妧 鈥?鍚庡彴绠＄悊绯荤粺 JS ===== */

// ===== State =====
let APP = {
    token: '',
    mode: 'local',        // 'local' | 'github'
    products: [],
    settings: {},
    currentPage: 'dashboard-overview',
};

const GITHUB_REPO = 'pzhenhai7/wanhong-tech';
const GITHUB_BRANCH = 'main';
const PRODUCTS_PATH = 'data/products.json';
const ADMIN_USER = 'admin';
const ADMIN_PASS = 'wanhong888';

// ===== Init =====
document.addEventListener('DOMContentLoaded', () => {
    // Check session
    const saved = sessionStorage.getItem('wanhong_admin');
    if (saved) {
        try {
            const data = JSON.parse(saved);
            APP.token = data.token || '';
            APP.mode = data.mode || 'local';
            document.getElementById('loginPage').style.display = 'none';
            document.getElementById('dashboard').style.display = 'flex';
            initDashboard();
        } catch { sessionStorage.removeItem('wanhong_admin'); }
    }

    // Login tab switch
    document.querySelectorAll('.login-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.login-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const isPass = tab.dataset.tab === 'password';
            document.getElementById('loginPassword').style.display = isPass ? 'flex' : 'none';
            document.getElementById('loginToken').style.display = isPass ? 'none' : 'flex';
        });
    });

    // Sidebar navigation
    document.querySelectorAll('.sidebar-item').forEach(item => {
        item.addEventListener('click', () => switchPage(item.dataset.page));
    });
});

// ===== Login =====
function loginWithPassword() {
    const user = document.getElementById('loginUser').value.trim();
    const pass = document.getElementById('loginPass').value.trim();
    const err = document.getElementById('loginError');
    if (user === ADMIN_USER && pass === ADMIN_PASS) {
        APP.token = '';
        APP.mode = 'local';
        err.style.display = 'none';
        sessionStorage.setItem('wanhong_admin', JSON.stringify({ token: '', mode: 'local' }));
        document.getElementById('loginPage').style.display = 'none';
        document.getElementById('dashboard').style.display = 'flex';
        initDashboard();
    } else {
        err.textContent = '璐﹀彿鎴栧瘑鐮侀敊璇?;
        err.style.display = 'block';
    }
}

function loginWithToken() {
    const token = document.getElementById('loginTokenInput').value.trim();
    const err = document.getElementById('loginError');
    if (!token.startsWith('ghp_') && !token.startsWith('github_pat_')) {
        err.textContent = '璇疯緭鍏ユ湁鏁堢殑GitHub Token (ghp_ 鎴?github_pat_ 寮€澶?';
        err.style.display = 'block';
        return;
    }
    APP.token = token;
    APP.mode = 'github';
    err.style.display = 'none';
    sessionStorage.setItem('wanhong_admin', JSON.stringify({ token, mode: 'github' }));
    document.getElementById('loginPage').style.display = 'none';
    document.getElementById('dashboard').style.display = 'flex';
    initDashboard();
}

function logout() {
    sessionStorage.removeItem('wanhong_admin');
    APP.token = '';
    APP.mode = 'local';
    document.getElementById('loginPage').style.display = 'flex';
    document.getElementById('dashboard').style.display = 'none';
    document.getElementById('loginError').style.display = 'none';
    document.getElementById('loginUser').value = '';
    document.getElementById('loginPass').value = '';
}

// ===== Dashboard Init =====
async function initDashboard() {
    updateModeBadge();
    showStatus('姝ｅ湪鍔犺浇鏁版嵁...', '');
    if (APP.mode === 'github') {
        await syncFromGithub();
    } else {
        await loadLocalData();
    }
    hideStatus();
    renderDashboard();
}

function updateModeBadge() {
    const badge = document.getElementById('loginModeBadge');
    if (APP.mode === 'github') {
        badge.textContent = '鉁?GitHub宸茶繛鎺?;
        badge.dataset.mode = 'github';
        badge.style.background = '#d4edda';
        badge.style.color = '#155724';
    } else {
        badge.textContent = '鏈湴妯″紡锛堟湭杩炴帴GitHub锛?;
        badge.dataset.mode = 'local';
    }
}

function showStatus(msg, type = '') {
    const bar = document.getElementById('statusBar');
    const text = document.getElementById('statusText');
    bar.style.display = 'flex';
    bar.className = 'status-bar' + (type ? ' ' + type : '');
    text.textContent = msg;
}

function hideStatus() {
    document.getElementById('statusBar').style.display = 'none';
}

// ===== Data Loading =====
async function loadLocalData() {
    try {
        const resp = await fetch('../data/products.json?_=' + Date.now());
        const data = await resp.json();
        APP.products = data.products || [];
        APP.settings = data.settings || {};
        APP.settings.githubToken = '';
    } catch {
        APP.products = [];
        APP.settings = {};
    }
}

async function syncFromGithub() {
    if (APP.mode !== 'github' || !APP.token) {
        showToast('璇蜂娇鐢℅itHub Token鐧诲綍', 'error');
        return;
    }
    showStatus('姝ｅ湪浠嶨itHub鍚屾鏁版嵁...', '');
    try {
        const resp = await fetch(`https://api.github.com/repos/${GITHUB_REPO}/contents/${PRODUCTS_PATH}`, {
            headers: { 'Authorization': 'token ' + APP.token, 'Accept': 'application/vnd.github.v3+json' }
        });
        if (!resp.ok) throw new Error('GitHub API鍝嶅簲: ' + resp.status);
        const json = await resp.json();
        const content = atob(json.content.replace(/\n/g, ''));
        const data = JSON.parse(content);
        APP.products = data.products || [];
        APP.settings = data.settings || {};
        localStorage.setItem('wanhong_settings', JSON.stringify(APP.settings));
        showStatus('鉁?鏁版嵁鍚屾鎴愬姛锛佸叡 ' + APP.products.length + ' 涓骇鍝?, '');
        setTimeout(hideStatus, 2000);
        renderDashboard();
        showToast('鏁版嵁鍚屾鎴愬姛');
    } catch (e) {
        showStatus('鉂?鍚屾澶辫触: ' + e.message, 'error');
        // Fallback to local
        await loadLocalData();
        renderDashboard();
    }
}

async function publishToGithub() {
    if (APP.mode !== 'github' || !APP.token) {
        showToast('璇蜂娇鐢℅itHub Token鐧诲綍鍚庢墠鑳藉彂甯?, 'error');
        return;
    }
    showStatus('姝ｅ湪鍙戝竷鍒癎itHub...', '');

    // Merge settings
    APP.settings.githubToken = '';

    const content = JSON.stringify({ products: APP.products, settings: APP.settings }, null, 2);

    try {
        // Get current file SHA
        let sha = '';
        try {
            const resp = await fetch(`https://api.github.com/repos/${GITHUB_REPO}/contents/${PRODUCTS_PATH}`, {
                headers: { 'Authorization': 'token ' + APP.token, 'Accept': 'application/vnd.github.v3+json' }
            });
            if (resp.ok) {
                const json = await resp.json();
                sha = json.sha;
            }
        } catch {}

        // Commit
        const commitResp = await fetch(`https://api.github.com/repos/${GITHUB_REPO}/contents/${PRODUCTS_PATH}`, {
            method: 'PUT',
            headers: { 'Authorization': 'token ' + APP.token, 'Accept': 'application/vnd.github.v3+json', 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: '馃攧 鍚庡彴鏇存柊浜у搧鏁版嵁 - ' + new Date().toLocaleString('zh-CN'),
                content: btoa(unescape(encodeURIComponent(content))),
                sha: sha || undefined,
                branch: GITHUB_BRANCH
            })
        });

        if (!commitResp.ok) {
            const err = await commitResp.json();
            throw new Error(err.message || '鎻愪氦澶辫触');
        }

        showStatus('鉁?宸叉垚鍔熷彂甯冨埌GitHub锛佺瓑寰匬ages鑷姩閮ㄧ讲...', '');
        setTimeout(hideStatus, 3000);
        showToast('鍙戝竷鎴愬姛锛?);
    } catch (e) {
        showStatus('鉂?鍙戝竷澶辫触: ' + e.message, 'error');
        showToast('鍙戝竷澶辫触: ' + e.message, 'error');
    }
}

// ===== Render =====
function renderDashboard() {
    // Stats
    document.getElementById('statProducts').textContent = APP.products.length;
    const cats = new Set(APP.products.map(p => p.category));
    document.getElementById('statCategories').textContent = cats.size;
    document.getElementById('statOrders').textContent = '鈥?;
    document.getElementById('statStatus').textContent = APP.mode === 'github' ? '宸茶繛鎺itHub' : '鏈湴妯″紡';
    document.getElementById('statStatus').style.color = APP.mode === 'github' ? '#155724' : '#856404';

    // Product list
    renderProductList();

    // Settings
    renderSettings();
}

// ===== Product List =====
function renderProductList() {
    const list = document.getElementById('productList');
    if (APP.products.length === 0) {
        list.innerHTML = '<div class="empty-state"><p>杩樻病鏈変骇鍝侊紝鐐瑰嚮鍙充笂瑙掓坊鍔?/p></div>';
        return;
    }
    list.innerHTML = APP.products.map((p, i) => `
        <div class="product-card">
            <div class="pc-img">
                ${p.image ? `<img src="../${p.image}" alt="${p.name}">` : p.id}
            </div>
            <div class="pc-info">
                <div class="pc-name">${p.name}</div>
                <div class="pc-meta">${p.category} 路 ${p.subtitle || ''} 路 ID: ${p.id}</div>
            </div>
            <div class="pc-price">楼${p.price.toFixed(2)}</div>
            <div class="pc-actions">
                <button class="pc-btn pc-btn-edit" onclick="editProduct(${i})">缂栬緫</button>
                <button class="pc-btn pc-btn-del" onclick="deleteProduct(${i})">鍒犻櫎</button>
            </div>
        </div>
    `).join('');
}

// ===== Product CRUD =====
function showAddProduct() {
    document.getElementById('modalTitle').textContent = '娣诲姞浜у搧';
    document.getElementById('editProductId').value = '';
    ['pf_id','pf_name','pf_subtitle','pf_price','pf_tag','pf_description','pf_fullDesc','pf_apps','pf_image'].forEach(id => {
        document.getElementById(id).value = '';
    });
    document.getElementById('pf_category').value = '鐢靛瓙鐑熺數姹?;
    document.getElementById('pf_featured').checked = false;
    document.getElementById('modalError').style.display = 'none';
    // Reset specs
    document.getElementById('specEditor').innerHTML = `
        <div class="spec-row">
            <input class="form-input spec-key" placeholder="鍙傛暟鍚?>
            <input class="form-input spec-val" placeholder="鍙傛暟鍊?>
            <button class="btn-sm btn-add" onclick="addSpecRow()">+</button>
        </div>
    `;
    document.getElementById('productModal').style.display = 'flex';
}

function editProduct(index) {
    const p = APP.products[index];
    document.getElementById('modalTitle').textContent = '缂栬緫浜у搧';
    document.getElementById('editProductId').value = index;
    document.getElementById('pf_id').value = p.id;
    document.getElementById('pf_name').value = p.name;
    document.getElementById('pf_subtitle').value = p.subtitle || '';
    document.getElementById('pf_category').value = p.category || '鐢靛瓙鐑熺數姹?;
    document.getElementById('pf_price').value = p.price;
    document.getElementById('pf_tag').value = p.tag || '';
    document.getElementById('pf_description').value = p.description || '';
    document.getElementById('pf_fullDesc').value = (p.fullDescription || '').replace(/<br>/g, '\n');
    document.getElementById('pf_apps').value = (p.applications || []).join(', ');
    document.getElementById('pf_image').value = p.image || '';
    document.getElementById('pf_featured').checked = p.featured || false;
    document.getElementById('modalError').style.display = 'none';

    // Specs
    const specEditor = document.getElementById('specEditor');
    const specs = p.specList || [];
    if (specs.length === 0) {
        specEditor.innerHTML = `<div class="spec-row"><input class="form-input spec-key" placeholder="鍙傛暟鍚?><input class="form-input spec-val" placeholder="鍙傛暟鍊?><button class="btn-sm btn-add" onclick="addSpecRow()">+</button></div>`;
    } else {
        specEditor.innerHTML = specs.map((s, i) => `
            <div class="spec-row">
                <input class="form-input spec-key" value="${s.label}">
                <input class="form-input spec-val" value="${s.value}">
                <button class="btn-sm ${i === 0 ? 'btn-add' : 'btn-cancel'}" onclick="${i === 0 ? 'addSpecRow()' : 'this.parentElement.remove()'}">${i === 0 ? '+' : '鉁?}</button>
            </div>
        `).join('');
    }
    document.getElementById('productModal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('productModal').style.display = 'none';
}

function closeModalOnOverlay(e) {
    if (e.target.classList.contains('modal-overlay')) closeModal();
}

function addSpecRow() {
    const editor = document.getElementById('specEditor');
    const row = document.createElement('div');
    row.className = 'spec-row';
    row.innerHTML = `
        <input class="form-input spec-key" placeholder="鍙傛暟鍚?>
        <input class="form-input spec-val" placeholder="鍙傛暟鍊?>
        <button class="btn-sm btn-cancel" onclick="this.parentElement.remove()">鉁?/button>
    `;
    editor.appendChild(row);
}

function saveProduct() {
    const err = document.getElementById('modalError');
    err.style.display = 'none';

    const id = document.getElementById('pf_id').value.trim();
    const name = document.getElementById('pf_name').value.trim();
    const price = parseFloat(document.getElementById('pf_price').value);

    if (!id) { err.textContent = '璇疯緭鍏ヤ骇鍝両D'; err.style.display = 'block'; return; }
    if (!name) { err.textContent = '璇疯緭鍏ヤ骇鍝佸悕绉?; err.style.display = 'block'; return; }
    if (isNaN(price) || price <= 0) { err.textContent = '璇疯緭鍏ユ湁鏁堜环鏍?; err.style.display = 'block'; return; }

    // Collect specs
    const specList = [];
    document.querySelectorAll('#specEditor .spec-row').forEach(row => {
        const key = row.querySelector('.spec-key').value.trim();
        const val = row.querySelector('.spec-val').value.trim();
        if (key && val) specList.push({ label: key, value: val });
    });

    // Build specs object
    const specs = {};
    specList.forEach(s => { specs[s.label] = s.value; });

    const apps = document.getElementById('pf_apps').value.split(',').map(s => s.trim()).filter(Boolean);

    const product = {
        id,
        name,
        subtitle: document.getElementById('pf_subtitle').value.trim(),
        fullName: name,
        category: document.getElementById('pf_category').value,
        price,
        priceDesc: '鍗曚环 / 鍚◣鍚繍璐癸紝鎵归噺浠锋牸鍙﹁',
        image: document.getElementById('pf_image').value.trim(),
        tag: document.getElementById('pf_tag').value.trim() || '',
        tagColor: 'orange',
        badge: document.getElementById('pf_tag').value.trim() || '',
        badgeType: 'new',
        featured: document.getElementById('pf_featured').checked,
        specs,
        features: [],
        applications: apps,
        description: document.getElementById('pf_description').value.trim(),
        fullDescription: document.getElementById('pf_fullDesc').value.trim() || `<p>${document.getElementById('pf_description').value.trim()}</p>`,
        specList,
        createdAt: new Date().toISOString().slice(0, 10)
    };

    const editIdx = document.getElementById('editProductId').value;
    if (editIdx !== '') {
        APP.products[parseInt(editIdx)] = product;
    } else {
        // Check duplicate ID
        if (APP.products.some(p => p.id === id)) {
            err.textContent = '浜у搧ID "' + id + '" 宸插瓨鍦紝璇蜂娇鐢ㄤ笉鍚岀殑ID';
            err.style.display = 'block';
            return;
        }
        APP.products.push(product);
    }

    closeModal();
    renderProductList();
    updateStats();
    showToast(editIdx !== '' ? '浜у搧宸叉洿鏂? : '浜у搧宸叉坊鍔?);
}

function deleteProduct(index) {
    if (!confirm('纭畾瑕佸垹闄?"' + APP.products[index].name + '" 鍚楋紵')) return;
    APP.products.splice(index, 1);
    renderProductList();
    updateStats();
    showToast('浜у搧宸插垹闄?);
}

function updateStats() {
    document.getElementById('statProducts').textContent = APP.products.length;
    const cats = new Set(APP.products.map(p => p.category));
    document.getElementById('statCategories').textContent = cats.size;
}

// ===== Settings =====
function renderSettings() {
    const s = APP.settings;
    document.getElementById('sf_companyName').value = s.companyName || '';
    document.getElementById('sf_phone').value = s.phone || '';
    document.getElementById('sf_email').value = s.email || '';
    document.getElementById('sf_contactPerson').value = s.contactPerson || '';
    document.getElementById('sf_address').value = s.address || '';
    if (APP.token) {
        document.getElementById('sf_githubToken').value = APP.token;
    }
}

function saveSettings() {
    APP.settings.companyName = document.getElementById('sf_companyName').value.trim();
    APP.settings.phone = document.getElementById('sf_phone').value.trim();
    APP.settings.email = document.getElementById('sf_email').value.trim();
    APP.settings.contactPerson = document.getElementById('sf_contactPerson').value.trim();
    APP.settings.address = document.getElementById('sf_address').value.trim();

    const tk = document.getElementById('sf_githubToken').value.trim();
    if (tk) APP.token = tk;

    document.getElementById('settingsStatus').textContent = '鉁?璁剧疆宸蹭繚瀛?;
    document.getElementById('settingsStatus').style.color = '#155724';
    setTimeout(() => { document.getElementById('settingsStatus').textContent = ''; }, 3000);
    showToast('璁剧疆宸蹭繚瀛?);
}

// ===== Utility =====
function switchPage(page) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.sidebar-item').forEach(p => p.classList.remove('active'));
    document.getElementById('page-' + page).classList.add('active');
    document.querySelector(`.sidebar-item[data-page="${page}"]`).classList.add('active');
    APP.currentPage = page;
}

function showToast(msg, type = 'success') {
    let t = document.querySelector('.admin-toast');
    if (!t) {
        t = document.createElement('div'); t.className = 'admin-toast';
        document.body.appendChild(t);
    }
    t.style.background = type === 'error' ? '#E55E00' : type === 'warning' ? '#856404' : '#00A65A';
    t.textContent = msg;
    t.style.opacity = '1';
    clearTimeout(t._timer);
    t._timer = setTimeout(() => { t.style.opacity = '0'; }, 3000);
}
