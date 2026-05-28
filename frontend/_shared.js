// _shared.js — v2 with Auth, Theme, Wishlist, Navigation

// ─── AUTH HELPERS ───
function getToken() { return localStorage.getItem('lp_token') || ''; }
function authHeaders() { return { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + getToken() }; }

async function getCurrentUser() {
  const token = getToken();
  if (!token) return null;
  try {
    const r = await fetch('/auth/me', { headers: { 'Authorization': 'Bearer ' + token } });
    if (!r.ok) return null;
    return await r.json();
  } catch { return null; }
}

// ─── THEME ───
function toggleTheme() {
  const h = document.documentElement;
  const isDark = h.getAttribute('data-theme') === 'dark';
  h.setAttribute('data-theme', isDark ? 'light' : 'dark');
  const btn = document.getElementById('themeBtn');
  if (btn) btn.textContent = isDark ? '🌙' : '☀️';
  localStorage.setItem('lp_theme', isDark ? 'light' : 'dark');
}

function initTheme() {
  const t = localStorage.getItem('lp_theme') || 'dark';
  document.documentElement.setAttribute('data-theme', t);
  const b = document.getElementById('themeBtn');
  if (b) b.textContent = t === 'dark' ? '☀️' : '🌙';
}

// ─── WISHLIST BADGE ───
function updWBadge() {
  const w = JSON.parse(localStorage.getItem('lp_wish') || '[]');
  ['wBadge', 'wishlistCount'].forEach(id => {
    const b = document.getElementById(id);
    if (b) b.textContent = w.length;
  });
}

// ─── TAB NAVIGATION ───
function showTab(tabName) {
  const map = {
    'search'         : '/app',
    'build'          : '/build',
    'history'        : '/history-page',
    'wishlist'       : '/wishlist-page',
    'CPU Comparison' : '/cpu-compare'
  };
  const url = map[tabName];
  if (url) window.location.href = url;
}

// ─── TOAST ───
function toast(type, msg) {
  const w = document.getElementById('toastWrap');
  if (!w) return;
  const d = document.createElement('div');
  d.className = 'toast ' + (type || '');
  d.textContent = msg;
  w.appendChild(d);
  setTimeout(() => {
    d.style.opacity = '0';
    d.style.transition = 'opacity .3s';
    setTimeout(() => d.remove(), 300);
  }, 3000);
}

// ─── 52-WEEK WIDGET ───
function w52Html(price) {
  if (!price || price === 0) return '';
  const low  = Math.round(price * .80);
  const high = Math.round(price * 1.20);
  const pct  = Math.round(((price - low) / (high - low)) * 100);
  return `<div class="w52">
    <div class="w52-header">
      <span class="w52-low-lbl">52w Low<br><strong>₹${low.toLocaleString('en-IN')}</strong></span>
      <span class="w52-cur-lbl">Now<br><strong>₹${price.toLocaleString('en-IN')}</strong></span>
      <span class="w52-high-lbl">52w High<br><strong>₹${high.toLocaleString('en-IN')}</strong></span>
    </div>
    <div class="w52-track">
      <div class="w52-range"></div>
      <div class="w52-dot" style="left:${pct}%">
        <div class="w52-tooltip">₹${price.toLocaleString('en-IN')}</div>
      </div>
    </div>
  </div>`;
}

// ─── LOGOUT ───
async function doLogoutShared() {
  const token = getToken();
  await fetch('/auth/logout', { method: 'POST', headers: { 'Authorization': 'Bearer ' + token } }).catch(() => {});
  const accs = JSON.parse(localStorage.getItem('lp_accounts') || '[]').filter(a => a.token !== token);
  localStorage.setItem('lp_accounts', JSON.stringify(accs));
  localStorage.removeItem('lp_token');
  location.href = '/';
}

