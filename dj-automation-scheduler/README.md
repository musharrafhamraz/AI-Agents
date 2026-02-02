# DJ Automation Scheduler

A complete system for managing DJ mixes and tracks with automated scheduling and live streaming playback.

## Features

- 🎵 **Audio Library Management**: Upload and manage DJ mixes and tracks
- 📅 **Smart Scheduling**: Schedule content with overlap detection
- 🔴 **Live Playback**: Public-facing player with automatic seek positioning
- ☁️ **Dropbox Integration**: Direct file uploads to Dropbox with shared links
- 🎨 **Modern UI**: Beautiful gradient design with Tailwind CSS
- ⚡ **Real-time Updates**: Polling system for live playback sync

## Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **SQLAlchemy**: Database ORM
- **SQLite**: Lightweight database (upgradeable to PostgreSQL)
- **Dropbox API**: Cloud storage integration

### Frontend
- **React 18**: Modern UI library
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool
- **Tailwind CSS**: Utility-first styling
- **React Router**: Client-side routing
- **Axios**: HTTP client

## Project Structure

```
dj-automation-scheduler/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Database models
│   ├── schemas.py           # Pydantic schemas
│   ├── database.py          # Database configuration
│   ├── dropbox_service.py   # Dropbox integration
│   ├── routes/
│   │   ├── public.py        # Public API endpoints
│   │   └── admin.py         # Admin API endpoints
│   ├── test_api.py          # API tests
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Environment variables
└── frontend/
    ├── src/
    │   ├── api/
    │   │   └── client.ts    # API client
    │   ├── pages/
    │   │   ├── NowPlaying.tsx  # Public player
    │   │   └── Admin.tsx       # Admin dashboard
    │   ├── App.tsx          # Main app component
    │   └── main.tsx         # Entry point
    ├── package.json
    └── .env                 # Frontend config
```

## Setup Instructions

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd dj-automation-scheduler/backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment variables are already configured** in `.env` with your Dropbox credentials

5. **Run the backend**:
   ```bash
   python main.py
   ```

   Backend will be available at: http://localhost:8000
   API Documentation: http://localhost:8000/docs

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd dj-automation-scheduler/frontend
   ```

2. **Dependencies are already installed**

3. **Run the frontend**:
   ```bash
   npm run dev
   ```

   Frontend will be available at: http://localhost:5173

## Usage Guide

### 1. Upload Audio Files

1. Go to Admin page: http://localhost:5173/admin
2. Click "Upload Files" tab
3. Select an audio file (MP3, WAV, etc.)
4. Click "Upload to Dropbox"
5. File will be uploaded and URL will be auto-filled

### 2. Create Audio Assets

1. In Admin page, go to "Audio Library" tab
2. Fill in the form:
   - **Title**: Name of the mix/track
   - **Type**: Mix or Track
   - **Audio URL**: Dropbox shared link (auto-filled after upload)
   - **Duration**: Length in seconds
3. Click "Create Asset"

### 3. Schedule Content

1. In Admin page, go to "Schedule" tab
2. Select an asset from dropdown
3. Set start and end times
4. Click "Create Schedule Event"
5. System will prevent overlapping schedules

### 4. View Live Stream

1. Go to Now Playing page: http://localhost:5173
2. If content is scheduled and active:
   - Audio player will auto-start at correct position
   - Shows current track info
   - Displays "Up Next" information
3. Page auto-refreshes every 10 seconds

## API Endpoints

### Public Endpoints

- `GET /api/now-playing` - Get currently playing content
- `GET /api/schedule` - Get all scheduled events

### Admin Endpoints

**Assets**:
- `POST /api/admin/assets` - Create asset
- `GET /api/admin/assets` - List all assets
- `GET /api/admin/assets/{id}` - Get specific asset
- `DELETE /api/admin/assets/{id}` - Delete asset

**Schedule**:
- `POST /api/admin/schedule` - Create schedule event
- `GET /api/admin/schedule` - List all events
- `DELETE /api/admin/schedule/{id}` - Delete event

**Upload**:
- `POST /api/admin/upload` - Upload file to Dropbox
- `GET /api/admin/dropbox/files` - List Dropbox files

## Testing

### Run Backend Tests

```bash
cd backend
pytest test_api.py -v
```

Tests cover:
- Now playing logic with time calculations
- Schedule overlap detection
- Asset CRUD operations
- Future event handling

### Manual Testing Scenarios

1. **Test Current Playback**:
   - Create an asset
   - Schedule it to start NOW
   - Open Now Playing page
   - Verify audio starts at correct position

2. **Test Future Schedule**:
   - Schedule an asset for 5 minutes from now
   - Check "Up Next" appears
   - Wait for start time
   - Verify automatic playback

3. **Test Overlap Prevention**:
   - Try to schedule overlapping events
   - Verify error message appears

## Configuration

### Dropbox Setup

Your Dropbox credentials are already configured in `backend/.env`:
- App Key: `idxbi8p074xr2rb`
- App Secret: `d0rmxlrlar2eptd`
- Access Token: Configured

Files will be uploaded to `/dj-assets` folder in your Dropbox.

### Database

Default: SQLite (`dj_scheduler.db`)

To upgrade to PostgreSQL:
1. Update `DATABASE_URL` in `.env`
2. Install: `pip install psycopg2-binary`
3. Restart backend

## Features in Detail

### Automatic Seek Positioning

The system calculates exact playback position:
- Tracks when event started
- Calculates elapsed time
- Sets audio player to correct position
- Ensures synchronized playback across all viewers

### Overlap Detection

Prevents scheduling conflicts:
- Checks for time overlaps before creating events
- Returns clear error messages
- Maintains schedule integrity

### Real-time Updates

Public player polls every 10 seconds:
- Updates current track info
- Adjusts seek position
- Shows upcoming content
- Handles transitions smoothly

## Troubleshooting

### Backend Issues

**Database errors**:
```bash
# Delete database and restart
rm dj_scheduler.db
python main.py
```

**Dropbox errors**:
- Verify access token is valid
- Check Dropbox app permissions
- Ensure `/dj-assets` folder exists

### Frontend Issues

**API connection errors**:
- Verify backend is running on port 8000
- Check CORS settings in `backend/main.py`
- Confirm `.env` has correct API URL

**Audio not playing**:
- Check audio URL is accessible
- Verify browser allows autoplay
- Check browser console for errors

## Future Enhancements

- [ ] S3 storage support
- [ ] User authentication
- [ ] Analytics dashboard
- [ ] Mobile app
- [ ] Playlist management
- [ ] Social media integration
- [ ] Live chat during streams

## License

MIT License - Feel free to use and modify!

## Support

For issues or questions, check:
- API Documentation: http://localhost:8000/docs
- Browser console for frontend errors
- Backend logs for API errors
