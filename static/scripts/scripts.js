//responsive navbar
const toggle = document.getElementById("menu-toggle");
const navLinks = document.getElementById("nav-links");

toggle.addEventListener("click", () => {
  toggle.classList.toggle("open");
  navLinks.classList.toggle("show");
});


//filters for product category
document.addEventListener('DOMContentLoaded', () => {
  const filterButtons = document.querySelectorAll('.product-filters button');
  const productCards = document.querySelectorAll('.product-card');

  filterButtons.forEach(button => {
    button.addEventListener('click', () => {
      const filter = button.getAttribute('data-filter');

      productCards.forEach(card => {
        const category = card.getAttribute('data-category');
        if (filter === 'all' || category === filter) {
          card.style.display = 'block';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });
});


// dynamic orders
document.addEventListener('DOMContentLoaded', () => {
  const minusBtn = document.querySelector('.quantity-control button:first-child');
  const plusBtn = document.querySelector('.quantity-control button:last-child');
  const quantityInput = document.getElementById('quantity');
  const quantityDisplay = document.querySelector('.order-summary div:nth-child(3) span:last-child');
  const totalDisplay = document.querySelector('.order-summary .total .total-amount');

  // Get unit price from the visible product-price element
  const priceText = document.querySelector('.product-price').textContent; // e.g. "150 درهم"
  const unitPrice = parseFloat(priceText.replace(/[^\d.]/g, '')); // Extract 150

  function updateSummary() {
    const quantity = parseInt(quantityInput.value);
    const total = quantity * unitPrice;
    quantityDisplay.textContent = quantity;
    totalDisplay.textContent = `${total} درهم`;
  }

  minusBtn.addEventListener('click', () => {
    let currentValue = parseInt(quantityInput.value);
    if (currentValue > 1) {
      quantityInput.value = currentValue - 1;
      updateSummary();
    }
  });

  plusBtn.addEventListener('click', () => {
    let currentValue = parseInt(quantityInput.value);
    quantityInput.value = currentValue + 1;
    updateSummary();
  });

  quantityInput.addEventListener('input', () => {
    if (quantityInput.value < 1) quantityInput.value = 1;
    updateSummary();
  });

  updateSummary(); // Initial call
});


//flash messages
  setTimeout(() => {
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach((msg) => {
      msg.style.opacity = '0';
      setTimeout(() => msg.remove(), 500); // Remove after fade
    });
  }, 4000); // Show for 4 seconds