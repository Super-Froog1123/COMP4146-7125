<template>
  <div class="app-layout" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <Sidebar
      :conversation-list="conversationList"
      :active-conversation-id="activeConversationId"
      :collapsed="sidebarCollapsed"
      @create="handleCreateConversation"
      @select="handleSelectConversation"
      @remove="handleRemoveConversation"
      @toggle-collapse="sidebarCollapsed = !sidebarCollapsed"
    />
    <ChatWindow
      :conversation="activeConversation"
      :loading="loading"
      :error-message="errorMessage"
      :suggestions="suggestionList"
      @send="handleSendMessage"
      @use-suggestion="handleSendMessage"
    />
  </div>
</template>

<script setup>
import { computed, ref, watch, onMounted, onUnmounted } from 'vue';
import Sidebar from './components/Sidebar.vue';
import ChatWindow from './components/ChatWindow.vue';
import { loadConversations, saveConversations, loadActiveId, saveActiveId } from './historyManager.js';

const conversationList = ref(loadConversations());
const activeConversationId = ref(loadActiveId());
const loading = ref(false);
const errorMessage = ref('');
const conversationCounter = ref(
  conversationList.value.length > 0
    ? Math.max(...conversationList.value.map((c) => parseInt(c.title.match(/\d+/)?.[0] || '0'))) + 1
    : 1
);
const sidebarCollapsed = ref(false);

// 小屏时默认折叠，监听窗口变化
function handleResize() {
  if (window.innerWidth <= 920) {
    sidebarCollapsed.value = true;
  }
}
onMounted(() => {
  handleResize();
  window.addEventListener('resize', handleResize);
});
onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});

// 对话列表或激活ID变化时自动保存到 localStorage
watch(
  () => [conversationList.value, activeConversationId.value],
  () => {
    saveConversations(conversationList.value);
    saveActiveId(activeConversationId.value);
  },
  { deep: true }
);

const suggestionList = [
  "ITM's teaching syllabus",
  "Course requirements for COMP7125",
  "COMP7125 Exam Time"
];

const activeConversation = computed(() => {
  return conversationList.value.find((item) => item.id === activeConversationId.value) || null;
});

const nowISO = () => new Date().toISOString();
const generateId = () => `${Date.now()}-${Math.random().toString(16).slice(2)}`;
const CHAT_API_URL = '/api/ask';

const SYSTEM_PROMPT = '';


// createConversation(title: string)：
// 创建会话，返回 { id, title, messageList, createdAt, updatedAt }
function createConversation(title) {
  const time = nowISO();
  return {
    id: generateId(),
    title,
    messageList: [],
    createdAt: time,
    updatedAt: time
  };
}

// getConversationById(conversationId: string)：
// 根据会话 id 获取目标会话
function getConversationById(conversationId) {
  return conversationList.value.find((item) => item.id === conversationId);
}

// pushMessage(conversation: object, payload: object)：
// 追加消息并刷新 updatedAt
function pushMessage(conversation, payload) {
  conversation.messageList.push({
    id: generateId(),
    role: payload.role,
    content: payload.content,
    status: payload.status || 'sent',
    time: nowISO()
  });
  conversation.updatedAt = nowISO();
}

// createDefaultTitle()：
// 生成默认标题（新对话 1/2/3...）
function createDefaultTitle() {
  const title = `新对话 ${conversationCounter.value}`;
  conversationCounter.value += 1;
  return title;
}

// createTitleFromFirstMessage(message: string)：
// 根据首条消息生成标题
function createTitleFromFirstMessage(message) {
  const trimmed = message.trim();
  if (!trimmed) return createDefaultTitle();
  const maxLength = 18;
  return trimmed.length > maxLength ? `${trimmed.slice(0, maxLength)}...` : trimmed;
}

// ensureConversation()：
// 保证至少存在一个会话
function ensureConversation() {
  if (conversationList.value.length > 0) return;
  const firstConversation = createConversation(createDefaultTitle());
  conversationList.value.push(firstConversation);
  activeConversationId.value = firstConversation.id;
}

