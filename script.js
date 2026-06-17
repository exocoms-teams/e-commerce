/* ── CART (localStorage — shared with product.html) ── */
function getCart() {
  return JSON.parse(localStorage.getItem("lumiere_cart") || "[]");
}

function saveCart(cart) {
  localStorage.setItem("lumiere_cart", JSON.stringify(cart));
}

function addToCart(product, qty = 1, selectedShade = null) {
  const cart = getCart();
  const key = selectedShade ? `${product.id}-${selectedShade}` : `${product.id}`;
  const existing = cart.find(i => i.key === key);

  if (existing) {
    existing.qty += qty;
  } else {
    cart.push({
      key,
      id: product.id,
      name: product.name,
      category: product.category,
      price: product.price,
      img: product.img,
      shade: product.shade,
      icon: product.icon,
      shadeName: "",
      qty
    });
  }

  saveCart(cart);
  updateCartUI();
}

function removeFromCart(key) {
  saveCart(getCart().filter(i => i.key !== key));
  updateCartUI();
}

function changeQty(key, delta) {
  const cart = getCart();
  const item = cart.find(i => i.key === key);
  if (!item) return;
  item.qty += delta;
  if (item.qty <= 0) saveCart(cart.filter(i => i.key !== key));
  else saveCart(cart);
  updateCartUI();
}

function updateCartUI() {
  const cart = getCart();
  const totalItems = cart.reduce((s, i) => s + i.qty, 0);
  const totalPrice = cart.reduce((s, i) => s + i.price * i.qty, 0);

  const badge = document.getElementById("cart-count");
  badge.textContent = totalItems;
  badge.classList.toggle("visible", totalItems > 0);

  const headerCount = document.getElementById("cart-header-count");
  headerCount.textContent = totalItems > 0 ? `(${totalItems})` : "";

  const emptyEl  = document.getElementById("cart-empty");
  const itemsEl  = document.getElementById("cart-items");
  const footerEl = document.getElementById("cart-footer");

  if (cart.length === 0) {
    emptyEl.style.display  = "flex";
    itemsEl.style.display  = "none";
    footerEl.style.display = "none";
  } else {
    emptyEl.style.display  = "none";
    itemsEl.style.display  = "block";
    footerEl.style.display = "block";
  }

  itemsEl.innerHTML = cart.map(item => `
    <div class="cart-item">
      <div class="cart-item-img" style="background:${item.shade}">
        <img src="${item.img}" alt="${item.name}" onerror="this.style.display='none'">
      </div>
      <div class="cart-item-details">
        <span class="cart-item-category">${item.category}</span>
        <p class="cart-item-name">${item.name}</p>
        <p class="cart-item-price">$${item.price}</p>
        <div class="cart-item-controls">
          <button class="qty-btn" onclick="changeQty('${item.key}', -1)">−</button>
          <span class="qty-value">${item.qty}</span>
          <button class="qty-btn" onclick="changeQty('${item.key}', 1)">+</button>
        </div>
      </div>
      <button class="cart-item-remove" onclick="removeFromCart('${item.key}')">
        <i class="fa-solid fa-xmark"></i>
      </button>
    </div>
  `).join("");

  document.getElementById("cart-total").textContent = `$${totalPrice.toFixed(2)}`;
}

/* ── CART OPEN / CLOSE ── */
function openCart() {
  document.getElementById("cart-sidebar").classList.add("active");
  document.getElementById("cart-overlay").classList.add("active");
  document.body.style.overflow = "hidden";
}

function closeCart() {
  document.getElementById("cart-sidebar").classList.remove("active");
  document.getElementById("cart-overlay").classList.remove("active");
  document.body.style.overflow = "";
}

document.getElementById("cart-btn").addEventListener("click", openCart);
document.getElementById("cart-close").addEventListener("click", closeCart);
document.getElementById("cart-overlay").addEventListener("click", closeCart);
document.getElementById("cart-shop-link").addEventListener("click", closeCart);
document.querySelector(".checkout-btn").addEventListener("click", () => {
  alert("Thank you! Checkout coming soon.");
});

/* ── TOAST ── */
function showToast(msg) {
  const toast = document.getElementById("toast");
  document.getElementById("toast-msg").textContent = msg;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2800);
}

/* ── MOBILE MENU ── */
const menuIcon = document.querySelector("#menu-icon");
const navbar   = document.querySelector(".navbar");

menuIcon.onclick = () => {
  menuIcon.classList.toggle("fa-xmark");
  navbar.classList.toggle("active");
};

document.querySelectorAll(".navbar a").forEach(link => {
  link.onclick = () => {
    menuIcon.classList.remove("fa-xmark");
    navbar.classList.remove("active");
  };
});

/* ── RENDER PRODUCTS GRID ── */
function renderProducts(filter = "all") {
  const grid = document.getElementById("products-grid");
  grid.innerHTML = "";

  const filtered = filter === "all"
    ? products
    : products.filter(p => p.category === filter);

  filtered.forEach(product => {
    const card = document.createElement("div");
    card.className = "product-card";

    card.innerHTML = `
      <div class="product-img">
        <div class="swatch" style="background:${product.shade}">
          <img src="${product.img}" alt="${product.name}" onerror="this.style.display='none'">
          <i class="fa-solid ${product.icon}"></i>
        </div>
        <button class="add-to-bag-overlay" data-id="${product.id}">
          + Add to Bag
        </button>
      </div>
      <div class="product-info">
        <span class="product-category">${product.category}</span>
        <h3 class="product-name">${product.name}</h3>
        <p class="product-price">$${product.price}</p>
      </div>
    `;

    /* Click card → product page */
    card.addEventListener("click", () => {
      window.location.href = `product.html?id=${product.id}`;
    });

    /* Click Add to Bag → add without navigating */
    card.querySelector(".add-to-bag-overlay").addEventListener("click", e => {
      e.stopPropagation();
      addToCart(product);
      showToast(`${product.name} added to bag`);
      openCart();
    });

    grid.appendChild(card);
  });
}

/* ── FILTER BUTTONS ── */
document.querySelectorAll(".filter-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    renderProducts(btn.dataset.filter);
  });
});

/* ── CONTACT FORM ── */
document.addEventListener("DOMContentLoaded", () => {
  const form       = document.getElementById("contact-form");
  const successMsg = document.getElementById("form-success");

  if (form) {
    form.addEventListener("submit", e => {
      e.preventDefault();
      emailjs
        .sendForm("YOUR_SERVICE_ID", "YOUR_TEMPLATE_ID", form)
        .then(() => {
          successMsg.style.display = "block";
          form.reset();
          setTimeout(() => { successMsg.style.display = "none"; }, 3000);
        })
        .catch(err => console.log("EmailJS error:", err));
    });
  }

  renderProducts();
  updateCartUI();
});
