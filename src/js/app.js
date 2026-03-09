/* ============================================
   PeptideSource — Main Application JavaScript
   SPA Router, Cart, Chatbot, Animations
   ============================================ */

// ==========================================
// DATA
// ==========================================
const PRODUCTS = [
  {
    id: "bpc-157-capsules", name: "BPC-157 Oral Capsules", category: "recovery", subcategory: "gut-health",
    price: 89.99, originalPrice: 129.99, rating: 4.9, reviews: 2847, badge: "Best Seller", stock: 23,
    description: "Pharmaceutical-grade BPC-157 body protection compound in easy-to-take capsule form. Supports gut health, tissue repair, and overall recovery.",
    benefits: ["Gut Health Support", "Tissue Recovery", "Joint Comfort", "Anti-Inflammatory"],
    dosage: "500mcg per capsule, 60 capsules per bottle",
    ingredients: "BPC-157 (Body Protection Compound), Microcrystalline Cellulose, Vegetable Capsule (HPMC)",
    tags: ["recovery", "gut-health", "bestseller", "anti-aging"], featured: true, trending: true
  },
  {
    id: "ghk-cu-serum", name: "GHK-Cu Copper Peptide Serum", category: "skin", subcategory: "anti-aging",
    price: 74.99, originalPrice: 109.99, rating: 4.8, reviews: 1923, badge: "Trending", stock: 15,
    description: "Clinically-studied GHK-Cu copper peptide serum for visible skin rejuvenation, collagen stimulation, and cellular renewal.",
    benefits: ["Skin Rejuvenation", "Collagen Boost", "Wrinkle Reduction", "Wound Healing"],
    dosage: "Apply 3-5 drops twice daily to clean skin",
    ingredients: "GHK-Cu (Copper Tripeptide-1), Hyaluronic Acid, Niacinamide, Aloe Vera Extract",
    tags: ["skin", "anti-aging", "trending", "collagen"], featured: true, trending: true
  },
  {
    id: "collagen-peptides-powder", name: "Hydrolyzed Collagen Peptides", category: "collagen", subcategory: "beauty",
    price: 49.99, originalPrice: 69.99, rating: 4.7, reviews: 5621, badge: "Most Popular", stock: 142,
    description: "Multi-source hydrolyzed collagen peptides (Type I, II, III) from grass-fed bovine. Unflavored, dissolves instantly in any beverage.",
    benefits: ["Hair & Nail Growth", "Skin Elasticity", "Joint Support", "Gut Lining Repair"],
    dosage: "1 scoop (10g) daily mixed with any beverage",
    ingredients: "Hydrolyzed Bovine Collagen Peptides (Type I & III), Hydrolyzed Chicken Collagen (Type II)",
    tags: ["collagen", "beauty", "joints", "bestseller"], featured: true, trending: false
  },
  {
    id: "tb500-capsules", name: "TB-500 Recovery Complex", category: "recovery", subcategory: "athletic",
    price: 94.99, originalPrice: 139.99, rating: 4.8, reviews: 1456, badge: "Athletes' Choice", stock: 31,
    description: "Advanced TB-500 thymosin beta-4 complex for accelerated muscle recovery, flexibility, and athletic performance support.",
    benefits: ["Muscle Recovery", "Flexibility", "Athletic Performance", "Injury Support"],
    dosage: "750mcg per capsule, 30 capsules per bottle",
    ingredients: "Thymosin Beta-4 Fragment, L-Arginine, BioPerine Black Pepper Extract, Veggie Capsule",
    tags: ["recovery", "athletic", "performance", "muscle"], featured: true, trending: true
  },
  {
    id: "aod-9604-caps", name: "AOD-9604 Metabolic Optimizer", category: "weight", subcategory: "metabolism",
    price: 79.99, originalPrice: 119.99, rating: 4.6, reviews: 987, badge: "Hot", stock: 8,
    description: "AOD-9604, the modified growth hormone fragment, formulated for metabolic optimization and healthy body composition support.",
    benefits: ["Metabolic Support", "Body Composition", "Fat Metabolism", "Energy Levels"],
    dosage: "300mcg per capsule, 60 capsules per bottle",
    ingredients: "AOD-9604 (HGH Fragment 176-191), Chromium Picolinate, Green Tea Extract, Veggie Capsule",
    tags: ["weight", "metabolism", "energy", "trending"], featured: false, trending: true
  },
  {
    id: "ss31-mito-complex", name: "SS-31 Mitochondrial Complex", category: "longevity", subcategory: "cellular",
    price: 109.99, originalPrice: 159.99, rating: 4.9, reviews: 634, badge: "Premium", stock: 12,
    description: "Next-generation SS-31 (Elamipretide) inspired mitochondrial support complex for cellular energy, longevity, and mitochondrial health.",
    benefits: ["Mitochondrial Support", "Cellular Energy", "Longevity", "Oxidative Defense"],
    dosage: "2 capsules daily with food",
    ingredients: "SS-31 Analog Complex, CoQ10, PQQ, NAD+ Precursor, Veggie Capsule",
    tags: ["longevity", "cellular", "premium", "anti-aging"], featured: true, trending: false
  },
  {
    id: "dihexa-nootropic", name: "Dihexa Cognitive Peptide", category: "cognitive", subcategory: "nootropic",
    price: 99.99, originalPrice: 149.99, rating: 4.7, reviews: 823, badge: "Brain Boost", stock: 19,
    description: "Dihexa-inspired cognitive peptide complex for enhanced neuroplasticity, memory formation, and mental clarity.",
    benefits: ["Neuroplasticity", "Memory Enhancement", "Mental Clarity", "Focus"],
    dosage: "1 capsule daily, cycle 5 days on / 2 days off",
    ingredients: "Dihexa Peptide Analog, Lion's Mane Extract, Phosphatidylserine, Bacopa Monnieri",
    tags: ["cognitive", "nootropic", "focus", "memory"], featured: false, trending: true
  },
  {
    id: "epithalon-longevity", name: "Epithalon Telomere Support", category: "longevity", subcategory: "anti-aging",
    price: 119.99, originalPrice: 179.99, rating: 4.8, reviews: 445, badge: "Premium", stock: 7,
    description: "Epithalon-inspired tetrapeptide complex targeting telomerase activation for cellular longevity and anti-aging support.",
    benefits: ["Telomere Support", "Cellular Longevity", "Sleep Quality", "Immune Function"],
    dosage: "1 capsule before bed, 20-day cycles",
    ingredients: "Epithalon Analog (Ala-Glu-Asp-Gly), Astragalus Root Extract, Resveratrol, Melatonin",
    tags: ["longevity", "anti-aging", "telomeres", "premium"], featured: true, trending: false
  },
  {
    id: "ll37-immune", name: "LL-37 Immune Defense Peptide", category: "immune", subcategory: "defense",
    price: 84.99, originalPrice: 124.99, rating: 4.6, reviews: 712, badge: "Shield", stock: 34,
    description: "LL-37 cathelicidin-inspired antimicrobial peptide complex for comprehensive immune system defense and biofilm disruption.",
    benefits: ["Immune Defense", "Antimicrobial", "Biofilm Disruption", "Inflammation Balance"],
    dosage: "1 capsule twice daily with meals",
    ingredients: "LL-37 Peptide Analog, Lactoferrin, Beta-Glucan, Vitamin D3, Zinc",
    tags: ["immune", "defense", "antimicrobial", "health"], featured: false, trending: false
  },
  {
    id: "foxo4-dri-senolytic", name: "FOXO4-DRI Senolytic Complex", category: "longevity", subcategory: "senolytic",
    price: 134.99, originalPrice: 199.99, rating: 4.9, reviews: 298, badge: "Cutting Edge", stock: 5,
    description: "Breakthrough FOXO4-DRI inspired senolytic peptide complex targeting senescent cells for cellular rejuvenation and healthspan extension.",
    benefits: ["Senolytic Action", "Cellular Rejuvenation", "Healthspan", "Tissue Renewal"],
    dosage: "2 capsules, 3 consecutive days per month",
    ingredients: "FOXO4-DRI Peptide Analog, Fisetin, Quercetin, Dasatinib Analog, Veggie Capsule",
    tags: ["longevity", "senolytic", "premium", "cutting-edge"], featured: true, trending: true
  },
  {
    id: "mots-c-energy", name: "MOTS-c Metabolic Peptide", category: "weight", subcategory: "energy",
    price: 89.99, originalPrice: 129.99, rating: 4.7, reviews: 567, badge: "Energy+", stock: 28,
    description: "Mitochondrial-derived MOTS-c peptide complex for metabolic activation, exercise mimetic benefits, and energy optimization.",
    benefits: ["Metabolic Activation", "Exercise Mimetic", "Energy Production", "Insulin Sensitivity"],
    dosage: "1 capsule daily with breakfast",
    ingredients: "MOTS-c Peptide Analog, Berberine, Alpha-Lipoic Acid, Chromium, Veggie Capsule",
    tags: ["weight", "energy", "metabolism", "performance"], featured: false, trending: true
  },
  {
    id: "pentadecapeptide-stack", name: "The Pentadecapeptide Stack", category: "recovery", subcategory: "comprehensive",
    price: 149.99, originalPrice: 219.99, rating: 4.9, reviews: 1834, badge: "Ultimate", stock: 11,
    description: "Our flagship comprehensive peptide stack combining BPC-157, KPV, and Larazotide for the ultimate gut-body recovery protocol.",
    benefits: ["Complete Recovery", "Gut Restoration", "Systemic Healing", "Peak Performance"],
    dosage: "2 capsules morning, 1 capsule evening",
    ingredients: "BPC-157, KPV Tripeptide, Larazotide Acetate, L-Glutamine, Zinc Carnosine",
    tags: ["recovery", "stack", "premium", "comprehensive", "bestseller"], featured: true, trending: true
  }
];

