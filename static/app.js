// CineMatch AI Frontend Logic

let appConfig = {
  has_openrouter_key: false,
  active_model: "meta-llama/llama-3.3-70b-instruct",
  models: []
};

// Inicialización al cargar la página
document.addEventListener("DOMContentLoaded", () => {
  if (window.lucide) {
    lucide.createIcons();
  }
  loadConfig();
  loadTrending();
});

// Navegación de pestañas
function switchTab(tabId) {
  const tabs = ['discover', 'couple', 'trending'];
  tabs.forEach(t => {
    const section = document.getElementById(`tab-${t}`);
    const navBtn = document.getElementById(`nav-${t}`);
    if (t === tabId) {
      section.classList.remove('hidden');
      if (navBtn) {
        navBtn.className = "px-4 py-1.5 text-sm font-medium rounded-lg transition-all text-white bg-violet-600 shadow-sm";
      }
    } else {
      section.classList.add('hidden');
      if (navBtn) {
        navBtn.className = "px-4 py-1.5 text-sm font-medium rounded-lg transition-all text-slate-400 hover:text-white hover:bg-slate-800";
      }
    }
  });
  if (window.lucide) lucide.createIcons();
}

// Carga de configuración inicial
async function loadConfig() {
  try {
    const res = await fetch("/api/config");
    if (!res.ok) return;
    appConfig = await res.json();
    
    // Actualizar badge de estado
    const badge = document.getElementById("api-status-badge");
    if (appConfig.has_openrouter_key) {
      badge.className = "w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_#34d399]";
      badge.title = "OpenRouter API conectada";
    } else {
      badge.className = "w-2 h-2 rounded-full bg-amber-400 animate-pulse";
      badge.title = "Modo Demo Local (Introduce tu clave OpenRouter en Ajustes)";
    }

    // Rellenar selector de modelos en el modal de ajustes
    const modelSelect = document.getElementById("cfg-openrouter-model");
    if (modelSelect && appConfig.models) {
      modelSelect.innerHTML = appConfig.models.map(m => `
        <option value="${m.id}" ${m.id === appConfig.active_model ? 'selected' : ''}>
          ${m.name} ${m.free ? '(Gratuito)' : ''}
        </option>
      `).join("");
    }
  } catch (err) {
    console.error("Error al cargar configuración:", err);
  }
}

let currentTrendingPlatform = "Todas";

// Carga de películas en tendencia con soporte de carrusel y filtro de plataforma
async function loadTrending(platform = "Todas") {
  currentTrendingPlatform = platform;
  const countText = document.getElementById("trending-count-text");
  if (countText) countText.textContent = "Filtrando catálogo...";

  try {
    const res = await fetch(`/api/trending?platform=${encodeURIComponent(platform)}`);
    if (!res.ok) return;
    const data = await res.json();
    const items = data.items || [];

    if (platform === "Todas") {
      renderTrendingCarousels(items, "trending-grid");
      if (countText) countText.textContent = `Mostrando ${items.length} títulos organizados por plataforma (desliza horizontalmente)`;
    } else {
      renderCards(items, "trending-grid");
      if (countText) countText.textContent = `Mostrando ${items.length} títulos disponibles en ${platform}`;
    }
  } catch (err) {
    console.error("Error al cargar tendencias:", err);
    if (countText) countText.textContent = "Error al cargar títulos";
  }
}

// Renderiza carruseles con scroll horizontal continuo por plataforma
function renderTrendingCarousels(items, containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  // Restaurar layout de bloque para secciones
  container.className = "space-y-8";

  const platformsList = [
    { name: "Netflix", dot: "bg-[#E50914]" },
    { name: "Max", dot: "bg-[#9333EA]" },
    { name: "Disney+", dot: "bg-[#3B82F6]" },
    { name: "Prime Video", dot: "bg-[#00A8E1]" },
    { name: "Filmin", dot: "bg-[#10B981]" },
    { name: "Apple TV+", dot: "bg-slate-200" },
    { name: "Movistar+", dot: "bg-[#06B6D4]" }
  ];

  let html = "";

  platformsList.forEach(plat => {
    const platItems = items.filter(it => 
      (it.platforms || []).some(p => p.toLowerCase().includes(plat.name.toLowerCase()))
    );

    if (platItems.length > 0) {
      html += `
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2.5">
              <span class="w-3 h-3 rounded-full ${plat.dot} shadow-sm"></span>
              <h3 class="text-lg font-bold text-white tracking-wide">${plat.name}</h3>
              <span class="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-semibold">${platItems.length} títulos</span>
            </div>
            <button onclick="filterTrending('${plat.name}')" class="text-xs text-violet-400 hover:text-violet-300 font-bold flex items-center gap-1 transition">
              <span>Ver catálogo completo</span>
              <i data-lucide="chevron-right" class="w-3.5 h-3.5"></i>
            </button>
          </div>

          <!-- Horizontal Scroll Row -->
          <div class="flex gap-5 overflow-x-auto pb-4 pt-1 px-1 scrollbar-thin snap-x scroll-smooth">
            ${platItems.map(item => renderCardHtml(item, true)).join('')}
          </div>
        </div>
      `;
    }
  });

  container.innerHTML = html;
  if (window.lucide) lucide.createIcons();
}

