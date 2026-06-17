/* ── CART (localStorage) ── */
function getCart() {
  return JSON.parse(localStorage.getItem("lumiere_cart") || "[]");
}

function saveCart(cart) {
  localStorage.setItem("lumiere_cart", JSON.stringify(cart));
}

function addToCart(product, qty, selectedShade) {
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
      shade: selectedShade || product.shade,
      icon: product.icon,
      shadeName: selectedShade
        ? (product.shades.find(s => s.color === selectedShade) || {}).name || ""
        : "",
      qty
    });
  }

  saveCart(cart);
  updateCartUI();
}

function removeFromCart(key) {
  const cart = getCart().filter(i => i.key !== key);
  saveCart(cart);
  updateCartUI();
}

function changeQty(key, delta) {
  const cart = getCart();
  const item = cart.find(i => i.key === key);
  if (!item) return;
  item.qty += delta;
  if (item.qty <= 0) {
    saveCart(cart.filter(i => i.key !== key));
  } else {
    saveCart(cart);
  }
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
        <img src="${item.img}" alt="${item.name}"
             onerror="this.style.display='none'">
      </div>
      <div class="cart-item-details">
        <span class="cart-item-category">${item.category}</span>
        <p class="cart-item-name">${item.name}${item.shadeName ? ` <em style="font-size:1.1rem;color:var(--text-muted)">— ${item.shadeName}</em>` : ""}</p>
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

/* ── STAR RATING ── */
function renderStars(rating) {
  let stars = "";
  for (let i = 1; i <= 5; i++) {
    if (i <= Math.floor(rating)) {
      stars += '<i class="fa-solid fa-star"></i>';
    } else if (i - rating < 1) {
      stars += '<i class="fa-solid fa-star-half-stroke"></i>';
    } else {
      stars += '<i class="fa-regular fa-star"></i>';
    }
  }
  return stars;
}

/* ── RENDER RELATED PRODUCTS ── */
function renderRelated(currentProduct) {
  const grid = document.getElementById("related-grid");
  let related = products.filter(
    p => p.category === currentProduct.category && p.id !== currentProduct.id
  );

  if (related.length < 3) {
    const others = products.filter(
      p => p.id !== currentProduct.id && !related.includes(p)
    );
    related = [...related, ...others].slice(0, 3);
  } else {
    related = related.slice(0, 3);
  }

  grid.innerHTML = related.map(p => `
    <div class="product-card" onclick="window.location='product.html?id=${p.id}'">
      <div class="product-img">
        <div class="swatch" style="background:${p.shade}">
          <img src="${p.img}" alt="${p.name}" onerror="this.style.display='none'">
          <i class="fa-solid ${p.icon}"></i>
        </div>
        <button class="add-to-bag-overlay" onclick="event.stopPropagation(); quickAdd(${p.id})">
          + Add to Bag
        </button>
      </div>
      <div class="product-info">
        <span class="product-category">${p.category}</span>
        <h3 class="product-name">${p.name}</h3>
        <p class="product-price">$${p.price}</p>
      </div>
    </div>
  `).join("");
}

function quickAdd(id) {
  const product = products.find(p => p.id === id);
  addToCart(product, 1, null);
  showToast(`${product.name} added to bag`);
  openCart();
}

/* ── PRODUCT PAGE INIT ── */
document.addEventListener("DOMContentLoaded", () => {
  const params = new URLSearchParams(window.location.search);
  const id = parseInt(params.get("id"));
  const product = products.find(p => p.id === id);

  if (!product) {
    document.querySelector(".product-page").innerHTML =
      `<p style="text-align:center;padding:10rem;font-size:2rem;color:var(--text-muted)">
        Product not found. <a href="index.html#shop" style="color:var(--main-color)">Back to Shop</a>
      </p>`;
    return;
  }

  /* Page title */
  document.title = `LUMIÈRE — ${product.name}`;

  /* Breadcrumb */
  document.getElementById("bc-category").textContent = product.category;
  document.getElementById("bc-name").textContent = product.name;

  /* Main image */
  const mainImg = document.getElementById("main-img");
  mainImg.style.background = product.shade;
  mainImg.innerHTML = `
    <img src="${product.img}" alt="${product.name}" onerror="this.style.display='none'">
    <i class="fa-solid ${product.icon} img-icon"></i>
  `;

  /* Thumbnails (decorative — same product, slightly varied opacity) */
  const thumbsEl = document.getElementById("img-thumbs");
  for (let i = 0; i < 3; i++) {
    const t = document.createElement("div");
    t.className = "thumb" + (i === 0 ? " active" : "");
    t.style.background = product.shade;
    t.style.opacity = 1 - i * 0.2;
    t.innerHTML = `<img src="${product.img}" alt="" onerror="this.style.display='none'">`;
    t.addEventListener("click", () => {
      document.querySelectorAll(".thumb").forEach(el => el.classList.remove("active"));
      t.classList.add("active");
    });
    thumbsEl.appendChild(t);
  }

  /* Category & name */
  document.getElementById("detail-category").textContent = product.category;
  document.getElementById("detail-name").textContent = product.name;

  /* Rating */
  document.getElementById("detail-rating").innerHTML = `
    <div class="stars">${renderStars(product.rating)}</div>
    <span class="rating-num">${product.rating}</span>
    <span class="rating-count">(${product.reviews} reviews)</span>
  `;

  /* Price */
  document.getElementById("detail-price").textContent = `$${product.price}`;

  /* Description */
  document.getElementById("detail-desc").textContent = product.description;

  /* Specs */
  document.getElementById("detail-specs").innerHTML = `
    <div class="spec-item"><span class="spec-label">Type</span><span class="spec-value">${product.type}</span></div>
    <div class="spec-item"><span class="spec-label">Finish</span><span class="spec-value">${product.finish}</span></div>
    <div class="spec-item"><span class="spec-label">Best For</span><span class="spec-value">${product.bestFor}</span></div>
  `;

  /* Ingredients */
  document.getElementById("detail-ingredients").innerHTML = `
    <span class="ing-label">Key Ingredients</span>
    <p class="ing-value">${product.keyIngredients}</p>
  `;

  /* Shade picker */
  let selectedShade = product.shades.length > 0 ? product.shades[0].color : null;
  const shadeEl = document.getElementById("shade-picker");

  if (product.shades.length > 0) {
    const shadeNameEl = document.createElement("div");
    shadeNameEl.className = "shade-label";
    shadeNameEl.innerHTML = `Shade: <strong id="shade-name-display">${product.shades[0].name}</strong>`;

    const shadeCircles = document.createElement("div");
    shadeCircles.className = "shade-circles";

    product.shades.forEach((s, i) => {
      const circle = document.createElement("button");
      circle.className = "shade-circle" + (i === 0 ? " active" : "");
      circle.style.background = s.color;
      circle.title = s.name;
      circle.addEventListener("click", () => {
        document.querySelectorAll(".shade-circle").forEach(c => c.classList.remove("active"));
        circle.classList.add("active");
        selectedShade = s.color;
        document.getElementById("shade-name-display").textContent = s.name;
      });
      shadeCircles.appendChild(circle);
    });

    shadeEl.appendChild(shadeNameEl);
    shadeEl.appendChild(shadeCircles);
  } else {
    shadeEl.style.display = "none";
  }

  /* Quantity */
  let qty = 1;
  const qtyDisplay = document.getElementById("qty-value");

  document.getElementById("qty-minus").addEventListener("click", () => {
    if (qty > 1) { qty--; qtyDisplay.textContent = qty; }
  });

  document.getElementById("qty-plus").addEventListener("click", () => {
    qty++;
    qtyDisplay.textContent = qty;
  });

  /* Add to Bag */
  document.getElementById("add-bag-btn").addEventListener("click", () => {
    addToCart(product, qty, selectedShade);
    showToast(`${product.name} added to bag`);
    openCart();
  });

  /* Wishlist (decorative) */
  document.getElementById("wishlist-btn").addEventListener("click", function () {
    this.classList.toggle("wished");
    const icon = this.querySelector("i");
    icon.classList.toggle("fa-regular");
    icon.classList.toggle("fa-solid");
    showToast(this.classList.contains("wished") ? "Added to wishlist ♡" : "Removed from wishlist");
  });

  /* Related products */
  renderRelated(product);

  /* Load cart state */
  updateCartUI();
});
