# OpenVox Roadmap

> Spotify for docs. Billion-dollar UX. Mobile-first. Self-hosted TTS.

---

## Legend

| Priority | Meaning |
|----------|---------|
| **P0** | Must have - blocking features |
| **P1** | High - important user value |
| **P2** | Medium - nice to have |
| **P3** | Low - future consideration |
| **P4** | Speculative - experimental |

---

## ✨ UX Overhaul (P0)

This is NOT a developer tool. It's a consumer product.

### Mobile-First (Primary)
- [ ] **Complete UI rewrite** - Spotify-level polish, not a developer tool
- [ ] **Bottom tab navigation** - Home, Library, Search, Settings (no sidebars!)
- [ ] **Full-screen views** - No panels, immersive content
- [ ] **Swipe gestures** - Navigate between screens naturally
- [ ] **Mini player** - Persistent bottom bar when playing, tap to expand
- [ ] **Bottom sheets** - All actions in sheets, not modals

### Visual Design
- [ ] **Custom typography** - Distinctive fonts, not Inter/Roboto
- [ ] **Bold color scheme** - Cohesive aesthetic, sharp accents
- [ ] **Motion design** - Smooth transitions, staggered reveals, micro-interactions
- [ ] **Backgrounds** - Gradient meshes, noise textures, depth (not flat colors)
- [ ] **Haptic feedback** - Physical sensations on mobile

### Desktop
- [ ] **Optional sidebar** - Can show library tree, but not default
- [ ] **Don't stretch mobile** - Desktop has its own elegant layout
- [ ] **Keyboard shortcuts** - Power user features

### Player
- [ ] **Waveform visualization** - Animated, beautiful
- [ ] **Gesture controls** - Swipe left/right for skip on mobile
- [ ] **Sleep timer** - 15/30/45/60 min, end of chapter
- [ ] **Media Session API** - Lock screen controls
- [ ] **Share functionality** - Web Share API

---

## 🎛️ TTS Server (Core)

### P0
- [ ] **Model improvements**
  - Support newer/different TTS models
  - Model selection UI in settings
- [ ] **Voice management**
  - Better voice preview (play sample)
  - Voice categories/tags
  - Search/filter voices

### P1
- [ ] **Voice cloning UI**
  - Upload voice sample (30s-5min)
  - Preview cloned voice
  - Save to personal voice library
- [ ] **Better streaming**
  - Lower latency streaming
  - Stream quality vs speed options

### P2
- [ ] **SSML support**
  - Add pauses (`<break>`)
  - Emphasis tags
  - Pronunciation hints

### P3
- [ ] **Custom voice embeddings**
  - Fine-tune voices on dataset

---

## 📥 Import Sources

### P0
- [ ] **More sources**
  - YouTube video → extract audio → TTS
  - PDF parsing
  - EPUB support

### P1
- [ ] **GitHub/GitLab**
  - Import README.md directly from repos
  - Branch selection
  - Subpath support (already exists)

### P2
- [ ] **Notion integration**
  - Fetch pages via Notion API
- [ ] **Google Docs**
  - Import directly

### P3
- [ ] **Browser extension**
  - "Listen to this page" button

---

## 🎧 Studio UI

### P1
- [ ] **Better player**
  - Chapter markers from headings
  - Skip-to-chapter
  - Playback speed presets
- [ ] **Improved library**
  - Smart playlists (recent, in-progress, favorites)
  - Search across all content
  - Bulk operations

### P2
- [ ] **Transcript view**
  - Show text alongside audio
  - Highlight current position
  - Click to seek

### P3
- [ ] **PWA/offline**
   - Service worker caching
   - Playback offline
   - Queue sync

---

## 📖 Content Accessibility Features

*Features inspired by Speechify and Natural Reader for enhanced accessibility and productivity*

### P1 (High Priority)
- [ ] **Extended Speed Control** — 0.5x to 9x playback (Speechify feature)
  - Browser audio processing to exceed native limits
  - Preset speeds: 0.5x, 0.75x, 1x, 1.25x, 1.5x, 2x, 3x, 4.5x, 9x
  - Fine-grained slider in player

