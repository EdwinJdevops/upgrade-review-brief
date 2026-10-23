"use strict";
document.querySelectorAll("[data-review-form]").forEach((form) => {
  form.addEventListener("submit", () => {
    form.querySelector("button").disabled = true;
    const status = document.querySelector(".working");
    if (status) status.hidden = false;
  });
});
document.querySelectorAll("[data-download]").forEach((button) => {
  button.addEventListener("click", () => {
    const text = document.getElementById(button.dataset.download).value;
    const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = button.dataset.filename;
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
});
window.addEventListener("pageshow", () => {
  document.querySelectorAll("[data-review-form] button").forEach((button) => {
    // The server's model-unavailable state must remain disabled.
    if (!document.querySelector(".notice")) button.disabled = false;
  });
  const status = document.querySelector(".working");
  if (status) status.hidden = true;
});
