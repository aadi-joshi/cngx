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

  const embeddedCommunity = window.TRACKER_DATA || {};
  const meta = window.TRACKER_META || {};
  const liveUrl = window.TRACKER_LIVE_URL || "";

  let communityData = { ...embeddedCommunity };
  let active = null;
  const charts = [];
  let liveFetchedAt = 0;
  let liveFetchDone = !liveUrl;

  function currentModels() {
    return Object.keys(communityData);
  }

  function liveRecordCount() {
    return Object.values(communityData).reduce((sum, rows) => sum + rows.length, 0);
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
        status.textContent = String(liveRecordCount());
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

    if (title) title.textContent = active || "none";

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
      .map(
        (m) =>
          `<button type="button" class="tab${m === active ? " active" : ""}" data-model="${m}" aria-pressed="${m === active}">${m}</button>`
      )
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
        communityData = payload.by_model;
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
