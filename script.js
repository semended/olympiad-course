document.addEventListener("DOMContentLoaded", function () {

  const updateOpenHeights = () => {
    document.querySelectorAll('.program-card.is-open').forEach((card) => {
      const content = card.querySelector('.program-content');
      if (content) {
        content.style.maxHeight = content.scrollHeight + "px";
      }
    });
  };

  const cards = document.querySelectorAll('.program-card');

  cards.forEach((card) => {
    const header = card.querySelector('.program-header');
    const content = card.querySelector('.program-content');

    if (!header || !content) return;

    // стартовое состояние
    content.style.maxHeight = "0px";

    header.addEventListener('click', () => {
      const isOpen = card.classList.contains('is-open');

      if (isOpen) {
        content.style.maxHeight = null;
        card.classList.remove('is-open');
      } else {
        content.style.maxHeight = content.scrollHeight + "px";
        card.classList.add('is-open');
      }

      requestAnimationFrame(updateOpenHeights);
    });
  });

  window.addEventListener('resize', updateOpenHeights);

});
