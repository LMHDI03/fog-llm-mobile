const chatEl = document.getElementById("chat");
const promptEl = document.getElementById("prompt");
const sendBtn = document.getElementById("send");
const metaEl = document.getElementById("meta");

const modal = document.getElementById("modal");
const settingsBtn = document.getElementById("settingsBtn");
const apiUrlInput = document.getElementById("apiUrl");
const saveBtn = document.getElementById("save");
const closeBtn = document.getElementById("close");

const DEFAULT_API = "http://localhost:8000";

function getApiBase() {
  return localStorage.getItem("API_BASE") || DEFAULT_API;
}

function setApiBase(v) {
  localStorage.setItem("API_BASE", v.replace(/\/$/, ""));
}

function addMsg(role, text) {
  const div = document.createElement("div");
  div.className = `msg ${role === "user" ? "user" : "bot"}`;
  div.textContent = text;
  chatEl.appendChild(div);
  chatEl.scrollTop = chatEl.scrollHeight;
}

async function dispatchPrompt(prompt) {
  const base = getApiBase();
  const url = `${base}/dispatch`;

  const r = await fetch(url, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({prompt})
  });

  if (!r.ok) {
    const t = await r.text();
    throw new Error(`HTTP ${r.status} - ${t}`);
  }
  return await r.json();
}

async function onSend() {
  const p = promptEl.value.trim();
  if (!p) return;

  addMsg("user", p);
  promptEl.value = "";

  metaEl.textContent = "⏳ Envoi au dispatcher...";
  try {
    const res = await dispatchPrompt(p);

    const header =
      `Layer: ${res.layer || "?"} | ` +
      `Latency: ${res.latency_ms ?? "?"} ms | ` +
      `Reason: ${res.reason || ""}`;

    addMsg("bot", `${header}\n\n${res.text || ""}`);
    metaEl.textContent = "✅ OK";
  } catch (e) {
    addMsg("bot", `❌ Erreur: ${e.message}`);
    metaEl.textContent = "❌ Erreur";
  }
}

sendBtn.addEventListener("click", onSend);
promptEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    onSend();
  }
});

// Settings
settingsBtn.addEventListener("click", () => {
  apiUrlInput.value = getApiBase();
  modal.classList.remove("hidden");
});
closeBtn.addEventListener("click", () => modal.classList.add("hidden"));
saveBtn.addEventListener("click", () => {
  setApiBase(apiUrlInput.value.trim() || DEFAULT_API);
  modal.classList.add("hidden");
  metaEl.textContent = `API: ${getApiBase()}`;
});

// init
metaEl.textContent = `API: ${getApiBase()}`;
