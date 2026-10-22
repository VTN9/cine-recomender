# 🎬 CineMatch AI — Recomendador Local de Cine y Series con OpenRouter

Una aplicación web moderna, rápida y local que utiliza modelos de lenguaje (LLMs) a través de **OpenRouter** para recomendar películas y series según tu estado de ánimo, plataforma de streaming o preferencias compartidas en pareja.

---

## 🌟 Características Principales

1. **Búsqueda Semántica con IA (OpenRouter)**:
   - Describe lo que te apetece en lenguaje natural (*"Thriller nórdico con nieve y giros constantes"*, *"Peli estilo Interstellar bajo el mar"*, *"Comedia negra para desconectar"*).
   - Compatible con cualquier modelo de OpenRouter: **Llama 3.3 70B**, **DeepSeek Chat / R1**, **Gemini 2.5 Flash**, **Mistral Small**, etc.
2. **Modo Pareja & Amigos**:
   - Introduce los gustos opuestos de dos personas (ej. uno quiere terror psicológico y el otro comedia ligera) y la IA encuentra el puente y compromiso cinematográfico exacto.
3. **Filtro de Dónde Ver (Streaming)**:
   - Netflix, Amazon Prime Video, Max, Disney+, Filmin, Apple TV+, Movistar+.
4. **Filtros por Estado de Ánimo (Moods)**:
   - Mente Explotada, Domingo de Manta, Para Llorar, Risas, Adrenalina pura, Cine de autor.
5. **Enlaces Directos a Tráilers**:
   - Cada tarjeta incluye botón de visualización de tráiler en YouTube.
6. **Configuración Visual e Intuitiva**:
   - Puedes ingresar tu API Key de OpenRouter y cambiar de modelo directamente desde la interfaz web (botón **Ajustes & API**), sin editar código manualmente.

---

## 🚀 Cómo Iniciar la Aplicación en tu Ordenador

Tienes dos opciones muy sencillas:

### Opción 1: Doble Clic (Recomendada en Windows)
Haz doble clic en el archivo **`iniciar.bat`**. Se abrirá la consola y tu navegador web se abrirá automáticamente en `http://localhost:8000`.

### Opción 2: Desde la Terminal
Abre PowerShell o CMD en esta carpeta y ejecuta:

```bash
python run.py
```

Luego abre en tu navegador: **`http://localhost:8000`**

---

## 🔑 Configurar tu OpenRouter API Key

1. Accede a [openrouter.ai/keys](https://openrouter.ai/keys) y genera tu clave gratuita o de saldo.
2. Abre la aplicación en `http://localhost:8000`.
3. Haz clic en el botón superior derecho **"Ajustes & API"**.
4. Pega tu API Key y elige tu modelo preferido (por ejemplo, *Llama 3.3 70B* o *DeepSeek*).
5. Pulsa **"Guardar Cambios"**. La clave quedará guardada de forma segura en tu archivo local `.env`.

> 💡 *Nota:* Si aún no tienes API Key, la aplicación incluye un **Modo Demo Local** con un catálogo curado para que puedas probar la interfaz y sus funciones de inmediato.

---

## 🛠️ Estructura del Proyecto

```text
cine-recommender/
│── main.py              # Backend FastAPI con endpoints y conexión a OpenRouter
│── run.py               # Lanzador con apertura automática de navegador
│── iniciar.bat          # Acceso directo para Windows
│── requirements.txt     # Dependencias de Python
│── .env                 # Variables de entorno locales (API keys)
└── static/
    │── index.html       # Interfaz visual responsive con Tailwind CSS y Lucide Icons
    │── app.js           # Lógica del cliente, llamadas a la API y renderizado
    └── style.css        # Estilos, efectos de brillo y badges de plataformas
```
