// Focus Mate Extension - Content Script
// Monitors page visibility and enforces lock mode

let lockModeActive = false;
let lastVisibilityState = document.visibilityState;

// Check lock mode status from background
chrome.runtime.sendMessage({ type: 'get_state' }, (response) => {
  if (response) {
    lockModeActive = response.lockMode || false;
    if (lockModeActive) {
      initLockMode();
    }
  }
});

// Listen for visibility changes
document.addEventListener('visibilitychange', () => {
  const currentState = document.visibilityState;
  
  if (currentState !== lastVisibilityState) {
    lastVisibilityState = currentState;
    
    chrome.runtime.sendMessage({
      type: 'visibility',
      visible: currentState === 'visible',
    });

    if (lockModeActive && currentState === 'hidden') {
      chrome.runtime.sendMessage({
        type: 'lock_mode_attempt',
      });
    }
  }
});

// Listen for window blur/focus
window.addEventListener('blur', () => {
  chrome.runtime.sendMessage({
    type: 'visibility',
    visible: false,
  });

  if (lockModeActive) {
    chrome.runtime.sendMessage({
      type: 'lock_mode_attempt',
    });
  }
});

window.addEventListener('focus', () => {
  chrome.runtime.sendMessage({
    type: 'visibility',
    visible: true,
  });
});

// Listen for page unload
window.addEventListener('pagehide', () => {
  chrome.runtime.sendMessage({
    type: 'visibility',
    visible: false,
  });
});

// Initialize lock mode enforcement
function initLockMode() {
  console.log('[Focus Mate] Lock mode active');

  // Prevent context menu
  document.addEventListener('contextmenu', (e) => {
    e.preventDefault();
    showLockModeWarning('Right-click disabled in lock mode');
  });

  // Prevent certain keyboard shortcuts
  document.addEventListener('keydown', (e) => {
    // Block Ctrl+T (new tab), Ctrl+W (close tab), Ctrl+N (new window)
    if (e.ctrlKey || e.metaKey) {
      if (['t', 'w', 'n', 'Tab'].includes(e.key)) {
        e.preventDefault();
        showLockModeWarning('Keyboard shortcut blocked in lock mode');
        chrome.runtime.sendMessage({
          type: 'lock_mode_attempt',
        });
      }
    }

    // Block Alt+Tab, Alt+F4
    if (e.altKey && ['Tab', 'F4'].includes(e.key)) {
      e.preventDefault();
      showLockModeWarning('Window switching blocked in lock mode');
      chrome.runtime.sendMessage({
        type: 'lock_mode_attempt',
      });
    }
  });

  // Intercept link clicks that would navigate away
  document.addEventListener('click', (e) => {
    const link = e.target.closest('a');
    if (link && link.href) {
      const currentOrigin = window.location.origin;
      const linkUrl = new URL(link.href, window.location.href);
      
      if (linkUrl.origin !== currentOrigin) {
        e.preventDefault();
        showLockModeWarning('External navigation blocked in lock mode');
        chrome.runtime.sendMessage({
          type: 'lock_mode_attempt',
        });
      }
    }
  }, true);
}

// Show lock mode warning overlay
function showLockModeWarning(message) {
  // Remove existing warning if any
  const existing = document.getElementById('focusmate-lock-warning');
  if (existing) {
    existing.remove();
  }

  const warning = document.createElement('div');
  warning.id = 'focusmate-lock-warning';
  warning.style.cssText = `
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: #dc2626;
    color: white;
    padding: 12px 24px;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    z-index: 999999;
    font-family: system-ui, -apple-system, sans-serif;
    font-size: 14px;
    font-weight: 500;
    animation: slideDown 0.3s ease-out;
  `;
  warning.textContent = `🔒 ${message}`;

  // Add animation
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideDown {
      from {
        opacity: 0;
        transform: translateX(-50%) translateY(-20px);
      }
      to {
        opacity: 1;
        transform: translateX(-50%) translateY(0);
      }
    }
  `;
  document.head.appendChild(style);
  document.body.appendChild(warning);

  // Auto-remove after 3 seconds
  setTimeout(() => {
    warning.style.animation = 'slideDown 0.3s ease-out reverse';
    setTimeout(() => warning.remove(), 300);
  }, 3000);
}

// Listen for lock mode updates from background
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'lock_mode_warning') {
    showLockModeWarning(message.message);
    sendResponse({ ok: true });
  }
  
  if (message.type === 'lock_mode_update') {
    lockModeActive = message.enabled;
    if (lockModeActive) {
      initLockMode();
      showLockModeWarning('Lock mode enabled');
    }
    sendResponse({ ok: true });
  }
});

console.log('[Focus Mate] Content script loaded');
