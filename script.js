const STORAGE_KEY = 'loginLogoutTrackerData';

const nameInput = document.getElementById('nameInput');
const sectionInput = document.getElementById('sectionInput');
const loginButton = document.getElementById('loginButton');
const logoutButton = document.getElementById('logoutButton');
const exportButton = document.getElementById('exportButton');
const statusMessage = document.getElementById('statusMessage');
const logTableBody = document.getElementById('logTableBody');
const sessionTableBody = document.getElementById('sessionTableBody');
const tabButtons = document.querySelectorAll('.tab-button');
const tabs = document.querySelectorAll('.tab-panel');

let state = {
  users: [],
  sessions: [],
  logs: []
};

function loadState() {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored) {
    try {
      state = JSON.parse(stored);
    } catch (error) {
      console.error('Unable to parse saved state:', error);
      state = { users: [], sessions: [], logs: [] };
    }
  }
}

function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function getUserId(name, section) {
  const trimmedName = name.trim();
  const trimmedSection = section.trim();
  const existing = state.users.find(
    (user) => user.name.toLowerCase() === trimmedName.toLowerCase() && user.section.toLowerCase() === trimmedSection.toLowerCase()
  );
  if (existing) return existing.id;

  const id = Date.now() + Math.floor(Math.random() * 1000);
  const createdAt = currentTimestamp();
  state.users.push({ id, name: trimmedName, section: trimmedSection, createdAt });
  return id;
}

function getOpenSession(userId) {
  return state.sessions.find((session) => session.userId === userId && !session.logoutTime);
}

function currentTimestamp() {
  return new Date().toISOString().slice(0, 19).replace('T', ' ');
}

function showStatus(message, isError = false) {
  statusMessage.textContent = message;
  statusMessage.style.color = isError ? '#b91c1c' : '#0f172a';
}

function clearStatus() {
  statusMessage.textContent = '';
}

function validateInputs() {
  const name = nameInput.value.trim();
  const section = sectionInput.value.trim();
  if (!name || !section) {
    showStatus('Please enter both Name and Section.', true);
    return null;
  }
  return { name, section };
}

function addLogEntry(userId, actionType) {
  const timestamp = currentTimestamp();
  const id = Date.now() + Math.floor(Math.random() * 1000);
  state.logs.push({ id, userId, actionType, timestamp });
  return timestamp;
}

function createSession(userId, loginTime) {
  state.sessions.push({ id: Date.now() + Math.floor(Math.random() * 1000), userId, loginTime, logoutTime: null });
}

function closeSession(userId, logoutTime) {
  const session = getOpenSession(userId);
  if (session) {
    session.logoutTime = logoutTime;
  }
}

function logIn() {
  clearStatus();
  const values = validateInputs();
  if (!values) return;

  const userId = getUserId(values.name, values.section);
  if (getOpenSession(userId)) {
    showStatus('Already logged in. Please log out before a new login.', true);
    return;
  }

  const timestamp = currentTimestamp();
  createSession(userId, timestamp);
  addLogEntry(userId, 'In');
  saveState();
  renderTables();
  showStatus(`Logged in ${values.name} (${values.section}) at ${timestamp}`);
}

function logOut() {
  clearStatus();
  const values = validateInputs();
  if (!values) return;

  const userId = getUserId(values.name, values.section);
  const openSession = getOpenSession(userId);
  if (!openSession) {
    showStatus('No open login session found. Please log in first.', true);
    return;
  }

  const timestamp = currentTimestamp();
  closeSession(userId, timestamp);
  addLogEntry(userId, 'Out');
  saveState();
  renderTables();
  showStatus(`Logged out ${values.name} (${values.section}) at ${timestamp}`);
}

function renderTables() {
  logTableBody.innerHTML = '';
  sessionTableBody.innerHTML = '';

  const sortedLogs = [...state.logs].sort((a, b) => a.timestamp.localeCompare(b.timestamp));
  sortedLogs.forEach((log) => {
    const user = state.users.find((u) => u.id === log.userId) || { name: 'Unknown', section: 'Unknown' };
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${log.timestamp}</td>
      <td>${user.name}</td>
      <td>${user.section}</td>
      <td>${log.actionType}</td>
    `;
    logTableBody.appendChild(row);
  });

  const sortedSessions = [...state.sessions].sort((a, b) => a.loginTime.localeCompare(b.loginTime));
  sortedSessions.forEach((session) => {
    const user = state.users.find((u) => u.id === session.userId) || { name: 'Unknown', section: 'Unknown' };
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${session.loginTime}</td>
      <td>${session.logoutTime || 'OPEN'}</td>
      <td>${user.name}</td>
      <td>${user.section}</td>
    `;
    sessionTableBody.appendChild(row);
  });
}

function exportCsv() {
  if (!state.logs.length) {
    showStatus('No log history available to export.', true);
    return;
  }

  const rows = [ ['Timestamp', 'Name', 'Section', 'Action Type'] ];
  const sortedLogs = [...state.logs].sort((a, b) => a.timestamp.localeCompare(b.timestamp));
  sortedLogs.forEach((log) => {
    const user = state.users.find((u) => u.id === log.userId) || { name: 'Unknown', section: 'Unknown' };
    rows.push([log.timestamp, user.name, user.section, log.actionType]);
  });

  const csvContent = rows.map((r) => r.map(escapeCsv).join(',')).join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = 'login_history.csv';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  showStatus('Export completed: login_history.csv');
}

function escapeCsv(value) {
  const stringValue = value == null ? '' : String(value);
  if (/[",\n]/.test(stringValue)) {
    return '"' + stringValue.replace(/"/g, '""') + '"';
  }
  return stringValue;
}

function setupTabs() {
  tabButtons.forEach((button) => {
    button.addEventListener('click', () => {
      const target = button.dataset.tab;
      tabButtons.forEach((btn) => btn.classList.toggle('active', btn === button));
      tabs.forEach((panel) => panel.classList.toggle('active', panel.id === `${target}Tab`));
    });
  });
}

loginButton.addEventListener('click', logIn);
logoutButton.addEventListener('click', logOut);
exportButton.addEventListener('click', exportCsv);

loadState();
setupTabs();
renderTables();
