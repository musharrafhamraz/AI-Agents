# Work Insights - Privacy-First Productivity Tracker

> Understand your work patterns without surveillance vibes

A desktop application that tracks your work activity with your explicit consent and provides actionable insights about your productivity patterns—without judgment or guilt.

## 🎯 Philosophy

- **Consent-first**: You control all tracking
- **Local-first**: All data stays on your device
- **Insight-focused**: Patterns, not productivity scores
- **Privacy-respecting**: No external data sharing
- **No guilt**: Neutral language, empowering insights

## ✨ Features

### Core Tracking
- **App usage monitoring**: Track which applications you use and for how long
- **Context switch detection**: Understand when and why you switch between tasks
- **Idle time tracking**: Automatic detection of breaks and away time
- **Smart categorization**: Auto-categorize apps into Deep Work, Communication, Research, etc.

### Insights (No Judgment)
- **Peak performance times**: "You do deep work best between 9:40–11:20 AM"
- **Focus patterns**: Identify your natural work rhythms
- **Context switch analysis**: Understand interruption patterns
- **Work rhythms**: Discover your optimal work/break cycles
- **Weekly summaries**: Actionable insights delivered weekly

### Privacy Controls
- **Pause anytime**: Quick toggle to stop tracking
- **Blocked apps**: Exclude sensitive apps (banking, health, etc.)
- **Data retention**: Auto-delete after configurable period
- **Export/Delete**: Full control over your data
- **Local storage**: Everything stays on your device

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Rust (latest stable)
- Platform-specific requirements (see [QUICK_START.md](QUICK_START.md))

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/work-insights-app.git
cd work-insights-app

# Install dependencies
npm install

# Run in development mode
npm run tauri dev

# Build for production
npm run tauri build
```

## 📊 Screenshots

*(Add screenshots here once UI is built)*

## 🏗️ Tech Stack

- **Desktop Framework**: Tauri (Rust + Web)
- **Frontend**: React + TypeScript + TailwindCSS
- **State Management**: Zustand
- **Charts**: Recharts
- **Database**: SQLite (local)
- **Build**: Vite

## 📖 Documentation

- [Implementation Plan](IMPLEMENTATION_PLAN.md) - Detailed development roadmap
- [Project Structure](PROJECT_STRUCTURE.md) - Code organization
- [Quick Start Guide](QUICK_START.md) - Step-by-step setup
- [Privacy Policy](docs/PRIVACY_POLICY.md) - How we handle your data
- [User Guide](docs/USER_GUIDE.md) - How to use the app

## 🛠️ Development

### Project Structure
```
work-insights-app/
├── src-tauri/          # Rust backend
│   ├── src/
│   │   ├── activity/   # Activity monitoring
│   │   ├── database/   # SQLite operations
│   │   ├── insights/   # Pattern detection
│   │   └── commands/   # Tauri IPC
├── src/                # React frontend
│   ├── components/     # UI components
│   ├── hooks/          # Custom hooks
│   ├── store/          # State management
│   └── services/       # API services
```

### Development Commands

```bash
# Run development server
npm run tauri dev

# Run tests
cargo test              # Rust tests
npm test               # Frontend tests

# Build for production
npm run tauri build

# Lint code
npm run lint
cargo clippy
```

## 🎨 Design Principles

- **Minimal**: Clean, distraction-free interface
- **Calming**: Blues, greens, neutral colors
- **No guilt**: Avoid red/alarm colors
- **Dark mode**: Essential for developers
- **Smooth**: Delightful micro-interactions

## 🔒 Privacy & Security

- **Local-only storage**: No cloud, no servers
- **Encrypted database**: SQLCipher for data at rest
- **No tracking**: No analytics, no telemetry
- **Open source**: Audit the code yourself
- **Transparent**: Clear about what's tracked

## 🗺️ Roadmap

### Phase 1: MVP (Weeks 1-4)
- [x] Project setup
- [ ] Activity monitoring (Windows/macOS/Linux)
- [ ] SQLite database
- [ ] Basic dashboard
- [ ] Privacy controls

### Phase 2: Insights (Weeks 5-6)
- [ ] Pattern detection algorithms
- [ ] Deep work analysis
- [ ] Context switch insights
- [ ] Weekly summaries

### Phase 3: Polish (Week 7)
- [ ] System tray integration
- [ ] Notifications
- [ ] Data export
- [ ] Onboarding flow

### Future Enhancements
- [ ] Calendar integration
- [ ] Pomodoro timer
- [ ] Team insights (optional, anonymized)
- [ ] Mobile companion app
- [ ] AI-powered recommendations

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines first.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by the need for privacy-respecting productivity tools
- Built with Tauri for lightweight, secure desktop apps
- Designed for knowledge workers who value their privacy

## 📧 Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/work-insights-app/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/work-insights-app/discussions)
- **Email**: your.email@example.com

---

**Remember**: This app is about understanding yourself, not judging yourself. Work smarter, not harder. 🌟
