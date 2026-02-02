import { useState, useEffect } from 'react';
import { adminApi } from '../api/client';
import type { AudioAsset, ScheduleEvent, DropboxFile } from '../api/client';

export default function Admin() {
  const [assets, setAssets] = useState<AudioAsset[]>([]);
  const [scheduleEvents, setScheduleEvents] = useState<ScheduleEvent[]>([]);
  const [dropboxFiles, setDropboxFiles] = useState<DropboxFile[]>([]);
  const [activeTab, setActiveTab] = useState<'browse' | 'library' | 'schedule'>('browse');
  const [loading, setLoading] = useState(false);

  // Import form state
  const [selectedFile, setSelectedFile] = useState<DropboxFile | null>(null);
  const [importForm, setImportForm] = useState({
    title: '',
    type: 'mix' as 'mix' | 'track',
    duration_seconds: 0,
  });

  // Schedule form state
  const [scheduleForm, setScheduleForm] = useState({
    audio_asset_id: '',
    start_at: '',
    end_at: '',
  });

  useEffect(() => {
    loadAssets();
    loadSchedule();
    loadDropboxFiles();
  }, []);

  const loadDropboxFiles = async () => {
    try {
      setLoading(true);
      const response = await adminApi.listDropboxFiles();
      setDropboxFiles(response.data.files);
    } catch (error) {
      console.error('Error loading Dropbox files:', error);
      alert('Failed to load Dropbox files. Make sure your Dropbox token is valid.');
    } finally {
      setLoading(false);
    }
  };

  const loadAssets = async () => {
    try {
      const response = await adminApi.listAssets();
      setAssets(response.data);
    } catch (error) {
      console.error('Error loading assets:', error);
    }
  };

  const loadSchedule = async () => {
    try {
      const response = await adminApi.listScheduleEvents();
      setScheduleEvents(response.data);
    } catch (error) {
      console.error('Error loading schedule:', error);
    }
  };

  const handleSelectFile = (file: DropboxFile) => {
    setSelectedFile(file);
    setImportForm({
      title: file.name.replace(/\.[^/.]+$/, ''), // Remove extension
      type: 'mix',
      duration_seconds: 0,
    });
  };

  const handleImportFile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    setLoading(true);
    try {
      console.log('Importing file:', {
        file_path: selectedFile.path,
        title: importForm.title,
        type: importForm.type,
        duration_seconds: importForm.duration_seconds,
      });

      await adminApi.importFromDropbox({
        file_path: selectedFile.path,
        title: importForm.title,
        type: importForm.type,
        duration_seconds: importForm.duration_seconds,
      });
      
      await loadAssets();
      await loadDropboxFiles(); // Refresh to show updated import status
      setSelectedFile(null);
      setImportForm({ title: '', type: 'mix', duration_seconds: 0 });
      setActiveTab('library');
      alert('File imported successfully!');
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Import failed!';
      alert(`Import failed: ${errorMessage}`);
      console.error('Import error:', error);
      console.error('Error response:', error.response);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAsset = async (id: string) => {
    if (!confirm('Are you sure you want to delete this asset?')) return;
    
    try {
      await adminApi.deleteAsset(id);
      await loadAssets();
      await loadSchedule();
    } catch (error) {
      console.error('Error deleting asset:', error);
    }
  };

  const handleCreateSchedule = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await adminApi.createScheduleEvent(scheduleForm);
      await loadSchedule();
      setScheduleForm({ audio_asset_id: '', start_at: '', end_at: '' });
      alert('Schedule event created successfully!');
    } catch (error: any) {
      console.error('Error creating schedule:', error);
      alert(error.response?.data?.detail || 'Failed to create schedule event');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSchedule = async (id: string) => {
    if (!confirm('Are you sure you want to delete this schedule event?')) return;
    
    try {
      await adminApi.deleteScheduleEvent(id);
      await loadSchedule();
    } catch (error) {
      console.error('Error deleting schedule:', error);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white py-6 shadow-lg">
        <div className="container mx-auto px-4">
          <h1 className="text-3xl font-bold">DJ Scheduler Admin</h1>
          <p className="text-purple-100">Browse Dropbox → Import → Schedule → Stream</p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Tabs */}
        <div className="flex gap-4 mb-6">
          <button
            onClick={() => setActiveTab('browse')}
            className={`px-6 py-3 rounded-lg font-semibold transition ${
              activeTab === 'browse'
                ? 'bg-purple-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            📁 Browse Dropbox ({dropboxFiles.length})
          </button>
          <button
            onClick={() => setActiveTab('library')}
            className={`px-6 py-3 rounded-lg font-semibold transition ${
              activeTab === 'library'
                ? 'bg-purple-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            🎵 Imported Library ({assets.length})
          </button>
          <button
            onClick={() => setActiveTab('schedule')}
            className={`px-6 py-3 rounded-lg font-semibold transition ${
              activeTab === 'schedule'
                ? 'bg-purple-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            📅 Schedule ({scheduleEvents.length})
          </button>
        </div>

        {/* Browse Dropbox Tab */}
        {activeTab === 'browse' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Dropbox Files List */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold">Dropbox Files</h2>
                <button
                  onClick={loadDropboxFiles}
                  disabled={loading}
                  className="text-sm bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-gray-400"
                >
                  {loading ? 'Loading...' : '🔄 Refresh'}
                </button>
              </div>
              
              {dropboxFiles.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <p className="mb-2">No audio files found in Dropbox</p>
                  <p className="text-sm">Upload audio files to /dj-assets folder</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-[600px] overflow-y-auto">
                  {dropboxFiles.map((file) => {
                    const isImported = assets.some(a => a.dropbox_path === file.path);
                    return (
                      <div
                        key={file.path}
                        className={`border rounded p-4 cursor-pointer transition ${
                          selectedFile?.path === file.path
                            ? 'border-purple-500 bg-purple-50'
                            : isImported
                            ? 'border-green-300 bg-green-50'
                            : 'hover:bg-gray-50'
                        }`}
                        onClick={() => !isImported && handleSelectFile(file)}
                      >
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <h3 className="font-semibold text-sm">{file.name}</h3>
                            <div className="text-xs text-gray-600 mt-1">
                              <div>Size: {formatFileSize(file.size)}</div>
                              <div>Modified: {new Date(file.modified).toLocaleDateString()}</div>
                            </div>
                          </div>
                          {isImported && (
                            <span className="text-xs bg-green-500 text-white px-2 py-1 rounded">
                              ✓ Imported
                            </span>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Import Form */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-2xl font-bold mb-4">Import to Library</h2>
              
              {selectedFile ? (
                <form onSubmit={handleImportFile} className="space-y-4">
                  <div className="bg-purple-50 border border-purple-200 rounded p-3 mb-4">
                    <div className="text-sm font-semibold text-purple-900">Selected File:</div>
                    <div className="text-sm text-purple-700">{selectedFile.name}</div>
                    <div className="text-xs text-purple-600">{formatFileSize(selectedFile.size)}</div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Title</label>
                    <input
                      type="text"
                      value={importForm.title}
                      onChange={(e) => setImportForm({ ...importForm, title: e.target.value })}
                      className="w-full border rounded p-2"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Type</label>
                    <select
                      value={importForm.type}
                      onChange={(e) => setImportForm({ ...importForm, type: e.target.value as 'mix' | 'track' })}
                      className="w-full border rounded p-2"
                    >
                      <option value="mix">Mix</option>
                      <option value="track">Track</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Duration (seconds)</label>
                    <input
                      type="number"
                      value={importForm.duration_seconds}
                      onChange={(e) => setImportForm({ ...importForm, duration_seconds: parseInt(e.target.value) })}
                      className="w-full border rounded p-2"
                      required
                      min="1"
                    />
                    <div className="text-xs text-gray-500 mt-1">
                      Example: 3600 = 1 hour, 1800 = 30 minutes
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <button
                      type="submit"
                      disabled={loading}
                      className="flex-1 bg-purple-600 text-white py-2 rounded hover:bg-purple-700 disabled:bg-gray-400"
                    >
                      {loading ? 'Importing...' : 'Import to Library'}
                    </button>
                    <button
                      type="button"
                      onClick={() => setSelectedFile(null)}
                      className="px-4 bg-gray-300 text-gray-700 py-2 rounded hover:bg-gray-400"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <div className="text-4xl mb-4">👈</div>
                  <p>Select a file from Dropbox to import</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Library Tab */}
        {activeTab === 'library' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold mb-4">Imported Audio Library</h2>
            
            {assets.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                <p className="mb-2">No assets imported yet</p>
                <p className="text-sm">Go to "Browse Dropbox" tab to import files</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-[600px] overflow-y-auto">
                {assets.map((asset) => (
                  <div key={asset.id} className="border rounded p-4 hover:bg-gray-50">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-semibold">{asset.title}</h3>
                        <div className="text-sm text-gray-600 mt-1">
                          <span className="inline-block px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs mr-2">
                            {asset.type}
                          </span>
                          Duration: {Math.floor(asset.duration_seconds / 60)}:{(asset.duration_seconds % 60).toString().padStart(2, '0')}
                        </div>
                        {asset.dropbox_path && (
                          <div className="text-xs text-gray-500 mt-1">
                            📁 {asset.dropbox_path}
                          </div>
                        )}
                      </div>
                      <button
                        onClick={() => handleDeleteAsset(asset.id)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Schedule Tab */}
        {activeTab === 'schedule' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Create Schedule Form */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-2xl font-bold mb-4">Schedule New Event</h2>
              <form onSubmit={handleCreateSchedule} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Select Asset</label>
                  <select
                    value={scheduleForm.audio_asset_id}
                    onChange={(e) => setScheduleForm({ ...scheduleForm, audio_asset_id: e.target.value })}
                    className="w-full border rounded p-2"
                    required
                  >
                    <option value="">Choose an asset...</option>
                    {assets.map((asset) => (
                      <option key={asset.id} value={asset.id}>
                        {asset.title} ({asset.type})
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Start Time</label>
                  <input
                    type="datetime-local"
                    value={scheduleForm.start_at}
                    onChange={(e) => setScheduleForm({ ...scheduleForm, start_at: e.target.value })}
                    className="w-full border rounded p-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">End Time</label>
                  <input
                    type="datetime-local"
                    value={scheduleForm.end_at}
                    onChange={(e) => setScheduleForm({ ...scheduleForm, end_at: e.target.value })}
                    className="w-full border rounded p-2"
                    required
                  />
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-purple-600 text-white py-2 rounded hover:bg-purple-700 disabled:bg-gray-400"
                >
                  Create Schedule Event
                </button>
              </form>
            </div>

            {/* Schedule List */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-2xl font-bold mb-4">Scheduled Events</h2>
              <div className="space-y-3 max-h-[600px] overflow-y-auto">
                {scheduleEvents.map((event) => (
                  <div key={event.id} className="border rounded p-4 hover:bg-gray-50">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-semibold">{event.audio_asset?.title}</h3>
                        <div className="text-sm text-gray-600 mt-1">
                          <div>Start: {new Date(event.start_at).toLocaleString()}</div>
                          <div>End: {new Date(event.end_at).toLocaleString()}</div>
                        </div>
                      </div>
                      <button
                        onClick={() => handleDeleteSchedule(event.id)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
