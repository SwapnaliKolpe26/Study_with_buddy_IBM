/**
 * Study With Buddy — Main JavaScript
 * Handles: theme toggle, chat send/receive, markdown rendering,
 *          typing indicator, auto-resize textarea, clear chat.
 */

// ── 1. Dark / Light Mode Toggle ─────────────────────────────────
(function initTheme() {
  const html       = document.documentElement;
  const btn        = document.getElementById("themeToggle");
  const icon       = document.getElementById("themeIcon");
  const label      = document.getElementById("themeLabel");

  if (!btn) return;

  // Load saved preference or default to light
  const saved = localStorage.getItem("swb-theme") || "light";
  applyTheme(saved);

  btn.addEventListener("click", () => {
    const next = html.getAttribute("data-bs-theme") === "dark" ? "light" : "dark";
    applyTheme(next);
    localStorage.setItem("swb-theme", next);
  });

  function applyTheme(theme) {
    html.setAttribute("data-bs-theme", theme);
    if (theme === "dark") {
      icon.className  = "bi bi-sun-fill";
      if (label) label.textContent = "Light Mode";
    } else {
      icon.className  = "bi bi-moon-stars-fill";
      if (label) label.textContent = "Dark Mode";
    }
  }
})();

// ── 2. Chat UI — Element references ─────────────────────────────
const chatMessages   = document.getElementById("chatMessages");
const userInput      = document.getElementById("userInput");
const charCount      = document.getElementById("charCount");
const sendBtn        = document.getElementById("sendBtn");
const typingIndicator= document.getElementById("typingIndicator");
const welcomeBlock   = document.getElementById("welcomeBlock");

// Render any existing server-rendered Buddy bubbles with Markdown
document.addEventListener("DOMContentLoaded", () => {
  renderExistingMarkdown();
  scrollToBottom();
  setupTextareaAutoResize();
});

/**
 * Render Markdown in Buddy bubbles that were server-rendered
 * (i.e., bubbles that came from Jinja template history).
 */
function renderExistingMarkdown() {
  if (typeof marked === "undefined") return;
  document.querySelectorAll(".markdown-body[data-raw]").forEach(el => {
    const raw = el.getAttribute("data-raw") || el.textContent;
    el.innerHTML = marked.parse(raw);
    el.removeAttribute("data-raw");
  });
}

// ── 3. Textarea — auto-resize + character counter ────────────────
function setupTextareaAutoResize() {
  if (!userInput) return;
  userInput.addEventListener("input", () => {
    autoResizeTextarea(userInput);
    if (charCount) charCount.textContent = `${userInput.value.length} / 2000`;
  });
  // Send on Enter (without Shift)
  userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(e);
    }
  });
}

function autoResizeTextarea(el) {
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 140) + "px";
}

// ── 4. Send Message ──────────────────────────────────────────────
async function sendMessage(e) {
  if (e) e.preventDefault();
  if (!userInput) return;

  const text = userInput.value.trim();
  if (!text) return;

  // Hide welcome screen on first message
  if (welcomeBlock) welcomeBlock.style.display = "none";

  // Append user bubble
  appendBubble("user", text, currentTime());

  // Clear & reset textarea
  userInput.value = "";
  if (charCount) charCount.textContent = "0 / 2000";
  autoResizeTextarea(userInput);

  // Disable input while waiting
  setInputEnabled(false);
  showTyping(true);

  try {
    const res  = await fetch("/api/chat", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ message: text }),
    });
    const data = await res.json();

    showTyping(false);

    if (data.error) {
      appendBubble("buddy", `⚠️ **Error:** ${data.error}`, currentTime(), true);
    } else {
      appendBubble("buddy", data.reply, data.timestamp || currentTime(), true);
    }
  } catch (err) {
    showTyping(false);
    appendBubble("buddy",
      "⚠️ **Network error.** Please check your connection and try again.",
      currentTime(), true
    );
    console.error("Chat fetch error:", err);
  } finally {
    setInputEnabled(true);
    userInput.focus();
  }
}

// ── 5. Append a Chat Bubble ──────────────────────────────────────
function appendBubble(role, content, time, renderMarkdown = false) {
  const row = document.createElement("div");
  row.className = `chat-bubble-row ${role === "user" ? "user-row" : "buddy-row"}`;

  if (role === "user") {
    row.innerHTML = `
      <div class="chat-bubble user-bubble">
        <div class="bubble-content">${escapeHtml(content)}</div>
        <div class="bubble-time">${time}</div>
      </div>`;
  } else {
    const contentHtml = renderMarkdown && typeof marked !== "undefined"
      ? marked.parse(content)
      : escapeHtml(content);

    row.innerHTML = `
      <div class="buddy-bubble-avatar"><i class="bi bi-mortarboard-fill"></i></div>
      <div class="chat-bubble buddy-bubble">
        <div class="bubble-content markdown-body">${contentHtml}</div>
        <div class="bubble-time">${time}</div>
      </div>`;
  }

  // Insert before the typing indicator
  chatMessages.insertBefore(row, typingIndicator);
  scrollToBottom();
}

// ── 6. Typing Indicator ──────────────────────────────────────────
function showTyping(show) {
  if (!typingIndicator) return;
  typingIndicator.classList.toggle("d-none", !show);

  const statusEl = document.getElementById("buddyStatus");
  if (statusEl) {
    statusEl.textContent = show ? "Buddy is typing…" : "Your AI Study Companion";
  }
  scrollToBottom();
}

// ── 7. Clear Chat ────────────────────────────────────────────────
async function clearChat() {
  if (!confirm("Clear all chat messages? This cannot be undone.")) return;

  try {
    await fetch("/api/clear-chat", { method: "POST" });
  } catch (_) { /* ignore network error on clear */ }

  // Remove all bubbles from DOM (keep typing indicator)
  const rows = chatMessages.querySelectorAll(".chat-bubble-row:not(#typingIndicator)");
  rows.forEach(r => r.remove());

  // Re-show welcome block if it exists
  if (welcomeBlock) welcomeBlock.style.display = "";

  // Reset hidden welcome block if it was hidden via style
  const newWelcome = document.getElementById("welcomeBlock");
  if (newWelcome) newWelcome.style.display = "";
}

// ── 8. Suggestion chips (quick-start messages) ───────────────────
function sendSuggestion(text) {
  if (!userInput) return;
  userInput.value = text;
  autoResizeTextarea(userInput);
  sendMessage(null);
}

// ── 9. Helpers ───────────────────────────────────────────────────
function scrollToBottom() {
  if (chatMessages) {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
}

function setInputEnabled(enabled) {
  if (userInput) userInput.disabled = !enabled;
  if (sendBtn)   sendBtn.disabled   = !enabled;
}

function currentTime() {
  return new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
}

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
