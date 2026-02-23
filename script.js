const programGrid = document.querySelector('#programGrid');

if (programGrid) {
  const headers = Array.from(programGrid.querySelectorAll('.program-card__header'));

  const closeCard = (header) => {
    const card = header.closest('.program-card');
    const content = header.nextElementSibling;

    if (!card || !content) {
      return;
    }

    header.setAttribute('aria-expanded', 'false');
    card.classList.remove('is-open');
    content.style.maxHeight = '0px';
    content.style.opacity = '0';
  };

  const openCard = (header) => {
    const card = header.closest('.program-card');
    const content = header.nextElementSibling;

    if (!card || !content) {
      return;
    }

    header.setAttribute('aria-expanded', 'true');
    card.classList.add('is-open');
    content.style.maxHeight = `${content.scrollHeight}px`;
    content.style.opacity = '1';
  };

  headers.forEach((header) => {
    const content = header.nextElementSibling;

    if (content) {
      content.hidden = false;
      content.style.maxHeight = '0px';
      content.style.opacity = '0';
    }

    header.addEventListener('click', () => {
      const isExpanded = header.getAttribute('aria-expanded') === 'true';

      headers.forEach((item) => {
        if (item !== header) {
          closeCard(item);
        }
      });

      if (isExpanded) {
        closeCard(header);
      } else {
        openCard(header);
      }
    });
  });

  window.addEventListener('resize', () => {
    headers.forEach((header) => {
      if (header.getAttribute('aria-expanded') === 'true') {
        const content = header.nextElementSibling;

        if (content) {
          content.style.maxHeight = `${content.scrollHeight}px`;
        }
      }
    });
  });
}