// Filtrar tendencias por plataforma (desde botones o desplegable)
function filterTrending(platform) {
  // Sincronizar el desplegable
  const select = document.getElementById("select-trending-platform");
  if (select) select.value = platform;

  // Actualizar estilo visual de los botones píldora
  const pills = document.querySelectorAll("#trending-platform-pills .pill-platform");
  pills.forEach(p => {
    const plat = p.getAttribute("data-platform");
    if (plat === platform) {
      p.className = "pill-platform active-pill px-3.5 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 whitespace-nowrap bg-violet-600 text-white shadow-md shadow-violet-600/30";
    } else {
      p.className = "pill-platform px-3.5 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 whitespace-nowrap bg-slate-900 text-slate-300 hover:text-white hover:bg-slate-800 border border-slate-800";
    }
  });

  loadTrending(platform);
}

// Ejecutar búsqueda rápida desde sugerencias
function setQuickSearch(query) {
  const input = document.getElementById("search-input");
  input.value = query;
  input.focus();
  document.getElementById("search-form").dispatchEvent(new Event('submit', { cancelable: true }));
}

// Búsqueda inteligente con OpenRouter
async function handleSearch(e) {
  e.preventDefault();
  const query = document.getElementById("search-input").value.trim();
  if (!query) return;

  const platform = document.getElementById("filter-platform").value;
  const contentType = document.getElementById("filter-type").value;
  const mood = document.getElementById("filter-mood").value;

  const spinner = document.getElementById("loading-spinner");
  const resultsContainer = document.getElementById("results-container");
  const btnSearch = document.getElementById("btn-search");

  spinner.classList.remove("hidden");
  resultsContainer.classList.add("hidden");
  btnSearch.disabled = true;
  btnSearch.classList.add("opacity-50");

  try {
    const response = await fetch("/api/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt: query,
        platform: platform,
        content_type: contentType,
        mood: mood
      })
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "Error en la llamada a la IA");
    }

    const data = await response.json();

    // Mostrar veredicto / resumen
    document.getElementById("results-summary").textContent = data.summary;
    renderCards(data.recommendations, "movies-grid");
    resultsContainer.classList.remove("hidden");

    // Scroll suave a resultados
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });

  } catch (err) {
    alert("Hubo un problema al generar la recomendación:\n" + err.message);
  } finally {
    spinner.classList.add("hidden");
    btnSearch.disabled = false;
    btnSearch.classList.remove("opacity-50");
    if (window.lucide) lucide.createIcons();
  }
}

