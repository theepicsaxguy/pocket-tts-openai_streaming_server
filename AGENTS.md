# Project Overview

A self-hosted **TTS server** with an OpenAI-compatible API and a Studio UI for consuming documentation. Turn technical documentation, markdown files, and web pages into listenable audio — runs locally on CPU.

**Not a podcast creation tool** — this is a **Spotify for docs**. Billion-dollar UX. Mobile-first. Spotify should look like a cheap copy.

## UX Vision

This is NOT a developer tool. It's a consumer product that happens to be self-hosted.

- **Spotify-level polish**: Every interaction feels premium, smooth, intentional
- **Mobile-first**: Design for phone first, then scale up to desktop
- **No sidebars on mobile**: Bottom tab navigation only (like Spotify, Apple Music)
- **Billion-dollar aesthetic**: Bold, distinctive, unforgettable. Not generic "AI slop"
- **Instantly addictive**: The UX is so good users can't stop using it

## Architecture

```
server.py                    # Entry point, CLI, starts Waitress
    └── app/__init__.py      # Flask app factory
        ├── app/routes.py    # API endpoints (OpenAI-compatible)
        ├── app/config.py    # Environment config
        └── app/services/
            ├── tts.py       # TTSService: model, voice cache
            └── audio.py     # Format conversion, streaming
        └── app/studio/      # Podcast Studio feature set
            ├── __init__.py  # Blueprint registration
            ├── db.py        # SQLite persistence (no ORM)
            ├── repositories.py # DB query abstraction layer
            ├── sources_routes.py   # Source CRUD endpoints
            ├── episodes_routes.py  # Episode CRUD endpoints
            ├── folders_routes.py   # Folder CRUD endpoints
            ├── tags_routes.py      # Tag CRUD endpoints
            ├── playback_routes.py  # Playback state endpoints
            ├── settings_routes.py  # Settings endpoints
            ├── library_routes.py   # Library tree, generation status
            ├── ingestion.py # File/URL/text import
            ├── git_ingestion.py   # Git repository import
            ├── normalizer.py # Text cleaning/normalization
            ├── chunking.py  # Text chunking strategies
            ├── breathing.py # Natural pause insertion
            ├── generation.py # Single-worker audio generation queue
            └── audio_assembly.py # Merge chunks to full episode
```

## Key Files

| File | Purpose |
|------|---------|
| `server.py` | Entry point, CLI args, Waitress server |
| `app/routes.py` | HTTP endpoints: `/`, `/health`, `/v1/voices`, `/v1/audio/speech` |
| `app/services/tts.py` | Model loading, voice caching, generation |
| `app/services/audio.py` | Audio format conversion, streaming |
| `app/studio/repositories.py` | DB query abstraction (Source, Episode, Chunk, Folder, Tag, Playback, Settings) |
| `app/studio/sources_routes.py` | Source CRUD, cover art, re-clean |
| `app/studio/episodes_routes.py` | Episode CRUD, chunk audio, regenerate |
| `app/studio/folders_routes.py` | Folder CRUD, playlist |
| `app/studio/tags_routes.py` | Tag management |
| `app/studio/playback_routes.py` | Playback state |
| `app/studio/settings_routes.py` | User settings |
| `app/studio/library_routes.py` | Library tree, generation status, preview |
| `app/studio/db.py` | SQLite schema and connection management |
| `app/studio/generation.py` | Background audio generation queue |
| `templates/studio.html` | Mobile-first Studio UI shell |
| `static/js/studio/` | Frontend JavaScript modules |
| `static/css/studio.css` | Dark mode UI styles |

## API Endpoints

### OpenAI-Compatible (unchanged)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Web UI (Studio) |
| `/health` | GET | Health check |
| `/v1/voices` | GET | List voices |
| `/v1/audio/speech` | POST | Generate speech |

### Studio API (`/api/studio`)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/sources` | GET/POST | List/create sources |
| `/sources/{id}` | GET/PUT/DELETE | Source operations |
| `/sources/{id}/re-clean` | POST | Re-normalize text |
| `/preview-clean` | POST | Preview text normalization |
| `/preview-chunks` | POST | Preview chunking |
| `/episodes` | GET/POST | List/create episodes |
| `/episodes/{id}` | GET/DELETE | Episode operations |
| `/episodes/{id}/regenerate` | POST | Regenerate all chunks |
| `/episodes/{id}/chunks/{idx}/regenerate` | POST | Regenerate single chunk |
| `/episodes/{id}/audio/{idx}` | GET | Serve chunk audio |
| `/episodes/{id}/audio/full` | GET | Download full episode |
| `/generation/status` | GET | Queue status |
| `/library/tree` | GET | Full library structure |
| `/folders` | POST | Create folder |
| `/folders/{id}` | PUT/DELETE | Folder operations |
| `/playback/{id}` | GET/POST | Playback state |
| `/settings` | GET/PUT | User settings |
| `/tags` | GET/POST | Tag management |