const BLOG_POSTS = [
  { id: "peptide-revolution-2026", title: "The Peptide Revolution: Why 2026 Is the Year of Peptide Supplements", excerpt: "From biohackers to mainstream wellness, peptides have exploded onto the scene. Here's the science behind the trend.", author: "Dr. Sarah Chen", date: "2026-03-01", readTime: "8 min", category: "Science" },
  { id: "bpc157-complete-guide", title: "BPC-157: The Complete Guide to the Body Protection Compound", excerpt: "Everything you need to know about BPC-157 — the gut-healing, tissue-repairing peptide everyone's talking about.", author: "Dr. Marcus Webb", date: "2026-02-22", readTime: "12 min", category: "Education" },
  { id: "collagen-peptides-myths", title: "5 Collagen Peptide Myths Debunked by Science", excerpt: "Separating fact from fiction: what the latest clinical trials actually say about collagen peptide supplementation.", author: "Dr. Lisa Park", date: "2026-02-15", readTime: "6 min", category: "Myth Busting" },
  { id: "peptides-vs-sarms", title: "Peptides vs SARMs: Understanding the Difference", excerpt: "Why peptide supplements are the safer, legal, and more effective alternative to SARMs for performance and recovery.", author: "Dr. James Rivera", date: "2026-02-08", readTime: "10 min", category: "Comparison" },
  { id: "longevity-peptides-guide", title: "The Longevity Peptide Protocol: Epithalon, FOXO4-DRI & Beyond", excerpt: "How cutting-edge peptides are being used in anti-aging protocols to extend healthspan.", author: "Dr. Sarah Chen", date: "2026-01-30", readTime: "15 min", category: "Longevity" },
  { id: "peptide-stacking-101", title: "Peptide Stacking 101: How to Combine Peptides Safely", excerpt: "A beginner-friendly guide to combining peptide supplements for synergistic benefits.", author: "Dr. Marcus Webb", date: "2026-01-22", readTime: "9 min", category: "Education" }
];

