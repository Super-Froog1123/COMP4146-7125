<template>
  <section class="chat-window">
    <header class="chat-header">
      <h2>{{ conversation?.title || '新对话' }}</h2>
      <span v-if="loading" class="loading">...</span>
    </header>

    <div ref="messageContainerRef" class="message-container">
      <Welcome
        v-if="messageList.length === 0"
        :suggestions="suggestions"
        @select="$emit('use-suggestion', $event, searchMode)"
      />

      <div
        v-for="message in messageList"
        :key="message.id"
        class="message-row"
        :class="message.role"
      >
        <div class="message-bubble" :class="{ error: message.status === 'error' }">
          <div v-if="message.role === 'assistant'" class="md-content" v-html="renderMarkdown(message.content)"></div>
          <p v-else>{{ message.content }}</p>
          <time>{{ formatTime(message.time) }}</time>
        </div>
      </div>
    </div>

    <p v-if="errorMessage" class="error-tip">{{ errorMessage }}</p>

    <form class="input-area" @submit.prevent="onSend">
      <button
        type="button"
        class="search-btn"
        :class="{ active: searchMode }"
        @click="searchMode = !searchMode"
      >
        {{ searchMode ? 'Search ON' : 'Search OFF' }}
      </button>
      <textarea
        v-model="draft"
        class="input"
        placeholder="Input content, Click Enter to send, Shift + Enter to line break"
        rows="2"
        @keydown.enter.exact.prevent="onSend"
      />
      <button type="submit" class="send-btn" :disabled="sendDisabled">Send</button>
    </form>
  </section>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue';
import Welcome from './Welcome.vue';
import { marked } from 'marked';

// props
// conversation: object | null：当前会话
// loading: boolean：加载状态
// errorMessage: string：错误提示
// suggestions: Array<string>：示例问题
const props = defineProps({
  conversation: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  },
  errorMessage: {
    type: String,
    default: ''
  },
  suggestions: {
    type: Array,
    default: () => []
  }
});

// emits
// send(text: string)：发送消息
// use-suggestion(text: string)：触发示例问题
const emit = defineEmits(['send', 'use-suggestion']);
const draft = ref('');
const messageContainerRef = ref(null);
const searchMode = ref(false);

const messageList = computed(() => props.conversation?.messageList || []);
const sendDisabled = computed(() => !draft.value.trim() || props.loading);

// renderMarkdown(text: string)：将 Markdown 文本转为 HTML
function renderMarkdown(text) {
  if (!text) return '';
  return marked.parse(text, { breaks: true });
}

// onSend()：读取输入并发送，清空输入
// formatTime(value: string)：格式化为 HH:mm
// scrollToBottom()：自动滚动到底部
// watch([...])：监听消息/加载/会话变化触发滚动
function onSend() {
  const text = draft.value.trim();
  if (!text || props.loading) return;
  emit('send', text, searchMode.value);
  draft.value = '';
}

function formatTime(value) {
  if (!value) return '';
  return new Date(value).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit'
  });
}

async function scrollToBottom() {
  await nextTick();
  const element = messageContainerRef.value;
  if (!element) return;
  element.scrollTop = element.scrollHeight;
}

watch(
  () => [messageList.value.length, props.loading, props.conversation?.id],
  () => {
    scrollToBottom();
  },
  { immediate: true }
);
</script>

<style scoped>
.chat-window {
  display: grid;
  grid-template-rows: auto 1fr auto auto;
  gap: 12px;
  height: 100%;
  padding: 16px;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

h2 {
  margin: 0;
  font-size: 18px;
}

.loading {
  color: #1d4ed8;
  font-size: 13px;
}

.message-container {
  border: 1px solid #e2e8f5;
  background: #ffffff;
  border-radius: 12px;
  padding: 14px;
  overflow-y: auto;
}

.message-row {
  display: flex;
  margin-bottom: 10px;
}

.message-row.user {
  justify-content: flex-end;
}

.message-row.assistant {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 72%;
  border-radius: 10px;
  padding: 10px;
  background: #f3f4f6;
}

.message-row.user .message-bubble {
  background: #dbeafe;
}

.message-bubble.error {
  border: 1px solid #ef4444;
  background: #fee2e2;
}

.message-bubble p {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.5;
}

.message-bubble .md-content {
  line-height: 1.6;
  word-break: break-word;
}

.message-bubble .md-content p {
  margin: 0 0 8px;
  white-space: normal;
}

.message-bubble .md-content p:last-child {
  margin-bottom: 0;
}

.message-bubble .md-content code {
  background: #e5e7eb;
  border-radius: 4px;
  padding: 2px 5px;
  font-size: 13px;
}

.message-bubble .md-content pre {
  background: #1e293b;
  color: #e2e8f0;
  border-radius: 8px;
  padding: 12px;
  overflow-x: auto;
  margin: 8px 0;
}

.message-bubble .md-content pre code {
  background: none;
  padding: 0;
  color: inherit;
}

.message-bubble .md-content ul,
.message-bubble .md-content ol {
  margin: 4px 0;
  padding-left: 20px;
}

.message-bubble .md-content li {
  margin: 2px 0;
}

.message-bubble .md-content blockquote {
  border-left: 3px solid #1d4ed8;
  margin: 8px 0;
  padding: 4px 12px;
  color: #4b5563;
}

.message-bubble .md-content h1,
.message-bubble .md-content h2,
.message-bubble .md-content h3 {
  margin: 8px 0 4px;
}

.message-bubble .md-content table {
  border-collapse: collapse;
  margin: 8px 0;
}

.message-bubble .md-content th,
.message-bubble .md-content td {
  border: 1px solid #d1d5db;
  padding: 6px 10px;
}

.message-bubble .md-content th {
  background: #f3f4f6;
}

.message-bubble time {
  display: block;
  margin-top: 6px;
  color: #6b7280;
  font-size: 12px;
  text-align: right;
}

.error-tip {
  margin: 0;
  font-size: 13px;
  color: #dc2626;
}

.input-area {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 10px;
}

.search-btn {
  border: 1px solid #d9e3f7;
  border-radius: 10px;
  padding: 0 14px;
  background: #fff;
  color: #6b7280;
  cursor: pointer;
  font-size: 13px;
  white-space: nowrap;
}

.search-btn.active {
  border-color: #1d4ed8;
  background: #dbeafe;
  color: #1d4ed8;
}

.input {
  width: 100%;
  resize: vertical;
  border: 1px solid #cfd8ea;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 14px;
  font-family: inherit;
}

.send-btn {
  border: none;
  border-radius: 10px;
  padding: 0 18px;
  background: #1d4ed8;
  color: #fff;
  cursor: pointer;
}

.send-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

@media (max-width: 920px) {
  .message-bubble {
    max-width: 88%;
  }
}
</style>
