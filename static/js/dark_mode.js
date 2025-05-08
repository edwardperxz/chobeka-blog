document.addEventListener("DOMContentLoaded", () => {
  const prefersDark = localStorage.getItem("theme") === "dark";
  const body = document.getElementById("body");
  const icon = document.getElementById("theme-icon");
  if (prefersDark) {
    body.classList.add("dark");
    if (icon) icon.textContent = "🌙";
    const label = document.getElementById("theme-label");
    if (label) label.textContent = "Modo Oscuro";
  } else {
    if (icon) icon.textContent = "🌞";
    const label = document.getElementById("theme-label");
    if (label) label.textContent = "Modo Claro";
  }
});

function toggleDarkMode() {
  const body = document.getElementById("body");
  const icon = document.getElementById("theme-icon");
  const isDark = body.classList.toggle("dark");
  localStorage.setItem("theme", isDark ? "dark" : "light");
  if (icon) {
    icon.classList.add("rotate-180");
    setTimeout(() => {
      icon.textContent = isDark ? "🌙" : "🌞";
      const label = document.getElementById("theme-label");
      if (label) label.style.opacity = 0;
      setTimeout(() => {
        label.textContent = isDark ? "Modo Oscuro" : "Modo Claro";
        label.style.opacity = 1;
      }, 250);
      icon.classList.remove("rotate-180");
    }, 250);
  }
}