const REVIEWS_DATA = [
  { name: "Michael T.", rating: 5, verified: true, text: "BPC-157 completely changed my gut health. After years of digestive issues, I noticed improvement within the first week. Three months in and I feel like a new person.", product: "BPC-157 Oral Capsules", date: "2 days ago" },
  { name: "Sarah K.", rating: 5, verified: true, text: "The GHK-Cu serum is incredible. My skin texture has improved dramatically — fine lines are visibly reduced. Friends keep asking what I'm doing differently!", product: "GHK-Cu Copper Peptide Serum", date: "5 days ago" },
  { name: "James R.", rating: 5, verified: true, text: "As a competitive CrossFitter, recovery is everything. TB-500 has noticeably reduced my recovery time between sessions. PR'd my clean & jerk last week.", product: "TB-500 Recovery Complex", date: "1 week ago" },
  { name: "Dr. Emily W.", rating: 5, verified: true, text: "As a physician, I'm very particular about supplement quality. PeptideSource's COAs and transparency are unmatched. I recommend them to my patients.", product: "Hydrolyzed Collagen Peptides", date: "1 week ago" },
  { name: "David L.", rating: 4, verified: true, text: "The Pentadecapeptide Stack is the real deal. Gut issues resolved, energy is up, and my joint pain has decreased significantly. Worth every penny.", product: "The Pentadecapeptide Stack", date: "2 weeks ago" },
  { name: "Amanda C.", rating: 5, verified: true, text: "I was skeptical about peptide supplements but the collagen peptides have made a visible difference in my hair and nails. My hairdresser even noticed!", product: "Hydrolyzed Collagen Peptides", date: "2 weeks ago" },
  { name: "Robert M.", rating: 5, verified: true, text: "Epithalon has improved my sleep quality tremendously. I'm sleeping deeper and waking up more refreshed. Also noticed my immune system seems stronger.", product: "Epithalon Telomere Support", date: "3 weeks ago" },
  { name: "Lisa P.", rating: 5, verified: true, text: "AOD-9604 combined with consistent training has helped me break through a weight loss plateau I'd been stuck at for months. Very impressed with the quality.", product: "AOD-9604 Metabolic Optimizer", date: "3 weeks ago" }
];

const SOCIAL_PROOF_NAMES = [
  { name: "John D.", initials: "JD" }, { name: "Sarah M.", initials: "SM" }, { name: "Alex K.", initials: "AK" },
  { name: "Emma R.", initials: "ER" }, { name: "Chris T.", initials: "CT" }, { name: "Lisa W.", initials: "LW" },
  { name: "Ryan P.", initials: "RP" }, { name: "Kate B.", initials: "KB" }, { name: "Tom H.", initials: "TH" }
];

// ==========================================
// STATE
// ==========================================
let cart = [];
let currentPage = 'home';
let currentProduct = null;
let currentFilter = 'all';
let currentSort = 'featured';
let detailQty = 1;
let chatbotOpen = false;

// ==========================================
// INITIALIZATION
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initHeader();
  initParticles();
  initScrollAnimations();
  initCountUp();
  renderFeaturedProducts();
  renderHomeReviews();
  renderRecommended();
  renderBlogPosts();
  startSocialProof();
  startPricingTimer();
  renderShopProducts();
});

// ==========================================
// THEME
// ==========================================
function initTheme() {
  const saved = localStorage.getItem('theme') || 'dark';
  document.documentElement.setAttribute('data-theme', saved);
  updateThemeIcon(saved);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
  updateThemeIcon(next);
}

function updateThemeIcon(theme) {
  const btn = document.getElementById('themeToggle');
  btn.textContent = theme === 'dark' ? '\u2600\uFE0F' : '\uD83C\uDF19';
}

// ==========================================
// HEADER
// ==========================================
function initHeader() {
  window.addEventListener('scroll', () => {
    const header = document.getElementById('header');
    header.classList.toggle('scrolled', window.scrollY > 20);

    // Scroll progress
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
    document.getElementById('scrollProgress').style.width = progress + '%';
  });
}

// ==========================================
// NAVIGATION (SPA)
// ==========================================
function navigateTo(page, data) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  const target = document.getElementById('page-' + page);
  if (target) {
    target.classList.add('active');
    currentPage = page;
    window.scrollTo({ top: 0, behavior: 'smooth' });

    if (page === 'shop') renderShopProducts();
    if (page === 'product' && data) loadProductDetail(data);
    if (page === 'checkout') renderCheckout();
  }
}

// ==========================================
// MOBILE MENU
// ==========================================
function toggleMobileMenu() {
  document.getElementById('mobileNav').classList.toggle('active');
}

// ==========================================
// SEARCH
// ==========================================
function handleSearch(query) {
  const results = document.getElementById('searchResults');
  if (!query.trim()) { results.classList.remove('active'); return; }

  const filtered = PRODUCTS.filter(p =>
    p.name.toLowerCase().includes(query.toLowerCase()) ||
    p.tags.some(t => t.includes(query.toLowerCase())) ||
    p.category.includes(query.toLowerCase())
  );

  if (filtered.length === 0) {
    results.innerHTML = '<div style="padding:20px;text-align:center;color:var(--text-tertiary)">No products found</div>';
  } else {
    results.innerHTML = filtered.map(p => `
      <div class="search-result-item" onclick="navigateTo('product','${p.id}');document.getElementById('searchResults').classList.remove('active');document.getElementById('searchInput').value=''">
        <div style="width:40px;height:40px;background:var(--bg-tertiary);border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:1.2rem">&#129516;</div>
        <div>
          <div style="font-weight:600;font-size:0.85rem">${p.name}</div>
          <div style="font-size:0.8rem;color:var(--brand-primary)">$${p.price.toFixed(2)}</div>
        </div>
      </div>
    `).join('');
  }
  results.classList.add('active');
}

// ==========================================
// PRODUCT RENDERING
// ==========================================
function createProductCard(product) {
  const savePercent = Math.round((1 - product.price / product.originalPrice) * 100);
  const badgeClass = product.badge === 'Hot' ? 'hot' : product.badge === 'Trending' ? 'trending' :
    (product.badge === 'Premium' || product.badge === 'Ultimate' || product.badge === 'Cutting Edge') ? 'premium' : '';

  return `
    <div class="product-card animate-on-scroll" data-category="${product.category}">
      ${product.badge ? `<span class="product-badge ${badgeClass}">${product.badge}</span>` : ''}
      <div class="product-image" onclick="navigateTo('product','${product.id}')">
        <div class="product-image-placeholder" style="font-size:4rem;opacity:0.5">&#129516;</div>
        <div class="product-quick-actions">
          <button class="quick-action-btn" title="Quick view" onclick="event.stopPropagation();navigateTo('product','${product.id}')">&#128065;</button>
          <button class="quick-action-btn" title="Add to cart" onclick="event.stopPropagation();addToCart('${product.id}')">&#128722;</button>
        </div>
      </div>
      <div class="product-info">
        <div class="product-category">${product.category}</div>
        <h3 class="product-name">${product.name}</h3>
        <div class="product-rating">
          <span class="stars">${'&#9733;'.repeat(Math.floor(product.rating))}${product.rating % 1 >= 0.5 ? '&#9733;' : ''}</span>
          <span>${product.rating}</span>
          <span class="review-count">(${product.reviews.toLocaleString()})</span>
        </div>
        <div class="product-pricing">
          <span class="price-current">$${product.price.toFixed(2)}</span>
          <span class="price-original">$${product.originalPrice.toFixed(2)}</span>
          <span class="price-save">-${savePercent}%</span>
        </div>
        ${product.stock <= 20 ? `<div class="product-scarcity"><span class="scarcity-dot"></span>Only ${product.stock} left in stock</div>` : ''}
        <button class="product-add-btn" onclick="addToCart('${product.id}')">Add to Cart</button>
      </div>
    </div>
  `;
}

