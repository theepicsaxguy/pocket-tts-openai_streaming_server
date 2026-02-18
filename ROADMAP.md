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

### P3
- [ ] **Webhooks**
  - Events: generation complete, import failed
  - Configurable retry

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