- [ ] **OCR / Camera Scanning** — Scan physical books (Speechify's standout feature)
  - Use Tesseract.js in browser for client-side OCR
  - Camera capture via getUserMedia API
  - Support for photographed documents, handwritten notes
  - Server-side fallback with pytesseract for batch processing

- [ ] **Pronunciation Editor** — Custom word pronunciations (Natural Reader feature)
  - Dictionary UI per source
  - IPA or phonetic spelling support
  - Bulk import/export pronunciation lists

### P2 (Medium Priority)
- [ ] **MP3 Export** — Downloadable audio files (Natural Reader wins here)
  - Convert WAV to MP3 on server using pydub
  - Bitrate options: 64kbps, 128kbps, 192kbps, 320kbps
  - Batch export for playlists

- [ ] **Dyslexia Font Support** — Reading accessibility
  - OpenDyslexic font option in settings
  - Toggle in player for subtitle display
  - Adjustable letter spacing

- [ ] **Floating Toolbar** — Persistent TTS bar (Natural Reader feature)
  - Always-on-top mini player
  - Global keyboard shortcut activation
  - Works across browser tabs (as browser extension concept)

- [ ] **Bookmarking & Annotations** — Study features
  - Save timestamps with notes
  - Highlight passages
  - Export annotations as markdown

### P3 (Lower Priority)
- [ ] **Dictionary Lookup** — Tap word for definition
  - Integrate free dictionary API
  - Show in subtitle overlay

- [ ] **Highlight & Repeat** — Loop sections
  - A-B loop controls in player
  - Save loop points for reuse

- [ ] **AI Smart Filtering** — Auto-skip non-content
  - Detect and skip headers, page numbers, footers
  - Configurable filters in cleaning settings

---

## 👥 Collaboration

### P0
- [ ] **Multi-user support**
  - User authentication (email, passkeys)
  - Per-user library isolation
  - Session management

### P1
- [ ] **Episode sharing**
  - Public URL generation
  - Optional password protection
  - Embed player

### P2
- [ ] **Team workspaces**
  - Shared folders
  - Role-based access (owner, editor, viewer)

### P2
- [ ] **API tokens**
  - Programmatic access
  - Token management UI
  - Rate limiting

### P2
- [ ] **WebSockets**
  - Real-time generation progress updates
  - Live playback position sync across clients
  - Import progress streaming
  - Connection status indicator in UI

---

## 🧩 Integrations

### P1
- [ ] **WingmanAI improvements**
  - Better hotkey support
  - Quick-speak overlay
  - Profile per-game settings

### P2
- [ ] **OBS plugin**
  - Text-to-speech in OBS
  - Voice selection
  - Read chat, read file, etc.

### P3
- [ ] **Home Assistant**
   - TTS entity for HA
   - Automations

---

## Technical Implementation Notes

### New Dependencies
```
# Backend
pytesseract>=0.3.10    # OCR processing
pydub>=0.25.1          # MP3 conversion

# Frontend (CDN)
tesseract.js            # Client-side OCR
```

### Database Schema Additions
```sql
-- pronunciation_dictionary table
CREATE TABLE pronunciation_dictionary (
    id TEXT PRIMARY KEY,
    source_id TEXT,
    word TEXT,
    pronunciation TEXT,
    FOREIGN KEY(source_id) REFERENCES sources(id)
);

-- bookmarks table  
CREATE TABLE bookmarks (
    id TEXT PRIMARY KEY,
    episode_id TEXT,
    chunk_index INTEGER,
    position_secs REAL,
    note TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(episode_id) REFERENCES episodes(id)
);
```

### New API Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/studio/sources/{id}/pronunciations` | POST | Set pronunciation dictionary |
| `/api/studio/sources/ocr` | POST | Upload image for OCR |
| `/api/studio/bookmarks` | POST | Create bookmark |
| `/api/studio/episodes/{id}/bookmarks` | GET | Get episode bookmarks |
| `/api/studio/export/mp3` | POST | Convert and export MP3 |

---

## Prioritized Quick Wins

1. **UX Overhaul** - This IS the product. Billion-dollar or nothing.
2. **Voice cloning UI** - Huge feature, highly requested
3. **PDF/EPUB import** - Major content gap
4. **Multi-user** - Foundational for self-hosting
5. **Episode sharing** - Quick win for demos

---

## Released

| Version | Date | Features |
|---------|------|----------|
| 0.1.0 | 2026-02 | Initial release - TTS, library, player |
| 0.0.1 | - | Docker versioning |