// ─── INJECT NAVBAR USER SECTION ───
async function injectNavUser() {
  // Find or create the user-pill slot — NEVER wipe the whole nav-right
  let slot = document.getElementById('navUserSlot');
  if (!slot) {
    slot = document.createElement('div');
    slot.id = 'navUserSlot';
    slot.style.cssText = 'display:flex;align-items:center;gap:8px;';
    const nr = document.getElementById('navUserSection');
    if (!nr) return;
    nr.appendChild(slot);
  }
  const user = await getCurrentUser();
  if (!user) {
    slot.innerHTML = `
      <a href="/login" class="nav-auth-btn nav-login">Login</a>
      <a href="/login" class="nav-auth-btn nav-signup">Sign Up</a>`;
  } else {
    const initials = user.username.substring(0, 2).toUpperCase();
    slot.innerHTML = `
      <div class="nav-user-pill" tabindex="0">
        <div class="nav-avatar" style="background:${user.avatar_color || '#f5a623'}">${initials}</div>
        <span class="nav-uname">${user.username}</span>
        <i class="fa fa-chevron-down" style="font-size:9px;color:var(--text2);"></i>
        <div class="nav-dropdown">
          <div class="nd-header">
            <div class="nd-name">${user.username}</div>
            <div class="nd-email">${user.email || ''}</div>
          </div>
          <a class="nd-item" href="/wishlist-page"><i class="fa fa-heart"></i> My Wishlist</a>
          <a class="nd-item" href="/history-page"><i class="fa fa-history"></i> History</a>
          <div class="nd-sep"></div>
          <div class="nd-item" onclick="openSwitchAccountModal()"><i class="fa fa-exchange-alt"></i> Switch Account</div>
          <div class="nd-item nd-logout" onclick="doLogoutShared()"><i class="fa fa-sign-out-alt"></i> Logout</div>
        </div>
      </div>`;
  }
}

// Switch Account Modal (shared across pages)
function openSwitchAccountModal() {
  let modal = document.getElementById('sharedSwitchModal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'sharedSwitchModal';
    modal.style.cssText = 'position:fixed;inset:0;z-index:900;background:rgba(0,0,0,.7);backdrop-filter:blur(8px);display:flex;align-items:center;justify-content:center;';
    modal.innerHTML = `
      <div style="background:var(--card);border:1px solid var(--border);border-radius:22px;padding:36px;width:100%;max-width:400px;position:relative;">
        <button onclick="document.getElementById('sharedSwitchModal').remove()" style="position:absolute;top:14px;right:14px;background:rgba(255,255,255,.05);border:1px solid var(--border);color:var(--text2);width:30px;height:30px;border-radius:7px;cursor:pointer;font-size:13px;">✕</button>
        <div style="font-size:17px;font-weight:700;font-family:'Syne',sans-serif;margin-bottom:4px;">Switch Account</div>
        <div style="font-size:13px;color:var(--text2);margin-bottom:20px;">Select or add an account</div>
        <div id="switchAccList"></div>
        <a href="/login" style="display:block;text-align:center;padding:11px;border-radius:10px;border:1px solid var(--border);color:var(--text2);text-decoration:none;font-size:14px;font-weight:600;margin-top:12px;transition:.2s;" onmouseover="this.style.borderColor='var(--accent2)'" onmouseout="this.style.borderColor='var(--border)'">
          <i class="fa fa-plus"></i> Add Another Account
        </a>
      </div>`;
    document.body.appendChild(modal);
    modal.addEventListener('click', e => { if(e.target===modal) modal.remove(); });
  }
  const list = document.getElementById('switchAccList');
  const curToken = getToken();
  const accs = JSON.parse(localStorage.getItem('lp_accounts') || '[]');
  list.innerHTML = accs.map(a => `
    <div onclick="switchToAcc('${a.token}')" style="display:flex;align-items:center;gap:12px;padding:11px 14px;border-radius:12px;background:rgba(255,255,255,.04);border:1px solid ${a.token===curToken?'var(--accent)':'var(--border)'};cursor:pointer;margin-bottom:8px;transition:.2s;">
      <div style="width:36px;height:36px;border-radius:50%;background:${a.color||'#f5a623'};display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px;color:#fff;flex-shrink:0;">${a.username.substring(0,2).toUpperCase()}</div>
      <div style="flex:1;"><div style="font-size:14px;font-weight:600;">${a.username}</div><div style="font-size:11px;color:var(--text2);">${a.email||''}</div></div>
      ${a.token===curToken?'<span style="font-size:10px;padding:2px 8px;border-radius:20px;background:rgba(245,166,35,.15);color:var(--accent);font-weight:700;">Active</span>':''}
    </div>`).join('') || '<div style="color:var(--text2);font-size:13px;text-align:center;padding:16px;">No saved accounts</div>';
  modal.style.display = 'flex';
}

function switchToAcc(token) {
  localStorage.setItem('lp_token', token);
  document.getElementById('sharedSwitchModal')?.remove();
  location.reload();
}

// ─── INIT ───
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  updWBadge();
  injectNavUser();
});

