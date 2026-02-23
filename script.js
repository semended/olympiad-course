document.addEventListener("DOMContentLoaded", function () {

  const programGrid = document.querySelector("#programGrid");
  if (!programGrid) return;

  const cards = programGrid.querySelectorAll(".program-card");

  cards.forEach((card) => {
    const header = card.querySelector(".program-header");
    const content = card.querySelector(".program-content");

    if (!header || !content) return;

    // начальное состояние
    content.style.maxHeight = "0px";
    content.style.overflow = "hidden";

    header.addEventListener("click", function () {
      const isOpen = card.classList.contains("is-open");

      if (isOpen) {
        // закрываем
        content.style.maxHeight = content.scrollHeight + "px";

        requestAnimationFrame(() => {
          content.style.maxHeight = "0px";
        });

        card.classList.remove("is-open");
      } else {
        // открываем
        card.classList.add("is-open");
        content.style.maxHeight = content.scrollHeight + "px";
      }
    });
  });

  // пересчёт высоты при resize
  window.addEventListener("resize", function () {
    const openCards = programGrid.querySelectorAll(".program-card.is-open");
    openCards.forEach((card) => {
      const content = card.querySelector(".program-content");
      if (content) {
        content.style.maxHeight = content.scrollHeight + "px";
      }
    });
  });

});
