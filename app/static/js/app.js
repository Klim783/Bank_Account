'use strict';

/* ============================================================
   STATE
   ============================================================ */
const state = {
  baseUrl: localStorage.getItem('ledger_base_url') || 'http://127.0.0.1:8000/api/v1',
  token: localStorage.getItem('ledger_token') || '',
  login: localStorage.getItem('ledger_login') || '',
  wallets: [],
  operations: [],
  balance: 0,
};

const CCY_LABEL = { RUB: 'RUB', USD: 'USD', EUR: 'EUR' };
const TYPE_LABEL = { INCOME: 'доход', EXPENSE: 'расход', TRANSFER: 'перевод' };

/* ============================================================
   DOM SHORTCUTS
   ============================================================ */
const $ = (id) => document.getElementById(id);

const el = {
  settingsToggle: $('settingsToggle'),
  settingsPanel: $('settingsPanel'),
  baseUrlInput: $('baseUrlInput'),
  saveBaseUrl: $('saveBaseUrl'),

  authForm: $('authForm'),
  authChip: $('authChip'),
  loginInput: $('loginInput'),
  passwordInput: $('passwordInput'),
  loginBtn: $('loginBtn'),
  registerBtn: $('registerBtn'),
  logoutBtn: $('logoutBtn'),
  authLoginLabel: $('authLoginLabel'),

  gate: $('gate'),
  dashboard: $('dashboard'),

  balanceDigits: $('balanceDigits'),

  walletsGrid: $('walletsGrid'),
  walletCount: $('walletCount'),
  openAddWallet: $('openAddWallet'),

  filterWallet: $('filterWallet'),
  filterFrom: $('filterFrom'),
  filterTo: $('filterTo'),
  applyFilters: $('applyFilters'),

  operationsBody: $('operationsBody'),
  operationsEmpty: $('operationsEmpty'),

  openIncome: $('openIncome'),
  openExpense: $('openExpense'),
  openTransfer: $('openTransfer'),

  modalWallet: $('modalWallet'),
  formWallet: $('formWallet'),

  modalOperation: $('modalOperation'),
  formOperation: $('formOperation'),
  operationTitle: $('operationTitle'),
  operationWalletSelect: $('operationWalletSelect'),
  operationSubmit: $('operationSubmit'),

  modalTransfer: $('modalTransfer'),
  formTransfer: $('formTransfer'),
  transferFromSelect: $('transferFromSelect'),
  transferToSelect: $('transferToSelect'),

  toasts: $('toasts'),
};

let pendingOperationType = 'income'; // 'income' | 'expense'

/* ============================================================
   TOASTS
   ============================================================ */
function toast(message, kind = 'ok') {
  const node = document.createElement('div');
  node.className = 'toast' + (kind === 'error' ? ' toast--error' : '');
  node.textContent = message;
  el.toasts.appendChild(node);
  setTimeout(() => {
    node.style.opacity = '0';
    node.style.transition = 'opacity .25s ease';
    setTimeout(() => node.remove(), 260);
  }, 4200);
}

/* ============================================================
   API WRAPPER
   ============================================================ */
async function api(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (state.token) headers['Authorization'] = `Bearer ${state.token}`;

  let response;
  try {
    response = await fetch(state.baseUrl.replace(/\/$/, '') + path, {
      ...options,
      headers,
    });
  } catch (err) {
    throw new ApiError(
      `Не удалось связаться с ${state.baseUrl}. Проверьте адрес API в настройках и что сервер запущен.`,
      0
    );
  }

  if (response.status === 204) return null;

  let body = null;
  try {
    body = await response.json();
  } catch (_) {
    body = null;
  }

  if (!response.ok) {
    const detail = (body && (body.detail || body.message)) || `Ошибка запроса (${response.status})`;
    throw new ApiError(typeof detail === 'string' ? detail : JSON.stringify(detail), response.status);
  }

  return body;
}

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

/* ============================================================
   AUTH
   ============================================================ */
