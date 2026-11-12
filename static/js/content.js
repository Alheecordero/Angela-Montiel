/* Interacciones de la capa de contenido: mapa de reorganizaciones,
   filtros por formato o área, buscador del glosario, vista previa de
   video. Sin dependencias. Cada bloque funciona también sin JS. */
(function () {
  "use strict";

  var normalizar = function (texto) {
    return (texto || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .trim();
  };

  /* Mapa de reorganizaciones ------------------------------------------ */
  document.querySelectorAll("[data-map]").forEach(function (mapa) {
    var fuente = mapa.querySelector("[data-map-data]");
    if (!fuente) return;
    var opciones;
    try {
      opciones = JSON.parse(fuente.textContent);
    } catch (e) {
      return;
    }
    var botones = mapa.querySelectorAll("[data-map-option]");
    var resultado = mapa.querySelector("[data-map-result]");
    var vacio = mapa.querySelector("[data-map-empty]");
    var campos = {
      name: resultado.querySelector("[data-map-name]"),
      para: resultado.querySelector("[data-map-para]"),
      atencion: resultado.querySelector("[data-map-atencion]"),
      link: resultado.querySelector("[data-map-link]"),
    };

    var mostrar = function (boton, enfocar) {
      var opcion = opciones[parseInt(boton.getAttribute("data-map-option"), 10)];
      if (!opcion) return;
      botones.forEach(function (b) {
        b.classList.toggle("is-active", b === boton);
        b.setAttribute("aria-pressed", b === boton ? "true" : "false");
      });
      campos.name.textContent = opcion.name;
      campos.para.textContent = opcion.para;
      campos.atencion.textContent = opcion.atencion;
      campos.link.setAttribute("href", opcion.page);
      campos.link.textContent = "Ver " + opcion.name.toLowerCase() + " en detalle";
      if (vacio) vacio.hidden = true;
      resultado.hidden = false;
      resultado.classList.remove("is-shown");
      void resultado.offsetWidth;
      resultado.classList.add("is-shown");
      if (enfocar) resultado.focus({ preventScroll: true });
    };

    botones.forEach(function (boton) {
      boton.addEventListener("click", function () {
        mostrar(boton, true);
      });
    });

    /* Parte con la primera opción elegida: así el panel nunca se ve vacío. */
    if (botones.length) mostrar(botones[0], false);
  });

  /* Filtros (publicaciones por formato, videos por área) -------------- */
  document.querySelectorAll("[data-filter-group]").forEach(function (grupo) {
    var objetivo = grupo.getAttribute("data-filter-group");
    var elementos = document.querySelectorAll("[data-filter-item='" + objetivo + "']");
    var descripciones = document.querySelectorAll("[data-filter-desc='" + objetivo + "']");
    var vacio = document.querySelector("[data-filter-empty='" + objetivo + "']");
    var chips = grupo.querySelectorAll("[data-filter]");

    var aplicar = function (clave) {
      var visibles = 0;
      elementos.forEach(function (el) {
        var claves = (el.getAttribute("data-key") || "").split(" ");
        var mostrar = clave === "todas" || claves.indexOf(clave) !== -1;
        el.hidden = !mostrar;
        if (mostrar) visibles += 1;
      });
      descripciones.forEach(function (d) {
        d.hidden = d.getAttribute("data-key") !== clave;
      });
      if (vacio) vacio.hidden = visibles !== 0;
      chips.forEach(function (c) {
        var activo = c.getAttribute("data-filter") === clave;
        c.classList.toggle("active", activo);
        c.setAttribute("aria-pressed", activo ? "true" : "false");
      });
    };

    chips.forEach(function (chip) {
      chip.addEventListener("click", function (ev) {
        ev.preventDefault();
        aplicar(chip.getAttribute("data-filter"));
      });
    });

    var inicial = new URLSearchParams(window.location.search).get(grupo.getAttribute("data-filter-param") || "f");
    if (inicial) aplicar(inicial);
  });

  /* Glosario ---------------------------------------------------------------- */
  document.querySelectorAll("[data-glossary]").forEach(function (bloque) {
    var entrada = bloque.querySelector("[data-glossary-input]");
    var items = bloque.querySelectorAll("[data-glossary-item]");
    var vacio = bloque.querySelector("[data-glossary-empty]");
    if (!entrada) return;
    entrada.addEventListener("input", function () {
      var q = normalizar(entrada.value);
      var visibles = 0;
      items.forEach(function (item) {
        var coincide = !q || (item.getAttribute("data-search") || "").indexOf(q) !== -1;
        item.hidden = !coincide;
        if (coincide) visibles += 1;
      });
      if (vacio) vacio.hidden = visibles !== 0;
    });
  });

  /* Vista previa liviana de YouTube --------------------------------------- */
  document.querySelectorAll("[data-video-facade]").forEach(function (caja) {
    var boton = caja.querySelector("[data-video-play]");
    if (!boton) return;
    boton.addEventListener("click", function () {
      var iframe = document.createElement("iframe");
      iframe.src = caja.getAttribute("data-video-facade");
      iframe.title = boton.getAttribute("aria-label") || "Video";
      iframe.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share";
      iframe.setAttribute("allowfullscreen", "");
      iframe.setAttribute("loading", "lazy");
      caja.innerHTML = "";
      caja.appendChild(iframe);
    });
  });
})();
