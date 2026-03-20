// ══ 드라마 LIFE — Main JS ══

// Mobile menu
const navToggle = document.getElementById('navToggle');
const mobileMenu = document.getElementById('mobileMenu');

if (navToggle && mobileMenu) {
    navToggle.addEventListener('click', () => {
        const isOpen = mobileMenu.classList.contains('open');
        if (!isOpen) {
            // reset animations so they replay each open
            mobileMenu.querySelectorAll('li').forEach(li => {
                li.style.opacity = '0';
                li.style.transform = 'translateY(20px)';
            });
            mobileMenu.classList.add('open');
            // force reflow then let CSS transitions run
            requestAnimationFrame(() => {
                mobileMenu.querySelectorAll('li').forEach(li => {
                    li.style.opacity = '';
                    li.style.transform = '';
                });
            });
        } else {
            mobileMenu.classList.remove('open');
        }
        document.body.style.overflow = mobileMenu.classList.contains('open') ? 'hidden' : '';
    });

    mobileMenu.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            mobileMenu.classList.remove('open');
            document.body.style.overflow = '';
        });
    });
}

// Nav scroll effect
const nav = document.querySelector('.nav');
window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        nav.style.background = 'rgba(2,11,24,0.97)';
        nav.style.borderBottomColor = 'rgba(255,255,255,0.06)';
    } else {
        nav.style.background = 'linear-gradient(to bottom, rgba(2,11,24,0.95) 0%, transparent 100%)';
        nav.style.borderBottomColor = 'rgba(255,255,255,0.04)';
    }
}, { passive: true });

// Intersection Observer for fade-ins
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.animationPlayState = 'running';
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

document.querySelectorAll('.fade-in').forEach(el => {
    el.style.animationPlayState = 'paused';
    observer.observe(el);
});

// Smooth parallax on hero backdrop
const heroBg = document.querySelector('.hero-backdrop img');
if (heroBg) {
    window.addEventListener('scroll', () => {
        const y = window.scrollY;
        heroBg.style.transform = `translateY(${y * 0.3}px)`;
    }, { passive: true });
}