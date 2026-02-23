document.addEventListener("DOMContentLoaded", function () {

  const cards = document.querySelectorAll(".program-card");

  cards.forEach((card) => {
    const header = card.querySelector(".program-header");
    const content = card.querySelector(".program-content");

    header.addEventListener("click", function () {
      const isOpen = card.classList.contains("is-open");

      if (isOpen) {
        card.classList.remove("is-open");
        content.style.maxHeight = null;
      } else {
        card.classList.add("is-open");
        content.style.maxHeight = content.scrollHeight + "px";
      }
    });
  });

});