function renderFeaturedProducts() {
  const container = document.getElementById('featuredProducts');
  const featured = PRODUCTS.filter(p => p.featured);
  container.innerHTML = featured.map(createProductCard).join('');
  setTimeout(() => initScrollAnimations(), 100);
}

function renderShopProducts() {
  const container = document.getElementById('shopProducts');
  let filtered = currentFilter === 'all' ? [...PRODUCTS] : PRODUCTS.filter(p => p.category === currentFilter);

  switch (currentSort) {
    case 'price-low': filtered.sort((a, b) => a.price - b.price); break;
    case 'price-high': filtered.sort((a, b) => b.price - a.price); break;
    case 'rating': filtered.sort((a, b) => b.rating - a.rating); break;
    case 'reviews': filtered.sort((a, b) => b.reviews - a.reviews); break;
    default: filtered.sort((a, b) => (b.featured ? 1 : 0) - (a.featured ? 1 : 0));
  }

  container.innerHTML = filtered.map(createProductCard).join('');
  setTimeout(() => initScrollAnimations(), 100);
}

function filterProducts(category) {
  currentFilter = category;
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.classList.toggle('active', btn.textContent.toLowerCase().replace(/\s*&\s*/g, '').includes(category) ||
      (category === 'all' && btn.textContent === 'All'));
  });
  renderShopProducts();
}

function sortProducts(value) {
  currentSort = value;
  renderShopProducts();
}

// ==========================================
// PRODUCT DETAIL
// ==========================================
function loadProductDetail(productId) {
  const product = PRODUCTS.find(p => p.id === productId);
  if (!product) return;
  currentProduct = product;
  detailQty = 1;

  const savePercent = Math.round((1 - product.price / product.originalPrice) * 100);
  const subPrice = (product.price * 0.8).toFixed(2);

  document.getElementById('detailTitle').textContent = product.name;
  document.getElementById('detailBreadcrumb').textContent = product.name;
  document.getElementById('detailRating').textContent = product.rating;
  document.getElementById('detailReviewCount').textContent = product.reviews.toLocaleString();
  document.getElementById('detailBadge').textContent = product.badge;
  document.getElementById('detailPrice').textContent = '$' + product.price.toFixed(2);
  document.getElementById('detailOriginalPrice').textContent = '$' + product.originalPrice.toFixed(2);
  document.getElementById('detailSave').textContent = 'Save ' + savePercent + '%';
  document.getElementById('detailSubPrice').textContent = '$' + subPrice + '/mo';
  document.getElementById('detailDescription').textContent = product.description;
  document.getElementById('detailDosage').textContent = product.dosage;
  document.getElementById('detailCartPrice').textContent = '$' + product.price.toFixed(2);
  document.getElementById('qtyValue').textContent = '1';
  document.getElementById('reviewAvg').textContent = product.rating;
  document.getElementById('reviewTotal').textContent = product.reviews.toLocaleString();

  if (product.stock <= 30) {
    document.getElementById('detailScarcity').innerHTML = `<span class="scarcity-dot"></span>Only <strong>${product.stock}</strong> left in stock — selling fast!`;
    document.getElementById('detailScarcity').style.display = 'flex';
  } else {
    document.getElementById('detailScarcity').style.display = 'none';
  }

  const benefitsContainer = document.getElementById('detailBenefits');
  benefitsContainer.innerHTML = product.benefits.map(b => `<span class="detail-benefit-tag">${b}</span>`).join('');

  renderProductReviews(product);
}

function renderProductReviews(product) {
  const reviews = REVIEWS_DATA.filter(r => r.product === product.name).concat(
    REVIEWS_DATA.filter(r => r.product !== product.name).slice(0, 3)
  );

  document.getElementById('productReviews').innerHTML = reviews.map(r => `
    <div class="review-card">
      <div class="review-header">
        <div class="review-author">
          <div class="review-avatar">${r.name.charAt(0)}</div>
          <div>
            <div style="font-weight:600">${r.name}</div>
            ${r.verified ? '<div class="review-verified">&#10004; Verified Purchase</div>' : ''}
          </div>
        </div>
        <div>
          <div class="stars" style="font-size:0.85rem">${'&#9733;'.repeat(r.rating)}</div>
          <div style="font-size:0.75rem;color:var(--text-tertiary);margin-top:4px">${r.date}</div>
        </div>
      </div>
      <p class="review-text">${r.text}</p>
    </div>
  `).join('');
}

function updateQty(delta) {
  detailQty = Math.max(1, Math.min(10, detailQty + delta));
  document.getElementById('qtyValue').textContent = detailQty;
  if (currentProduct) {
    document.getElementById('detailCartPrice').textContent = '$' + (currentProduct.price * detailQty).toFixed(2);
  }
}

function addDetailToCart() {
  if (!currentProduct) return;
  for (let i = 0; i < detailQty; i++) addToCart(currentProduct.id);
}

function buyNow() {
  if (!currentProduct) return;
  addDetailToCart();
  navigateTo('checkout');
}

function toggle3DView() {
  const container = document.getElementById('threeDContainer');
  const isVisible = container.style.display !== 'none';
  container.style.display = isVisible ? 'none' : 'block';
  if (!isVisible) init3DView();
}

