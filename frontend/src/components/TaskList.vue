<template>
  <div v-if="tasks.length" class="list-group">
    <TaskItem
      v-for="task in tasks"
      :key="task.id"
      :task="task"
      @edit="emit('edit', $event)"
      @delete="emit('delete', $event)"
      @add-child="emit('add-child', $event)"
    />
  </div>
  <p v-else class="text-muted">表示できるタスクがありません。</p>
</template>

<script setup>
import { defineEmits, defineProps } from 'vue'
import TaskItem from './TaskItem.vue'

defineProps({
  tasks: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['edit', 'delete', 'add-child'])
</script>
