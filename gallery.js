const items = Array.from(document.querySelectorAll('.gallery-item'));
const lightbox = document.getElementById('gallery-lightbox');
const lightboxImage = document.getElementById('lightbox-image');
const lightboxCaption = document.getElementById('lightbox-caption');
const closeButton = document.getElementById('lightbox-close');
const prevButton = document.getElementById('lightbox-prev');
const nextButton = document.getElementById('lightbox-next');
const toolbarPrev = document.getElementById('gallery-prev');
const toolbarNext = document.getElementById('gallery-next');

let currentIndex = 0;

const render = index => {
  if (!items.length) {
    return;
  }

  currentIndex = (index + items.length) % items.length;
  const item = items[currentIndex];
  const img = item.querySelector('img');
  const caption = item.closest('figure')?.querySelector('figcaption')?.textContent || '';
  lightboxImage.src = item.getAttribute('href') || img?.src || '';
  lightboxImage.alt = img?.alt || 'Gallery image';
  lightboxCaption.textContent = caption;
};

const openLightbox = index => {
  render(index);
  lightbox.hidden = false;
  document.body.style.overflow = 'hidden';
};

const closeLightbox = () => {
  lightbox.hidden = true;
  document.body.style.overflow = '';
};

window.__closeGallery = closeLightbox;

items.forEach((item, index) => {
  item.addEventListener('click', event => {
    event.preventDefault();
    openLightbox(index);
  });
});

if (toolbarPrev) {
  toolbarPrev.addEventListener('click', () => openLightbox(currentIndex - 1));
}
if (toolbarNext) {
  toolbarNext.addEventListener('click', () => openLightbox(currentIndex + 1));
}

if (prevButton) {
  prevButton.addEventListener('click', () => render(currentIndex - 1));
}
if (nextButton) {
  nextButton.addEventListener('click', () => render(currentIndex + 1));
}
if (closeButton) {
  closeButton.addEventListener('click', closeLightbox);
}

lightbox?.addEventListener('click', event => {
  if (event.target === lightbox) {
    closeLightbox();
  }
});

document.addEventListener('keydown', event => {
  if (lightbox?.hidden) {
    return;
  }

  if (event.key === 'Escape') {
    closeLightbox();
  }
  if (event.key === 'ArrowRight') {
    render(currentIndex + 1);
  }
  if (event.key === 'ArrowLeft') {
    render(currentIndex - 1);
  }
});
