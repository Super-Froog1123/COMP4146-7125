<template>
  <div class="app-layout">
    <Sidebar
      :conversation-list="conversationList"
      :active-conversation-id="activeConversationId"
      @create="handleCreateConversation"
      @select="handleSelectConversation"
      @remove="handleRemoveConversation"
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
import { computed, ref } from 'vue';
import Sidebar from './components/Sidebar.vue';
import ChatWindow from './components/ChatWindow.vue';

const conversationList = ref([]);
const activeConversationId = ref('');
const loading = ref(false);
const errorMessage = ref('');
const conversationCounter = ref(1);

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
const CHAT_API_URL = '/api/chat';


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
// 删除会话并兜底处理
function handleRemoveConversation(conversationId) {
  const index = conversationList.value.findIndex((item) => item.id === conversationId);
  if (index === -1) return;

  const isActive = conversationId === activeConversationId.value;
  conversationList.value.splice(index, 1);

  if (conversationList.value.length === 0) {
    const fallback = createConversation(createDefaultTitle());
    conversationList.value.push(fallback);
    activeConversationId.value = fallback.id;
    errorMessage.value = '';
    return;
  }

  if (isActive) {
    const nextConversation = conversationList.value[index] || conversationList.value[index - 1];
    activeConversationId.value = nextConversation.id;
    errorMessage.value = '';
  }
}

function buildRequestPayload(conversation, text) {
  return {
    conversationId: conversation.id,
    message: {
      role: 'user',
      content: text
    },
    history: conversation.messageList.map((item) => ({
      role: item.role,
      content: item.content
    }))
  };
}

function extractAssistantContent(data) {
  if (typeof data?.reply === 'string' && data.reply.trim()) return data.reply;
  if (typeof data?.content === 'string' && data.content.trim()) return data.content;
  if (typeof data?.message?.content === 'string' && data.message.content.trim()) {
    return data.message.content;
  }
  throw new Error('后端返回格式不正确，缺少回复内容');
}

async function requestAssistantReply(conversation, text) {
  const payload = buildRequestPayload(conversation, text);
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

  const data = await response.json();
  return extractAssistantContent(data);
}

// handleSendMessage(content: string)：
// 发送主流程（校验/追加/回复/loading/错误）
async function handleSendMessage(content) {
  const text = content.trim();
  if (!text || loading.value) return;

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
    const reply = await requestAssistantReply(conversation, text);
    const targetConversation = getConversationById(currentId);
    if (!targetConversation) return;
    pushMessage(targetConversation, {
      role: 'assistant',
      content: reply
    });
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
}

@media (max-width: 920px) {
  .app-layout {
    grid-template-columns: 1fr;
    grid-template-rows: 220px 1fr;
  }
}
</style>
