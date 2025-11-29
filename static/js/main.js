/**
 * BirdQuest - Main JavaScript
 * Common functionality and navigation
 */

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    initNavigation();
    initFlashMessages();
    initSmoothScroll();
    initFormValidation();
});

/**
 * Mobile Navigation Toggle
 */
function initNavigation() {
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    const navLinks = document.querySelector('.nav-links');

    if (navToggle) {
        navToggle.addEventListener('click', function() {
            navToggle.classList.toggle('active');

            if (navMenu) {
                navMenu.classList.toggle('active');
            }

            if (navLinks) {
                navLinks.classList.toggle('active');
            }

            // Toggle aria-expanded for accessibility
            const isExpanded = navToggle.getAttribute('aria-expanded') === 'true';
            navToggle.setAttribute('aria-expanded', !isExpanded);
        });
    }

    // Close mobile menu when clicking outside
    document.addEventListener('click', function(e) {
        if (navMenu && navToggle) {
            if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
                navMenu.classList.remove('active');
                navToggle.classList.remove('active');
                navToggle.setAttribute('aria-expanded', 'false');
            }
        }
    });

    // Close mobile menu when window is resized to desktop size
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            if (navMenu) navMenu.classList.remove('active');
            if (navToggle) {
                navToggle.classList.remove('active');
                navToggle.setAttribute('aria-expanded', 'false');
            }
            if (navLinks) navLinks.classList.remove('active');
        }
    });
}

/**
 * Flash Messages - Auto dismiss after delay
 */
function initFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash-message');

    flashMessages.forEach(function(message, index) {
        // Auto dismiss after 5 seconds (staggered)
        setTimeout(function() {
            dismissFlashMessage(message);
        }, 5000 + (index * 500));
    });

    // Close button functionality
    document.querySelectorAll('.flash-close').forEach(function(btn) {
        btn.addEventListener('click', function() {
            dismissFlashMessage(this.parentElement);
        });
    });
}

function dismissFlashMessage(element) {
    if (!element) return;

    element.style.animation = 'slideOut 0.3s ease forwards';
    setTimeout(function() {
        element.remove();
    }, 300);
}

// Add slide out animation
const styleSheet = document.createElement('style');
styleSheet.textContent = `
    @keyframes slideOut {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100%);
        }
    }
`;
document.head.appendChild(styleSheet);

/**
 * Smooth Scroll for anchor links
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');

            if (targetId === '#') return;

            const target = document.querySelector(targetId);

            if (target) {
                e.preventDefault();

                const navHeight = document.querySelector('.navbar')?.offsetHeight || 0;
                const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - navHeight - 20;

                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });

                // Close mobile menu if open
                const navMenu = document.getElementById('navMenu');
                const navToggle = document.getElementById('navToggle');
                if (navMenu) navMenu.classList.remove('active');
                if (navToggle) navToggle.classList.remove('active');
            }
        });
    });
}

/**
 * Form Validation Helpers
 */
function initFormValidation() {
    // Password confirmation validation
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirm_password');

    if (password && confirmPassword) {
        confirmPassword.addEventListener('input', function() {
            if (this.value !== password.value) {
                this.setCustomValidity('Passwords do not match');
            } else {
                this.setCustomValidity('');
            }
        });

        password.addEventListener('input', function() {
            if (confirmPassword.value && confirmPassword.value !== this.value) {
                confirmPassword.setCustomValidity('Passwords do not match');
            } else {
                confirmPassword.setCustomValidity('');
            }
        });
    }

    // Add input validation styling
    document.querySelectorAll('input, select, textarea').forEach(function(input) {
        input.addEventListener('invalid', function() {
            this.classList.add('invalid');
        });

        input.addEventListener('input', function() {
            if (this.validity.valid) {
                this.classList.remove('invalid');
            }
        });
    });
}

/**
 * Utility Functions
 */

// Show a toast notification
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container') || createToastContainer();

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icons = {
        success: '✅',
        error: '❌',
        info: 'ℹ️',
        warning: '⚠️'
    };

    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <span class="toast-message">${message}</span>
    `;

    container.appendChild(toast);

    // Auto remove after 4 seconds
    setTimeout(function() {
        toast.style.animation = 'toastSlideOut 0.3s ease forwards';
        setTimeout(function() {
            toast.remove();
        }, 300);
    }, 4000);

    return toast;
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);

    // Add toast slide out animation if not exists
    if (!document.getElementById('toast-animations')) {
        const style = document.createElement('style');
        style.id = 'toast-animations';
        style.textContent = `
            @keyframes toastSlideOut {
                from {
                    opacity: 1;
                    transform: translateX(0);
                }
                to {
                    opacity: 0;
                    transform: translateX(100%);
                }
            }
        `;
        document.head.appendChild(style);
    }

    return container;
}

// Format numbers with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// Debounce function for performance
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = function() {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle function for scroll/resize handlers
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(function() {
                inThrottle = false;
            }, limit);
        }
    };
}

// Fetch wrapper with error handling
async function fetchJSON(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'Something went wrong');
        }

        return data;
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

// Animate number counting
function animateNumber(element, start, end, duration = 1000) {
    const startTime = performance.now();
    const diff = end - start;

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Ease out quad
        const easeProgress = 1 - (1 - progress) * (1 - progress);

        const current = Math.round(start + diff * easeProgress);
        element.textContent = formatNumber(current);

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

// Local storage helpers with expiry
const storage = {
    set: function(key, value, expiryMinutes = null) {
        const item = {
            value: value,
            timestamp: Date.now()
        };

        if (expiryMinutes) {
            item.expiry = expiryMinutes * 60 * 1000;
        }

        localStorage.setItem(key, JSON.stringify(item));
    },

    get: function(key) {
        const itemStr = localStorage.getItem(key);

        if (!itemStr) return null;

        try {
            const item = JSON.parse(itemStr);

            if (item.expiry) {
                const now = Date.now();
                if (now - item.timestamp > item.expiry) {
                    localStorage.removeItem(key);
                    return null;
                }
            }

            return item.value;
        } catch (e) {
            return null;
        }
    },

    remove: function(key) {
        localStorage.removeItem(key);
    }
};

// Check if element is in viewport
function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

// Add entrance animations when elements come into view
function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('[data-animate]');

    if (animatedElements.length === 0) return;

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });

    animatedElements.forEach(function(el) {
        observer.observe(el);
    });
}

// Initialize scroll animations if supported
if ('IntersectionObserver' in window) {
    document.addEventListener('DOMContentLoaded', initScrollAnimations);
}

// Export functions for use in other scripts
window.BirdQuest = {
    showToast,
    formatNumber,
    debounce,
    throttle,
    fetchJSON,
    animateNumber,
    storage,
    isInViewport
};
