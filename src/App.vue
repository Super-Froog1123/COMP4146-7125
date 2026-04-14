<template>
  <div class="app-layout">
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
import { computed, onMounted, onUnmounted, ref } from 'vue';
import Sidebar from './components/Sidebar.vue';
import ChatWindow from './components/ChatWindow.vue';

const conversationList = ref([]);
const activeConversationId = ref('');
const loading = ref(false);
const errorMessage = ref('');
const conversationCounter = ref(1);
const sidebarCollapsed = ref(false);

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

// appendMessageContent(conversation: object, messageId: string, token: string)：
// 向已有消息追加内容，用于流式输出逐 token 更新
function appendMessageContent(conversation, messageId, token) {
  const message = conversation.messageList.find((item) => item.id === messageId);
  if (message) {
    message.content += token;
    conversation.updatedAt = nowISO();
  }
}

// updateMessageStatus(conversation: object, messageId: string, status: string)：
// 更新消息状态（sent / error）
function updateMessageStatus(conversation, messageId, status) {
  const message = conversation.messageList.find((item) => item.id === messageId);
  if (message) {
    message.status = status;
  }
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
// 删除会话，列表清空则置空 activeConversationId
function handleRemoveConversation(conversationId) {
  const index = conversationList.value.findIndex((item) => item.id === conversationId);
  if (index === -1) return;

  const isActive = conversationId === activeConversationId.value;
  conversationList.value.splice(index, 1);

  if (conversationList.value.length === 0) {
    activeConversationId.value = '';
    errorMessage.value = '';
    return;
  }

  if (isActive) {
    const nextConversation = conversationList.value[index] || conversationList.value[index - 1];
    activeConversationId.value = nextConversation.id;
    errorMessage.value = '';
  }
}

function buildRequestPayload(conversation, text, searchMode) {
  return {
    question: text,
    context: 'None',
    is_search: searchMode,
    use_neural_retrieval: false
  };
}






// requestAssistantReply(conversation, text, onToken)：
// 向后端发送请求并流式读取回复，每收到一个 token 调用 onToken(token)
async function requestAssistantReply(conversation, text, onToken, searchMode) {
  const payload = buildRequestPayload(conversation, text, searchMode);
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

  const reader = response.body.getReader();
  const decoder = new TextDecoder('utf-8');

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const token = decoder.decode(value, { stream: true });
    onToken(token);
  }
}






// handleSendMessage(content: string)：
// 发送主流程（校验/追加/流式回复/loading/错误）
async function handleSendMessage(content, searchMode = false) {
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

  // 先创建一条空的 assistant 消息，用于流式追加
  const assistantMessageId = generateId();
  const targetConversation = getConversationById(currentId);
  if (!targetConversation) return;
  targetConversation.messageList.push({
    id: assistantMessageId,
    role: 'assistant',
    content: '',
    status: 'loading',
    time: nowISO()
  });
  targetConversation.updatedAt = nowISO();

  loading.value = true;
  try {
    await requestAssistantReply(conversation, text, (token) => {
      const conv = getConversationById(currentId);
      if (conv) {
        appendMessageContent(conv, assistantMessageId, token);
      }
    }, searchMode);
    const conv = getConversationById(currentId);
    if (conv) {
      updateMessageStatus(conv, assistantMessageId, 'sent');
    }
  } catch (error) {
    const conv = getConversationById(currentId);
    if (conv) {
      const message = conv.messageList.find((item) => item.id === assistantMessageId);
      if (message && !message.content) {
        message.content = 'Sorry, the response failed this time. Please try again.';
      }
      updateMessageStatus(conv, assistantMessageId, 'error');
    }
    errorMessage.value = 'Reply failed, please try again later.';
  } finally {
    loading.value = false;
  }
}

ensureConversation();

// 小屏幕时自动折叠侧边栏
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
</script>

<style scoped>
.app-layout {
  display: grid;
  grid-template-columns: v-bind("sidebarCollapsed ? '48px' : '280px'") 1fr;
  height: 100vh;
  background: #f4f6fb;
  transition: grid-template-columns 0.2s;
}
</style>