// handleCreateConversation()：
// 新建并激活会话
function handleCreateConversation() {
  const conversation = createConversation(createDefaultTitle());
  conversationList.value.unshift(conversation);
  activeConversationId.value = conversation.id;
  errorMessage.value = '';
}

// handleSelectConversation(conversationId: string)：
// 切换会话
function handleSelectConversation(conversationId) {
  activeConversationId.value = conversationId;
  errorMessage.value = '';
}

// handleRemoveConversation(conversationId: string)：
// 删除会话
function handleRemoveConversation(conversationId) {
  const index = conversationList.value.findIndex((item) => item.id === conversationId);
  if (index === -1) return;

  const isActive = conversationId === activeConversationId.value;
  conversationList.value.splice(index, 1);

  if (conversationList.value.length === 0) {
    activeConversationId.value = '';
    return;
  }

  if (isActive) {
    const nextConversation = conversationList.value[index] || conversationList.value[index - 1];
    activeConversationId.value = nextConversation.id;
    errorMessage.value = '';
  }
}

function buildRequestPayload(conversation, text, searchMode = false) {
  const context = [{ role: 'system', content: SYSTEM_PROMPT }];
  for (const item of conversation.messageList) {
    context.push({ role: item.role, content: item.content });
  }
  return {
    question: text,
    context,
    is_search: searchMode,
    use_neural_retrieval: false
  };
}



// 向后端发送请求并流式读取回复
async function requestAssistantReply(conversation, text, searchMode = false) {
  const payload = buildRequestPayload(conversation, text, searchMode);
  console.log('%c[REQUEST] POST /api/ask', 'color: #60a5fa; font-weight: bold');
  console.log(JSON.stringify(payload, null, 2));
  const response = await fetch(CHAT_API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error(`请求失败: ${response.status}`);
  }

  // 先插入一条空的 assistant 消息
  const currentId = activeConversationId.value;
  const targetConversation = getConversationById(currentId);
  if (!targetConversation) return;
  pushMessage(targetConversation, {
    role: 'assistant',
    content: ''
  });
  const assistantMsg = targetConversation.messageList[targetConversation.messageList.length - 1];

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const chunk = decoder.decode(value, { stream: true });
    assistantMsg.content += chunk;
  }
}






// handleSendMessage(content: string)：
// 发送主流程（校验/追加/回复/loading/错误）
async function handleSendMessage(content, searchMode = false) {
  const text = content.trim();
  if (!text || loading.value) return;

  // 列表为空时先自动创建对话
  if (conversationList.value.length === 0) {
    handleCreateConversation();
  }

  const currentId = activeConversationId.value;
  const conversation = getConversationById(currentId);
  if (!conversation) return;

  errorMessage.value = '';
  pushMessage(conversation, {
    role: 'user',
    content: text
  });

  if (conversation.messageList.length === 1 && conversation.title.startsWith('新对话')) {
    conversation.title = createTitleFromFirstMessage(text);
  }

  loading.value = true;
  try {
    await requestAssistantReply(conversation, text, searchMode);
  } catch (error) {
    const targetConversation = getConversationById(currentId);
    if (targetConversation) {
      pushMessage(targetConversation, {
        role: 'assistant',
        content: 'Sorry, the response failed this time. Please try again.',
        status: 'error'
      });
    }
    errorMessage.value = 'Reply failed, please try again later.';
  } finally {
    loading.value = false;
  }
}

ensureConversation();
</script>

<style scoped>
.app-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  height: 100vh;
  background: #f4f6fb;
  transition: grid-template-columns 0.2s;
}

.app-layout.sidebar-collapsed {
  grid-template-columns: 48px 1fr;
}

@media (max-width: 920px) {
  .app-layout {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
  }

  .app-layout.sidebar-collapsed {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
  }
}
</style>
