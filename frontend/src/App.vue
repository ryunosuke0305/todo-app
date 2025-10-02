<template>
  <main class="container py-4">
    <header class="mb-4">
      <h1 class="h3">タスク一覧</h1>
      <p class="text-muted">Flask バックエンドから取得したサンプルタスクを表示します。</p>
    </header>
    <TaskList :tasks="tasks" />
  </main>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import axios from 'axios'
import TaskList from './components/TaskList.vue'

const tasks = ref([])

onMounted(async () => {
  const response = await axios.get('/api/tasks')
  tasks.value = response.data.tasks
})
</script>
