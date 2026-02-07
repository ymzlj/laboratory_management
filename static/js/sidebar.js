/**
 * Sidebar Navigation Controller
 * Handles responsive behavior, theme toggling, and accessibility
 */

class SidebarController {
  constructor() {
    // DOM Elements
    this.sidebar = document.getElementById('sidebar');
    this.sidebarToggle = document.getElementById('sidebarToggle');
    this.themeToggle = document.getElementById('themeToggle');
    this.mainContent = document.getElementById('mainContent');
    this.topNavbar = document.querySelector('.top-navbar');
    this.overlay = document.getElementById('sidebarOverlay');
    
    // State
    this.isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    this.currentTheme = localStorage.getItem('theme') || 'light';
    
    this.init();
  }

  init() {
    // Initialize state
    this.applySidebarState();
    this.applyTheme();
    
    // Event Listeners
    this.bindEvents();
    
    // Keyboard Navigation
    this.setupKeyboardNav();
  }

  bindEvents() {
    // Sidebar Toggle
    if (this.sidebarToggle) {
      this.sidebarToggle.addEventListener('click', () => this.toggleSidebar());
    }

    // Theme Toggle
    if (this.themeToggle) {
      this.themeToggle.addEventListener('click', () => this.toggleTheme());
    }

    // Overlay Click (Mobile)
    if (this.overlay) {
      this.overlay.addEventListener('click', () => this.closeMobileSidebar());
    }

    // Window Resize Handler
    window.addEventListener('resize', this.debounce(() => {
      if (window.innerWidth > 768) {
        this.overlay?.classList.remove('show');
        this.sidebar?.classList.remove('mobile-open');
      }
    }, 200));
  }

  toggleSidebar() {
    if (window.innerWidth <= 768) {
      this.toggleMobileSidebar();
    } else {
      this.isCollapsed = !this.isCollapsed;
      localStorage.setItem('sidebarCollapsed', this.isCollapsed);
      this.applySidebarState();
    }
  }

  toggleMobileSidebar() {
    this.sidebar?.classList.toggle('mobile-open');
    this.overlay?.classList.toggle('show');
    const isOpen = this.sidebar?.classList.contains('mobile-open');
    this.sidebarToggle?.setAttribute('aria-expanded', isOpen);
  }

  closeMobileSidebar() {
    this.sidebar?.classList.remove('mobile-open');
    this.overlay?.classList.remove('show');
    this.sidebarToggle?.setAttribute('aria-expanded', 'false');
  }

  applySidebarState() {
    if (window.innerWidth > 768) {
      if (this.isCollapsed) {
        this.sidebar?.classList.add('collapsed');
        this.mainContent?.classList.add('expanded');
        this.topNavbar?.classList.add('expanded');
      } else {
        this.sidebar?.classList.remove('collapsed');
        this.mainContent?.classList.remove('expanded');
        this.topNavbar?.classList.remove('expanded');
      }
      this.sidebarToggle?.setAttribute('aria-expanded', !this.isCollapsed);
    }
  }

  toggleTheme() {
    this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
    localStorage.setItem('theme', this.currentTheme);
    this.applyTheme();
  }

  applyTheme() {
    document.documentElement.setAttribute('data-theme', this.currentTheme);
    if (this.themeToggle) {
      const icon = this.themeToggle.querySelector('i');
      if (icon) {
        icon.className = this.currentTheme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
      }
      this.themeToggle.setAttribute('aria-label', 
        this.currentTheme === 'light' ? '切换到暗色模式' : '切换到亮色模式'
      );
    }
  }

  setupKeyboardNav() {
    const navLinks = this.sidebar?.querySelectorAll('.nav-link');
    
    navLinks?.forEach((link, index) => {
      link.addEventListener('keydown', (e) => {
        let targetIndex = null;

        switch(e.key) {
          case 'ArrowDown':
            e.preventDefault();
            targetIndex = index + 1 >= navLinks.length ? 0 : index + 1;
            break;
          case 'ArrowUp':
            e.preventDefault();
            targetIndex = index - 1 < 0 ? navLinks.length - 1 : index - 1;
            break;
          case 'Home':
            e.preventDefault();
            targetIndex = 0;
            break;
          case 'End':
            e.preventDefault();
            targetIndex = navLinks.length - 1;
            break;
        }

        if (targetIndex !== null) {
          navLinks[targetIndex].focus();
        }
      });
    });
  }

  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.sidebarCtrl = new SidebarController();
});
