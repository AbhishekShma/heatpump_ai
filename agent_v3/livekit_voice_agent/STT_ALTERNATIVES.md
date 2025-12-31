# Alternative STT Providers for LiveKit Agents

## Current Setup
- **Current**: OpenAI Whisper STT (slow, ~2-5s latency)
- **Issue**: Designed for batch processing, not real-time streaming

## Available Options

### 1. **OpenAI Realtime API** ⚡ FASTEST
- **Latency**: <500ms
- **Status**: ✅ Available in LiveKit (`openai.realtime.RealtimeModel`)
- **Pros**: 
  - Fastest option
  - Built-in streaming STT
  - Already have backup code
- **Cons**: 
  - Bundles STT/LLM/TTS (not separate components)
  - Can't mix providers

### 2. **Deepgram** 🚀 FAST (RECOMMENDED)
- **Latency**: <300ms
- **Status**: ✅ Available! (`livekit-plugins-deepgram`)
- **Package**: `pip install livekit-plugins-deepgram`
- **Pros**: 
  - Very fast real-time STT (<300ms latency)
  - Good accuracy
  - Separate STT component (can use with OpenAI LLM/TTS)
  - Optimized for streaming
- **Cons**: 
  - Need Deepgram API key
  - Additional dependency

### 3. **Azure Speech-to-Text** 🏢 ENTERPRISE
- **Latency**: ~300-500ms
- **Status**: ✅ Available! (`livekit-plugins-azure`)
- **Package**: `pip install livekit-plugins-azure`
- **Pros**: 
  - Enterprise-grade
  - Good language support
  - Separate STT component
- **Cons**: 
  - Requires Azure account
  - Slightly slower than Deepgram

### 4. **Google Cloud Speech-to-Text** 🌐
- **Latency**: ~300-500ms
- **Status**: ✅ Available! (`livekit-plugins-google`)
- **Package**: `pip install livekit-plugins-google`
- **Pros**: 
  - Good accuracy
  - Separate STT component
- **Cons**: 
  - Requires GCP account
  - Slightly slower than Deepgram

## Recommendation

**For fastest performance with separate components:**
1. ✅ **Try Deepgram** - Fastest alternative (<300ms latency)
   - Install: `pip install livekit-plugins-deepgram`
   - Use: `from livekit.plugins import deepgram; stt = deepgram.STT()`
   - Keep OpenAI LLM and TTS separate

2. **Alternative**: Azure or Google (if you have accounts)

3. **Fallback**: Switch back to OpenAI Realtime API (fastest overall, but bundled)

## Quick Start with Deepgram

```python
from livekit.plugins import deepgram, openai

# Fast STT
stt = deepgram.STT()  # <300ms latency, streaming optimized

# Keep OpenAI for LLM and TTS
llm = openai.LLM()
tts = openai.TTS(voice="shimmer")
```

**Setup:**
1. Get Deepgram API key from https://deepgram.com
2. Set `DEEPGRAM_API_KEY` environment variable
3. Install: `pip install livekit-plugins-deepgram`
4. Update code to use `deepgram.STT()` instead of `openai.STT()`