// Resolver dilema de Pareja con IA
async function handleCoupleMatch(e) {
  e.preventDefault();
  const p1 = document.getElementById("couple-p1").value.trim();
  const p2 = document.getElementById("couple-p2").value.trim();
  const platform = document.getElementById("couple-platform").value;
  const btn = document.getElementById("btn-couple");
  const resultContainer = document.getElementById("couple-result");

  if (!p1 || !p2) return;

  btn.disabled = true;
  btn.classList.add("opacity-50");
  resultContainer.classList.remove("hidden");
  resultContainer.innerHTML = `
    <div class="text-center py-8 space-y-2">
      <div class="w-8 h-8 rounded-full border-2 border-rose-500/30 border-t-rose-500 animate-spin mx-auto"></div>
      <p class="text-sm text-rose-300 font-medium">Buscando el consenso cinematográfico perfecto...</p>
    </div>
  `;

  try {
    const res = await fetch("/api/match", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user1_preferences: p1,
        user2_preferences: p2,
        platform: platform
      })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Error al calcular el match");
    }

    const match = await res.json();

    resultContainer.innerHTML = `
      <div class="bg-gradient-to-br from-rose-950/40 via-purple-950/20 to-slate-900 border border-rose-500/30 rounded-2xl p-6 space-y-4">
        <div class="flex items-center justify-between flex-wrap gap-2">
          <div class="flex items-center gap-2">
            <span class="p-2 rounded-lg bg-rose-500/20 text-rose-400">
              <i data-lucide="sparkles" class="w-5 h-5"></i>
            </span>
            <span class="text-xs font-bold text-rose-300 uppercase tracking-widest">Coincidencia Encontrada</span>
          </div>
          <span class="px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 text-xs font-bold">
            ${match.compatibility_score || 95}% de Compatibilidad
          </span>
        </div>

        <div>
          <h3 class="text-2xl font-black text-white">${match.title} <span class="text-slate-400 text-base font-normal">(${match.year || 'Estreno'})</span></h3>
          <p class="text-rose-200 text-sm italic mt-0.5">"${match.hook}"</p>
        </div>

        <p class="text-slate-300 text-sm leading-relaxed">${match.compromise_analysis}</p>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
          <div class="bg-slate-950/60 p-3 rounded-xl border border-violet-500/20">
            <span class="text-xs font-bold text-violet-300 block mb-1">Para Persona 1:</span>
            <p class="text-xs text-slate-300">${match.why_person_1_will_love_it}</p>
          </div>
          <div class="bg-slate-950/60 p-3 rounded-xl border border-rose-500/20">
            <span class="text-xs font-bold text-rose-300 block mb-1">Para Persona 2:</span>
            <p class="text-xs text-slate-300">${match.why_person_2_will_love_it}</p>
          </div>
        </div>

        <div class="flex items-center gap-2 pt-2">
          <span class="text-xs text-slate-400 font-semibold">Disponible en:</span>
          ${(match.platforms || []).map(p => `<span class="px-2.5 py-0.5 rounded-md text-xs font-bold ${getPlatformClass(p)}">${p}</span>`).join('')}
        </div>
      </div>
    `;

    if (window.lucide) lucide.createIcons();

  } catch (err) {
    resultContainer.innerHTML = `<p class="text-rose-400 text-xs text-center">Error: ${err.message}</p>`;
  } finally {
    btn.disabled = false;
    btn.classList.remove("opacity-50");
  }
}

// Renderizar tarjetas de películas (para cuadrículas)
function renderCards(items, containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  // Restaurar cuadrícula responsiva
  if (containerId === "trending-grid" || containerId === "movies-grid") {
    container.className = "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6";
  }

  if (!items || items.length === 0) {
    container.innerHTML = `
      <div class="col-span-full text-center py-12 text-slate-400">
        No se encontraron recomendaciones con los filtros seleccionados. Prueba una descripción más abierta.
      </div>
    `;
    return;
  }

  container.innerHTML = items.map(item => renderCardHtml(item, false)).join('');
  if (window.lucide) lucide.createIcons();
}

