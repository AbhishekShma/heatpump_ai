'use client';
import { useEffect, useRef } from 'react';
import {
  ControlBar,
  RoomAudioRenderer,
  useSession,
  SessionProvider,
  useAgent,
  BarVisualizer,
} from '@livekit/components-react';
import { TokenSource, TokenSourceConfigurable, TokenSourceFetchOptions } from 'livekit-client';
import '@livekit/components-styles';

// Token server URL - update this to match your backend
const TOKEN_SERVER_URL = 'http://localhost:8000/token';

/**
 * Custom token source that fetches tokens from our FastAPI backend
 */
class CustomTokenSource implements TokenSourceConfigurable {
  async fetchToken(options?: TokenSourceFetchOptions): Promise<string> {
    const response = await fetch(TOKEN_SERVER_URL);
    if (!response.ok) {
      throw new Error(`Failed to fetch token: ${response.statusText}`);
    }
    const data = await response.json();
    return data.token;
  }
}

export default function App() {
  const tokenSource: TokenSourceConfigurable = useRef(
    new CustomTokenSource(),
  ).current;
  const tokenOptions: TokenSourceFetchOptions = { agentName: 'assistant' };

  const session = useSession(tokenSource, tokenOptions);

  // Connect to session
  useEffect(() => {
    session.start();
    return () => {
      session.end();
    };
  }, []);

  return (
    <SessionProvider session={session}>
      <div data-lk-theme="default" style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
        {/* Your custom component with basic voice agent functionality. */}
        <MyAgentView />
        {/* Controls for the user to start/stop audio and disconnect from the session */}
        <ControlBar controls={{ microphone: true, camera: false, screenShare: false }} />
        {/* The RoomAudioRenderer takes care of room-wide audio for you. */}
        <RoomAudioRenderer />
      </div>
    </SessionProvider>
  );
}

function MyAgentView() {
  const agent = useAgent();
  return (
    <div style={{ 
      height: '350px', 
      display: 'flex', 
      flexDirection: 'column', 
      justifyContent: 'center', 
      alignItems: 'center',
      padding: '2rem'
    }}>
      <h1>LiveKit Voice Agent</h1>
      <p>Agent state: <strong>{agent.state}</strong></p>
      {/* Renders a visualizer for the agent's audio track */}
      {agent.canListen && (
        <div style={{ width: '100%', maxWidth: '400px', marginTop: '2rem' }}>
          <BarVisualizer track={agent.microphoneTrack} state={agent.state} barCount={5} />
        </div>
      )}
      {!agent.canListen && (
        <p style={{ marginTop: '2rem', color: '#888' }}>
          Waiting for agent to connect...
        </p>
      )}
    </div>
  );
}