// ==========================================
// 3D PRODUCT VIEW (Canvas-based)
// ==========================================
function init3DView() {
  const canvas = document.getElementById('threeDCanvas');
  const ctx = canvas.getContext('2d');
  canvas.width = canvas.offsetWidth * 2;
  canvas.height = canvas.offsetHeight * 2;

  let rotX = 0, rotY = 0, isDragging = false, lastX = 0, lastY = 0, zoom = 1;

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const cx = canvas.width / 2, cy = canvas.height / 2;
    const scale = Math.min(canvas.width, canvas.height) * 0.25 * zoom;

    // Draw rotating capsule/bottle shape
    ctx.save();
    ctx.translate(cx, cy);

    // Glow effect
    const gradient = ctx.createRadialGradient(0, 0, 0, 0, 0, scale * 1.5);
    gradient.addColorStop(0, 'rgba(0, 212, 170, 0.1)');
    gradient.addColorStop(1, 'rgba(0, 212, 170, 0)');
    ctx.fillStyle = gradient;
    ctx.fillRect(-scale * 2, -scale * 2, scale * 4, scale * 4);

    // Rotating rings (molecule visualization)
    for (let i = 0; i < 3; i++) {
      const angle = rotY + (i * Math.PI * 2 / 3);
      const ringScale = scale * (0.6 + i * 0.2);

      ctx.beginPath();
      ctx.ellipse(0, 0, ringScale, ringScale * Math.abs(Math.cos(angle + rotX)), angle, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(0, 212, 170, ${0.4 - i * 0.1})`;
      ctx.lineWidth = 2;
      ctx.stroke();

      // Nodes on rings
      for (let j = 0; j < 6; j++) {
        const nodeAngle = (j / 6) * Math.PI * 2 + rotY * 2;
        const nx = Math.cos(nodeAngle) * ringScale;
        const ny = Math.sin(nodeAngle) * ringScale * Math.abs(Math.cos(angle + rotX));
        ctx.beginPath();
        ctx.arc(nx, ny, 4, 0, Math.PI * 2);
        ctx.fillStyle = i === 0 ? '#00d4aa' : i === 1 ? '#6c5ce7' : '#fd79a8';
        ctx.fill();
        ctx.shadowColor = ctx.fillStyle;
        ctx.shadowBlur = 10;
      }
    }

    // Central sphere
    const sphereGrad = ctx.createRadialGradient(-scale * 0.1, -scale * 0.1, 0, 0, 0, scale * 0.3);
    sphereGrad.addColorStop(0, 'rgba(0, 212, 170, 0.8)');
    sphereGrad.addColorStop(0.7, 'rgba(108, 92, 231, 0.5)');
    sphereGrad.addColorStop(1, 'rgba(108, 92, 231, 0)');
    ctx.beginPath();
    ctx.arc(0, 0, scale * 0.25, 0, Math.PI * 2);
    ctx.fillStyle = sphereGrad;
    ctx.shadowBlur = 20;
    ctx.shadowColor = '#00d4aa';
    ctx.fill();

    // Label
    ctx.shadowBlur = 0;
    ctx.font = `${14 * zoom}px Inter, sans-serif`;
    ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--text-primary');
    ctx.textAlign = 'center';
    ctx.fillText('Peptide Molecular Structure', 0, scale * 1.3);

    ctx.restore();

    rotY += 0.008;
    requestAnimationFrame(draw);
  }

  canvas.addEventListener('mousedown', (e) => { isDragging = true; lastX = e.clientX; lastY = e.clientY; });
  canvas.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    rotY += (e.clientX - lastX) * 0.005;
    rotX += (e.clientY - lastY) * 0.005;
    lastX = e.clientX; lastY = e.clientY;
  });
  canvas.addEventListener('mouseup', () => isDragging = false);
  canvas.addEventListener('mouseleave', () => isDragging = false);
  canvas.addEventListener('wheel', (e) => {
    e.preventDefault();
    zoom = Math.max(0.5, Math.min(2, zoom - e.deltaY * 0.001));
  });

  // Touch support
  canvas.addEventListener('touchstart', (e) => { isDragging = true; lastX = e.touches[0].clientX; lastY = e.touches[0].clientY; });
  canvas.addEventListener('touchmove', (e) => {
    if (!isDragging) return;
    e.preventDefault();
    rotY += (e.touches[0].clientX - lastX) * 0.005;
    rotX += (e.touches[0].clientY - lastY) * 0.005;
    lastX = e.touches[0].clientX; lastY = e.touches[0].clientY;
  });
  canvas.addEventListener('touchend', () => isDragging = false);

  draw();
}

// ==========================================
// CART
// ==========================================
function addToCart(productId) {
  const product = PRODUCTS.find(p => p.id === productId);
  if (!product) return;

  const existing = cart.find(item => item.id === productId);
  if (existing) {
    existing.qty++;
  } else {
    cart.push({ id: productId, qty: 1 });
  }

  updateCartUI();
  showToast(`${product.name} added to cart!`);
}

function removeFromCart(productId) {
  cart = cart.filter(item => item.id !== productId);
  updateCartUI();
}

function updateCartItemQty(productId, delta) {
  const item = cart.find(i => i.id === productId);
  if (!item) return;
  item.qty = Math.max(1, item.qty + delta);
  updateCartUI();
}

function updateCartUI() {
  const totalItems = cart.reduce((sum, item) => sum + item.qty, 0);
  const countEl = document.getElementById('cartCount');
  countEl.textContent = totalItems;
  countEl.classList.toggle('visible', totalItems > 0);

  const itemsContainer = document.getElementById('cartItems');
  const footer = document.getElementById('cartFooter');

  if (cart.length === 0) {
    itemsContainer.innerHTML = `<div class="cart-empty"><div class="cart-empty-icon">&#128722;</div><p>Your cart is empty</p><button class="btn btn-primary btn-sm" style="margin-top:16px" onclick="navigateTo('shop'); toggleCart()">Start Shopping</button></div>`;
    footer.style.display = 'none';
    return;
  }

  footer.style.display = 'block';
  let subtotal = 0;

  itemsContainer.innerHTML = cart.map(item => {
    const product = PRODUCTS.find(p => p.id === item.id);
    if (!product) return '';
    const lineTotal = product.price * item.qty;
    subtotal += lineTotal;
    return `
      <div class="cart-item">
        <div class="cart-item-image">&#129516;</div>
        <div class="cart-item-info">
          <div class="cart-item-name">${product.name}</div>
          <div class="cart-item-price">$${product.price.toFixed(2)}</div>
          <div class="cart-item-qty">
            <button class="cart-qty-btn" onclick="updateCartItemQty('${item.id}',-1)">&#8722;</button>
            <span style="font-weight:600;min-width:24px;text-align:center">${item.qty}</span>
            <button class="cart-qty-btn" onclick="updateCartItemQty('${item.id}',1)">&#43;</button>
          </div>
        </div>
        <button class="cart-item-remove" onclick="removeFromCart('${item.id}')">&#10005;</button>
      </div>
    `;
  }).join('');

  document.getElementById('cartSubtotal').textContent = '$' + subtotal.toFixed(2);
  document.getElementById('cartTotal').textContent = '$' + subtotal.toFixed(2);
}

function toggleCart() {
  const overlay = document.getElementById('cartOverlay');
  const drawer = document.getElementById('cartDrawer');
  const isOpen = drawer.classList.contains('active');
  overlay.classList.toggle('active', !isOpen);
  drawer.classList.toggle('active', !isOpen);
  document.body.style.overflow = isOpen ? '' : 'hidden';
}

// ==========================================
// CHECKOUT
// ==========================================
function renderCheckout() {
  const container = document.getElementById('checkoutItems');
  let subtotal = 0;

  container.innerHTML = cart.map(item => {
    const product = PRODUCTS.find(p => p.id === item.id);
    if (!product) return '';
    const lineTotal = product.price * item.qty;
    subtotal += lineTotal;
    return `
      <div style="display:flex;justify-content:space-between;align-items:center;padding:12px 0;border-bottom:1px solid var(--border-light)">
        <div style="display:flex;align-items:center;gap:12px">
          <div style="width:48px;height:48px;background:var(--bg-tertiary);border-radius:8px;display:flex;align-items:center;justify-content:center">&#129516;</div>
          <div>
            <div style="font-weight:600;font-size:0.85rem">${product.name}</div>
            <div style="color:var(--text-tertiary);font-size:0.8rem">Qty: ${item.qty}</div>
          </div>
        </div>
        <div style="font-weight:600">$${lineTotal.toFixed(2)}</div>
      </div>
    `;
  }).join('');

  const tax = subtotal * 0.08;
  document.getElementById('checkoutSubtotal').textContent = '$' + subtotal.toFixed(2);
  document.getElementById('checkoutTax').textContent = '$' + tax.toFixed(2);
  document.getElementById('checkoutTotal').textContent = '$' + (subtotal + tax).toFixed(2);
}

function handleCheckout() {
  showToast('Order placed successfully! Thank you for your purchase.');
  cart = [];
  updateCartUI();
  setTimeout(() => navigateTo('home'), 2000);
}

// ==========================================
// REVIEWS (Home page)
// ==========================================
function renderHomeReviews() {
  const container = document.getElementById('homeReviews');
  container.innerHTML = REVIEWS_DATA.slice(0, 3).map(r => `
    <div class="review-card animate-on-scroll">
      <div class="review-header">
        <div class="review-author">
          <div class="review-avatar">${r.name.charAt(0)}</div>
          <div>
            <div style="font-weight:600">${r.name}</div>
            ${r.verified ? '<div class="review-verified">&#10004; Verified Purchase</div>' : ''}
          </div>
        </div>
        <div class="stars" style="font-size:0.85rem">${'&#9733;'.repeat(r.rating)}</div>
      </div>
      <p class="review-text">"${r.text}"</p>
      <p style="font-size:0.8rem;color:var(--brand-primary);font-weight:600;margin-top:12px">Re: ${r.product}</p>
    </div>
  `).join('');
}

// ==========================================
// AI RECOMMENDED
// ==========================================
function renderRecommended() {
  const container = document.getElementById('recommendedCarousel');
  const recommended = PRODUCTS.filter(p => p.trending).slice(0, 6);
  container.innerHTML = recommended.map(createProductCard).join('');
}

// ==========================================
// BLOG
// ==========================================
function renderBlogPosts() {
  const container = document.getElementById('blogGrid');
  container.innerHTML = BLOG_POSTS.map(post => `
    <article class="blog-card animate-on-scroll">
      <div class="blog-image" style="display:flex;align-items:center;justify-content:center;font-size:3rem;opacity:0.3">&#128218;</div>
      <div class="blog-content">
        <div class="blog-meta">
          <span>${post.category}</span>
          <span>${post.readTime} read</span>
          <span>${new Date(post.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
        </div>
        <h3 class="blog-title">${post.title}</h3>
        <p class="blog-excerpt">${post.excerpt}</p>
        <span class="blog-read-more">Read Article &#8594;</span>
      </div>
    </article>
  `).join('');
}

// ==========================================
// FAQ
// ==========================================
function toggleFaq(button) {
  const item = button.parentElement;
  const answer = item.querySelector('.faq-answer');
  const isOpen = item.classList.contains('open');

  // Close all
  document.querySelectorAll('.faq-item').forEach(i => {
    i.classList.remove('open');
    i.querySelector('.faq-answer').style.maxHeight = '0';
  });

  if (!isOpen) {
    item.classList.add('open');
    answer.style.maxHeight = answer.scrollHeight + 'px';
  }
}

// ==========================================
// FORMS
// ==========================================
function handleNewsletterSubmit(e) {
  e.preventDefault();
  showToast('Welcome! Check your email for your 15% discount code.');
  e.target.reset();
}

function handleContactSubmit(e) {
  e.preventDefault();
  showToast('Message sent! We\'ll get back to you within 2 hours.');
  e.target.reset();
}

// ==========================================
// TOAST NOTIFICATIONS
// ==========================================
function showToast(message) {
  const toast = document.getElementById('toast');
  document.getElementById('toastMessage').textContent = message;
  toast.classList.add('visible');
  setTimeout(() => toast.classList.remove('visible'), 3000);
}

// ==========================================
// SOCIAL PROOF POPUP
// ==========================================
function startSocialProof() {
  const popup = document.getElementById('socialProofPopup');
  const times = ['1 minute ago', '2 minutes ago', '3 minutes ago', '5 minutes ago', '8 minutes ago', '12 minutes ago'];

  function showProof() {
    const person = SOCIAL_PROOF_NAMES[Math.floor(Math.random() * SOCIAL_PROOF_NAMES.length)];
    const product = PRODUCTS[Math.floor(Math.random() * PRODUCTS.length)];
    const time = times[Math.floor(Math.random() * times.length)];

    document.getElementById('proofAvatar').textContent = person.initials;
    document.getElementById('proofName').textContent = person.name;
    document.getElementById('proofProduct').textContent = product.name;
    document.getElementById('proofTime').textContent = time;

    popup.classList.add('visible');
    setTimeout(() => popup.classList.remove('visible'), 4000);
  }

  // Show first after 8 seconds, then every 25-40 seconds
  setTimeout(() => {
    showProof();
    setInterval(showProof, 25000 + Math.random() * 15000);
  }, 8000);
}

// ==========================================
// PRICING TIMER (Dynamic urgency)
// ==========================================
function startPricingTimer() {
  // Set end time to random hours ahead
  const endTime = Date.now() + (4 * 60 * 60 * 1000) + (32 * 60 * 1000) + (15 * 1000);

  function updateTimer() {
    const remaining = Math.max(0, endTime - Date.now());
    const hours = Math.floor(remaining / 3600000);
    const mins = Math.floor((remaining % 3600000) / 60000);
    const secs = Math.floor((remaining % 60000) / 1000);

    const hEl = document.getElementById('timerHours');
    const mEl = document.getElementById('timerMins');
    const sEl = document.getElementById('timerSecs');
    if (hEl) hEl.textContent = String(hours).padStart(2, '0');
    if (mEl) mEl.textContent = String(mins).padStart(2, '0');
    if (sEl) sEl.textContent = String(secs).padStart(2, '0');
  }

  setInterval(updateTimer, 1000);
  updateTimer();
}

// ==========================================
// PARTICLES
// ==========================================
function initParticles() {
  const container = document.getElementById('heroParticles');
  if (!container) return;
  for (let i = 0; i < 20; i++) {
    const particle = document.createElement('div');
    particle.className = 'particle';
    particle.style.left = Math.random() * 100 + '%';
    particle.style.top = (60 + Math.random() * 40) + '%';
    particle.style.animationDelay = Math.random() * 15 + 's';
    particle.style.animationDuration = (10 + Math.random() * 10) + 's';
    container.appendChild(particle);
  }
}

// ==========================================
// SCROLL ANIMATIONS
// ==========================================
function initScrollAnimations() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

  document.querySelectorAll('.animate-on-scroll').forEach(el => observer.observe(el));
}