// Generador de HTML para tarjeta individual
function renderCardHtml(item, isCarousel = false) {
  const poster = item.poster || "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=500&auto=format&fit=crop&q=80";
  const platforms = item.platforms || [];
  const rating = item.rating ? Number(item.rating).toFixed(1) : "8.0";
  const matchScore = item.match_percentage ? `${item.match_percentage}% Match` : "Destacado";
  const trailerUrl = `https://www.youtube.com/results?search_query=${encodeURIComponent(item.title + ' trailer español')}`;

  const containerClasses = isCarousel 
    ? "movie-card min-w-[270px] sm:min-w-[290px] max-w-[310px] flex-shrink-0 snap-start bg-slate-900/95 border border-slate-800/90 rounded-2xl overflow-hidden flex flex-col group shadow-lg"
    : "movie-card bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden flex flex-col group shadow-lg";

  return `
    <article class="${containerClasses}">
      <!-- Poster & Overlay -->
      <div class="relative h-60 sm:h-64 w-full overflow-hidden bg-slate-950">
        <img 
          src="${poster}" 
          alt="${item.title}" 
          class="w-full h-full object-cover object-center group-hover:scale-105 transition duration-500"
          loading="lazy"
          onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=500&auto=format&fit=crop&q=80';"
        />
        <div class="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/30 to-transparent"></div>
        
        <!-- Badges on top -->
        <div class="absolute top-3 left-3 right-3 flex items-center justify-between">
          <span class="px-2.5 py-1 rounded-full text-xs font-extrabold bg-violet-600/90 text-white backdrop-blur-md shadow-md">
            ${matchScore}
          </span>
          <div class="flex items-center gap-1.5 px-2 py-1 rounded-lg bg-slate-950/80 backdrop-blur-md border border-slate-700/60 text-xs font-bold text-amber-300">
            <i data-lucide="star" class="w-3.5 h-3.5 fill-amber-400 text-amber-400"></i>
            <span>${rating}</span>
          </div>
        </div>

        <!-- Bottom Title overlay -->
        <div class="absolute bottom-3 left-4 right-4">
          <span class="text-[11px] font-semibold tracking-wider uppercase text-violet-400 block">${item.type || 'Película'} • ${item.year || ''}</span>
          <h4 class="text-lg sm:text-xl font-bold text-white leading-tight drop-shadow-sm truncate">${item.title}</h4>
        </div>
      </div>

      <!-- Content Body -->
      <div class="p-4 sm:p-5 flex-1 flex flex-col justify-between space-y-3.5">
        <div class="space-y-2.5">
          <!-- Hook -->
          ${item.hook ? `<p class="text-xs font-medium text-slate-300 italic border-l-2 border-violet-500 pl-2.5 leading-snug line-clamp-2">"${item.hook}"</p>` : ''}
          
          <!-- Synopsis -->
          <p class="text-xs text-slate-400 leading-relaxed line-clamp-3">
            ${item.synopsis || item.why_recommended || ''}
          </p>

          <!-- Why Recommended Pill (if present) -->
          ${item.why_recommended ? `
            <div class="p-2.5 rounded-xl bg-violet-500/10 border border-violet-500/20 text-[11px] text-violet-200">
              <span class="font-bold text-violet-300 block mb-0.5">Por qué encaja:</span>
              <p class="line-clamp-2">${item.why_recommended}</p>
            </div>
          ` : ''}

          <!-- Mood Tags -->
          ${item.mood_tags ? `
            <div class="flex flex-wrap gap-1.5 pt-1">
              ${item.mood_tags.slice(0, 3).map(t => `<span class="text-[10px] px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 border border-slate-700/60 font-medium">#${t}</span>`).join('')}
            </div>
          ` : ''}
        </div>

        <!-- Platforms and Trailer Button -->
        <div class="pt-3 border-t border-slate-800/80 space-y-2.5">
          <div class="flex items-center justify-between flex-wrap gap-1.5">
            <span class="text-[11px] font-semibold text-slate-400">Dónde ver:</span>
            <div class="flex flex-wrap gap-1">
              ${platforms.map(p => `
                <span class="text-[10px] px-2 py-0.5 rounded-md font-bold border ${getPlatformClass(p)}">
                  ${p}
                </span>
              `).join('')}
            </div>
          </div>

          <a 
            href="${trailerUrl}" 
            target="_blank" 
            class="w-full flex items-center justify-center gap-2 py-2 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-200 hover:text-white text-xs font-bold transition border border-slate-700/60"
          >
            <i data-lucide="play" class="w-3.5 h-3.5 text-rose-500 fill-rose-500"></i>
            <span>Ver Tráiler</span>
          </a>
        </div>
      </div>
    </article>
  `;
}

// Estilos de plataforma
function getPlatformClass(platform) {
  const p = platform.toLowerCase();
  if (p.includes("netflix")) return "badge-netflix";
  if (p.includes("prime")) return "badge-prime";
  if (p.includes("max") || p.includes("hbo")) return "badge-max";
  if (p.includes("disney")) return "badge-disney";
  if (p.includes("filmin")) return "badge-filmin";
  if (p.includes("apple")) return "badge-apple";
  if (p.includes("movistar")) return "badge-movistar";
  return "badge-default";
}

// Modal de ajustes
function openSettingsModal() {
  const modal = document.getElementById("settings-modal");
  modal.classList.remove("hidden");
  if (window.lucide) lucide.createIcons();
}

function closeSettingsModal() {
  document.getElementById("settings-modal").classList.add("hidden");
}

function togglePasswordView(inputId) {
  const el = document.getElementById(inputId);
  el.type = el.type === "password" ? "text" : "password";
}

async function saveSettings(e) {
  e.preventDefault();
  const apiKey = document.getElementById("cfg-openrouter-key").value.trim();
  const model = document.getElementById("cfg-openrouter-model").value;
  const tmdbKey = document.getElementById("cfg-tmdb-key").value.trim();

  const payload = { openrouter_model: model };
  if (apiKey) payload.openrouter_api_key = apiKey;
  if (tmdbKey) payload.tmdb_api_key = tmdbKey;

  try {
    const res = await fetch("/api/config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error("No se pudo guardar la configuración");

    closeSettingsModal();
    await loadConfig();
    alert("¡Configuración guardada exitosamente en tu ordenador!");
  } catch (err) {
    alert("Error al guardar: " + err.message);
  }
}
