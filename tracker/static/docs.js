/** Docs page: sidebar active section + copy buttons. */
(function () {
  function initCopyButtons() {
    document.querySelectorAll(".copy-wrap").forEach((wrap) => {
      const pre = wrap.querySelector("pre");
      const btn = wrap.querySelector(".copy-btn");
      if (!pre || !btn) return;
      btn.addEventListener("click", async () => {
        try {
          await navigator.clipboard.writeText(pre.textContent || "");
          const prev = btn.textContent;
          btn.textContent = "copied";
          setTimeout(() => {
            btn.textContent = prev;
          }, 1200);
        } catch (_err) {
          btn.textContent = "failed";
        }
      });
    });
  }

  function initSidebar() {
    const links = Array.from(document.querySelectorAll(".docs-sidebar a[href^='#']"));
    if (!links.length) return;

    const sections = links
      .map((link) => {
        const id = link.getAttribute("href").slice(1);
        const el = document.getElementById(id);
        return el ? { link, el } : null;
      })
      .filter(Boolean);

    function onScroll() {
      let current = sections[0];
      for (const item of sections) {
        if (item.el.getBoundingClientRect().top <= 120) current = item;
      }
      links.forEach((l) => l.classList.remove("active"));
      if (current) current.link.classList.add("active");
    }

    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  initCopyButtons();
  initSidebar();
})();
