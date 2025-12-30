import { Room, RoomEvent, createLocalAudioTrack, Track } from 'livekit-client';
const TOKEN_SERVER_URL = 'http://localhost:8000/token';
const DISPATCH_AGENT_URL = 'http://localhost:8000/dispatch-agent';
let room = null;
let localAudioTrack = null;
let isConnecting = false;
let isConnected = false;
let agentDispatched = false;
const statusEl = document.getElementById('status');
const connectBtn = document.getElementById('connectBtn');
const disconnectBtn = document.getElementById('disconnectBtn');
/**
 * Updates the UI status display.
 */
function updateStatus(status, message) {
    statusEl.className = `status ${status}`;
    statusEl.textContent = message || status.charAt(0).toUpperCase() + status.slice(1);
}
/**
 * Fetches a LiveKit access token from the token server.
 */
async function fetchToken() {
    const response = await fetch(TOKEN_SERVER_URL);
    if (!response.ok) {
        throw new Error(`Failed to fetch token: ${response.statusText}`);
    }
    return await response.json();
}
/**
 * Connects to LiveKit room and sets up audio.
 */
async function connect() {
    // Prevent multiple simultaneous connections
    if (isConnecting || isConnected || room !== null) {
        console.log('Already connecting or connected, ignoring click');
        return;
    }
    try {
        isConnecting = true;
        updateStatus('connecting', 'Connecting...');
        connectBtn.disabled = true;
        // Fetch token from server
        const { token, url } = await fetchToken();
        console.log('Token received, connecting to:', url);
        // Create room and connect
        room = new Room();
        // Set up event handlers
        room.on(RoomEvent.Connected, () => {
            console.log('Connected to room');
            isConnecting = false;
            isConnected = true;
            updateStatus('connected', 'Connected - Speak now');
            disconnectBtn.disabled = false;
        });
        room.on(RoomEvent.Disconnected, () => {
            console.log('Disconnected from room');
            isConnecting = false;
            isConnected = false;
            agentDispatched = false; // Reset dispatch flag on disconnect
            updateStatus('disconnected');
            connectBtn.disabled = false;
            disconnectBtn.disabled = true;
            room = null;
        });
        // Handle track subscriptions - attach audio tracks to play them
        room.on(RoomEvent.TrackSubscribed, (track, publication, participant) => {
            console.log('Track subscribed:', track.kind, 'from', participant.identity);
            if (track.kind === Track.Kind.Audio) {
                // Attach audio track to create audio element and play it
                const audioElement = track.attach();
                document.body.appendChild(audioElement);
                audioElement.setAttribute('playsinline', 'true');
                audioElement.play().catch(err => console.error('Error playing audio:', err));
            }
        });
        room.on(RoomEvent.ParticipantConnected, (participant) => {
            console.log('Participant connected:', participant.identity);
            // Check for existing audio tracks and attach them
            participant.audioTrackPublications.forEach((publication) => {
                if (publication.track) {
                    const audioElement = publication.track.attach();
                    document.body.appendChild(audioElement);
                    audioElement.setAttribute('playsinline', 'true');
                    audioElement.play().catch(err => console.error('Error playing audio:', err));
                }
            });
        });
        // Connect to room - room name is "test-room"
        await room.connect(url, token, {
            autoSubscribe: true,
        });
        // Ensure we're in the right room
        if (room.name !== "test-room") {
            console.warn(`Expected room "test-room", but connected to "${room.name}"`);
        }
        // Enable microphone
        localAudioTrack = await createLocalAudioTrack();
        await room.localParticipant.publishTrack(localAudioTrack);
        console.log('Microphone enabled');
        // Dispatch agent explicitly (required for named agents) - only once
        if (!agentDispatched) {
            agentDispatched = true;
            try {
                const dispatchResponse = await fetch(DISPATCH_AGENT_URL, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });
                if (dispatchResponse.ok) {
                    console.log('Agent dispatched');
                }
                else {
                    console.error('Failed to dispatch agent:', await dispatchResponse.text());
                    agentDispatched = false; // Reset on failure
                }
            }
            catch (error) {
                console.error('Error dispatching agent:', error);
                agentDispatched = false; // Reset on error
            }
        }
        else {
            console.log('Agent already dispatched, skipping');
        }
    }
    catch (error) {
        console.error('Connection error:', error);
        isConnecting = false;
        isConnected = false;
        agentDispatched = false; // Reset dispatch flag on error
        updateStatus('disconnected', `Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
        connectBtn.disabled = false;
        disconnectBtn.disabled = true;
        room = null;
    }
}
/**
 * Disconnects from LiveKit room and cleans up.
 */
async function disconnect() {
    try {
        isConnecting = false;
        isConnected = false;
        agentDispatched = false; // Reset dispatch flag on disconnect
        if (localAudioTrack) {
            localAudioTrack.stop();
            localAudioTrack = null;
        }
        if (room) {
            await room.disconnect();
            room = null;
        }
        updateStatus('disconnected');
        connectBtn.disabled = false;
        disconnectBtn.disabled = true;
    }
    catch (error) {
        console.error('Disconnect error:', error);
        // Reset flags even on error
        isConnecting = false;
        isConnected = false;
        agentDispatched = false;
        connectBtn.disabled = false;
    }
}
// Set up button event listeners
connectBtn.addEventListener('click', connect);
disconnectBtn.addEventListener('click', disconnect);
// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (room) {
        room.disconnect();
    }
});
