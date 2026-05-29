// 惠州市万泓科技有限公司 — 全站交互

// 购物车角标
function updateCartBadge() {
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
            else { e.preventDefault(); showToast('📄 产品详情页正在建设中...'); }
        });
    });

    // ===================== Hero btn
    document.querySelectorAll('.hero-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (this.getAttribute('href') === '#' || !this.getAttribute('href')) {
                e.preventDefault();
                showToast('📄 页面正在建设中，请联系廖总 13682629862');
            }
        });
    });

    // ===================== Feature btn
    const featuredBtn = document.querySelector('.featured-btn');
    if (featuredBtn) {
        featuredBtn.addEventListener('click', function(e) {
            if (this.getAttribute('href') === '#' || !this.getAttribute('href')) {
                e.preventDefault();
                showToast('📩 正在为您转接询盘流程...');
            }
        });
    }

    // ===================== Contact btn
    const contactBtn = document.querySelector('.contact-btn');
    if (contactBtn) {
        contactBtn.addEventListener('click', function(e) {
            if (this.getAttribute('href') === '#' || !this.getAttribute('href')) {
                e.preventDefault();
                showToast('📩 正在为您转接询盘流程...');
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
