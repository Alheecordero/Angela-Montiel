document.addEventListener("DOMContentLoaded", () => {
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  initScrollProgress();
  initHeroBanners(reducedMotion);
  initScrollReveals(reducedMotion);
  initServicesCarousel(reducedMotion);
  initAboutInteractivity(reducedMotion);
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
    if (reducedMotion || document.hidden) return;
    timer = setInterval(() => show(index + 1), 7000);
  };

  dots.forEach((dot, dotIndex) => {
    dot.addEventListener("click", () => {
      show(dotIndex);
      start();
    });
  });

  const finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  if (finePointer) {
    root.addEventListener("mouseenter", () => clearInterval(timer));
    root.addEventListener("mouseleave", start);
  }

  root.addEventListener("focusin", () => clearInterval(timer));
  root.addEventListener("focusout", (event) => {
    if (!root.contains(event.relatedTarget)) start();
  });

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) clearInterval(timer);
    else start();
  });

  const hero = root.closest(".firm-hero");
  if (hero && "IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) start();
        else clearInterval(timer);
      });
    }, { threshold: 0.25 });
    observer.observe(hero);
  }

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

function initAboutInteractivity(reducedMotion) {
  const section = document.querySelector("[data-about-interactive]");
  const card = section?.querySelector("[data-about-card]");
  const tiltTarget = section?.querySelector("[data-about-tilt]");
  const highlights = section ? Array.from(section.querySelectorAll("[data-about-highlight]")) : [];
  if (!section || !card) return;

  let highlightIndex = 0;
  let highlightTimer = null;

  const setHighlight = (index) => {
    if (!highlights.length) return;
    highlightIndex = (index + highlights.length) % highlights.length;
    highlights.forEach((item, idx) => {
      const active = idx === highlightIndex;
      item.classList.toggle("is-active", active);
      item.setAttribute("aria-selected", active ? "true" : "false");
      item.tabIndex = active ? 0 : -1;
    });
  };

  const startHighlights = () => {
    clearInterval(highlightTimer);
    if (reducedMotion || document.hidden) return;
    highlightTimer = setInterval(() => setHighlight(highlightIndex + 1), 4500);
  };

  highlights.forEach((item, idx) => {
    const activate = () => {
      setHighlight(idx);
      startHighlights();
    };
    item.addEventListener("click", activate);
    item.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        activate();
      }
      if (event.key === "ArrowRight") {
        event.preventDefault();
        setHighlight(highlightIndex + 1);
        startHighlights();
      }
      if (event.key === "ArrowLeft") {
        event.preventDefault();
        setHighlight(highlightIndex - 1);
        startHighlights();
      }
    });
  });

  const finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  if (finePointer && tiltTarget && !reducedMotion) {
    const maxTilt = 5;
    card.addEventListener("mousemove", (event) => {
      const rect = tiltTarget.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width - 0.5;
      const y = (event.clientY - rect.top) / rect.height - 0.5;
      tiltTarget.style.transform =
        `perspective(1100px) rotateX(${(-y * maxTilt).toFixed(2)}deg) rotateY(${(x * maxTilt).toFixed(2)}deg)`;
    });
    card.addEventListener("mouseleave", () => {
      tiltTarget.style.transform = "";
    });
  }

  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            card.classList.add("is-about-live");
            startHighlights();
          } else {
            card.classList.remove("is-about-live");
            clearInterval(highlightTimer);
          }
        });
      },
      { threshold: 0.35 }
    );
    observer.observe(section);
  } else {
    card.classList.add("is-about-live");
    startHighlights();
  }

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) clearInterval(highlightTimer);
    else if (card.classList.contains("is-about-live")) startHighlights();
  });

  if (finePointer) {
    section.addEventListener("mouseenter", () => clearInterval(highlightTimer));
    section.addEventListener("mouseleave", () => {
      if (card.classList.contains("is-about-live")) startHighlights();
    });
  }
}

