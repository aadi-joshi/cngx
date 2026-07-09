/**
 * cngx drift tracker charts.
 * Community data is default. Sample data is opt-in via toggle only.
 */
(function () {
  const FG = "#ffffff";
  const MUTED = "#666666";
  const LINE = "#333333";
  const GRID = "#1a1a1a";

  const communityData = window.TRACKER_DATA || {};
  const sampleData = window.TRACKER_SAMPLE_DATA || {};
  const meta = window.TRACKER_META || {};

  let showingSample = false;
  let active = null;
  const charts = [];

  function currentData() {
    return showingSample ? sampleData : communityData;
  }

  function currentModels() {
    const data = currentData();
    return Object.keys(data);
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
    const recs = (currentData()[active] || []);
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

  function updateEmptyState() {
    const hasCommunity = (meta.community_record_count || 0) > 0;
    const hasSample = (meta.sample_record_count || 0) > 0;
    const showCharts = showingSample ? hasSample : hasCommunity;

    setVisible("empty-state", !showCharts);
    setVisible("chart-section", showCharts);
    setVisible("sample-banner", showingSample && hasSample);

    const toggle = document.getElementById("sample-toggle");
    if (toggle) {
      toggle.classList.toggle("hidden", !hasSample);
      toggle.setAttribute("aria-pressed", showingSample ? "true" : "false");
      toggle.textContent = showingSample
        ? "hide illustrative sample"
        : "show illustrative sample";
    }
  }

  function renderCharts() {
    destroyCharts();
    const models = currentModels();
    if (!active || !models.includes(active)) {
      active = models[0] || null;
    }

    const title = document.getElementById("active-model-label");
    const mode = document.getElementById("data-mode-label");
    const recs = active ? currentData()[active] || [] : [];

    if (title) title.textContent = active || "none";
    if (mode) {
      mode.textContent = showingSample ? "illustrative sample" : "community submissions";
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

  function bindSampleToggle() {
    const toggle = document.getElementById("sample-toggle");
    if (!toggle) return;
    toggle.addEventListener("click", () => {
      showingSample = !showingSample;
      active = null;
      updateEmptyState();
      renderTabs();
      renderCharts();
    });
  }

  function init() {
    updateEmptyState();
    bindSampleToggle();
    renderTabs();
    renderCharts();
    initAnnotations();
  }

  init();

  window.addEventListener("resize", () => {
    charts.forEach((c) => c.resize());
  });
})();
