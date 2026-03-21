<template>
  <section class="welcome">
    <h1>欢迎使用 ChatBot Demo</h1>
    <p>这是一个前端聊天骨架。你可以从下面的问题开始，或直接输入你的问题。</p>

    <div class="suggestion-list">
      <button
        v-for="item in suggestions"
        :key="item"
        type="button"
        class="suggestion-btn"
        @click="$emit('select', item)"
      >
        {{ item }}
      </button>
    </div>
  </section>
</template>

<script setup>
// props
// suggestions: Array<string>：示例问题
defineProps({
  suggestions: {
    type: Array,
    default: () => []
  }
});

// emits
// select(question: string)：选择问题
defineEmits(['select']);
</script>

<style scoped>
.welcome {
  border: 1px dashed #cfd8ea;
  background: #f8fbff;
  border-radius: 14px;
  padding: 20px;
}

h1 {
  margin: 0 0 8px;
  font-size: 24px;
}

p {
  margin: 0 0 16px;
  color: #4b5563;
}

.suggestion-list {
  display: grid;
  gap: 10px;
}

.suggestion-btn {
  text-align: left;
  border: 1px solid #d9e3f7;
  background: #fff;
  border-radius: 10px;
  padding: 12px;
  cursor: pointer;
}

.suggestion-btn:hover {
  border-color: #1d4ed8;
}
</style>
