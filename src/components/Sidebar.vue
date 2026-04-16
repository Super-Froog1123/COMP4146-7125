<template>
  <aside class="sidebar" :class="{ collapsed, 'mobile-open': !collapsed }">
    <button class="toggle-btn" type="button" @click="$emit('toggle-collapse')">
      {{ collapsed ? '>' : '<' }}
    </button>

    <div class="sidebar-body" :class="{ open: !collapsed }">
      <button class="close-btn" type="button" @click="$emit('toggle-collapse')">Close</button>
      <div class="sidebar-header">
        <h2>Conversations</h2>
        <button class="new-btn" type="button" @click="$emit('create')">+ Add</button>
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
            title="Delete conversation"
            @click.stop="$emit('remove', conversation.id)"
          >
            Delete
          </button>
        </li>
      </ul>
    </div>
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
  },
  collapsed: {
    type: Boolean,
    default: false
  }
});

// emits
// create：新建会话
// select(conversationId: string)：切换会话
// remove(conversationId: string)：删除会话
// toggle-collapse：折叠/展开
defineEmits(['create', 'select', 'remove', 'toggle-collapse']);

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
  position: relative;
  border-right: 1px solid #e7eaf2;
  background: #ffffff;
  overflow-y: auto;
  transition: padding 0.2s;
  padding: 16px;
}

.sidebar.collapsed {
  padding: 8px;
}

.toggle-btn {
  display: block;
  width: 32px;
  height: 32px;
  border: 1px solid #e6ebf5;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
  font-size: 14px;
  margin-bottom: 8px;
  flex-shrink: 0;
}

.sidebar.collapsed .toggle-btn {
  margin: 0 auto;
}

.sidebar-body {
  display: none;
}

.sidebar-body.open {
  display: block;
}

.close-btn {
  display: none;
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

/* ===== 小屏：按钮在左侧，对话列表从顶部弹出 ===== */
@media (max-width: 920px) {
  .sidebar {
    position: static;
    padding: 8px;
    overflow: visible;
    border-right: none;
    border-bottom: 1px solid #e7eaf2;
  }

  .sidebar.collapsed {
    padding: 8px;
  }

  .toggle-btn {
    margin: 0;
  }

  .sidebar-body {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    max-height: 60vh;
    background: #ffffff;
    border-bottom: 1px solid #e7eaf2;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
    padding: 12px 16px;
    overflow-y: auto;
    z-index: 100;
  }

  .sidebar-body.open {
    display: block;
  }

  .close-btn {
    display: block;
    width: 100%;
    border: 1px solid #e6ebf5;
    border-radius: 6px;
    background: #fff;
    padding: 8px;
    cursor: pointer;
    font-size: 14px;
    color: #6b7280;
    margin-bottom: 8px;
  }
}
</style>
