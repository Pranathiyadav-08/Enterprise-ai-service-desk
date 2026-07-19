// API Configuration
const API_BASE = 'http://localhost:8000';

// DOM Elements
const connectionStatus = document.getElementById('connectionStatus');
const connectionText = document.getElementById('connectionText');
const chatFeed = document.getElementById('chatFeed');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const typingIndicator = document.getElementById('typingIndicator');
const sendBtn = document.getElementById('sendBtn');

const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
const uploadStatus = document.getElementById('uploadStatus');
const uploadStatusText = document.getElementById('uploadStatusText');
const documentsList = document.getElementById('documentsList');
const docCountBadge = document.getElementById('docCount');
const emptyDocsState = document.getElementById('emptyDocs');
const reindexBtn = document.getElementById('reindexBtn');
const reindexIcon = document.getElementById('reindexIcon');
const toastContainer = document.getElementById('toastContainer');

// State Variables
let isConnected = false;

// ─────────────────────────────────────────────────────────────────────────────
// INITIALIZATION
// ─────────────────────────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  // Initial Health Check
  checkBackendHealth();
  // Poll health status every 10 seconds
  setInterval(checkBackendHealth, 10000);

  // Setup Event Listeners
  setupChatListeners();
  setupUploadListeners();
  setupReindexListeners();
});

// ─────────────────────────────────────────────────────────────────────────────
// BACKEND HEALTH SERVICE
// ─────────────────────────────────────────────────────────────────────────── */
async function checkBackendHealth() {
  try {
    const response = await fetch(`${API_BASE}/health`, { method: 'GET' });
    if (response.ok) {
      const data = await response.json();
      if (data.status === 'healthy') {
        setConnectionState(true, 'Connected to backend');
        // If we just got connected, fetch the document list
        if (!isConnected) {
          fetchDocuments();
        }
        isConnected = true;
        return;
      }
    }
    throw new Error('Healthy status check failed');
  } catch (error) {
    setConnectionState(false, 'Disconnected from backend');
    isConnected = false;
  }
}

function setConnectionState(connected, text) {
  if (connected) {
    connectionStatus.className = 'status-indicator status-connected';
    connectionText.textContent = text;
  } else {
    connectionStatus.className = 'status-indicator status-disconnected';
    connectionText.textContent = text;
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// TOAST NOTIFICATIONS
// ─────────────────────────────────────────────────────────────────────────── */
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  // Icon based on type
  let icon = '';
  if (type === 'success') {
    icon = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--success-color)"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
  } else if (type === 'error') {
    icon = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--error-color)"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>`;
  } else {
    icon = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--primary-color)"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`;
  }

  toast.innerHTML = `
    ${icon}
    <span>${message}</span>
    <button class="toast-close">&times;</button>
  `;

  toastContainer.appendChild(toast);

  // Close button action
  toast.querySelector('.toast-close').addEventListener('click', () => {
    toast.remove();
  });

  // Auto remove
  setTimeout(() => {
    toast.style.animation = 'fadeOut 0.3s forwards';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// ─────────────────────────────────────────────────────────────────────────────
// CHAT INTERFACE FUNCTIONS
// ─────────────────────────────────────────────────────────────────────────── */
function setupChatListeners() {
  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = messageInput.value.trim();
    if (!text) return;

    if (!isConnected) {
      showToast('Cannot send message. Backend is offline.', 'error');
      return;
    }

    // Add user bubble
    appendMessage(text, 'user');
    messageInput.value = '';
    
    // Show typing state
    showTyping(true);

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });

      if (!response.ok) {
        throw new Error('API server returned error');
      }

      const data = await response.json();
      showTyping(false);
      
      if (data.status === 'success') {
        appendMessage(data.response, 'ai', {
          intent: data.intent,
          assignedAgent: data.assigned_agent
        });
      } else {
        appendMessage('The system was unable to answer. Please try again.', 'ai');
      }

    } catch (error) {
      showTyping(false);
      showToast('Failed to connect to agent service', 'error');
      appendMessage('Sorry, I encountered an error communicating with the agent supervisor. Please verify your backend server is active and try again.', 'ai');
    }
  });
}

