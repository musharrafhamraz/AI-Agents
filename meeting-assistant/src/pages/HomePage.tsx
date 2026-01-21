import { useNavigate } from 'react-router-dom';
import { Mic, Clock, FileText, Globe, Shield, Sparkles } from 'lucide-react';
import { useMeetingStore } from '@/store';
import './HomePage.css';

const features = [
  {
    icon: Mic,
    title: 'Live Transcription',
    description: 'Real-time speech-to-text with speaker identification',
  },
  {
    icon: Sparkles,
    title: 'AI Assistant',
    description: 'Ask questions and get instant answers from your meeting',
  },
  {
    icon: FileText,
    title: 'Smart Notes',
    description: 'Auto-generated notes, action items, and summaries',
  },
  {
    icon: Globe,
    title: 'Multi-Language',
    description: 'Transcription and live translation in 80+ languages',
  },
  {
    icon: Shield,
    title: 'Privacy First',
    description: 'Local processing option - your data stays on your device',
  },
  {
    icon: Clock,
    title: 'Meeting History',
    description: 'Search and review all your past meetings',
  },
];

export function HomePage() {
  const navigate = useNavigate();
  const { startMeeting } = useMeetingStore();

  const handleStartMeeting = () => {
    startMeeting('');
    navigate('/meeting');
  };

  return (
    <div className="home-page animate-fade-in">
      <div className="home-hero">
        <div className="home-hero-content">
          <h1 className="home-title">
            Your AI-Powered
            <span className="gradient-text"> Meeting Companion</span>
          </h1>
          <p className="home-subtitle">
            Never miss a detail. Get real-time transcription, smart notes, 
            and AI assistance during every meeting.
          </p>
          <button className="btn-primary" onClick={handleStartMeeting}>
            <Mic className="btn-icon" />
            Start New Meeting
          </button>
        </div>
        <div className="home-hero-glow" />
      </div>

      <section className="home-features">
        <h2 className="features-title">Everything you need for productive meetings</h2>
        <div className="features-grid">
          {features.map((feature, index) => (
            <div 
              key={feature.title} 
              className="feature-card animate-slide-up"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <div className="feature-icon-wrapper">
                <feature.icon className="feature-icon" />
              </div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
