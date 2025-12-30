# LiveKit Voice Agent Frontend

Basic TypeScript frontend for connecting to the LiveKit voice agent.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Server Deployment

The Vite dev server is configured to listen on all network interfaces (`0.0.0.0`), making it accessible from other machines on your network.

### Development Server (Recommended for testing)
```bash
npm run dev
```

The server will be accessible at:
- `http://localhost:5173` (local)
- `http://<your-server-ip>:5173` (from other machines)

### Production Build

For production deployment:

1. Build the frontend:
```bash
npm run build
```

2. Preview the production build:
```bash
npm run preview
```

Or serve the `dist/` folder with any static file server (nginx, Apache, etc.)

## Usage

1. Make sure the token server is running on `http://localhost:8000`
2. Make sure the LiveKit agent is running
3. Open the frontend in your browser
4. Click "Connect" to start a voice conversation
5. Speak into your microphone - the agent will respond
6. Click "Disconnect" when done

## Features

- Simple connect/disconnect interface
- Real-time status display
- Automatic microphone access
- Clean, modern UI




