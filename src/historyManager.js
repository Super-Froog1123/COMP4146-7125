const STORAGE_KEY = 'chat_conversations';
const ACTIVE_KEY = 'chat_active_id';

export function loadConversations() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function saveConversations(list) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
}

export function loadActiveId() {
  return localStorage.getItem(ACTIVE_KEY) || '';
}

export function saveActiveId(id) {
  localStorage.setItem(ACTIVE_KEY, id);
}
