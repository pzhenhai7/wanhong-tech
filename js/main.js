// 鎯犲窞甯備竾娉撶鎶€鏈夐檺鍏徃 鈥?鍏ㄧ珯浜や簰

// 璐墿杞﹁鏍?function updateCartBadge() {
    const badge = document.getElementById('cartBadge');
    if (!badge) return;
    try {
        const cart = JSON.parse(localStorage.getItem('wanhong_cart') || '[]');
        const total = cart.reduce((s, i) => s + i.qty, 0);
        badge.textContent = total;
        badge.style.display = total > 0 ? 'flex' : 'none';
    } catch {}
}

document.addEventListener('DOMContentLoaded', () => {
    updateCartBadge();

    // ===================== Toast
    function showToast(msg, type='success') {
        let t = document.getElementById('global-toast');
        if (!t) {
            t = document.createElement('div'); t.id = 'global-toast';
            t.style.cssText = 'position:fixed;bottom:40px;left:50%;transform:translateX(-50%);padding:14px 28px;border-radius:8px;font-size:14px;font-weight:500;color:#fff;z-index:9999;opacity:0;transition:opacity .4s,transform .4s;box-shadow:0 4px 20px rgba(0,0,0,.15);pointer-events:none;max-width:90vw;text-align:center;';
            document.body.appendChild(t);
        }
        t.style.background = type==='success' ? '#00A65A' : type==='error' ? '#E55E00' : '#333';
        t.textContent = msg;
        t.style.opacity = '1'; t.style.transform = 'translateX(-50%) translateY(0)';
        clearTimeout(t._timer);
        t._timer = setTimeout(() => { t.style.opacity = '0'; t.style.transform = 'translateX(-50%) translateY(20px)'; }, 3000);
    }

    // ===================== Carousel
    let currentSlide = 0;
    const slides = document.querySelectorAll('.carousel-slide');
    const dots = document.querySelectorAll('.dot');
    let autoTimer;

    window.goSlide = function(n) {
        slides.forEach(s => s.classList.remove('active'));
        dots.forEach(d => d.classList.remove('active'));
        currentSlide = n;
        slides[n].classList.add('active');
        dots[n].classList.add('active');
        resetAuto();
    };
    window.nextSlide = function() {
        goSlide((currentSlide + 1) % slides.length);
    };
    window.prevSlide = function() {
        goSlide((currentSlide - 1 + slides.length) % slides.length);
    };
    function resetAuto() {
        clearInterval(autoTimer);
        autoTimer = setInterval(nextSlide, 5000);
    }
    if (slides.length) resetAuto();

    // ===================== Nav scroll hide
    let lastScroll = 0;
    const nav = document.querySelector('.nav');
    window.addEventListener('scroll', () => {
        const cur = window.pageYOffset;
        if (cur > 120) {
            nav.style.transform = cur > lastScroll ? 'translateY(-100%)' : 'translateY(0)';
        } else { nav.style.transform = 'translateY(0)'; }
        lastScroll = cur;
    });

    // ===================== Mobile menu
    const toggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    if (toggle) {
        toggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });
        navMenu.querySelectorAll('a').forEach(a => {
            a.addEventListener('click', () => navMenu.classList.remove('active'));
        });
    }

    // ===================== Smooth nav links
    document.querySelectorAll('.nav-menu a').forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href && href.startsWith('#') && href.length > 1) {
                e.preventDefault();
                document.querySelector(href)?.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // ===================== Product buttons
    document.querySelectorAll('.product-showcase-card .ps-link, .product-showcase-card').forEach(el => {
        el.addEventListener('click', function(e) {
            const link = this.closest('.product-showcase-card')?.getAttribute('href');
            if (link && link !== '#') { if (e.target.tagName !== 'A') window.location.href = link; }
            else { e.preventDefault(); showToast('馃搫 浜у搧璇︽儏椤垫鍦ㄥ缓璁句腑...'); }
        });
    });

    // ===================== Hero btn
    document.querySelectorAll('.hero-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (this.getAttribute('href') === '#' || !this.getAttribute('href')) {
                e.preventDefault();
                showToast('馃搫 椤甸潰姝ｅ湪寤鸿涓紝璇疯仈绯诲粬鎬?13682629862');
            }
        });
    });

    // ===================== Feature btn
    const featuredBtn = document.querySelector('.featured-btn');
    if (featuredBtn) {
        featuredBtn.addEventListener('click', function(e) {
            if (this.getAttribute('href') === '#' || !this.getAttribute('href')) {
                e.preventDefault();
                showToast('馃摡 姝ｅ湪涓烘偍杞帴璇㈢洏娴佺▼...');
            }
        });
    }

    // ===================== Contact btn
    const contactBtn = document.querySelector('.contact-btn');
    if (contactBtn) {
        contactBtn.addEventListener('click', function(e) {
            if (this.getAttribute('href') === '#' || !this.getAttribute('href')) {
                e.preventDefault();
                showToast('馃摡 姝ｅ湪涓烘偍杞帴璇㈢洏娴佺▼...');
            }
        });
    }

    // ===================== Footer links
    document.querySelectorAll('.footer-col a').forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href && href.startsWith('#') && href.length > 1) {
                e.preventDefault();
                document.querySelector(href)?.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // ===================== Load products from JSON
    loadProducts();

    // ===================== Intersection Observer for fade-in
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.product-showcase-card, .showcase-card, .featured-product, .contact-wrap').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity .8s ease, transform .8s ease';
        observer.observe(el);
    });

});

