(() => {
  "use strict";

  const navItems = Array.from(document.querySelectorAll(".nav-item"));
  const panels = Array.from(document.querySelectorAll(".panel"));

  function showPanel(panelId) {
    navItems.forEach((item) => {
      const selected = item.dataset.panel === panelId;
      item.classList.toggle("active", selected);
      if (selected) {
        item.setAttribute("aria-current", "page");
      } else {
        item.removeAttribute("aria-current");
      }
    });

    panels.forEach((panel) => {
      const selected = panel.id === panelId;
      panel.hidden = !selected;
      panel.classList.toggle("active", selected);
      if (selected) {
        panel.focus({ preventScroll: true });
      }
    });
  }

  navItems.forEach((item) => {
    item.addEventListener("click", () => showPanel(item.dataset.panel));
  });
})();