// ==========================================
// COUNT-UP ANIMATION
// ==========================================
function initCountUp() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const target = parseInt(entry.target.getAttribute('data-count'));
        if (!target) return;
        animateCount(entry.target, 0, target, 2000);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });

  document.querySelectorAll('[data-count]').forEach(el => observer.observe(el));
}

function animateCount(element, start, end, duration) {
  const startTime = performance.now();
  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 4);
    const current = Math.round(start + (end - start) * eased);

    if (end >= 1000) {
      element.textContent = current.toLocaleString() + '+';
    } else if (end === 99) {
      element.textContent = current + '%';
    } else {
      element.textContent = current + '+';
    }

    if (progress < 1) requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
}

// ==========================================
// AI CHATBOT (Hugging Face Integration)
// ==========================================
function toggleChatbot() {
  chatbotOpen = !chatbotOpen;
  document.getElementById('chatbotWindow').classList.toggle('active', chatbotOpen);
}

function sendChatFromInput() {
  const input = document.getElementById('chatbotInput');
  const msg = input.value.trim();
  if (!msg) return;
  input.value = '';
  sendChatMessage(msg);
}

function sendChatMessage(message) {
  const container = document.getElementById('chatbotMessages');

  // Hide chips after first message
  document.getElementById('chatbotChips').style.display = 'none';

  // Add user message
  container.innerHTML += `<div class="chat-message user">${escapeHTML(message)}</div>`;

  // Add typing indicator
  container.innerHTML += `<div class="chat-typing" id="typingIndicator"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>`;
  container.scrollTop = container.scrollHeight;

  // Generate response (local AI knowledge base)
  setTimeout(() => {
    const typing = document.getElementById('typingIndicator');
    if (typing) typing.remove();

    const response = generateChatResponse(message);
    container.innerHTML += `<div class="chat-message bot">${response}</div>`;
    container.scrollTop = container.scrollHeight;
  }, 1000 + Math.random() * 1500);
}

