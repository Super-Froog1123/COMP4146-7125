<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <h2>会话列表</h2>
      <button class="new-btn" type="button" @click="$emit('create')">+ 新建</button>
    </div>

    <ul class="conversation-list">
      <li
        v-for="conversation in conversationList"
        :key="conversation.id"
        class="conversation-item"
        :class="{ active: conversation.id === activeConversationId }"
        @click="$emit('select', conversation.id)"
      >
        <div class="meta">
          <p class="title">{{ conversation.title }}</p>
          <p class="time">{{ formatTime(conversation.updatedAt) }}</p>
        </div>
        <button
          class="delete-btn"
          type="button"
          title="删除会话"
          @click.stop="$emit('remove', conversation.id)"
        >
          删除
        </button>
      </li>
    </ul>
  </aside>
</template>

<script setup>
// props
// conversationList: Array：会话列表
// activeConversationId: string：当前激活会话
const props = defineProps({
  conversationList: {
    type: Array,
    default: () => []
  },
  activeConversationId: {
    type: String,
    default: ''
  }
});

// emits
// create：新建会话
// select(conversationId: string)：切换会话
// select(conversationId: string)：切换会话
defineEmits(['create', 'select', 'remove']);

// formatTime(value: string)：格式化时间展示
function formatTime(value) {
  if (!value) return '';
  const date = new Date(value);
  return date.toLocaleString([], {
    hour: '2-digit',
    minute: '2-digit',
    month: '2-digit',
    day: '2-digit'
  });
}
</script>

<style scoped>
.sidebar {
  border-right: 1px solid #e7eaf2;
  background: #ffffff;
  padding: 16px;
  overflow-y: auto;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

h2 {
  margin: 0;
  font-size: 16px;
}

.new-btn {
  border: none;
  background: #1d4ed8;
  color: #fff;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
}

.conversation-list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.conversation-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  border: 1px solid #e6ebf5;
  border-radius: 10px;
  padding: 10px;
  cursor: pointer;
}

.conversation-item.active {
  border-color: #1d4ed8;
  background: #eef4ff;
}

.meta {
  min-width: 0;
}

.title {
  margin: 0;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.time {
  margin: 4px 0 0;
  color: #6b7280;
  font-size: 12px;
}

.delete-btn {
  border: 1px solid #e5e7eb;
  background: #fff;
  color: #ef4444;
  padding: 6px 8px;
  border-radius: 6px;
  cursor: pointer;
  flex-shrink: 0;
}
</style>
