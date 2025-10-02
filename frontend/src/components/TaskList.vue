<template>
  <div v-if="tasks.length" class="list-group">
    <TaskItem
      v-for="task in tasks"
      :key="task.id"
      :task="task"
    />
  </div>
  <p v-else class="text-muted">表示できるタスクがありません。</p>
</template>

<script setup>
import { defineProps } from 'vue'
import TaskItem from './TaskItem.vue'

defineProps({
  tasks: {
    type: Array,
    default: () => []
  }
})
</script>
