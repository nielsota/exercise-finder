// here we fetch handles from the html file
const out = document.getElementById("out");
const statusEl = document.getElementById("status");
const redoBtn = document.getElementById("redoBtn");
let lastPayload = null;

function setStatus(s) { statusEl.textContent = s; }

// Helper: wait for MathJax to be ready, then typeset the page
async function typesetMath() {
  if (!window.MathJax) return;
  // Wait for MathJax to finish loading (startup.promise exists once ready)
  if (window.MathJax.startup?.promise) {
    await window.MathJax.startup.promise;
  }
  // Typeset the whole document (more reliable than targeting a specific element)
  if (window.MathJax.typesetPromise) {
    await window.MathJax.typesetPromise();
  }
}

function escapeHtml(s) {
  return s.replaceAll("&", "&amp;")
          .replaceAll("<", "&lt;")
          .replaceAll(">", "&gt;")
          .replaceAll("\"", "&quot;")
          .replaceAll("'", "&#039;");
}

function renderResult(payload) {
  out.style.display = "block";

  // here we format the result: use default values if not present
  const formatted = payload.formatted || { stem: "", parts: [] };
  
  // here we format the parts: maps parts to list items
  const parts = (formatted.parts || [])
    .map(p => `<li>${escapeHtml(p.text)}</li>`)
    .join("");

  // here we format the figures: maps figures to image tags
  const figures = (payload.figure_images || [])
    .map(url => `<img src="${escapeHtml(url)}" loading="lazy" />`)
    .join("");

  // combine results into a single HTML-formatted string
  // uses ternary operator to conditionally render parts, pages, and figures
  out.innerHTML = `
    <div class="row">
      <span class="pill">record_id: ${escapeHtml(String(payload.record_id || ""))}</span>
      <span class="pill">score: ${escapeHtml(String(payload.score || ""))}</span>
    </div>
    <h3 style="margin-bottom: 8px;">Stem</h3>
    <div class="stem">${escapeHtml(formatted.stem || "")}</div>
    ${parts ? `<h3 style="margin: 14px 0 8px;">Questions</h3><ol class="parts">${parts}</ol>` : ""}
    ${figures ? `<h3 style="margin: 14px 0 8px;">Images</h3>` : ""}
    ${figures ? `<div class="muted" style="margin-top: 10px;">Figures</div><div class="imgs">${figures}</div>` : ""}
  `;
}

function renderError(errText) {
  out.style.display = "block";
  out.innerHTML = `<div class="error">${escapeHtml(errText)}</div>`;
}

async function run(mode, payloadOverride = null) {

  // when click event on bestBtn, randBtn, or redoBtn, this function is called
  // so the query is now populated from the textarea
  const query = document.getElementById("q").value.trim();
  
  // here we get the max results from the input field
  const maxResults = parseInt(document.getElementById("maxResults").value || "5", 10);
  
  // here we create the payload object
  const payload = payloadOverride || { query, max_results: maxResults, mode }; // mode shorthand for "mode": mode
  
  // here we check if the query is empty
  if (!payload.query) return;

  setStatus("Working…");
  redoBtn.disabled = true;


  try {

    // here we fetch the data from the api
    const resp = await fetch("/api/fetch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    // here we parse the response as text
    const text = await resp.text();

    // here we check if the response is ok
    if (!resp.ok) throw new Error(text || `HTTP ${resp.status}`);

    // here we parse the response as json
    const data = JSON.parse(text);

    // here we render the result
    renderResult(data);

    // DEBUG: log what's in the DOM before typesetting
    console.log("Stem from API:", data.formatted?.stem);
    console.log("DOM innerHTML before typeset:", out.innerHTML.slice(0, 500));

    // here we typeset the math
    await typesetMath();
    
    // DEBUG: log after typeset
    console.log("DOM innerHTML after typeset:", out.innerHTML.slice(0, 500));

    // here we set the last payload
    lastPayload = payload;

    // here we enable the redo button
    redoBtn.disabled = false;
    setStatus("Done");
  } catch (e) {
    // here we render the error
    renderError(String(e));
    setStatus("Error");
  }
}

document.getElementById("bestBtn").addEventListener("click", () => run("best"));
document.getElementById("randBtn").addEventListener("click", () => run("random"));
document.getElementById("redoBtn").addEventListener("click", () => {
  if (lastPayload) run(lastPayload.mode, lastPayload);
});