## Configuration (Environment Variables)

| Variable | Default | Purpose |
|----------|---------|---------|
| `POCKET_TTS_HOST` | `0.0.0.0` | Bind address |
| `POCKET_TTS_PORT` | `49112` | Port |
| `POCKET_TTS_VOICES_DIR` | None | Custom voices path |
| `POCKET_TTS_DATA_DIR` | `./data` | Studio data directory |
| `POCKET_TTS_STREAM_DEFAULT` | `true` | Default streaming |
| `POCKET_TTS_LOG_LEVEL` | `INFO` | Log verbosity |
| `HF_TOKEN` | None | HuggingFace token |

## Workflow

1. **Import** (`#import`) - Full-screen import: file upload, paste URL, or text
2. **Review** (`#source/{id}`) - View cleaned text, configure voice/chunk settings, generate
3. **Episode** (`#episode/{id}`) - Full-screen player, track generation progress, download
4. **Library** (`#library`) - Organize sources/episodes in folders, swipe to browse

## Development

```bash
# Run locally
pip install -r requirements.txt
python server.py --log-level DEBUG

# Run with Docker
docker compose up --build

# Test OpenAI endpoint
curl http://localhost:49112/health
curl -X POST http://localhost:49112/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello", "voice": "alba"}' -o test.mp3
```

## Code Style

- Linter/formatter: `ruff` (config in `pyproject.toml`)
- Line length: 100
- Single quotes
- Type hints optional but encouraged

## Roadmap

See [ROADMAP.md](./ROADMAP.md) for feature priorities and upcoming work.

## Deployment

- Docker-first with non-root user
- CPU-only PyTorch (smaller image)
- Single-worker generation queue (good for 1 CPU)
- Data persistence via volume mounts:
  - `./data` - SQLite DB, sources, audio files
  - `./logs` - Application logs

## Data Storage

All data stored in `POCKET_TTS_DATA_DIR` (default `/app/data`):

```
data/
├── podcast_studio.db    # SQLite database
├── sources/             # Original imported files
└── audio/               # Generated audio chunks
    └── {episode_id}/
        ├── 0.wav
        ├── 1.wav
        └── ...
```

## Generation Queue

- Single background thread processes episodes sequentially
- Good for CPU-constrained environments
- No GPU code paths (CPU-only)
- Status tracking: `pending` → `generating` → `ready`/`error`

## Frontend Architecture

### Mobile (Primary - No Sidebars!)
- **Bottom tab navigation** (like Spotify, Apple Music): Home, Library, Search, Settings
- **Full-screen views**: No sidebars, no panels
- **Swipe gestures**: Navigate between screens
- **Mini player**: Collapsed at bottom when playing, tap to expand
- **Bottom sheets**: All actions in bottom sheets, not modals

### Desktop (Secondary)
- Can show sidebar for library tree
- But maintain mobile UX feel - don't just stretch the mobile layout
- Three-pane optional, not default

### Screens (Hash Routes)
- `#home` - Home feed (recent, continue listening, recommended)
- `#library` - User's content organized
- `#search` - Search sources/episodes
- `#settings` - Settings panel
- `#import` - Import new content (full screen)
- `#source/{id}` - Source details
- `#episode/{id}` - Episode player (full screen)

JavaScript modules:
- `main.js` - Entry point, routing, bottom tab nav
- `home.js` - Home feed
- `library.js` - Library view, folder tree
- `search.js` - Search functionality
- `player.js` - Player coordinator (re-exports all player modules)
- `player-state.js` - Player state management
- `player-controls.js` - Play/pause, seek, volume controls
- `player-queue.js` - Queue management, shuffle, repeat
- `player-waveform.js` - Waveform visualization
- `player-render.js` - Mini/full player rendering
- `player-chunk.js` - Chunk loading and playback
- `editor.js` - Import, source, episode views
- `settings.js` - Settings panel
- `api.js` - API client
- `state.js` - Pub/sub state management
- `dom.js` - Safe DOM manipulation helpers

## Design Principles

### UX Philosophy
- **Think Spotify, but better**: Every pixel matters. Smooth transitions. Intuitive gestures. No friction.
- **Mobile-first, always**: If it doesn't work on mobile, it's not done
- **No compromises**: Generic is dead. Make it memorable.
- **Delight in details**: Micro-animations, haptic feedback, unexpected touches

