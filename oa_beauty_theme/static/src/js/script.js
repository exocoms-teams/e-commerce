// Global Application State & Shared Components Handler
document.addEventListener("DOMContentLoaded", () => {
  initGlobalNavigation();
  initCartSystem();
  initNewsletterForm();
  markActivePage();
});

// Navigation Bar Animations & Mobile Toggle Links
function initGlobalNavigation() {
  const header = document.querySelector(".header");
  const menuIcon = document.getElementById("menu-icon");
  const navbar = document.querySelector(".navbar");

  window.addEventListener("scroll", () => {
    if (window.scrollY > 50) {
      header.classList.add("scrolled");
    } else {
      header.classList.remove("scrolled");
    }
  });

  if (menuIcon && navbar) {
    menuIcon.addEventListener("click", () => {
      menuIcon.classList.toggle("fa-xmark");
      navbar.classList.toggle("active");
    });
  }
}

// Global Sync Pipeline for Shopping Cart Sidebar
function initCartSystem() {
  const cartBtn = document.getElementById("cart-btn");
  const cartClose = document.getElementById("cart-close");
  const cartOverlay = document.getElementById("cart-overlay");
  const cartSidebar = document.getElementById("cart-sidebar");

  if (cartBtn && cartSidebar && cartOverlay) {
    cartBtn.addEventListener("click", () => {
      cartSidebar.classList.add("active");
      cartOverlay.classList.add("active");
      document.body.style.overflow = "hidden";
    });

    const closeCartFn = () => {
      cartSidebar.classList.remove("active");
      cartOverlay.classList.remove("active");
      document.body.style.overflow = "";
    };

    if (cartClose) cartClose.addEventListener("click", closeCartFn);
    cartOverlay.addEventListener("click", closeCartFn);
  }

  updateCartBadge();
  renderSidebarCart();
}

// Low-Level LocalStorage Reactive Handlers
function getCartData() {
  return JSON.parse(localStorage.getItem("lumiere_cart_items") || "[]");
}

function saveCartData(cart) {
  localStorage.setItem("lumiere_cart_items", JSON.stringify(cart));
  updateCartBadge();
  renderSidebarCart();
  
  // Custom dispatch for page synchronization
  window.dispatchEvent(new Event("cartUpdated"));
}

function addProductToCart(productId, quantity = 1, selectedShadeName = null) {
  const catalogProduct = products.find(p => p.id === parseInt(productId));
  if (!catalogProduct) return;

  let cart = getCartData();
  const compositeKey = selectedShadeName ? `${productId}_${selectedShadeName}` : `${productId}`;
  const duplicateIndex = cart.findIndex(item => item.compositeKey === compositeKey);

  if (duplicateIndex > -1) {
    cart[duplicateIndex].quantity += quantity;
  } else {
    cart.push({
      compositeKey: compositeKey,
      id: catalogProduct.id,
      name: catalogProduct.name,
      category: catalogProduct.category,
      price: catalogProduct.price,
      img: catalogProduct.img,
      shade: selectedShadeName,
      quantity: quantity
    });
  }

  saveCartData(cart);
  triggerToastNotification(`${catalogProduct.name} added to your bag`);
}

function changeItemQuantity(compositeKey, balanceDelta) {
  let cart = getCartData();
  const index = cart.findIndex(item => item.compositeKey === compositeKey);
  if (index === -1) return;

  cart[index].quantity += balanceDelta;
  if (cart[index].quantity <= 0) {
    cart.splice(index, 1);
  }
  saveCartData(cart);
}

function deleteItemFromCart(compositeKey) {
  let cart = getCartData();
  cart = cart.filter(item => item.compositeKey !== compositeKey);
  saveCartData(cart);
}

function updateCartBadge() {
  const cart = getCartData();
  const totalCount = cart.reduce((acc, current) => acc + current.quantity, 0);
  const elements = document.querySelectorAll(".cart-count");
  
  elements.forEach(badge => {
    badge.textContent = totalCount;
    if (totalCount > 0) {
      badge.classList.add("visible");
    } else {
      badge.classList.remove("visible");
    }
  });
}

function renderSidebarCart() {
  const container = document.getElementById("sidebar-cart-list");
  const emptyContainer = document.getElementById("sidebar-cart-empty");
  const footerContainer = document.getElementById("sidebar-cart-footer");
  const totalLabel = document.getElementById("sidebar-cart-total");

  if (!container) return;

  const cart = getCartData();

  if (cart.length === 0) {
    emptyContainer.style.display = "flex";
    container.style.display = "none";
    if (footerContainer) footerContainer.style.display = "none";
    return;
  }

  emptyContainer.style.display = "none";
  container.style.display = "flex";
  if (footerContainer) footerContainer.style.display = "block";

  container.innerHTML = cart.map(item => {
    const shadeData = item.shade ? `<div class="cart-item-shade"><span class="shade-dot" style="background-color: ${getShadeHex(item.id, item.shade)}"></span>${item.shade}</div>` : "";
    return `
      <div class="cart-item">
        <div class="cart-item-img">
          <img src="${item.img}" alt="${item.name}">
        </div>
        <div class="cart-item-details">
          <h4>${item.name}</h4>
          ${shadeData}
          <div class="cart-item-price">$${item.price}</div>
          <div class="cart-item-qty-ctrl">
            <button onclick="changeItemQuantity('${item.compositeKey}', -1)">−</button>
            <span>${item.quantity}</span>
            <button onclick="changeItemQuantity('${item.compositeKey}', 1)">+</button>
          </div>
        </div>
        <button class="cart-item-remove" onclick="deleteItemFromCart('${item.compositeKey}')">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>
    `;
  }).join("");

  const aggregatePrice = cart.reduce((acc, current) => acc + (current.price * current.quantity), 0);
  if (totalLabel) totalLabel.textContent = `$${aggregatePrice.toFixed(2)}`;
}

function getShadeHex(productId, shadeName) {
  const prod = products.find(p => p.id === productId);
  if (!prod || !prod.shades) return "#fff";
  const shadeObj = prod.shades.find(s => s.name === shadeName);
  return shadeObj ? shadeObj.color : "#fff";
}

// Global Floating Notification Alert System
function triggerToastNotification(textMessage) {
  let element = document.getElementById("toast");
  if (!element) {
    element = document.createElement("div");
    element.id = "toast";
    element.className = "toast";
    document.body.appendChild(element);
  }
  element.innerHTML = `<i class="fa-solid fa-check"></i> <span>${textMessage}</span>`;
  element.classList.add("show");
  setTimeout(() => {
    element.classList.remove("show");
  }, 3000);
}

// Newsletter Email Collection Simulator
function initNewsletterForm() {
  const forms = document.querySelectorAll(".newsletter-form");
  forms.forEach(form => {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const input = form.querySelector("input[type='email']");
      if (input && input.value.trim() !== "") {
        triggerToastNotification("Welcome to the inner circle of LUMIÈRE");
        input.value = "";
      }
    });
  });
}

// Utility Navigation Active Route Highlighting
function markActivePage() {
  const activePath = window.location.pathname.split("/").pop();
  const queryLinks = document.querySelectorAll(".navbar a");
  queryLinks.forEach(link => {
    const reference = link.getAttribute("href");
    if (reference === activePath || (activePath === "" && reference === "index.html")) {
      link.classList.add("active");
    } else {
      link.classList.remove("active");
    }
  });
}