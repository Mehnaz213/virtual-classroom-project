// Focus Mate Extension - Background Service Worker
// Handles tab switch detection, lock mode enforcement, and API communication

const DEFAULT_API_BASE = 'http://localhost:8000/api';
const THROTTLE_MS = 1500;
const RETRY_DELAYS = [1000, 3000, 5000, 10000]; // Exponential backoff

const state = {
  apiBase: DEFAULT_API_BASE,
  token: '',
  sessionId: null,
  attendanceId: null,
  lockMode: false,
  tabSwitches: 0,
  lockViolations: 0,
  lastEventAt: 0,
  retryQueue: [],
  currentRetryIndex: 0,
};

// Load state from storage on startup
chrome.storage.local.get(['focusMateConfig'], (result) => {
  if (result.focusMateConfig) {
    Object.assign(state, result.focusMateConfig);
    updateBadge();
  }
});

// Save state to storage
const saveState = () => {
  chrome.storage.local.set({ focusMateConfig: state });
};

// Update badge with tab switch count
const updateBadge = () => {
  const count = state.tabSwitches + state.lockViolations;
  chrome.action.setBadgeText({
    text: count > 0 ? String(count) : '',
  });
  chrome.action.setBadgeBackgroundColor({
    color: state.lockMode ? '#dc2626' : '#f59e0b',
  });
};

// Post tab switch event to backend
const postTabSwitch = async (eventData) => {
  if (!state.token || !state.sessionId || !state.attendanceId) {
    console.log('[Focus Mate] Not configured, skipping event');
    return;
  }

  const payload = {
    session_id: state.sessionId,
    attendance_id: state.attendanceId,
    event_type: 'tab_switch',
    tab_visible: eventData.visible,
    tab_count: state.tabSwitches,
    timestamp: new Date().toISOString(),
    note: eventData.note || 'chrome-extension',
    lock_mode_active: state.lockMode,
    lock_mode_violation: eventData.lockViolation || false,
  };

  try {
    const response = await fetch(`${state.apiBase}/events/tab-switch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${state.token}`,
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    console.log('[Focus Mate] Tab switch event sent successfully');
    state.currentRetryIndex = 0; // Reset retry counter on success
  } catch (err) {
    console.error('[Focus Mate] Failed to send tab-switch event:', err);
    // Add to retry queue
    state.retryQueue.push({ payload, attempts: 0 });
    scheduleRetry();
  }
};

// Retry failed requests with exponential backoff
const scheduleRetry = () => {
  if (state.retryQueue.length === 0) return;

  const delay = RETRY_DELAYS[Math.min(state.currentRetryIndex, RETRY_DELAYS.length - 1)];
  state.currentRetryIndex++;

  setTimeout(async () => {
    const item = state.retryQueue.shift();
    if (!item) return;

    try {
      const response = await fetch(`${state.apiBase}/events/tab-switch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${state.token}`,
        },
        body: JSON.stringify(item.payload),
      });

      if (response.ok) {
        console.log('[Focus Mate] Retry successful');
        state.currentRetryIndex = 0;
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (err) {
      console.error('[Focus Mate] Retry failed:', err);
      if (item.attempts < 3) {
        item.attempts++;
        state.retryQueue.push(item);
      }
    }

    if (state.retryQueue.length > 0) {
      scheduleRetry();
    }
  }, delay);
};

// Handle visibility change events
const handleVisibilityChange = (visible, lockViolation = false) => {
  const now = Date.now();
  if (now - state.lastEventAt < THROTTLE_MS) {
    return;
  }
  state.lastEventAt = now;

  if (!visible) {
    state.tabSwitches++;
  }

  if (lockViolation) {
    state.lockViolations++;
  }

  updateBadge();
  saveState();

  postTabSwitch({
    visible,
    lockViolation,
    note: lockViolation ? 'lock-mode-violation' : 'tab-switch',
  });
};

// Listen for tab activation (user switches tabs)
chrome.tabs.onActivated.addListener((activeInfo) => {
  if (state.lockMode) {
    // In lock mode, any tab switch is a violation
    handleVisibilityChange(false, true);
  } else {
    handleVisibilityChange(false, false);
  }
});

// Listen for window focus changes
chrome.windows.onFocusChanged.addListener((windowId) => {
  if (windowId === chrome.windows.WINDOW_ID_NONE) {
    // User switched to another application
    handleVisibilityChange(false, state.lockMode);
  }
});

// Listen for navigation attempts in lock mode
chrome.webNavigation.onBeforeNavigate.addListener((details) => {
  if (state.lockMode && details.frameId === 0) {
    // Main frame navigation in lock mode
    chrome.tabs.get(details.tabId, (tab) => {
      if (tab && !tab.url.includes('localhost:5173') && !tab.url.includes('focusmate')) {
        // Block navigation and count as violation
        console.log('[Focus Mate] Blocked navigation in lock mode:', details.url);
        handleVisibilityChange(false, true);
        
        // Show warning
        chrome.tabs.sendMessage(details.tabId, {
          type: 'lock_mode_warning',
          message: 'Navigation blocked by Focus Mate lock mode',
        });
      }
    });
  }
});

// Handle messages from popup and content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'config') {
    // Update configuration
    state.apiBase = message.apiBase || DEFAULT_API_BASE;
    state.token = message.token || '';
    state.sessionId = Number(message.sessionId) || null;
    state.attendanceId = Number(message.attendanceId) || null;
    state.lockMode = Boolean(message.lockMode);
    
    // Reset counters on new config
    if (message.token) {
      state.tabSwitches = 0;
      state.lockViolations = 0;
      state.lastEventAt = 0;
    }
    
    updateBadge();
    saveState();
    sendResponse({ ok: true });
    return true;
  }

  if (message.type === 'visibility') {
    handleVisibilityChange(Boolean(message.visible), false);
    sendResponse({ ok: true });
    return true;
  }

  if (message.type === 'get_state') {
    sendResponse({ ...state });
    return true;
  }

  if (message.type === 'lock_mode_attempt') {
    // Content script detected a lock mode violation attempt
    handleVisibilityChange(false, true);
    sendResponse({ ok: true });
    return true;
  }
});

console.log('[Focus Mate] Background service worker initialized');