function showTyping(show) {
  if (show) {
    typingIndicator.classList.remove('hidden');
    chatFeed.scrollTop = chatFeed.scrollHeight;
    sendBtn.disabled = true;
  } else {
    typingIndicator.classList.add('hidden');
    sendBtn.disabled = false;
  }
}

function appendMessage(text, sender, meta = null) {
  const messageDiv = document.createElement('div');
  messageDiv.className = `message message-${sender}`;
  
  const avatarText = sender === 'ai' ? 'AI' : 'U';
  const formattedContent = sender === 'ai' ? formatMarkdown(text) : escapeHtml(text);
  const timeString = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  let metaHtml = '';
  if (sender === 'ai' && meta) {
    const intentClass = meta.intent.toLowerCase().includes('hr') ? 'hr' :
                        meta.intent.toLowerCase().includes('it') ? 'it' :
                        meta.intent.toLowerCase().includes('policy') ? 'policy' : 'general';
    
    metaHtml = `
      <div class="message-meta">
        <span class="badge badge-intent ${intentClass}" title="Intent Classified">${meta.intent}</span>
        <span class="badge" title="Handling Agent" style="background-color: rgba(255,255,255,0.02)">Agent: ${meta.assignedAgent}</span>
      </div>
    `;
  }

  messageDiv.innerHTML = `
    <div class="message-avatar">${avatarText}</div>
    <div class="message-content-wrapper">
      <div class="message-content">${formattedContent}</div>
      ${metaHtml}
      <div class="message-time">${timeString}</div>
    </div>
  `;

  chatFeed.appendChild(messageDiv);
  chatFeed.scrollTop = chatFeed.scrollHeight;
}

// Simple Helper to Escape HTML
function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// Basic markdown to html formatter for AI answers (bolding and list blocks)
function formatMarkdown(text) {
  let escaped = escapeHtml(text);
  
  // Replace double asterisks with bold tags
  escaped = escaped.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  
  // Format linebreaks and basic lists
  const lines = escaped.split('\n');
  let inList = false;
  const result = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line.startsWith('* ') || line.startsWith('- ')) {
      if (!inList) {
        result.push('<ul>');
        inList = true;
      }
      result.push(`<li>${line.substring(2)}</li>`);
    } else {
      if (inList) {
        result.push('</ul>');
        inList = false;
      }
      result.push(line ? line + '<br>' : '<br>');
    }
  }
  
  if (inList) {
    result.push('</ul>');
  }

  return result.join('\n');
}

// ─────────────────────────────────────────────────────────────────────────────
// UPLOAD & DOCUMENTS MANAGER
// ─────────────────────────────────────────────────────────────────────────── */
function setupUploadListeners() {
  // Click on zone trigger input click
  uploadZone.addEventListener('click', () => {
    fileInput.click();
  });

  // Handle file selection
  fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
      handleFileUpload(fileInput.files[0]);
    }
  });

  // Drag over effects
  uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('dragover');
  });

  uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('dragover');
  });

  uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  });
}

async function handleFileUpload(file) {
  // Validate File Type
  if (!file.name.endsWith('.pdf')) {
    showToast('Only PDF documents are supported.', 'error');
    fileInput.value = '';
    return;
  }

  // Validate File Size (e.g. max 15MB)
  if (file.size > 15 * 1024 * 1024) {
    showToast('Document size exceeds 15MB limit.', 'error');
    fileInput.value = '';
    return;
  }

  // Show uploading loading overlay
  uploadStatus.classList.remove('hidden');
  uploadStatusText.textContent = `Uploading and indexing "${file.name}"...`;

  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      body: formData
    });

    const data = await response.json();
    uploadStatus.classList.add('hidden');
    fileInput.value = '';

    if (response.ok && data.status === 'success') {
      showToast(`Indexed "${file.name}" successfully!`, 'success');
      fetchDocuments();
    } else {
      showToast(data.detail || 'Upload and indexing failed.', 'error');
    }
  } catch (error) {
    uploadStatus.classList.add('hidden');
    fileInput.value = '';
    showToast('Network error during file upload', 'error');
  }
}

