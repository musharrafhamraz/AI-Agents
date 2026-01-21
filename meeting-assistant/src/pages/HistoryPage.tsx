import { useState } from 'react';
import { Search, Calendar, Clock, Users, Download, Trash2 } from 'lucide-react';
import { useMeetingStore } from '@/store';
import { formatDate, formatDuration, formatRelativeTime } from '@/utils/formatters';
import './HistoryPage.css';

export function HistoryPage() {
  const { meetings } = useMeetingStore();
  const [searchQuery, setSearchQuery] = useState('');

  const filteredMeetings = meetings.filter(meeting =>
    meeting.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Demo meetings for UI preview
  const demoMeetings = [
    {
      id: '1',
      title: 'Product Strategy Meeting',
      startTime: new Date(Date.now() - 2 * 60 * 60 * 1000),
      endTime: new Date(Date.now() - 1 * 60 * 60 * 1000),
      participants: [{ id: '1', name: 'John', color: '#6366f1' }, { id: '2', name: 'Sarah', color: '#10b981' }],
      duration: 3600000,
      noteCount: 12,
    },
    {
      id: '2',
      title: 'Weekly Standup',
      startTime: new Date(Date.now() - 24 * 60 * 60 * 1000),
      endTime: new Date(Date.now() - 23.5 * 60 * 60 * 1000),
      participants: [{ id: '1', name: 'Team', color: '#f59e0b' }],
      duration: 1800000,
      noteCount: 5,
    },
    {
      id: '3',
      title: 'Client Presentation - Q4 Review',
      startTime: new Date(Date.now() - 48 * 60 * 60 * 1000),
      endTime: new Date(Date.now() - 47 * 60 * 60 * 1000),
      participants: [{ id: '1', name: 'Alex', color: '#22d3ee' }],
      duration: 5400000,
      noteCount: 18,
    },
  ];

  const displayMeetings = meetings.length > 0 ? filteredMeetings : demoMeetings;

  return (
    <div className="history-page animate-fade-in">
      <div className="history-header">
        <div className="search-bar">
          <Search className="search-icon" />
          <input
            type="text"
            placeholder="Search meetings..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        
        <div className="header-actions">
          <select className="filter-select">
            <option value="all">All Meetings</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
          </select>
        </div>
      </div>

      {displayMeetings.length === 0 ? (
        <div className="empty-state">
          <Calendar className="empty-icon" />
          <h3>No meetings found</h3>
          <p>Your meeting history will appear here</p>
        </div>
      ) : (
        <div className="meetings-list">
          {displayMeetings.map((meeting: any) => (
            <MeetingCard key={meeting.id} meeting={meeting} />
          ))}
        </div>
      )}
    </div>
  );
}

function MeetingCard({ meeting }: { meeting: any }) {
  const duration = meeting.endTime 
    ? meeting.endTime.getTime() - meeting.startTime.getTime()
    : meeting.duration || 0;

  return (
    <div className="meeting-card">
      <div className="card-main">
        <h3 className="card-title">{meeting.title}</h3>
        
        <div className="card-meta">
          <span className="meta-item">
            <Calendar className="meta-icon" />
            {formatDate(meeting.startTime)}
          </span>
          <span className="meta-item">
            <Clock className="meta-icon" />
            {formatDuration(duration)}
          </span>
          <span className="meta-item">
            <Users className="meta-icon" />
            {meeting.participants?.length || 0} participants
          </span>
        </div>
        
        <div className="card-stats">
          <span className="stat">{meeting.noteCount || 0} notes</span>
          <span className="stat-dot">•</span>
          <span className="stat">{formatRelativeTime(meeting.startTime)}</span>
        </div>
      </div>
      
      <div className="card-actions">
        <button className="action-btn" title="Download">
          <Download />
        </button>
        <button className="action-btn danger" title="Delete">
          <Trash2 />
        </button>
      </div>
    </div>
  );
}