function generateChatResponse(message) {
  const msg = message.toLowerCase();

  // Peptide knowledge base
  const responses = {
    recovery: `Great question! For <strong>recovery</strong>, our top recommendations are:<br><br>
      &#129516; <strong>BPC-157 Oral Capsules</strong> ($89.99) — The gold standard for gut health and tissue repair. 500mcg per capsule, 60 per bottle.<br><br>
      &#128170; <strong>TB-500 Recovery Complex</strong> ($94.99) — Excellent for muscle recovery and flexibility. Popular with athletes.<br><br>
      &#127942; <strong>The Pentadecapeptide Stack</strong> ($149.99) — Our ultimate combo: BPC-157 + KPV + Larazotide for comprehensive recovery.<br><br>
      Want me to help you choose between these?`,

    'bpc-157': `<strong>BPC-157</strong> (Body Protection Compound-157) is a 15-amino-acid peptide derived from human gastric juice. Here's what the research shows:<br><br>
      &#10004; <strong>Gut Healing</strong> — Protects and repairs intestinal lining, shown effective in leaky gut models<br>
      &#10004; <strong>Tissue Repair</strong> — Accelerates healing of tendons, ligaments, muscles, and bones<br>
      &#10004; <strong>Anti-Inflammatory</strong> — Modulates the NO system and reduces systemic inflammation<br>
      &#10004; <strong>Neuroprotective</strong> — Studies show benefits for dopamine system regulation<br><br>
      Our BPC-157 capsules are 99.4% pure, HPLC verified. <strong>$89.99 for 60 capsules (500mcg each)</strong>. Want to add it to your cart?`,

    'anti-aging': `For <strong>anti-aging and longevity</strong>, we have several powerful options:<br><br>
      &#128300; <strong>GHK-Cu Copper Peptide Serum</strong> ($74.99) — Stimulates collagen, reduces wrinkles, cellular renewal<br>
      &#128171; <strong>Epithalon Telomere Support</strong> ($119.99) — Targets telomerase activation for cellular longevity<br>
      &#127793; <strong>FOXO4-DRI Senolytic Complex</strong> ($134.99) — Clears senescent "zombie" cells for rejuvenation<br>
      &#9889; <strong>SS-31 Mitochondrial Complex</strong> ($109.99) — Optimizes mitochondrial function and energy<br><br>
      The most popular longevity stack is Epithalon + GHK-Cu + SS-31. Shall I explain the protocol?`,

    stack: `<strong>Peptide stacking</strong> is combining multiple peptides for synergistic benefits. Here are our recommended stacks:<br><br>
      &#128170; <strong>Recovery Stack</strong>: BPC-157 + TB-500 ($184.98) — Complementary healing pathways for maximum recovery<br><br>
      &#10024; <strong>Beauty Stack</strong>: GHK-Cu + Collagen Peptides ($124.98) — Topical + oral approach for skin, hair, nails<br><br>
      &#128171; <strong>Longevity Stack</strong>: Epithalon + SS-31 + FOXO4-DRI ($364.97) — Comprehensive anti-aging targeting telomeres, mitochondria, and senescent cells<br><br>
      &#129504; <strong>Cognitive Stack</strong>: Dihexa + MOTS-c ($189.98) — Brain + body energy optimization<br><br>
      Always introduce one peptide at a time and assess tolerance before adding another.`,

    collagen: `<strong>Collagen peptides</strong> are our most popular product category! Here's what you should know:<br><br>
      Our <strong>Hydrolyzed Collagen Peptides</strong> ($49.99) contain Types I, II, and III from grass-fed sources. Clinical benefits include:<br><br>
      &#10024; Improved skin elasticity (visible in 4-8 weeks)<br>
      &#128133; Stronger hair and nails<br>
      &#129463; Joint comfort and cartilage support<br>
      &#129516; Gut lining repair<br><br>
      Best taken daily — 10g per scoop, mixes into any beverage. With 5,621 reviews at 4.7 stars, it's our most-reviewed product!`,

    weight: `For <strong>weight management</strong>, these peptides support healthy metabolism:<br><br>
      &#128293; <strong>AOD-9604</strong> ($79.99) — Modified growth hormone fragment that supports fat metabolism without affecting blood sugar or growth<br><br>
      &#9889; <strong>MOTS-c Metabolic Peptide</strong> ($89.99) — Mitochondrial peptide that acts as an exercise mimetic, improving insulin sensitivity and metabolic activation<br><br>
      Both work best combined with regular exercise and a balanced diet. They're not magic pills, but powerful metabolic supporters.<br><br>
      Would you like more details on either of these?`,

    shipping: `&#128666; <strong>Shipping Info</strong>:<br><br>
      &#10004; <strong>Free shipping</strong> on all US orders over $75<br>
      &#10004; Standard US shipping: 3-5 business days ($5.99)<br>
      &#10004; Express US shipping: 1-2 business days ($12.99)<br>
      &#10004; International shipping to 40+ countries<br>
      &#10004; All orders include tracking<br>
      &#10004; Temperature-controlled packaging for sensitive products<br><br>
      Orders placed before 2pm EST ship same day!`,

    safety: `<strong>Safety & Quality</strong> are our top priorities:<br><br>
      &#128300; Every batch is independently tested by third-party labs<br>
      &#128272; Manufactured in FDA-registered, cGMP certified facilities in the USA<br>
      &#128203; Full Certificates of Analysis (COAs) available for every product<br>
      &#129516; 99%+ purity verified by HPLC testing<br>
      &#128176; 90-day money-back guarantee<br><br>
      Always consult your healthcare provider before starting any supplement. While peptides have strong safety profiles in research, individual responses vary.`
  };

  // Match against knowledge base
  if (msg.includes('recover') || msg.includes('healing') || msg.includes('injury') || msg.includes('gut'))
    return responses.recovery;
  if (msg.includes('bpc') || msg.includes('body protection'))
    return responses['bpc-157'];
  if (msg.includes('anti-aging') || msg.includes('aging') || msg.includes('longevity') || msg.includes('wrinkle') || msg.includes('young'))
    return responses['anti-aging'];
  if (msg.includes('stack') || msg.includes('combine') || msg.includes('together'))
    return responses.stack;
  if (msg.includes('collagen') || msg.includes('skin') || msg.includes('hair') || msg.includes('nail') || msg.includes('beauty'))
    return responses.collagen;
  if (msg.includes('weight') || msg.includes('fat') || msg.includes('metaboli') || msg.includes('lose'))
    return responses.weight;
  if (msg.includes('ship') || msg.includes('deliver') || msg.includes('track'))
    return responses.shipping;
  if (msg.includes('safe') || msg.includes('side effect') || msg.includes('quality') || msg.includes('test') || msg.includes('pure'))
    return responses.safety;
  if (msg.includes('price') || msg.includes('cost') || msg.includes('cheap') || msg.includes('discount'))
    return `We offer competitive pricing on all pharmaceutical-grade peptides, with discounts of 25-35% off retail. <br><br>&#128176; Use code <strong>PEPTIDE15</strong> for 15% off your first order!<br>&#128260; Subscribe & Save gets you 20% off recurring orders.<br>&#128230; Bundle any 3+ products for an extra 10% off.<br><br>Our most affordable option is <strong>Hydrolyzed Collagen Peptides at $49.99</strong>. Premium options range from $74.99-$149.99.`;
  if (msg.includes('cognitive') || msg.includes('brain') || msg.includes('focus') || msg.includes('memory') || msg.includes('nootropic'))
    return `For <strong>cognitive enhancement</strong>, our <strong>Dihexa Cognitive Peptide</strong> ($99.99) is exceptional:<br><br>&#129504; 10 million times more potent than BDNF at forming new neural connections (in preclinical studies)<br>&#128161; Supports neuroplasticity, memory formation, and mental clarity<br>&#127891; Enhanced with Lion's Mane and Bacopa Monnieri<br><br>Cycle: 5 days on, 2 days off. Most users report improved focus and memory within 2 weeks.`;
  if (msg.includes('hello') || msg.includes('hi') || msg.includes('hey'))
    return `Hey there! &#128075; Welcome to PeptideSource! I'm here to help you find the perfect peptide supplement. What are your health goals? I can recommend products for:<br><br>&#128170; Recovery & Gut Health<br>&#10024; Skin & Beauty<br>&#128171; Longevity & Anti-Aging<br>&#129504; Cognitive Performance<br>&#128293; Weight Management<br>&#128737; Immune Support`;

  // Default response
  return `That's a great question! Here's what I can help with:<br><br>
    &#129516; <strong>Product recommendations</strong> — Tell me your health goals<br>
    &#128218; <strong>Peptide education</strong> — Ask about any specific peptide<br>
    &#128260; <strong>Stacking advice</strong> — How to combine peptides safely<br>
    &#128666; <strong>Shipping & orders</strong> — Delivery info and tracking<br>
    &#128300; <strong>Quality & safety</strong> — Lab testing and certifications<br><br>
    Try asking something like "What's the best peptide for recovery?" or "Tell me about BPC-157" and I'll give you detailed, science-backed answers!`;
}

function escapeHTML(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}
