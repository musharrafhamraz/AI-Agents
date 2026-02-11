import { useEffect, useState } from 'react';
import { useTrackingStore } from '../store/trackingStore';
import { formatDuration } from '../utils/formatters';
import { invoke } from '@tauri-apps/api/core';
import { autostartService } from '../services/autostart';

export const Dashboard = () => {
  const { 
    isTracking, 
    todayStats, 
    isLoading,
    startTracking, 
    stopTracking, 
    fetchStatus,
    fetchTodayStats 
  } = useTrackingStore();

  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [activityCount, setActivityCount] = useState<number>(0);
  const [currentTime, setCurrentTime] = useState<Date>(new Date());
  const [autostartEnabled, setAutostartEnabled] = useState<boolean>(false);
  const [showSettings, setShowSettings] = useState<boolean>(false);

  useEffect(() => {
    // Update current time every second
    const timeInterval = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    // Check autostart status
    checkAutostartStatus();

    return () => clearInterval(timeInterval);
  }, []);

  const checkAutostartStatus = async () => {
    try {
      const enabled = await autostartService.isEnabled();
      setAutostartEnabled(enabled);
    } catch (error) {
      console.error('Failed to check autostart:', error);
    }
  };

  const toggleAutostart = async () => {
    try {
      if (autostartEnabled) {
        await autostartService.disable();
        setAutostartEnabled(false);
      } else {
        await autostartService.enable();
        setAutostartEnabled(true);
      }
    } catch (error) {
      console.error('Failed to toggle autostart:', error);
      alert('Failed to change autostart setting. Please try again.');
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchStatus();
    fetchTodayStats();
    setLastUpdate(new Date());
    updateActivityCount();
    
    // Set up interval for updates
    const interval = setInterval(() => {
      fetchTodayStats();
      setLastUpdate(new Date());
      updateActivityCount();
    }, 5000); // Update every 5 seconds for better responsiveness

    return () => clearInterval(interval);
  }, []); // Empty dependency array is fine here

  const updateActivityCount = async () => {
    try {
      const count = await invoke<number>('get_activity_count');
      setActivityCount(count);
    } catch (error) {
      console.error('Failed to get activity count:', error);
    }
  };

  const handleToggleTracking = async () => {
    if (isTracking) {
      await stopTracking();
    } else {
      await startTracking();
    }
    await fetchTodayStats();
    setLastUpdate(new Date());
    updateActivityCount();
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '0',
      margin: '0'
    }}>
      {/* Header */}
      <header style={{
        background: 'rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
        padding: '24px 32px'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
          <div style={{ flex: '1', minWidth: '250px' }}>
            <h1 style={{ fontSize: '32px', fontWeight: '700', color: '#ffffff', marginBottom: '4px' }}>
              Work Insights
            </h1>
            <p style={{ fontSize: '14px', color: 'rgba(255, 255, 255, 0.8)' }}>
              Understanding your work patterns • Activities: {activityCount}
            </p>
          </div>
          
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '16px',
            flexWrap: 'wrap'
          }}>
            {/* Real-time Clock */}
            <div style={{
              background: 'rgba(255, 255, 255, 0.15)',
              backdropFilter: 'blur(10px)',
              padding: '12px 20px',
              borderRadius: '12px',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '11px', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '2px' }}>
                CURRENT TIME
              </div>
              <div style={{ fontSize: '20px', fontWeight: '700', color: '#ffffff', fontFamily: 'monospace' }}>
                {currentTime.toLocaleTimeString()}
              </div>
              <div style={{ fontSize: '11px', color: 'rgba(255, 255, 255, 0.7)', marginTop: '2px' }}>
                Last update: {lastUpdate.toLocaleTimeString()}
              </div>
            </div>
            
            <button
              onClick={handleToggleTracking}
              disabled={isLoading}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '12px 24px',
                borderRadius: '12px',
                fontWeight: '600',
                fontSize: '14px',
                border: 'none',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                background: isTracking ? '#ef4444' : '#10b981',
                color: '#ffffff',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
                transition: 'all 0.2s',
                opacity: isLoading ? 0.6 : 1
              }}
              onMouseOver={(e) => {
                if (!isLoading) {
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = '0 6px 16px rgba(0, 0, 0, 0.2)';
                }
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
              }}
            >
              <span style={{ fontSize: '18px' }}>
                {isTracking ? '⏸' : '▶'}
              </span>
              {isTracking ? 'Pause Tracking' : 'Start Tracking'}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main style={{ maxWidth: '1200px', margin: '0 auto', padding: '32px' }}>
        {/* Status Banner */}
        <div style={{
          marginBottom: '32px',
          padding: '16px 20px',
          borderRadius: '12px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          background: isTracking 
            ? 'rgba(16, 185, 129, 0.2)' 
            : 'rgba(148, 163, 184, 0.2)',
          border: `2px solid ${isTracking ? 'rgba(16, 185, 129, 0.4)' : 'rgba(148, 163, 184, 0.4)'}`,
          backdropFilter: 'blur(10px)'
        }}>
          <div style={{
            width: '12px',
            height: '12px',
            borderRadius: '50%',
            background: isTracking ? '#10b981' : '#94a3b8',
            animation: isTracking ? 'pulse 2s infinite' : 'none'
          }} />
          <span style={{ fontWeight: '500', color: '#ffffff', fontSize: '14px' }}>
            {isTracking 
              ? '✅ Tracking active - Your activity is being monitored' 
              : '⏸️ Tracking paused - No data is being collected'}
          </span>
        </div>

        {/* Stats Grid */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', 
          gap: '24px', 
          marginBottom: '32px' 
        }}>
          {/* Focus Time Card */}
          <div style={{
            background: 'rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(10px)',
            borderRadius: '16px',
            padding: '24px',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
            transition: 'transform 0.2s'
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.transform = 'translateY(-4px)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
              <div style={{
                width: '48px',
                height: '48px',
                borderRadius: '12px',
                background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '24px'
              }}>
                ⏱️
              </div>
              <h3 style={{ fontSize: '16px', fontWeight: '600', color: 'rgba(255, 255, 255, 0.9)' }}>
                Focus Time
              </h3>
            </div>
            <p style={{ fontSize: '48px', fontWeight: '700', color: '#ffffff', marginBottom: '8px' }}>
              {todayStats ? formatDuration(Number(todayStats.active_time_seconds)) : '0m'}
            </p>
            <p style={{ fontSize: '13px', color: 'rgba(255, 255, 255, 0.7)' }}>
              Active work time today
            </p>
          </div>

          {/* Context Switches Card */}
          <div style={{
            background: 'rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(10px)',
            borderRadius: '16px',
            padding: '24px',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
            transition: 'transform 0.2s'
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.transform = 'translateY(-4px)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
              <div style={{
                width: '48px',
                height: '48px',
                borderRadius: '12px',
                background: 'linear-gradient(135deg, #a855f7 0%, #9333ea 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '24px'
              }}>
                ⚡
              </div>
              <h3 style={{ fontSize: '16px', fontWeight: '600', color: 'rgba(255, 255, 255, 0.9)' }}>
                Context Switches
              </h3>
            </div>
            <p style={{ fontSize: '48px', fontWeight: '700', color: '#ffffff', marginBottom: '8px' }}>
              {todayStats ? todayStats.context_switches : 0}
            </p>
            <p style={{ fontSize: '13px', color: 'rgba(255, 255, 255, 0.7)' }}>
              App switches today
            </p>
          </div>

          {/* Break Time Card */}
          <div style={{
            background: 'rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(10px)',
            borderRadius: '16px',
            padding: '24px',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
            transition: 'transform 0.2s'
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.transform = 'translateY(-4px)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
              <div style={{
                width: '48px',
                height: '48px',
                borderRadius: '12px',
                background: 'linear-gradient(135deg, #64748b 0%, #475569 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '24px'
              }}>
                ☕
              </div>
              <h3 style={{ fontSize: '16px', fontWeight: '600', color: 'rgba(255, 255, 255, 0.9)' }}>
                Break Time
              </h3>
            </div>
            <p style={{ fontSize: '48px', fontWeight: '700', color: '#ffffff', marginBottom: '8px' }}>
              {todayStats ? formatDuration(Number(todayStats.idle_time_seconds)) : '0m'}
            </p>
            <p style={{ fontSize: '13px', color: 'rgba(255, 255, 255, 0.7)' }}>
              Idle time today
            </p>
          </div>
        </div>

        {/* Insights Section */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(10px)',
          borderRadius: '16px',
          padding: '32px',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)'
        }}>
          <h2 style={{ fontSize: '24px', fontWeight: '700', color: '#ffffff', marginBottom: '24px' }}>
            Today's Insights
          </h2>
          
          {isTracking ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{
                padding: '16px 20px',
                background: 'rgba(59, 130, 246, 0.2)',
                borderRadius: '12px',
                border: '1px solid rgba(59, 130, 246, 0.3)'
              }}>
                <p style={{ color: '#ffffff', fontSize: '14px', lineHeight: '1.6' }}>
                  🎯 Keep tracking to discover your productivity patterns
                </p>
              </div>
              <div style={{
                padding: '16px 20px',
                background: 'rgba(168, 85, 247, 0.2)',
                borderRadius: '12px',
                border: '1px solid rgba(168, 85, 247, 0.3)'
              }}>
                <p style={{ color: '#ffffff', fontSize: '14px', lineHeight: '1.6' }}>
                  💡 Insights will appear after collecting enough data
                </p>
              </div>
              <div style={{
                padding: '16px 20px',
                background: 'rgba(16, 185, 129, 0.2)',
                borderRadius: '12px',
                border: '1px solid rgba(16, 185, 129, 0.3)'
              }}>
                <p style={{ color: '#ffffff', fontSize: '14px', lineHeight: '1.6' }}>
                  📊 Stats update every 5 seconds while tracking
                </p>
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '48px 0' }}>
              <div style={{ fontSize: '64px', marginBottom: '16px', opacity: 0.5 }}>
                📊
              </div>
              <p style={{ color: 'rgba(255, 255, 255, 0.9)', fontSize: '18px', marginBottom: '8px' }}>
                Start tracking to see your productivity insights
              </p>
              <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '14px' }}>
                We'll analyze your work patterns and provide actionable insights
              </p>
            </div>
          )}
        </div>

        {/* Privacy Notice */}
        <div style={{
          marginTop: '32px',
          padding: '20px 24px',
          background: 'rgba(16, 185, 129, 0.2)',
          borderRadius: '12px',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          backdropFilter: 'blur(10px)'
        }}>
          <h3 style={{ fontWeight: '600', color: '#ffffff', marginBottom: '8px', fontSize: '15px' }}>
            🔒 Your Privacy Matters
          </h3>
          <p style={{ color: 'rgba(255, 255, 255, 0.9)', fontSize: '13px', lineHeight: '1.6' }}>
            All data is stored locally on your device. We never send your activity data anywhere. 
            You have full control to pause, export, or delete your data at any time.
          </p>
        </div>

        {/* Settings Section */}
        <div style={{ marginTop: '24px' }}>
          <button
            onClick={() => setShowSettings(!showSettings)}
            style={{
              width: '100%',
              padding: '16px 24px',
              background: 'rgba(255, 255, 255, 0.1)',
              backdropFilter: 'blur(10px)',
              borderRadius: '12px',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              color: '#ffffff',
              fontSize: '15px',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              transition: 'all 0.2s'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.15)';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
            }}
          >
            <span>⚙️ Settings</span>
            <span style={{ fontSize: '12px' }}>{showSettings ? '▼' : '▶'}</span>
          </button>

          {showSettings && (
            <div style={{
              marginTop: '16px',
              padding: '24px',
              background: 'rgba(255, 255, 255, 0.1)',
              backdropFilter: 'blur(10px)',
              borderRadius: '12px',
              border: '1px solid rgba(255, 255, 255, 0.2)',
            }}>
              <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#ffffff', marginBottom: '20px' }}>
                Application Settings
              </h3>

              {/* Autostart Setting */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '16px',
                background: 'rgba(255, 255, 255, 0.05)',
                borderRadius: '8px',
                marginBottom: '12px'
              }}>
                <div>
                  <div style={{ fontSize: '15px', fontWeight: '600', color: '#ffffff', marginBottom: '4px' }}>
                    🚀 Start with Windows
                  </div>
                  <div style={{ fontSize: '13px', color: 'rgba(255, 255, 255, 0.7)' }}>
                    Automatically start tracking when your computer starts
                  </div>
                </div>
                <button
                  onClick={toggleAutostart}
                  style={{
                    padding: '8px 16px',
                    borderRadius: '8px',
                    border: 'none',
                    cursor: 'pointer',
                    fontWeight: '600',
                    fontSize: '13px',
                    background: autostartEnabled ? '#10b981' : '#6b7280',
                    color: '#ffffff',
                    transition: 'all 0.2s'
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.opacity = '0.8';
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.opacity = '1';
                  }}
                >
                  {autostartEnabled ? 'Enabled' : 'Disabled'}
                </button>
              </div>

              {/* Background Running Info */}
              <div style={{
                padding: '16px',
                background: 'rgba(59, 130, 246, 0.2)',
                borderRadius: '8px',
                border: '1px solid rgba(59, 130, 246, 0.3)'
              }}>
                <div style={{ fontSize: '14px', color: '#ffffff', lineHeight: '1.6' }}>
                  💡 <strong>Background Mode:</strong> When you close the window, the app continues running in the system tray. 
                  Click the tray icon to reopen the dashboard. Right-click for options.
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      <style>{`
        @keyframes pulse {
          0%, 100% {
            opacity: 1;
          }
          50% {
            opacity: 0.5;
          }
        }
      `}</style>
    </div>
  );
};
