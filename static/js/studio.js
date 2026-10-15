document.addEventListener("DOMContentLoaded", () => {
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  initScrollProgress();
  initHeroBanners(reducedMotion);
  initScrollReveals(reducedMotion);
  initPinnedServices(reducedMotion);
  if (!reducedMotion) {
    initParallaxAndScrubbing();
  }
});

function clamp(value, min = 0, max = 1) {
  return Math.min(max, Math.max(min, value));
}

function initScrollProgress() {
  const bar = document.querySelector("[data-scroll-progress]");
  if (!bar) return;

  const update = () => {
    const scrollable = document.documentElement.scrollHeight - window.innerHeight;
    const progress = scrollable > 0 ? window.scrollY / scrollable : 0;
    bar.style.transform = `scaleX(${clamp(progress)})`;
  };

  update();
  window.addEventListener("scroll", update, { passive: true });
  window.addEventListener("resize", update);
}

function initHeroBanners(reducedMotion) {
  const root = document.querySelector("[data-hero-banners]");
  if (!root) return;

  const slides = Array.from(root.querySelectorAll("[data-banner]"));
  const dots = Array.from(root.querySelectorAll("[data-banner-dot]"));
  if (slides.length < 2) return;

  let index = 0;
  let timer = null;

  const show = (next) => {
    index = (next + slides.length) % slides.length;
    slides.forEach((slide, slideIndex) => {
      const active = slideIndex === index;
      slide.classList.toggle("is-active", active);
      slide.setAttribute("aria-hidden", active ? "false" : "true");
    });
    dots.forEach((dot, dotIndex) => {
      const active = dotIndex === index;
      dot.classList.toggle("is-active", active);
      dot.setAttribute("aria-selected", active ? "true" : "false");
    });
  };

  const start = () => {
    clearInterval(timer);
    if (reducedMotion) return;
    timer = setInterval(() => show(index + 1), 7000);
  };

  dots.forEach((dot, dotIndex) => {
    dot.addEventListener("click", () => {
      show(dotIndex);
      start();
    });
  });

  root.addEventListener("mouseenter", () => clearInterval(timer));
  root.addEventListener("mouseleave", start);
  root.addEventListener("focusin", () => clearInterval(timer));
  root.addEventListener("focusout", (event) => {
    if (!root.contains(event.relatedTarget)) start();
  });

  show(0);
  start();
}

function initScrollReveals(reducedMotion) {
  const items = Array.from(document.querySelectorAll(".scrolly-reveal"));
  if (!items.length) return;

  if (reducedMotion || !("IntersectionObserver" in window)) {
    items.forEach((el) => el.classList.add("is-visible"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
        }
      });
    },
    { threshold: 0.16, rootMargin: "0px 0px -6% 0px" }
  );

  items.forEach((item) => observer.observe(item));
}

function initParallaxAndScrubbing() {
  const parallaxItems = Array.from(document.querySelectorAll("[data-parallax]"));
  const scrubSection = document.querySelector("[data-scrub-section]");
  const scrubCounter = document.querySelector("[data-scrub-counter]");
  const scrubCaption = document.querySelector("[data-scrub-caption]");
  const scrubPills = Array.from(document.querySelectorAll("[data-scrub-pill]"));
  const scenes = Array.from(document.querySelectorAll("[data-scroll-scene]"));

  const captions = [
    "Rigor técnico en cada decisión societaria",
    "Visión empresarial aplicada al derecho corporativo",
    "Estructura jurídica sólida para crecer con certeza",
  ];

  let ticking = false;

  const render = () => {
    ticking = false;
    const vh = window.innerHeight || 1;
    const isDesktop = window.innerWidth > 980;

    // 1. Parallax scrolling
    if (isDesktop) {
      parallaxItems.forEach((el) => {
        const speed = parseFloat(el.dataset.parallax || "0");
        const rect = el.parentElement ? el.parentElement.getBoundingClientRect() : el.getBoundingClientRect();
        const centerOffset = rect.top + rect.height * 0.5 - vh * 0.5;
        const shift = clamp(centerOffset * speed, -32, 32);
        el.style.transform = `translate3d(0, ${shift.toFixed(1)}px, 0)`;
      });
    } else {
      parallaxItems.forEach((el) => {
        el.style.transform = "";
      });
    }

    // 2. Scroll scrubbing en la franja editorial (#criterio)
    if (scrubSection) {
      const rect = scrubSection.getBoundingClientRect();
      const total = vh + rect.height;
      const raw = (vh - rect.top) / total;
      const progress = clamp(raw, 0, 1);
      scrubSection.style.setProperty("--scrub", progress.toFixed(3));

      const stage = progress < 0.36 ? 0 : progress < 0.68 ? 1 : 2;
      if (scrubCounter) {
        scrubCounter.textContent = `0${stage + 1}`;
      }
      if (scrubCaption && captions[stage]) {
        scrubCaption.textContent = captions[stage];
      }
      scrubPills.forEach((pill, idx) => {
        pill.classList.toggle("is-lit", idx <= stage);
      });
    }

    // 3. Desplazamiento suave de fondos en escenas
    scenes.forEach((scene) => {
      const rect = scene.getBoundingClientRect();
      if (rect.bottom < 0 || rect.top > vh) return;
      const ratio = (vh * 0.5 - (rect.top + rect.height * 0.5)) / vh;
      scene.style.setProperty("--scene-shift", `${(ratio * 14).toFixed(1)}px`);
    });
  };

  const requestTick = () => {
    if (!ticking) {
      ticking = true;
      window.requestAnimationFrame(render);
    }
  };

  render();
  window.addEventListener("scroll", requestTick, { passive: true });
  window.addEventListener("resize", requestTick);
}

function initPinnedServices(reducedMotion) {
  const section = document.querySelector("[data-pin-services]");
  if (!section) return;

  const cards = Array.from(section.querySelectorAll("[data-pin-card]"));
  const media = Array.from(section.querySelectorAll("[data-pin-media]"));
  const count = cards.length;
  if (!count) return;

  let activeIndex = 0;

  const activate = (index) => {
    const bounded = clamp(index, 0, count - 1);
    activeIndex = bounded;
    const pinned = window.innerWidth > 980;
    cards.forEach((card, idx) => {
      const active = idx === bounded;
      card.classList.toggle("is-active", active);
      if (pinned) card.setAttribute("aria-hidden", active ? "false" : "true");
      else card.removeAttribute("aria-hidden");
    });
    media.forEach((img, idx) => img.classList.toggle("is-active", idx === bounded));
  };

  if (reducedMotion) {
    cards.forEach((card) => card.classList.add("is-active"));
    return;
  }

  const onScroll = () => {
    if (window.innerWidth <= 980) {
      cards.forEach((card) => card.removeAttribute("aria-hidden"));
      return;
    }
    const rect = section.getBoundingClientRect();
    const scrollable = section.offsetHeight - window.innerHeight;
    if (scrollable <= 0) return;

    const progress = clamp(-rect.top / scrollable, 0, 1);
    const nextIndex = Math.min(count - 1, Math.floor(progress * count));
    if (nextIndex !== activeIndex) activate(nextIndex);
  };

  activate(0);
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll);
}
