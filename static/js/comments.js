document.addEventListener('DOMContentLoaded', () => {
  // Seleccionar todos los botones para mostrar el formulario de comentarios
  const toggleButtons = document.querySelectorAll('.toggle-comment-form');
  const cancelButtons = document.querySelectorAll('.cancel-comment');

  // Mostrar el formulario de comentarios al hacer clic en "Agregar comentario"
  toggleButtons.forEach(button => {
    button.addEventListener('click', () => {
      const reviewId = button.getAttribute('data-review-id');
      const formContainer = document.getElementById(`comment-form-${reviewId}`);

      // Mostrar el formulario
      formContainer.classList.remove('hidden');

      // Ocultar el botón de "Agregar comentario"
      button.classList.add('hidden');
    });
  });

  // Ocultar el formulario de comentarios al hacer clic en "Cancelar"
  cancelButtons.forEach(button => {
    button.addEventListener('click', () => {
      const reviewId = button.getAttribute('data-review-id');
      const formContainer = document.getElementById(`comment-form-${reviewId}`);
      const toggleButton = document.querySelector(
        `.toggle-comment-form[data-review-id="${reviewId}"]`
      );

      // Ocultar el formulario
      formContainer.classList.add('hidden');

      // Mostrar el botón de "Agregar comentario"
      toggleButton.classList.remove('hidden');
    });
  });
});