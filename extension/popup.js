// Focus Mate Extension - Popup UI Controller

const DEFAULT_API_BASE = 'http://localhost:8000/api';

document.addEventListener('DOMContentLoaded', async () => {
  const apiBaseInput = document.getElementById('apiBase');
  const tokenInput = document.getElementById('token');
  const sessionIdInput = document.getElementById('sessionId');
  const attendanceIdInput = document.getElementById('attendanceId');
  const lockModeCheckbox = document.getElementById('lockMode');
  const saveButton = document.getElementById('save');
  const clearButton = document.getElementById('clearConfig');
  const statusEl = document.getElementById('status');
  const tabCountEl = document.getElementById('tabCount');
  const lockViolationsEl = document.getElementById('lockViolations');

  // Load saved configuration
  const response = await chrome.runtime.sendMessage({ type: 'get_state' });
  if (response) {
    apiBaseInput.value = response.apiBase || DEFAULT_API_BASE;
    tokenInput.value = response.token || '';
    sessionIdInput.value = response.sessionId || '';
    attendanceIdInput.value = response.attendanceId || '';
    lockModeCheckbox.checked = response.lockMode || false;
    tabCountEl.textContent = response.tabSwitches || 0;
    lockViolationsEl.textContent = response.lockViolations || 0;

    if (response.token && response.sessionId && response.attendanceId) {
      statusEl.textContent = 'Configured and active';
      statusEl.className = 'status success';
    } else {
      statusEl.textContent = 'Not fully configured';
      statusEl.className = 'status';
    }
  }

  // Save configuration
  saveButton.addEventListener('click', async () => {
    const config = {
      type: 'config',
      apiBase: apiBaseInput.value || DEFAULT_API_BASE,
      token: tokenInput.value,
      sessionId: sessionIdInput.value,
      attendanceId: attendanceIdInput.value,
      lockMode: lockModeCheckbox.checked,
    };

    const saveResponse = await chrome.runtime.sendMessage(config);
    if (saveResponse && saveResponse.ok) {
      statusEl.textContent = 'Configuration saved! Tab switches will be tracked.';
      statusEl.className = 'status success';
    } else {
      statusEl.textContent = 'Failed to save configuration.';
      statusEl.className = 'status error';
    }
  });

  // Clear configuration
  clearButton.addEventListener('click', async () => {
    apiBaseInput.value = DEFAULT_API_BASE;
    tokenInput.value = '';
    sessionIdInput.value = '';
    attendanceIdInput.value = '';
    lockModeCheckbox.checked = false;

    await chrome.runtime.sendMessage({
      type: 'config',
      apiBase: DEFAULT_API_BASE,
      token: '',
      sessionId: null,
      attendanceId: null,
      lockMode: false,
    });

    tabCountEl.textContent = '0';
    lockViolationsEl.textContent = '0';
    statusEl.textContent = 'Configuration cleared';
    statusEl.className = 'status';
  });

  // Update stats periodically
  setInterval(async () => {
    const state = await chrome.runtime.sendMessage({ type: 'get_state' });
    if (state) {
      tabCountEl.textContent = state.tabSwitches || 0;
      lockViolationsEl.textContent = state.lockViolations || 0;
    }
  }, 1000);
});
