/**
 * Chaplin-UI Frontend Application
 * 
 * This handles all the browser-side logic:
 * - Camera access and video recording
 * - File uploads
 * - API communication with the backend
 * - UI updates and status messages
 * 
 * Want to customize the UI? Check out:
 * - style.css for colors, layout, fonts
 * - index.html for HTML structure
 * - This file (app.js) for behavior
 */

document.addEventListener('DOMContentLoaded', () => {
  // ========================================================================
  // DOM Element References
  // ========================================================================
  // Get references to all the UI elements we'll be interacting with
  const video = document.getElementById('video');
  const placeholder = document.getElementById('video-placeholder');
  const recordingDot = document.getElementById('recording-dot');
  const uploadBtn = document.getElementById('upload-btn');
  const recordBtn = document.getElementById('record-btn');
  const fileInput = document.getElementById('file-input');
  const rawOutput = document.getElementById('raw-output');
  const correctedOutput = document.getElementById('corrected-output');
  const copyBtn = document.getElementById('copy-btn');
  const statusEl = document.getElementById('status');
  const providerSelect = document.getElementById('provider-select');
  const modelInput = document.getElementById('model-input');
  const providerHint = document.getElementById('provider-hint');
  const settingsBtn = document.getElementById('settings-btn');
  const settingsPanel = document.getElementById('settings-panel');
  const settingsClose = document.getElementById('settings-close');
  const settingsBackdrop = document.getElementById('settings-backdrop');

  // ========================================================================
  // Application State
  // ========================================================================
  let stream = null;  // Camera stream (MediaStream object)
  let mediaRecorder = null;  // MediaRecorder for capturing video
  let recordedChunks = [];  // Array of video chunks from recording
  let isRecording = false;  // Whether we're currently recording
  let modelReady = false;  // Whether backend model is loaded (loads in background)

  // ========================================================================
  // Utility Functions
  // ========================================================================
  
  /**
   * Update the status message at the bottom of the UI
   * @param {string} text - Status message text
   * @param {string} type - Status type: 'ready', 'processing', 'error', 'warning'
   */
  function setStatus(text, type = '') {
    if (statusEl) {
      statusEl.textContent = text;
      statusEl.className = 'status ' + type;
    }
  }

  function setModelReady(ready) {
    modelReady = ready;
    uploadBtn.disabled = !ready;
    recordBtn.disabled = !ready;
    if (ready) {
      setStatus('Ready', 'ready');
    } else {
      setStatus('Loading model... (30–60 sec first time)', 'processing');
    }
  }

  /**
   * Request camera access and start video stream
   * This uses the browser's MediaDevices API to access the user's camera
   */
  async function startCamera() {
    try {
      // Request camera access
      // facingMode: 'user' means front-facing camera (selfie cam)
      // audio: false because we only need video for lip reading
      stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, facingMode: 'user' },
        audio: false,
      });
      
      // Display the camera feed in the video element
      video.srcObject = stream;
      placeholder.classList.add('hidden');  // Hide "Initializing camera..." message
    } catch (err) {
      // Handle camera permission denied or other errors
      placeholder.textContent = 'Camera Error\n\n' + (err.message || 'Could not access camera');
      setStatus('Camera error: ' + err.message, 'error');
      console.error('Camera error:', err);
    }
  }

  function stopCamera() {
    if (stream) {
      stream.getTracks().forEach(t => t.stop());
      stream = null;
    }
  }

  // ========================================================================
  // LLM Provider Settings
  // ========================================================================
  const PROVIDER_HINTS = {
    lmstudio: 'LM Studio: load model, enable Local Server (port 1234)',
    ollama: 'Ollama: run `ollama serve`, then `ollama pull <model>`',
  };

  function updateProviderHint() {
    const provider = providerSelect?.value || 'lmstudio';
    if (providerHint) providerHint.textContent = PROVIDER_HINTS[provider] || '';
  }

  providerSelect?.addEventListener('change', updateProviderHint);

  // Settings panel open/close
  function openSettings() {
    settingsPanel?.removeAttribute('hidden');
  }

  function closeSettings() {
    settingsPanel?.setAttribute('hidden', '');
  }

  settingsBtn?.addEventListener('click', openSettings);
  settingsClose?.addEventListener('click', closeSettings);
  settingsBackdrop?.addEventListener('click', closeSettings);

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && settingsPanel && !settingsPanel.hasAttribute('hidden')) {
      closeSettings();
    }
  });

  // ========================================================================
  // Model Readiness Polling
  // ========================================================================
  // Server starts immediately; model loads in background (~30–60 sec).
  // Poll /api/health until ready so users see the UI right away.
  async function pollUntilReady() {
    setModelReady(false);
    const maxAttempts = 120;  // 2 min at 1/sec
    for (let i = 0; i < maxAttempts; i++) {
      try {
        const res = await fetch('/api/health');
        const data = await res.json();
        if (data.model_loaded && data.llm_client_ready) {
          setModelReady(true);
          return;
        }
      } catch (_) {
        // Server might not be up yet
      }
      await new Promise(r => setTimeout(r, 1000));
    }
    setStatus('Model loading is taking longer than expected. Check server logs.', 'warning');
    setModelReady(false);
  }

  // ========================================================================
  // Event Handlers
  // ========================================================================
  
  // Upload button: trigger hidden file input
  uploadBtn.addEventListener('click', () => fileInput.click());

  // File input: handle video file selection
  fileInput.addEventListener('change', async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    fileInput.value = '';  // Reset so same file can be selected again
    await processVideoFile(file);
  });

  // Record button: toggle recording state
  recordBtn.addEventListener('click', toggleRecording);

  // ========================================================================
  // Recording Functions
  // ========================================================================
  
  /**
   * Toggle recording on/off
   * Called when user clicks the record button
   */
  async function toggleRecording() {
    if (isRecording) {
      stopRecording();
    } else {
      await startRecording();
    }
  }

  /**
   * Start recording from camera
   * Uses MediaRecorder API to capture video chunks
   */
  async function startRecording() {
    // Make sure camera is initialized first
    if (!stream) {
      setStatus('Start camera first', 'error');
      return;
    }
    
    // Reset chunks array for new recording
    recordedChunks = [];
    
    // Create MediaRecorder to capture video stream
    // WebM with VP9 codec is well-supported in modern browsers
    mediaRecorder = new MediaRecorder(stream, { mimeType: 'video/webm;codecs=vp9' });
    
    // Collect video chunks as they're recorded
    // We get chunks every 100ms (see mediaRecorder.start(100) below)
    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) {
        recordedChunks.push(e.data);
      }
    };
    
    // When recording stops, process the video
    mediaRecorder.onstop = () => {
      if (recordedChunks.length > 0) {
        // Combine all chunks into a single Blob (binary data)
        const blob = new Blob(recordedChunks, { type: 'video/webm' });
        // Convert Blob to File for upload
        const file = new File([blob], 'recording.webm', { type: 'video/webm' });
        // Send to backend for processing
        processVideoFile(file);
      }
    };
    
    // Start recording, collecting data every 100ms
    mediaRecorder.start(100);
    isRecording = true;
    
    // Update UI to show recording state
    recordBtn.textContent = 'Stop recording';
    recordBtn.classList.add('recording');  // Changes button to red
    recordingDot.hidden = false;  // Show green recording indicator
    setStatus('Recording...', 'processing');
  }

  /**
   * Stop recording and trigger processing
   */
  function stopRecording() {
    // Stop the MediaRecorder (this triggers the onstop handler)
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
    }
    
    // Update state and UI
    isRecording = false;
    recordBtn.textContent = 'Start recording';
    recordBtn.classList.remove('recording');  // Changes button back to blue
    recordingDot.hidden = true;  // Hide recording indicator
    setStatus('Processing...', 'processing');
  }

  /**
   * Process a video file through the VSR pipeline
   * This sends the video to the backend, which runs inference and returns transcription
   * 
   * @param {File} file - Video file to process (from upload or recording)
   */
  async function processVideoFile(file) {
    setStatus('Processing...', 'processing');
    rawOutput.value = '';
    correctedOutput.value = '';

    // Create form data for file upload
    // FastAPI expects multipart/form-data with 'video' and optional provider/model
    const formData = new FormData();
    formData.append('video', file);
    const provider = providerSelect?.value || 'lmstudio';
    const model = modelInput?.value?.trim() || null;
    if (provider) formData.append('provider', provider);
    if (model) formData.append('model', model);

    try {
      // Send video to backend for processing
      // The backend will:
      // 1. Save the video temporarily
      // 2. Run VSR inference (lip reading)
      // 3. Use LLM to correct the text
      // 4. Return both raw and corrected versions
      const res = await fetch('/api/process-video', {
        method: 'POST',
        body: formData,
      });

      // Check if request was successful
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        const msg = typeof err.detail === 'string' ? err.detail : (err.detail?.msg || err.detail || res.statusText || 'Request failed');
        throw new Error(msg);
      }

      // Parse response and update UI
      const data = await res.json();
      rawOutput.value = data.raw || '';
      correctedOutput.value = data.corrected || '';
      setStatus('Ready', 'ready');
    } catch (err) {
      // Show error to user
      setStatus('Error: ' + err.message, 'error');
      console.error('Processing error:', err);
    }
  }

  /**
   * Copy corrected text to clipboard
   * Uses the modern Clipboard API (works in secure contexts)
   */
  copyBtn.addEventListener('click', async () => {
    const text = correctedOutput.value;
    if (!text) return;
    
    try {
      // Use Clipboard API to copy text
      await navigator.clipboard.writeText(text);
      setStatus('Copied to clipboard!', 'ready');
      // Reset status message after 2 seconds
      setTimeout(() => setStatus('Ready', 'ready'), 2000);
    } catch (err) {
      // Clipboard API might fail in some browsers or contexts
      setStatus('Copy failed', 'error');
      console.error('Clipboard error:', err);
    }
  });

  // ========================================================================
  // Initialize Application
  // ========================================================================
  
  // Set initial provider hint
  updateProviderHint();

  // Start camera when page loads
  startCamera();

  // Poll until model is ready (server loads it in background)
  pollUntilReady();

  // Clean up camera stream when page unloads
  // This prevents camera from staying on after user leaves
  window.addEventListener('beforeunload', stopCamera);
});
