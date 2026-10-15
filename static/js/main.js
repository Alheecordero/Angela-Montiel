document.addEventListener("DOMContentLoaded", () => {
  initMobileMenu();
  initNavbarScroll();
  initStaggerGrids();
  initScrollReveal();
  initBackToTop();
  initLoadingForms();
  initHeroCarousel();
});

function initMobileMenu() {
  const toggle = document.querySelector(".menu-toggle");
  const drawer = document.querySelector(".nav-drawer");
  const backdrop = document.querySelector("[data-nav-backdrop]");
  if (!toggle || !drawer) return;

  const setOpen = (isOpen) => {
    drawer.classList.toggle("is-open", isOpen);
    drawer.setAttribute("aria-hidden", isOpen ? "false" : "true");
    toggle.classList.toggle("is-active", isOpen);
    document.body.classList.toggle("nav-open", isOpen);
    toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    toggle.setAttribute("aria-label", isOpen ? "Cerrar menú" : "Abrir menú");
    if (backdrop) {
      backdrop.hidden = !isOpen;
      backdrop.classList.toggle("is-visible", isOpen);
    }
  };

  toggle.addEventListener("click", () => {
    setOpen(!drawer.classList.contains("is-open"));
  });

  backdrop?.addEventListener("click", () => setOpen(false));

  drawer.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => setOpen(false));
  });

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape" || !drawer.classList.contains("is-open")) return;
    setOpen(false);
    toggle.focus();
  });

  window.addEventListener("resize", () => {
    if (window.innerWidth > 768 && drawer.classList.contains("is-open")) {
      setOpen(false);
    }
  });
}

function initNavbarScroll() {
  const navbar = document.querySelector(".navbar");
  if (!navbar) return;

  const onScroll = () => {
    navbar.classList.toggle("is-scrolled", window.scrollY > 24);
  };

  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });
}

function initScrollReveal() {
  const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const elements = document.querySelectorAll(".reveal");

  if (prefersReduced) {
    elements.forEach((el) => el.classList.add("is-visible"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.08, rootMargin: "0px 0px -24px 0px" }
  );

  elements.forEach((el) => observer.observe(el));
}

function initStaggerGrids() {
  const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (prefersReduced) return;

  document.querySelectorAll("[data-stagger]").forEach((grid) => {
    const children = grid.children;
    Array.from(children).forEach((child, index) => {
      child.classList.add("reveal");
      child.style.transitionDelay = `${index * 0.08}s`;
    });
  });
}

function initBackToTop() {
  const button = document.querySelector("[data-back-to-top]");
  if (!button) return;

  const onScroll = () => {
    button.hidden = window.scrollY < 480;
  };

  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });
  button.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
}

function initLoadingForms() {
  document.querySelectorAll("[data-loading-form]").forEach((form) => {
    form.addEventListener("submit", () => {
      const button = form.querySelector('button[type="submit"]');
      if (!button || button.disabled) return;
      button.disabled = true;
      button.classList.add("is-loading");
      const label = button.querySelector("span");
      if (label) label.dataset.originalText = label.textContent;
      if (label) label.textContent = "Enviando...";
    });
  });
}

function initHeroCarousel() {
  const root = document.querySelector("[data-carousel]");
  if (!root) return;

  const slides = Array.from(root.querySelectorAll("[data-carousel-slide]"));
  const dotsContainer = root.querySelector("[data-carousel-dots]");
  const prevBtn = root.querySelector("[data-carousel-prev]");
  const nextBtn = root.querySelector("[data-carousel-next]");
  if (!slides.length || !dotsContainer) return;

  let index = slides.findIndex((slide) => slide.classList.contains("is-active"));
  if (index < 0) index = 0;

  const dots = slides.map((_, slideIndex) => {
    const dot = document.createElement("button");
    dot.type = "button";
    dot.className = "hero-highlights-dot";
    dot.setAttribute("aria-label", `Ir al mensaje ${slideIndex + 1}`);
    dot.addEventListener("click", () => goTo(slideIndex));
    dotsContainer.appendChild(dot);
    return dot;
  });

  const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let timer;

  const syncSlides = (activeIndex) => {
    slides.forEach((slide, slideIndex) => {
      const isActive = slideIndex === activeIndex;
      slide.hidden = !isActive;
      slide.classList.toggle("is-active", isActive);
    });
    dots.forEach((dot, dotIndex) => {
      dot.classList.toggle("is-active", dotIndex === activeIndex);
    });
    index = activeIndex;
  };

  const goTo = (nextIndex) => {
    syncSlides((nextIndex + slides.length) % slides.length);
  };

  prevBtn?.addEventListener("click", () => {
    goTo(index - 1);
    restart();
  });

  nextBtn?.addEventListener("click", () => {
    goTo(index + 1);
    restart();
  });

  const restart = () => {
    if (prefersReduced) return;
    clearInterval(timer);
    timer = setInterval(() => goTo(index + 1), 5500);
  };

  syncSlides(index);
  restart();

  root.addEventListener("mouseenter", () => clearInterval(timer));
  root.addEventListener("mouseleave", restart);
  root.addEventListener("focusin", () => clearInterval(timer));
  root.addEventListener("focusout", restart);
}