// ─── CARD RENDERER (shared by search, history, wishlist pages) ───
function mkCard(it, idx, ctx) {
  const price    = it.price_value || it.price || 0;
  const priceStr = it.price || (price ? '₹' + Number(price).toLocaleString('en-IN') : 'N/A');
  const pred     = it.predicted_price;
  const deal     = it.deal;
  const img      = it.image || '';
  const title    = it.title || 'Laptop';
  const platform = it.platform || '';
  const link     = it.link || '#';
  const rating   = it.rating || '';
  const ram      = it.ram || '';
  const storage  = it.storage || '';
  const specs    = it.specs || it.specs_summary || '';

  // Deal badge
  let dealBadge = '';
  let cardClass = 'laptop-card';
  if (deal) {
    const lbl = deal.label || '';
    if (lbl.includes('Hot')) {
      dealBadge = `<div class="deal-badge hot">🔥 ${lbl}</div>`;
      cardClass += ' deal-hot';
    } else if (lbl.includes('Good')) {
      dealBadge = `<div class="deal-badge good">✅ ${lbl}</div>`;
      cardClass += ' deal-good';
    } else if (lbl.includes('Overpriced') || lbl.includes('High')) {
      dealBadge = `<div class="deal-badge over">⚠️ ${lbl}</div>`;
    }
  }

  // Price vs predicted
  let predHtml = '';
  if (pred && pred > 0) {
    const diff = Math.round(((price - pred) / pred) * 100);
    const diffStr = diff > 0 ? `+${diff}%` : `${diff}%`;
    const color = diff <= -10 ? 'var(--green)' : diff >= 15 ? 'var(--red)' : 'var(--text2)';
    predHtml = `<div class="pred-row">
      <span style="color:var(--text2);font-size:12px;">ML Fair Price:</span>
      <span style="color:var(--accent);font-size:13px;font-weight:700;">₹${Number(pred).toLocaleString('en-IN')}</span>
      <span style="color:${color};font-size:11px;font-weight:700;">(${diffStr})</span>
    </div>`;
  }

  // Wishlist button
  const wl = JSON.parse(localStorage.getItem('lp_wish') || '[]');
  const saved = wl.some(w => w.link === link);
  const heartIcon = saved ? '❤️' : '🤍';
  const wishBtn = ctx !== 'wishlist'
    ? `<button class="wl-btn" onclick="toggleWish(${idx})" title="Save to wishlist">${heartIcon}</button>`
    : `<button class="wl-btn" onclick="rmWish(${idx})" title="Remove from wishlist" style="color:var(--red)">🗑</button>`;

  const metaTags = [ram && `${ram} RAM`, storage && `${storage}GB`, platform].filter(Boolean)
    .map(t => `<span class="tag">${t}</span>`).join('');

  return `
  <div class="${cardClass}" data-idx="${idx}">
    ${dealBadge}
    <div class="card-img-wrap">
      ${img ? `<img src="${img}" alt="${title}" loading="lazy" onerror="this.style.display='none'">` : '<div class="no-img"><i class="fa fa-laptop" style="font-size:40px;color:var(--border)"></i></div>'}
    </div>
    <div class="card-body">
      <div class="card-title">${title}</div>
      <div class="card-tags">${metaTags}</div>
      ${rating ? `<div class="card-rating">⭐ ${rating}</div>` : ''}
      <div class="card-price">${priceStr}</div>
      ${predHtml}
      ${w52Html(price)}
      <div class="card-actions">
        <a href="${link}" target="_blank" rel="noopener" class="btn-buy">View Deal <i class="fa fa-external-link-alt"></i></a>
        ${wishBtn}
      </div>
    </div>
  </div>`;
}

// ─── WISHLIST TOGGLE (used in search results) ───
function toggleWish(idx) {
  const items = window._cards || [];
  const item  = items[idx];
  if (!item) return;
  const wl = JSON.parse(localStorage.getItem('lp_wish') || '[]');
  const pos = wl.findIndex(w => w.link === item.link);
  if (pos >= 0) {
    wl.splice(pos, 1);
    toast('', '🤍 Removed from wishlist');
  } else {
    wl.push(item);
    toast('ok', '❤️ Added to wishlist!');
  }
  localStorage.setItem('lp_wish', JSON.stringify(wl));
  updWBadge();
  // Refresh the heart icon on card
  const card = document.querySelector(`[data-idx="${idx}"] .wl-btn`);
  if (card) card.textContent = pos >= 0 ? '🤍' : '❤️';
}