function initParallaxAndScrubbing() {
  const parallaxItems = Array.from(document.querySelectorAll("[data-parallax]"));
  const scenes = Array.from(document.querySelectorAll("[data-scroll-scene]"));

  let ticking = false;
  let clearedMobileMotion = false;

  const render = () => {
    ticking = false;
    const vh = window.innerHeight || 1;
    const isDesktop = window.innerWidth > 980;

    // 1. Parallax scrolling. En móvil se limpia una sola vez: reescribir
    // el transform en cada frame retrasa el cambio de los banners.
    if (isDesktop) {
      clearedMobileMotion = false;
      parallaxItems.forEach((el) => {
        const speed = parseFloat(el.dataset.parallax || "0");
        const rect = el.parentElement ? el.parentElement.getBoundingClientRect() : el.getBoundingClientRect();
        const centerOffset = rect.top + rect.height * 0.5 - vh * 0.5;
        const shift = clamp(centerOffset * speed, -32, 32);
        el.style.transform = `translate3d(0, ${shift.toFixed(1)}px, 0)`;
      });
    } else if (!clearedMobileMotion) {
      parallaxItems.forEach((el) => {
        el.style.transform = "";
      });
      clearedMobileMotion = true;
    }

    // 2. Desplazamiento suave de fondos en escenas.
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

function initServicesCarousel(reducedMotion) {
  const section = document.querySelector("[data-services-carousel]");
  if (!section) return;

  const viewport = section.querySelector(".firm-services-viewport");
  const track = section.querySelector("[data-services-track]");
  const cards = Array.from(section.querySelectorAll("[data-service-card]"));
  const dotsHost = section.querySelector(".firm-services-dots");
  const live = section.querySelector("[data-services-live]");
  const prevBtn = section.querySelector("[data-services-prev]");
  const nextBtn = section.querySelector("[data-services-next]");
  const labels = ["Corporativa", "Contratos", "E-commerce", "Datos", "Marcas", "Defensa"];
  const AUTO_MS = 5200;
  const count = cards.length;
  if (!count || !track || !viewport) return;

  const dots = labels.slice(0, count).map((label, idx) => {
    const button = document.createElement("button");
    button.type = "button";
    button.role = "tab";
    button.setAttribute("aria-label", label);
    button.dataset.serviceDot = String(idx);
    dotsHost.appendChild(button);
    return button;
  });

  let activeIndex = 0;
  let timer = null;
  let dragStartX = 0;
  let dragDelta = 0;
  let dragging = false;
  let spreadPx = 0;

  const measure = () => {
    const cardWidth = cards[0]?.offsetWidth || 320;
    spreadPx = Math.min(cardWidth * 0.52, window.innerWidth * 0.34);
    return spreadPx;
  };

  const relativeOffset = (idx, active) => {
    let delta = idx - active;
    const half = count / 2;
    if (delta > half) delta -= count;
    if (delta < -half) delta += count;
    return delta;
  };

  const cardTransform = (offset, dragShift = 0) => {
    const abs = Math.abs(offset);
    if (abs > 3) {
      return {
        transform: `translate3d(${(offset * spreadPx) + dragShift}px, 0, -120px) scale(0.62) rotateY(${-offset * 24}deg)`,
        opacity: "0",
        zIndex: "0",
        pointer: "none",
      };
    }

    const scale = offset === 0 ? 1 : abs === 1 ? 0.9 : 0.8;
    const depth = offset === 0 ? 0 : abs === 1 ? -55 : -95;
    const rotateY = -offset * 26;
    const x = offset * spreadPx + dragShift;
    const opacity = offset === 0 ? 1 : abs === 1 ? 0.9 : 0.72;

    return {
      transform: `translate3d(${x}px, 0, ${depth}px) scale(${scale}) rotateY(${rotateY}deg)`,
      opacity: String(opacity),
      zIndex: String(10 - abs),
      pointer: abs <= 1 ? "auto" : "none",
    };
  };

  const layout = (animate = true, dragShift = 0) => {
    measure();
    cards.forEach((card, idx) => {
      const offset = relativeOffset(idx, activeIndex);
      const styles = cardTransform(offset, dragShift);
      card.style.transition = animate && !dragging
        ? ""
        : "none";
      card.style.transform = styles.transform;
      card.style.opacity = styles.opacity;
      card.style.zIndex = styles.zIndex;
      card.style.pointerEvents = styles.pointer;
      card.dataset.offset = String(offset);
      card.classList.toggle("is-center", offset === 0);
      card.setAttribute("aria-hidden", offset === 0 ? "false" : "true");
    });
  };

  const restartDotRing = () => {
    dots.forEach((dot, idx) => {
      dot.classList.remove("is-timing");
      if (idx === activeIndex) {
        void dot.offsetWidth;
        dot.classList.add("is-timing");
      }
    });
  };

  const activate = (index, animate = true) => {
    activeIndex = (index + count) % count;
    layout(animate);
    dots.forEach((dot, idx) => {
      const active = idx === activeIndex;
      dot.classList.toggle("is-active", active);
      dot.setAttribute("aria-selected", active ? "true" : "false");
    });
    if (live) live.textContent = labels[activeIndex] || "";
    restartDotRing();
  };

  const start = () => {
    clearInterval(timer);
    if (reducedMotion || document.hidden) return;
    timer = setInterval(() => activate(activeIndex + 1), AUTO_MS);
  };

  dots.forEach((dot, idx) => {
    dot.addEventListener("click", () => {
      activate(idx);
      start();
    });
  });

  prevBtn?.addEventListener("click", () => {
    activate(activeIndex - 1);
    start();
  });

  nextBtn?.addEventListener("click", () => {
    activate(activeIndex + 1);
    start();
  });

  cards.forEach((card, idx) => {
    card.addEventListener("click", (event) => {
      if (event.target.closest("a")) return;
      const offset = Number(card.dataset.offset || 0);
      if (offset === -1) activate(activeIndex - 1);
      else if (offset === 1) activate(activeIndex + 1);
      else if (offset !== 0) activate(idx);
      start();
    });
  });

  const finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  if (finePointer) {
    section.addEventListener("mouseenter", () => clearInterval(timer));
    section.addEventListener("mouseleave", start);
  }

  viewport.addEventListener("pointerdown", (event) => {
    if (event.target.closest("a, button")) return;
    dragging = true;
    dragStartX = event.clientX;
    dragDelta = 0;
    viewport.classList.add("is-dragging");
    clearInterval(timer);
    viewport.setPointerCapture(event.pointerId);
  });

  viewport.addEventListener("pointermove", (event) => {
    if (!dragging) return;
    dragDelta = event.clientX - dragStartX;
    layout(false, dragDelta);
  });

  const endDrag = (event) => {
    if (!dragging) return;
    dragging = false;
    viewport.classList.remove("is-dragging");
    if (viewport.hasPointerCapture(event.pointerId)) {
      viewport.releasePointerCapture(event.pointerId);
    }
    measure();
    if (Math.abs(dragDelta) > spreadPx * 0.22) {
      activate(activeIndex + (dragDelta < 0 ? 1 : -1));
    } else {
      layout(true);
    }
    start();
  };

  viewport.addEventListener("pointerup", endDrag);
  viewport.addEventListener("pointercancel", endDrag);

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) clearInterval(timer);
    else start();
  });

  window.addEventListener("resize", () => layout(false));

  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) start();
        else clearInterval(timer);
      });
    }, { threshold: 0.25 });
    observer.observe(section);
  }

  if (reducedMotion) {
    section.querySelector(".firm-services-orbit")?.remove();
    prevBtn?.remove();
    nextBtn?.remove();
    viewport.style.height = "auto";
    viewport.style.perspective = "none";
    viewport.style.overflowX = "auto";
    viewport.style.cursor = "auto";
    track.style.display = "flex";
    track.style.gap = "1rem";
    cards.forEach((card) => {
      card.style.position = "relative";
      card.style.left = "auto";
      card.style.marginLeft = "0";
      card.style.flex = "0 0 min(88vw, 340px)";
      card.style.transform = "none";
      card.style.opacity = "1";
      card.style.pointerEvents = "auto";
      card.classList.remove("is-center");
      card.setAttribute("aria-hidden", "false");
    });
    if (live) live.textContent = "";
    return;
  }

  activate(0, false);
  start();
}
