<template>
  <section class="welcome">
    <h1>Hello! I'm your HKBU Study Companion</h1>
    <p>You can start with the following question, or enter your question directly.</p>

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