// ===== Dynamic Product Loading =====
async function loadProducts() {
    try {
        const resp = await fetch('data/products.json?_=' + Date.now());
        const data = await resp.json();
        const products = data.products || [];

        // Render product showcase
        renderProductCards(products);

        // Render featured product
        const featured = products.find(p => p.featured) || products[0];
        if (featured) renderFeaturedProduct(featured);

        // Update carousel CTA links
        updateCarouselLinks(products);
    } catch {}
}

function renderProductCards(products) {
    const container = document.getElementById('productShowcase');
    if (!container) return;

    const colors = ['orange', '#0071e3', '#34c759', '#af52de'];
    container.innerHTML = products.map((p, i) => `
        <a href="product.html?id=${p.id}" class="product-showcase-card" data-index="${i}">
            <div class="ps-card-img">
                ${p.image
                    ? `<img src="${p.image}" alt="${p.name}" style="width:100%;height:100%;object-fit:cover;border-radius:8px;">`
                    : `<div class="ps-placeholder">${p.id.replace(/[^0-9a-zA-Z]/g,'')}</div>`
                }
                ${p.badge ? `<span class="ps-badge" style="${p.badgeType === 'hot' ? 'background:#0071e3;' : ''}">${p.badge}</span>` : ''}
            </div>
            <h3>${p.name}</h3>
            <p>${p.subtitle || ''}</p>
            <span class="ps-link">鏌ョ湅璇︽儏 鈫?/span>
        </a>
    `).join('');
}

function renderFeaturedProduct(product) {
    const section = document.getElementById('featuredProductSection');
    if (!section) return;

    const info = section.querySelector('.featured-info');
    const visual = section.querySelector('.featured-visual');

    if (info) {
        info.innerHTML = `
            <span class="featured-tag">馃敟 鐑崠鎺ㄨ崘</span>
            <h2>${product.fullName || product.name}</h2>
            <ul class="featured-list">
                ${(product.features || []).slice(0, 4).map(f => `<li>鉁?${f}</li>`).join('')}
            </ul>
            <a href="product.html?id=${product.id}" class="featured-btn">绔嬪嵆璇㈢洏 鈫?/a>
        `;
    }
    if (visual) {
        visual.innerHTML = product.image
            ? `<img src="${product.image}" alt="${product.name}" style="width:100%;height:100%;object-fit:contain;border-radius:12px;padding:20px;">`
            : `<div class="fv-placeholder">${product.id}</div>`;
    }
}

function updateCarouselLinks(products) {
    const btns = document.querySelectorAll('.hero-btn');
    if (btns.length > 0 && products.length > 0) {
        btns[0].href = 'product.html?id=' + products[0].id;
    }
}
