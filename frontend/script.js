const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const messages = document.getElementById("messages");
const backendUrlInput = document.getElementById("backendUrl");
const sessionIdElement = document.getElementById("sessionId");
const newSessionBtn = document.getElementById("newSessionBtn");

let sessionId = localStorage.getItem("ktu_chatbot_session_id");

if (!sessionId) {
  sessionId = createSessionId();
  localStorage.setItem("ktu_chatbot_session_id", sessionId);
}

sessionIdElement.textContent = sessionId;

newSessionBtn.addEventListener("click", () => {
  sessionId = createSessionId();
  localStorage.setItem("ktu_chatbot_session_id", sessionId);
  sessionIdElement.textContent = sessionId;

  messages.innerHTML = `
    <div class="empty-state">
      <h3>Yeni session başlatıldı</h3>
      <p>Şimdi yeni oturumla soru sorabilirsin.</p>
    </div>
  `;
});

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const userMessage = messageInput.value.trim();

  if (!userMessage) {
    return;
  }

  clearEmptyState();
  appendUserMessage(userMessage);
  messageInput.value = "";
  autoResizeTextarea();

  const submitButton = chatForm.querySelector("button");
  submitButton.disabled = true;

  appendLoadingMessage();

  try {
    const response = await fetch(backendUrlInput.value.trim(), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: userMessage,
        session_id: sessionId,
      }),
    });

    removeLoadingMessage();

    const data = await response.json();

    if (!response.ok) {
      appendErrorMessage(data);
      return;
    }

    if (data.session_id) {
      sessionId = data.session_id;
      localStorage.setItem("ktu_chatbot_session_id", sessionId);
      sessionIdElement.textContent = sessionId;
    }

    appendBotMessage(data);
  } catch (error) {
    removeLoadingMessage();

    appendErrorMessage({
      detail:
        "Backend'e bağlanılamadı. Backend çalışıyor mu? Backend URL doğru mu?",
      error: String(error),
    });
  } finally {
    submitButton.disabled = false;
    messageInput.focus();
  }
});

messageInput.addEventListener("input", autoResizeTextarea);

messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    chatForm.requestSubmit();
  }
});

function appendUserMessage(text) {
  const wrapper = document.createElement("div");
  wrapper.className = "message user";

  wrapper.innerHTML = `
    <div class="bubble">${escapeHtml(text)}</div>
  `;

  messages.appendChild(wrapper);
  scrollToBottom();
}

function appendBotMessage(data) {
  const mode = data.mode || "unknown";
  const modeClass = getModeClass(mode);

  const wrapper = document.createElement("div");
  wrapper.className = "message bot";

  wrapper.innerHTML = `
    <div class="message-title">
      <span class="badge ${modeClass}">${escapeHtml(mode.toUpperCase())}</span>
    </div>

    <div class="bubble">${escapeHtml(data.answer || "Cevap boş döndü.")}</div>

    <div class="debug-card">
      <div class="debug-grid">
        ${debugItem("mode", data.mode)}
        ${debugItem("intent", data.intent)}
        ${debugItem("confidence", formatConfidence(data.confidence))}
        ${debugItem("matched_question", data.matched_question)}
        ${debugItem("session_id", data.session_id)}
      </div>

      ${renderSources(data.sources)}

      <details class="raw-json">
        <summary>Raw JSON göster</summary>
        <pre>${escapeHtml(JSON.stringify(data, null, 2))}</pre>
      </details>
    </div>
  `;

  messages.appendChild(wrapper);
  scrollToBottom();
}

function appendLoadingMessage() {
  const wrapper = document.createElement("div");
  wrapper.className = "message bot";
  wrapper.id = "loadingMessage";

  wrapper.innerHTML = `
    <div class="bubble">Cevap bekleniyor...</div>
  `;

  messages.appendChild(wrapper);
  scrollToBottom();
}

function removeLoadingMessage() {
  const loadingMessage = document.getElementById("loadingMessage");

  if (loadingMessage) {
    loadingMessage.remove();
  }
}

function appendErrorMessage(errorData) {
  const wrapper = document.createElement("div");
  wrapper.className = "message bot";

  wrapper.innerHTML = `
    <div class="message-title">
      <span class="badge error">ERROR</span>
    </div>

    <div class="bubble">Bir hata oluştu.</div>

    <div class="debug-card">
      <details class="raw-json" open>
        <summary>Hata detayı</summary>
        <pre>${escapeHtml(JSON.stringify(errorData, null, 2))}</pre>
      </details>
    </div>
  `;

  messages.appendChild(wrapper);
  scrollToBottom();
}

function debugItem(label, value) {
  return `
    <div class="debug-item">
      <span class="debug-label">${escapeHtml(label)}</span>
      <span class="debug-value">${escapeHtml(value ?? "-")}</span>
    </div>
  `;
}

function renderSources(sources) {
  if (!Array.isArray(sources) || sources.length === 0) {
    return `
      <div class="sources">
        <span class="debug-label">sources</span>
        <div class="source-item">Kaynak yok.</div>
      </div>
    `;
  }

  const sourceHtml = sources
    .map((source, index) => {
      const normalizedSource = normalizeSource(source);

      return `
        <div class="source-item">
          <strong>${index + 1}. ${escapeHtml(normalizedSource.title)}</strong>
          <br />
          URL:
          ${
            normalizedSource.url
              ? `<a href="${escapeAttribute(
                  normalizedSource.url
                )}" target="_blank" rel="noopener noreferrer">${escapeHtml(
                  normalizedSource.url
                )}</a>`
              : "-"
          }
          <br />
          Type: ${escapeHtml(normalizedSource.type)}
          <br />
          Score: ${escapeHtml(normalizedSource.score)}
        </div>
      `;
    })
    .join("");

  return `
    <div class="sources">
      <span class="debug-label">sources</span>
      ${sourceHtml}
    </div>
  `;
}

function normalizeSource(source) {
  if (typeof source === "string") {
    return {
      title: source,
      url: "",
      type: "-",
      score: "-",
    };
  }

  return {
    title: source?.title || "Başlıksız kaynak",
    url: source?.url || "",
    type: source?.type || "-",
    score: source?.score ?? "-",
  };
}

function getModeClass(mode) {
  const normalizedMode = String(mode).toLowerCase();

  if (normalizedMode.includes("faq")) {
    return "faq";
  }

  if (normalizedMode.includes("fallback")) {
    return "fallback";
  }

  if (normalizedMode.includes("rag") || normalizedMode.includes("llm")) {
    return "rag";
  }

  return "unknown";
}

function formatConfidence(confidence) {
  if (confidence === null || confidence === undefined) {
    return "-";
  }

  const numericConfidence = Number(confidence);

  if (Number.isNaN(numericConfidence)) {
    return String(confidence);
  }

  return `${numericConfidence} (${Math.round(numericConfidence * 100)}%)`;
}

function clearEmptyState() {
  const emptyState = document.querySelector(".empty-state");

  if (emptyState) {
    emptyState.remove();
  }
}

function scrollToBottom() {
  messages.scrollTop = messages.scrollHeight;
}

function autoResizeTextarea() {
  messageInput.style.height = "auto";
  messageInput.style.height = `${messageInput.scrollHeight}px`;
}

function createSessionId() {
  if (window.crypto && window.crypto.randomUUID) {
    return window.crypto.randomUUID();
  }

  return `session-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function escapeAttribute(value) {
  return escapeHtml(value).replaceAll("`", "&#096;");
}