async function fetchDocuments() {
  if (!isConnected) return;

  try {
    const response = await fetch(`${API_BASE}/documents`);
    if (!response.ok) throw new Error('Failed to retrieve docs list');
    
    const data = await response.json();
    renderDocuments(data.documents);
  } catch (error) {
    console.error('Error fetching documents:', error);
  }
}

function renderDocuments(documents) {
  docCountBadge.textContent = documents.length;
  
  if (documents.length === 0) {
    emptyDocsState.classList.remove('hidden');
    // Remove any previously rendered items
    const items = documentsList.querySelectorAll('.doc-item');
    items.forEach(el => el.remove());
    return;
  }

  emptyDocsState.classList.add('hidden');
  
  // Clear old entries
  const existingItems = documentsList.querySelectorAll('.doc-item');
  existingItems.forEach(el => el.remove());

  // Render list
  documents.forEach(filename => {
    const docDiv = document.createElement('div');
    docDiv.className = 'doc-item';
    
    docDiv.innerHTML = `
      <div class="doc-info">
        <div class="doc-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
          </svg>
        </div>
        <span class="doc-name" title="${filename}">${filename}</span>
      </div>
      <button class="btn-delete" title="Delete from knowledge base" data-file="${filename}">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="3 6 5 6 21 6"></polyline>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
          <line x1="10" y1="11" x2="10" y2="17"></line>
          <line x1="14" y1="11" x2="14" y2="17"></line>
        </svg>
      </button>
    `;

    // Hook up delete button
    docDiv.querySelector('.btn-delete').addEventListener('click', async (e) => {
      e.stopPropagation();
      const fileToDelete = e.currentTarget.getAttribute('data-file');
      await deleteDocument(fileToDelete);
    });

    documentsList.appendChild(docDiv);
  });
}

async function deleteDocument(filename) {
  if (!confirm(`Are you sure you want to delete "${filename}"? This will rebuild the vector database.`)) {
    return;
  }

  showToast(`Deleting "${filename}"...`);
  
  try {
    const response = await fetch(`${API_BASE}/documents/${encodeURIComponent(filename)}`, {
      method: 'DELETE'
    });

    const data = await response.json();
    if (response.ok && data.status === 'success') {
      showToast(`Removed "${filename}" and rebuilt vector index`, 'success');
      fetchDocuments();
    } else {
      showToast(data.detail || 'Failed to delete file', 'error');
    }
  } catch (error) {
    showToast('Network error during file deletion', 'error');
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// REINDEX DATABASE
// ─────────────────────────────────────────────────────────────────────────── */
function setupReindexListeners() {
  reindexBtn.addEventListener('click', async () => {
    if (!isConnected) {
      showToast('Cannot reindex. Backend is offline.', 'error');
      return;
    }

    // Start spin animation
    reindexIcon.classList.add('spinning');
    reindexBtn.disabled = true;
    showToast('Rebuilding vector database index...');

    try {
      const response = await fetch(`${API_BASE}/reindex`, {
        method: 'POST'
      });

      const data = await response.json();
      reindexIcon.classList.remove('spinning');
      reindexBtn.disabled = false;

      if (response.ok && data.status === 'success') {
        showToast(`Index rebuilt successfully! Indexed ${data.documents_indexed} documents.`, 'success');
        fetchDocuments();
      } else {
        showToast(data.detail || 'Reindexing failed.', 'error');
      }
    } catch (error) {
      reindexIcon.classList.remove('spinning');
      reindexBtn.disabled = false;
      showToast('Network error during reindexing process.', 'error');
    }
  });
}