### Frontend Aesthetics (when building UI)
- **Typography**: Choose fonts that are beautiful, unique, interesting. Avoid generic fonts (Inter, Roboto, Arial). Pair a distinctive display font with a refined body font.
- **Color & Theme**: Commit to a cohesive aesthetic. Use CSS variables. Dominant colors with sharp accents beat timid, evenly-distributed palettes.
- **Motion**: Animations for effects and micro-interactions. Staggered reveals on page load. Scroll-triggering. Hover states that surprise.
- **Spatial Composition**: Unexpected layouts. Asymmetry. Overlap. Diagonal flow. Grid-breaking. Generous negative space OR controlled density.
- **Backgrounds**: Create atmosphere and depth. Gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows. NOT solid flat colors.

NEVER use: generic AI slop aesthetics, overused fonts, cliched purple gradients, predictable layouts, cookie-cutter design.

### SOLID Principles (Python)

- **S**ingle Responsibility: Each module/class should do one thing well
  - Route modules handle HTTP (`sources_routes.py`, `episodes_routes.py`, etc.)
  - `db.py` handles persistence, `generation.py` handles queue
  - Repositories handle all database queries
- **O**pen/Closed: Open for extension, closed for modification
  - Add new chunking strategies without modifying existing code
  - Add new cleaning options via options object, not if/else chains
- **L**iskov Substitution: Subtypes should be substitutable for base types
- **I**nterface Segregation: Prefer small, focused interfaces
- **D**ependency Inversion: Depend on abstractions, not concretions
  - Use service functions (`get_tts_service()`) rather than direct imports where appropriate

### Code Reuse Guidelines

Before writing new code, check if existing solutions exist:

1. **Frontend utilities**: Check `main.js` for `escapeHtml`, `formatTime`, `toast`, `confirm`, etc.
2. **DOM helpers**: Use `dom.js` for safe DOM manipulation (`setText`, `fromHTML`, `createElement`)
3. **State management**: Use `state.js` pub/sub - don't create new event systems
4. **API calls**: Use `api.js` functions, add new endpoints there
5. **CSS utilities**: Check existing classes in `studio.css` before adding new styles
6. **Python utilities**: Check `app/studio/` for existing helpers before adding new modules
7. **Database queries**: Use repository classes in `repositories.py` instead of raw SQL

Avoid:
- Reinventing common patterns (modals, toasts, dropdowns already exist)
- Duplicating similar logic in multiple places
- Adding new state management when `state.js` suffices
- Creating custom CSS when existing classes work

## Code Organization Principles

### Python Backend

**Route Module Splitting**
- Split large route files (>500 lines) into domain-specific modules
- Each domain gets its own file: `sources_routes.py`, `episodes_routes.py`, etc.
- All route modules must have `register_routes(bp)` function
- Register all route modules in `__init__.py`

**Database Layer**
- Never put raw SQL in route handlers - use repository classes
- Create repository classes in `repositories.py` for each entity
- Repository methods take `db` connection as first parameter
- Use parameterized queries exclusively (no SQL injection)

**Import Convention**
- All imports at top of file (never inline `import` inside functions)
- Order: stdlib → third-party → local imports
- Example:
  ```python
  import os
  import uuid
  from flask import jsonify, request
  from app.config import Config
  from app.studio.db import get_db
  from app.studio.repositories import SourceRepository
  ```

**Type Hints**
- Add type hints to all function signatures
- Use `sqlite3.Row | None` for optional database rows
- Add return types to route handlers

### JavaScript Frontend

**Module Splitting**
- Split monolithic files (>500 lines) into focused modules
- Player code split into: state, controls, queue, waveform, render, chunk
- Use ES modules with explicit exports

**DOM Safety**
- Never use `innerHTML` with user-provided data
- Use `dom.js` helpers: `setText()`, `fromHTML()`, `createElement()`
- Only use `innerHTML` for trusted static content (SVG icons, server-trusted API responses)

**State Management**
- Use `state.js` pub/sub for shared state
- Never create new event systems
- Sync state across components (mini player ↔ full player)

### Dead Code Removal

- Remove unused files immediately (templates, JS, CSS)
- Delete old route files when splitting
- Update CI configs to remove ignores for deleted files

## Additional Guidelines

1. **UI State Synchronization**: When multiple UI components share state (e.g., mini player and fullscreen player), changes in one must sync to the other. Use localStorage or shared event handlers.

2. **Database Foreign Key Validation**: Always validate that referenced entities exist before performing operations. Don't rely solely on FK constraints - check existence and return proper error messages.

3. **Recovery from Server Crashes**: For long-running background operations (like audio generation), implement startup recovery that resets stuck/inconsistent states to known good values.
