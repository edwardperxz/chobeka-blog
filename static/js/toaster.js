document.addEventListener("DOMContentLoaded", function () {
  // Configuration variables
  const toasts = document.querySelectorAll(".toast");
  const dismissDuration = 3000; // 3 seconds
  const staggerDelay = 150; // Delay between showing each toast
  const animationDuration = 500; // Duration of fade in/out animation
  const progressBarDelay = 50; // Small delay before starting progress bar

  toasts.forEach((toast, index) => {
    const progressBar = toast.querySelector(".toast-progress-bar");

    // Show toast with delay based on position
    setTimeout(() => {
      toast.classList.remove("opacity-0", "translate-x-full");
      // Start progress bar animation
      setTimeout(() => {
        progressBar.style.width = "100%";
      }, progressBarDelay);
    }, index * staggerDelay);

    // Auto dismiss after dismissDuration
    setTimeout(() => {
      dismissToast(toast);
    }, dismissDuration + index * staggerDelay);

    // Add click handler to close button
    toast.querySelector(".toast-close").addEventListener("click", function () {
      dismissToast(toast);
    });
  });

  function dismissToast(toast) {
    toast.classList.add("opacity-0", "translate-x-full");
    setTimeout(() => {
      toast.remove();
    }, animationDuration);
  }
});
