<template>
  <div class="list-group-item">
    <div class="d-flex justify-content-between align-items-center">
      <div>
        <strong>{{ task.title }}</strong>
        <small class="ms-2 text-muted">{{ task.assignee }} / {{ task.owner }}</small>
      </div>
      <span class="badge" :class="statusClass">{{ task.status }}</span>
    </div>
    <p class="mb-1 text-muted">{{ task.detail }}</p>
    <ul class="list-inline small mb-0">
      <li class="list-inline-item">優先度: {{ task.priority }}</li>
      <li class="list-inline-item">作業量: {{ task.effort }}</li>
      <li class="list-inline-item">期間: {{ task.start_date }} ~ {{ task.due_date }}</li>
    </ul>
    <div class="mt-3 d-flex flex-wrap gap-2">
      <button
        type="button"
        class="btn btn-sm btn-outline-primary"
        @click="emit('edit', task)"
      >
        編集
      </button>
      <button
        type="button"
        class="btn btn-sm btn-outline-secondary"
        @click="emit('add-child', task)"
      >
        子タスク追加
      </button>
      <button
        type="button"
        class="btn btn-sm btn-outline-danger"
        @click="emit('delete', task)"
      >
        削除
      </button>
    </div>
    <div v-if="task.children?.length" class="mt-3 ms-3 border-start ps-3">
      <TaskItem
        v-for="child in task.children"
        :key="child.id"
        :task="child"
        @edit="emit('edit', $event)"
        @delete="emit('delete', $event)"
        @add-child="emit('add-child', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, defineEmits, defineProps } from 'vue'

const props = defineProps({
  task: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['edit', 'delete', 'add-child'])

const statusClass = computed(() => {
  const status = props.task.status
  if (status === '完了') return 'bg-success'
  if (status === '作業中') return 'bg-primary'
  return 'bg-secondary'
})
</script>