function readCredentials() {
  const login = el.loginInput.value.trim();
  const password = el.passwordInput.value;
  if (!login || !password) {
    toast('Введите логин и пароль.', 'error');
    return null;
  }
  return { login, password };
}

async function register() {
  const creds = readCredentials();
  if (!creds) return;

  try {
    await api('/users', { method: 'POST', body: JSON.stringify(creds) });
    toast(`Аккаунт «${creds.login}» создан. Теперь войдите.`);
  } catch (err) {
    toast(err.message, 'error');
  }
}

async function login() {
  const creds = readCredentials();
  if (!creds) return;

  let tokenResponse;
  try {
    tokenResponse = await api('/login', { method: 'POST', body: JSON.stringify(creds) });
  } catch (err) {
    toast(err.message, 'error');
    return;
  }

  state.token = tokenResponse.access_token;
  state.login = creds.login;
  localStorage.setItem('ledger_token', state.token);
  localStorage.setItem('ledger_login', state.login);
  el.passwordInput.value = '';

  await enterDashboard();
}

function logout() {
  state.token = '';
  state.login = '';
  localStorage.removeItem('ledger_token');
  localStorage.removeItem('ledger_login');
  el.dashboard.classList.add('hidden');
  el.gate.classList.remove('hidden');
  el.authChip.classList.add('hidden');
  el.authForm.classList.remove('hidden');
  el.loginInput.value = '';
  el.passwordInput.value = '';
}

async function enterDashboard() {
  el.authForm.classList.add('hidden');
  el.authChip.classList.remove('hidden');
  el.authLoginLabel.textContent = state.login;
  el.gate.classList.add('hidden');
  el.dashboard.classList.remove('hidden');

  try {
    await api('/users'); // проверяем, что токен ещё валиден
  } catch (err) {
    if (err.status === 401) {
      toast('Сессия истекла, войдите снова.', 'error');
      logout();
      return;
    }
  }

  await refreshAll();
}

/* ============================================================
   DATA LOADING
   ============================================================ */
async function refreshAll() {
  await Promise.all([loadWallets(), loadBalance()]);
  await loadOperations();
}

async function loadWallets() {
  try {
    state.wallets = await api('/wallets');
    renderWallets();
    populateWalletSelects();
  } catch (err) {
    toast(err.message, 'error');
  }
}

async function loadBalance() {
  try {
    const res = await api('/balance');
    state.balance = Number(res.total_balance ?? 0);
    animateBalance(state.balance);
  } catch (err) {
    toast(err.message, 'error');
  }
}

async function loadOperations() {
  const params = new URLSearchParams();
  if (el.filterWallet.value) params.set('wallet_id', el.filterWallet.value);
  if (el.filterFrom.value) params.set('date_from', new Date(el.filterFrom.value).toISOString());
  if (el.filterTo.value) params.set('date_to', new Date(el.filterTo.value).toISOString());

  try {
    const query = params.toString();
    state.operations = await api('/operations' + (query ? `?${query}` : ''));
    renderOperations();
  } catch (err) {
    toast(err.message, 'error');
  }
}

/* ============================================================
   RENDERING
   ============================================================ */
