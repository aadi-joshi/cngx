/**
 * cngx drift tracker charts.
 * Community data loads from the live S3 index on page load (short cache).
 */
(function () {
  const FG = "#ffffff";
  const MUTED = "#666666";
  const LINE = "#333333";
  const GRID = "#1a1a1a";
  const LIVE_CACHE_MS = 2 * 60 * 1000;
  // Keep in sync with cngx/tracker_filter.py
  const BLOCKED_MODEL_RE = /^(cngx-.*|mock-model|agent-output|unknown|test|e2e.*)$/i;
  const BLOCKED_BASELINE_RE = /(e2e|cli-e2e|probe-baseline|launch-live-baseline)/i;

  const embeddedCommunity = window.TRACKER_DATA || {};
  const meta = window.TRACKER_META || {};
  const liveUrl = window.TRACKER_LIVE_URL || "";

  let communityData = filterCommunity({ ...embeddedCommunity });
  let active = null;
  const charts = [];
  let liveFetchedAt = 0;
  let liveFetchDone = !liveUrl;

  function isBlockedModel(name) {
    return !name || BLOCKED_MODEL_RE.test(String(name).trim());
  }

  function isBlockedBaseline(label) {
    return BLOCKED_BASELINE_RE.test(String(label || ""));
  }

  function shapeKey(r) {
    return [
      r.depth,
      r.verification_steps,
      Math.round(Number(r.hedging_ratio || 0) * 1000) / 1000,
      r.output_length,
      r.total_steps,
      r.correction_count,
      r.uncertainty_markers,
      r.reasoning_length,
    ].join("|");
  }

  function dedupeRows(rows) {
    const byShape = new Map();
    rows.forEach((r) => {
      const key = shapeKey(r);
      const prev = byShape.get(key);
      if (!prev) {
        byShape.set(key, r);
        return;
      }
      // Prefer earlier timestamp so charts do not spike on re-submits.
      if (String(r.timestamp || "") < String(prev.timestamp || "")) {
        byShape.set(key, r);
      }
    });
    // Also collapse same-second collisions that somehow differ in shape noise.
    const bySecond = new Map();
    Array.from(byShape.values())
      .sort((a, b) => String(a.timestamp).localeCompare(String(b.timestamp)))
      .forEach((r) => {
        const sec = String(r.timestamp || "").slice(0, 19);
        if (!bySecond.has(sec)) bySecond.set(sec, r);
      });
    return Array.from(bySecond.values()).sort((a, b) =>
      String(a.timestamp).localeCompare(String(b.timestamp))
    );
  }

  function filterCommunity(byModel) {
    const out = {};
    Object.keys(byModel || {}).forEach((model) => {
      if (isBlockedModel(model)) return;
      const rows = dedupeRows(
        (Array.isArray(byModel[model]) ? byModel[model] : []).filter(
          (r) => !isBlockedBaseline(r && r.baseline_label)
        )
      );
      if (rows.length) out[model] = rows;
    });
    return out;
  }

  function currentModels() {
    return Object.keys(communityData).sort((a, b) => {
      const ca = (communityData[a] || []).length;
      const cb = (communityData[b] || []).length;
      if (cb !== ca) return cb - ca;
      return a.localeCompare(b);
    });
  }

  function liveRecordCount() {
    return Object.values(communityData).reduce((sum, rows) => sum + rows.length, 0);
  }

  function liveModelCount() {
    return currentModels().length;
  }

  const chartDefaults = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: "#000000",
        titleColor: FG,
        bodyColor: MUTED,
        borderColor: LINE,
        borderWidth: 1,
        titleFont: { family: "ui-monospace, monospace", size: 11 },
        bodyFont: { family: "ui-monospace, monospace", size: 11 },
      },
    },
    scales: {
      x: {
        type: "time",
        time: { unit: "day", tooltipFormat: "yyyy-MM-dd" },
        grid: { color: GRID },
        ticks: { color: MUTED, font: { family: "ui-monospace, monospace", size: 10 } },
      },
    },
  };

  function destroyCharts() {
    while (charts.length) {
      const c = charts.pop();
      if (c) c.destroy();
    }
  }

  function makeChart(canvasId, label, field, yOpts) {
    const recs = communityData[active] || [];
    const ctx = document.getElementById(canvasId);
    if (!ctx || !recs.length) return null;

    const points = recs.map((r) => ({ x: r.timestamp, y: r[field] }));
    const chart = new Chart(ctx, {
      type: "line",
      data: {
        datasets: [
          {
            label,
            data: points,
            borderColor: FG,
            backgroundColor: "transparent",
            pointBackgroundColor: FG,
            pointBorderColor: FG,
            pointRadius: 3,
            pointHoverRadius: 5,
            borderWidth: 1,
            tension: 0,
            fill: false,
          },
        ],
      },
      options: {
        ...chartDefaults,
        scales: {
          ...chartDefaults.scales,
          y: {
            ...yOpts,
            grid: { color: GRID },
            ticks: { color: MUTED, font: { family: "ui-monospace, monospace", size: 10 } },
          },
        },
      },
    });
    charts.push(chart);
    return chart;
  }

  function setVisible(id, visible) {
    const el = document.getElementById(id);
    if (el) el.classList.toggle("hidden", !visible);
  }

  function updateView() {
    const loading = liveUrl && !liveFetchDone;
    const hasData = liveRecordCount() > 0;

    setVisible("loading-state", loading);
    setVisible("empty-state", !loading && !hasData);
    setVisible("chart-section", !loading && hasData);

    const status = document.getElementById("community-status");
    if (status) {
      if (loading) {
        status.textContent = "...";
      } else {
        const records = liveRecordCount();
        const models = liveModelCount();
        status.textContent =
          records === 0
            ? "0"
            : `${records} record${records === 1 ? "" : "s"} across ${models} model${models === 1 ? "" : "s"}`;
      }
    }

    const updatedWrap = document.getElementById("index-updated-wrap");
    if (updatedWrap) {
      if (!loading && meta.index_updated_at) {
        updatedWrap.textContent = ` · index updated ${meta.index_updated_at}`;
      } else {
        updatedWrap.textContent = "";
      }
    }
  }

  function renderCharts() {
    destroyCharts();
    const models = currentModels();
    if (!active || !models.includes(active)) {
      active = models[0] || null;
    }

    const title = document.getElementById("active-model-label");
    const recs = active ? communityData[active] || [] : [];

    if (title) {
      const n = recs.length;
      title.textContent = active
        ? `${active} (${n} point${n === 1 ? "" : "s"})`
        : "none";
    }

    if (!recs.length) return;

    makeChart("chart-depth", "Depth", "depth", {
      min: 0,
      title: { display: true, text: "steps", color: MUTED, font: { size: 10 } },
    });
    makeChart("chart-verification", "Verification", "verification_steps", {
      min: 0,
      title: { display: true, text: "count", color: MUTED, font: { size: 10 } },
    });
    makeChart("chart-hedging", "Hedging ratio", "hedging_ratio", {
      min: 0,
      max: 1,
      title: { display: true, text: "0 to 1", color: MUTED, font: { size: 10 } },
    });
    makeChart("chart-drift", "Drift score", "drift_score", {
      min: 0,
      max: 1,
      title: { display: true, text: "0 to 1", color: MUTED, font: { size: 10 } },
    });
  }

  function renderTabs() {
    const tabs = document.getElementById("model-tabs");
    if (!tabs) return;
    const models = currentModels();
    tabs.innerHTML = models
      .map((m) => {
        const n = (communityData[m] || []).length;
        return `<button type="button" class="tab${m === active ? " active" : ""}" data-model="${m}" aria-pressed="${m === active}">${m} <span class="tab-count">${n}</span></button>`;
      })
      .join("");
    tabs.querySelectorAll(".tab").forEach((btn) => {
      btn.addEventListener("click", () => {
        active = btn.dataset.model;
        renderTabs();
        renderCharts();
      });
    });
  }

  function initAnnotations() {
    const section = document.getElementById("annotations-section");
    const list = document.getElementById("annotation-list");
    const annotations = meta.annotations || [];
    if (!section || !list) return;

    if (!annotations.length) {
      section.classList.add("hidden");
      return;
    }

    section.classList.remove("hidden");
    list.innerHTML = annotations
      .map(
        (a) =>
          `<li><strong>${a.date}</strong>: ${a.label}` +
          (a.source_url ? ` <a href="${a.source_url}" rel="noopener">source</a>` : "") +
          "</li>"
      )
      .join("");
  }

  async function refreshLiveData(force) {
    if (!liveUrl) return;
    const now = Date.now();
    if (!force && liveFetchedAt && now - liveFetchedAt < LIVE_CACHE_MS) {
      return;
    }
    try {
      const response = await fetch(liveUrl, { cache: "no-store" });
      if (!response.ok) return;
      const payload = await response.json();
      if (payload && payload.by_model && typeof payload.by_model === "object") {
        communityData = filterCommunity(payload.by_model);
        liveFetchedAt = now;
        if (payload.updated_at) {
          meta.index_updated_at = payload.updated_at;
        }
        active = null;
        updateView();
        renderTabs();
        renderCharts();
      }
    } catch (_err) {
      // keep embedded fallback silently
    } finally {
      liveFetchDone = true;
      updateView();
    }
  }

  async function init() {
    updateView();
    await refreshLiveData(true);
    renderTabs();
    renderCharts();
    initAnnotations();
    if (liveUrl) {
      setInterval(() => refreshLiveData(false), LIVE_CACHE_MS);
    }
  }

  init();

  window.addEventListener("resize", () => {
    charts.forEach((c) => c.resize());
  });
})();
