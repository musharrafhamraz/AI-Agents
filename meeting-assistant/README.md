# Meeting Assistant

AI-powered cross-platform desktop meeting assistant with real-time transcription, smart notes, and multi-language support.

## Features

- 🎙️ **Live Transcription** - Real-time speech-to-text with Whisper
- 👥 **Speaker Diarization** - Automatic speaker identification with color coding
- 🤖 **AI Assistant** - Ask questions and get instant answers from your meeting
- 📝 **Smart Notes** - Auto-generated notes (key points, action items, decisions)
- ✨ **Live Note Generation** - AI extracts notes automatically every 30 seconds
- 🌍 **Multi-Language** - Transcription support (English by default)
- 🔒 **Privacy First** - Local processing option - your data stays on your device
- ⏰ **Meeting History** - Search and review all your past meetings
- 📤 **Export** - Markdown export with full meeting details

## Tech Stack

- **Frontend**: React + TypeScript + Vite
- **Backend**: Tauri (Rust)
- **Database**: SQLite
- **State Management**: Zustand
- **Styling**: CSS Variables + Modern Design System

## Getting Started

### Prerequisites

- Node.js 18+
- Rust 1.70+
- npm or yarn

### Installation

1. Clone the repository
2. Install npm dependencies:

```bash
cd meeting-assistant
npm install
```

3. Install Rust dependencies:

```bash
cd src-tauri
cargo build
```

### Development

Run the development server:

```bash
npm run tauri:dev
```

This will start both the Vite dev server and the Tauri application.

### Building

Build for production:

```bash
npm run tauri:build
```

The built application will be in `src-tauri/target/release`.

## Project Structure

```
meeting-assistant/
├── src/                          # React frontend
│   ├── components/               # Reusable UI components
│   ├── pages/                    # Page components
│   ├── store/                    # Zustand state management
│   ├── styles/                   # Global styles
│   ├── types/                    # TypeScript types
│   └── utils/                    # Utility functions
├── src-tauri/                    # Rust backend
│   ├── src/
│   │   ├── main.rs              # Tauri entry point
│   │   ├── commands.rs          # IPC commands
│   │   ├── models.rs            # Data models
│   │   └── db.rs                # Database operations
│   ├── Cargo.toml               # Rust dependencies
│   └── tauri.conf.json          # Tauri configuration
├── package.json
└── vite.config.ts
```

## Roadmap

### Phase 1: MVP ✅ COMPLETE
- [x] Project setup & core infrastructure
- [x] Audio capture module
- [x] Whisper transcription integration
- [x] AI assistant (OpenAI/Anthropic/Groq)
- [x] Meeting save/load (SQLite)
- [x] Export functionality (Markdown)

### Phase 2: Enhanced ✅ COMPLETE
- [x] Speaker diarization (simple algorithm)
- [x] Live note generation (AI-powered)
- [x] Screen context infrastructure
- [x] Enhanced UI with speakers and notes
- [x] Configurable services

### Phase 3: Pro Features (Next)
- [ ] Meeting summaries
- [ ] Action item extraction UI
- [ ] Calendar integrations
- [ ] More export formats
- [ ] Search across meetings
- [ ] Floating overlay mode

### Phase 4: Enterprise (Future)
- [ ] Team features
- [ ] Admin dashboard
- [ ] SSO integration
- [ ] Compliance features
- [ ] Custom model support
- [ ] API for integrations

## License

MIT