function animateBalance(target) {
  const start = Number(el.balanceDigits.dataset.value || 0);
  const duration = 700;
  const startTime = performance.now();

  function step(now) {
    const progress = Math.min((now - startTime) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const value = start + (target - start) * eased;
    el.balanceDigits.textContent = formatMoney(value);
    if (progress < 1) {
      requestAnimationFrame(step);
    } else {
      el.balanceDigits.dataset.value = target;
    }
  }
  requestAnimationFrame(step);
}

function formatMoney(value) {
  return Number(value).toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatDate(iso) {
  const d = new Date(iso);
  return d.toLocaleDateString('ru-RU', { day: '2-digit', month: 'short' }) + ' ' +
    d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
}

function walletById(id) {
  return state.wallets.find((w) => w.id === id);
}

function renderWallets() {
  el.walletCount.textContent = state.wallets.length;

  // remove existing cards (keep the add-card button)
  [...el.walletsGrid.querySelectorAll('.wallet-card:not(.wallet-card--add)')].forEach((n) => n.remove());

  state.wallets.forEach((wallet) => {
    const card = document.createElement('button');
    card.className = 'wallet-card';
    card.innerHTML = `
      <div class="wallet-card__top">
        <span class="wallet-card__name">${escapeHtml(wallet.name)}</span>
        <span class="wallet-card__ccy">${CCY_LABEL[wallet.currency] || wallet.currency}</span>
      </div>
      <div class="wallet-card__balance">${formatMoney(wallet.balance)}</div>
    `;
    card.addEventListener('click', () => {
      el.filterWallet.value = wallet.id;
      loadOperations();
      document.querySelector('.operations').scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    el.walletsGrid.insertBefore(card, el.openAddWallet);
  });
}

function populateWalletSelects() {
  const options = state.wallets
    .map((w) => `<option value="${w.name}">${escapeHtml(w.name)} · ${CCY_LABEL[w.currency]}</option>`)
    .join('');
  el.operationWalletSelect.innerHTML = options || '<option value="" disabled>Сначала создайте кошелёк</option>';

  const idOptions = state.wallets
    .map((w) => `<option value="${w.id}">${escapeHtml(w.name)} · ${CCY_LABEL[w.currency]}</option>`)
    .join('');
  el.transferFromSelect.innerHTML = idOptions || '<option value="" disabled>Сначала создайте кошелёк</option>';
  el.transferToSelect.innerHTML = idOptions || '<option value="" disabled>Сначала создайте кошелёк</option>';

  const filterOptions = state.wallets
    .map((w) => `<option value="${w.id}">${escapeHtml(w.name)}</option>`)
    .join('');
  const currentFilter = el.filterWallet.value;
  el.filterWallet.innerHTML = '<option value="">Все кошельки</option>' + filterOptions;
  el.filterWallet.value = currentFilter;
}

function renderOperations() {
  [...el.operationsBody.querySelectorAll('.ledger-table__row')].forEach((n) => n.remove());

  if (!state.operations.length) {
    el.operationsEmpty.classList.remove('hidden');
    return;
  }
  el.operationsEmpty.classList.add('hidden');

  const sorted = [...state.operations].sort(
    (a, b) => new Date(b.created_at) - new Date(a.created_at)
  );

  sorted.forEach((op) => {
    const wallet = walletById(op.wallet_id);
    const typeClass = op.type === 'INCOME' ? 'income' : op.type === 'EXPENSE' ? 'expense' : 'transfer';
    const sign = op.type === 'INCOME' ? '+' : op.type === 'EXPENSE' ? '−' : '⇄';

    const row = document.createElement('div');
    row.className = 'ledger-table__row';
    row.innerHTML = `
      <span class="op-date">${formatDate(op.created_at)}</span>
      <span class="op-wallet">${wallet ? escapeHtml(wallet.name) : `#${op.wallet_id}`}</span>
      <span class="op-category">${escapeHtml(op.category || '—')}</span>
      <span class="op-type op-type--${typeClass}">${TYPE_LABEL[op.type] || op.type}</span>
      <span class="op-amount op-amount--${typeClass}">${sign} ${formatMoney(op.amount)} ${CCY_LABEL[op.currency] || ''}</span>
    `;
    el.operationsBody.appendChild(row);
  });
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str ?? '';
  return div.innerHTML;
}

/* ============================================================
   MODALS
   ============================================================ */
function openModal(node) {
  node.classList.remove('hidden');
}
function closeModal(node) {
  node.classList.add('hidden');
}

document.querySelectorAll('[data-close-modal]').forEach((btn) => {
  btn.addEventListener('click', () => btn.closest('.modal-overlay').classList.add('hidden'));
});
document.querySelectorAll('.modal-overlay').forEach((overlay) => {
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) overlay.classList.add('hidden');
  });
});

el.openAddWallet.addEventListener('click', () => openModal(el.modalWallet));

el.openIncome.addEventListener('click', () => {
  pendingOperationType = 'income';
  el.operationTitle.textContent = 'Доход';
  el.operationSubmit.textContent = 'Записать доход';
  openModal(el.modalOperation);
});
el.openExpense.addEventListener('click', () => {
  pendingOperationType = 'expense';
  el.operationTitle.textContent = 'Расход';
  el.operationSubmit.textContent = 'Записать расход';
  openModal(el.modalOperation);
});
el.openTransfer.addEventListener('click', () => openModal(el.modalTransfer));

/* ============================================================
   FORMS
   ============================================================ */
el.formWallet.addEventListener('submit', async (e) => {
  e.preventDefault();
  const data = new FormData(el.formWallet);
  const payload = {
    name: data.get('name'),
    initial_balance: data.get('initial_balance'),
    currency: data.get('currency'),
  };
  try {
    await api('/wallets', { method: 'POST', body: JSON.stringify(payload) });
    toast(`Кошелёк «${payload.name}» создан.`);
    el.formWallet.reset();
    closeModal(el.modalWallet);
    await Promise.all([loadWallets(), loadBalance()]);
  } catch (err) {
    toast(err.message, 'error');
  }
});

el.formOperation.addEventListener('submit', async (e) => {
  e.preventDefault();
  const data = new FormData(el.formOperation);
  const payload = {
    wallet_name: data.get('wallet_name'),
    amount: data.get('amount'),
    description: data.get('description') || null,
  };
  const path = pendingOperationType === 'income' ? '/operations/income' : '/operations/expense';
  try {
    await api(path, { method: 'POST', body: JSON.stringify(payload) });
    toast(pendingOperationType === 'income' ? 'Доход записан.' : 'Расход записан.');
    el.formOperation.reset();
    closeModal(el.modalOperation);
    await refreshAll();
  } catch (err) {
    toast(err.message, 'error');
  }
});

el.formTransfer.addEventListener('submit', async (e) => {
  e.preventDefault();
  const data = new FormData(el.formTransfer);
  const fromId = Number(data.get('from_wallet_id'));
  const toId = Number(data.get('to_wallet_id'));

  if (fromId === toId) {
    toast('Кошельки для перевода должны различаться.', 'error');
    return;
  }

  const payload = {
    from_wallet_id: fromId,
    to_wallet_id: toId,
    amount: data.get('amount'),
  };
  try {
    await api('/operations/transfer', { method: 'POST', body: JSON.stringify(payload) });
    toast('Перевод выполнен.');
    el.formTransfer.reset();
    closeModal(el.modalTransfer);
    await refreshAll();
  } catch (err) {
    toast(err.message, 'error');
  }
});

el.applyFilters.addEventListener('click', () => loadOperations());

/* ============================================================
   AUTH WIRING
   ============================================================ */
el.loginBtn.addEventListener('click', login);
el.registerBtn.addEventListener('click', register);
el.passwordInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') login();
});
el.logoutBtn.addEventListener('click', logout);

/* ============================================================
   SETTINGS PANEL
   ============================================================ */
el.baseUrlInput.value = state.baseUrl;
el.settingsToggle.addEventListener('click', () => {
  el.settingsPanel.classList.toggle('hidden');
});
el.saveBaseUrl.addEventListener('click', () => {
  const value = el.baseUrlInput.value.trim();
  if (!value) return;
  state.baseUrl = value;
  localStorage.setItem('ledger_base_url', value);
  toast('Адрес API сохранён.');
  el.settingsPanel.classList.add('hidden');
});

/* ============================================================
   INIT
   ============================================================ */
(function init() {
  if (state.token) {
    el.loginInput.value = state.login;
    enterDashboard();
  }
})();