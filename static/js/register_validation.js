document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("register-form");
  if (!form) return; 

  const username = document.getElementById("id_username");
  const email = document.getElementById("id_email");
  const password1 = document.getElementById("id_password1");
  const password2 = document.getElementById("id_password2");

  // Validación en tiempo real
  [username, email, password1, password2].forEach((field) => {
    field.addEventListener("input", function () {
      clearError(this);
    });
  });

  // Validación al enviar
  form.addEventListener("submit", function (e) {
    let isValid = true;

    // Validar campos requeridos
    [username, email, password1, password2].forEach((field) => {
      if (!field.value.trim()) {
        showError(field, "Este campo es obligatorio.");
        isValid = false;
      }
    });

    // Validación adicional para email
    if (email.value.trim() && !validateEmail(email.value)) {
      showError(email, "Por favor ingresa un correo válido.");
      isValid = false;
    }

    // Validación para contraseñas coincidentes
    if (
      password1.value !== password2.value &&
      password1.value &&
      password2.value
    ) {
      showError(password2, "Las contraseñas no coinciden.");
      isValid = false;
    }

    if (!isValid) {
      e.preventDefault();
    }
  });

  // Funciones auxiliares
  function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  }

  function showError(field, message) {
    clearError(field); // Limpiar errores previos
    field.classList.add("border-red-500");

    let errorDiv = field.nextElementSibling;
    if (!errorDiv || !errorDiv.classList.contains("text-red-600")) {
      errorDiv = document.createElement("div");
      errorDiv.className = "mt-1 text-sm text-red-600 dark:text-red-400";
      field.parentNode.insertBefore(errorDiv, field.nextSibling);
    }

    errorDiv.textContent = message;
  }

  function clearError(field) {
    field.classList.remove("border-red-500");
    const errorDiv = field.nextElementSibling;
    if (errorDiv && errorDiv.classList.contains("text-red-600")) {
      errorDiv.textContent = "";
    }
  }
});
