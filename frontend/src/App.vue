<template>
  <main class="container py-4">
    <header class="mb-4">
      <h1 class="h3">タスク管理</h1>
      <p class="text-muted mb-0">API を通じてタスクの登録・更新・削除が行えます。</p>
    </header>

    <section class="mb-5">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h2 class="h5 mb-0">
          {{ isEditing ? 'タスクを更新' : 'タスクを登録' }}
          <span v-if="isEditing" class="badge bg-warning text-dark ms-2">編集中</span>
        </h2>
        <button
          type="button"
          class="btn btn-outline-success btn-sm"
          @click="resetForm()"
        >
          新規タスク
        </button>
      </div>
      <div v-if="errorMessage" class="alert alert-danger" role="alert">
        {{ errorMessage }}
      </div>
      <div
        v-if="formTask.parent_id"
        class="alert alert-info d-flex justify-content-between align-items-center"
        role="alert"
      >
        <span>
          親タスク: <strong>{{ parentTitle || formTask.parent_id }}</strong>
        </span>
        <button
          type="button"
          class="btn btn-sm btn-outline-light text-dark"
          @click="resetForm()"
        >
          親タスク解除
        </button>
      </div>
      <form class="row g-3" @submit.prevent="handleSubmit">
        <div class="col-md-6">
          <label class="form-label">タイトル<span class="text-danger">*</span></label>
          <input
            type="text"
            class="form-control"
            v-model="formTask.title"
            required
          />
        </div>
        <div class="col-md-6">
          <label class="form-label">担当者</label>
          <input
            type="text"
            class="form-control"
            v-model="formTask.assignee"
          />
        </div>
        <div class="col-md-6">
          <label class="form-label">責任者</label>
          <input
            type="text"
            class="form-control"
            v-model="formTask.owner"
          />
        </div>
        <div class="col-12">
          <label class="form-label">詳細</label>
          <textarea
            class="form-control"
            rows="3"
            v-model="formTask.detail"
          ></textarea>
        </div>
        <div class="col-md-6">
          <label class="form-label">開始日<span class="text-danger">*</span></label>
          <input
            type="date"
            class="form-control"
            v-model="formTask.start_date"
            required
          />
        </div>
        <div class="col-md-6">
          <label class="form-label">期限<span class="text-danger">*</span></label>
          <input
            type="date"
            class="form-control"
            v-model="formTask.due_date"
            required
          />
        </div>
        <div class="col-md-4">
          <label class="form-label">ステータス</label>
          <select class="form-select" v-model="formTask.status">
            <option value="未着手">未着手</option>
            <option value="作業中">作業中</option>
            <option value="完了">完了</option>
          </select>
        </div>
        <div class="col-md-4">
          <label class="form-label">優先度</label>
          <select class="form-select" v-model="formTask.priority">
            <option value="低">低</option>
            <option value="中">中</option>
            <option value="高">高</option>
          </select>
        </div>
        <div class="col-md-4">
          <label class="form-label">作業量</label>
          <select class="form-select" v-model="formTask.effort">
            <option value="小">小</option>
            <option value="中">中</option>
            <option value="大">大</option>
          </select>
        </div>
        <div class="col-12 d-flex justify-content-end gap-2">
          <button
            v-if="isEditing"
            type="button"
            class="btn btn-outline-secondary"
            @click="resetForm()"
          >
            キャンセル
          </button>
          <button type="submit" class="btn btn-primary">
            {{ isEditing ? '更新する' : '追加する' }}
          </button>
        </div>
      </form>
    </section>

    <section>
      <h2 class="h5 mb-3">タスク一覧</h2>
      <TaskList
        :tasks="tasks"
        @edit="handleEdit"
        @delete="handleDelete"
        @add-child="handleAddChild"
      />
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import axios from 'axios'
import TaskList from './components/TaskList.vue'

const tasks = ref([])
const isEditing = ref(false)
const editingId = ref(null)
const errorMessage = ref('')
const formTask = reactive(createDefaultTask())

function createDefaultTask() {
  const today = new Date().toISOString().slice(0, 10)
  return {
    title: '',
    detail: '',
    assignee: '',
    owner: '',
    start_date: today,
    due_date: today,
    status: '未着手',
    priority: '中',
    effort: '中',
    parent_id: null
  }
}

function resetForm(parentId = null) {
  Object.assign(formTask, createDefaultTask())
  formTask.parent_id = parentId

  if (parentId) {
    const parent = findTaskById(tasks.value, parentId)
    if (parent) {
      formTask.start_date = parent.start_date
      formTask.due_date = parent.due_date
    }
  }

  isEditing.value = false
  editingId.value = null
  errorMessage.value = ''
}

async function loadTasks() {
  const response = await axios.get('/api/tasks')
  tasks.value = response.data.tasks
}

onMounted(() => {
  loadTasks().catch((error) => {
    errorMessage.value = resolveErrorMessage(error)
  })
})

const parentTitle = computed(() => {
  if (!formTask.parent_id) {
    return ''
  }
  const parent = findTaskById(tasks.value, formTask.parent_id)
  return parent ? parent.title : ''
})

async function handleSubmit() {
  const trimmedTitle = formTask.title.trim()
  if (!trimmedTitle) {
    errorMessage.value = 'タイトルを入力してください。'
    return
  }

  const payload = {
    ...formTask,
    title: trimmedTitle
  }

  try {
    if (isEditing.value && editingId.value) {
      await axios.put(`/api/tasks/${editingId.value}`, payload)
    } else {
      await axios.post('/api/tasks', payload)
    }
    await loadTasks()
    resetForm()
  } catch (error) {
    errorMessage.value = resolveErrorMessage(error)
  }
}

function handleEdit(task) {
  const defaults = createDefaultTask()
  isEditing.value = true
  editingId.value = task.id
  errorMessage.value = ''

  Object.assign(formTask, {
    title: task.title ?? defaults.title,
    detail: task.detail ?? defaults.detail,
    assignee: task.assignee ?? defaults.assignee,
    owner: task.owner ?? defaults.owner,
    start_date: task.start_date ?? defaults.start_date,
    due_date: task.due_date ?? defaults.due_date,
    status: task.status ?? defaults.status,
    priority: task.priority ?? defaults.priority,
    effort: task.effort ?? defaults.effort,
    parent_id: task.parent_id ?? null
  })
}

async function handleDelete(task) {
  if (!task?.id) {
    return
  }

  if (!window.confirm(`「${task.title}」を削除しますか？`)) {
    return
  }

  try {
    await axios.delete(`/api/tasks/${task.id}`)
    if (editingId.value === task.id) {
      resetForm()
    }
    await loadTasks()
  } catch (error) {
    errorMessage.value = resolveErrorMessage(error)
  }
}

function handleAddChild(task) {
  resetForm(task?.id ?? null)
}

function findTaskById(list, id) {
  for (const item of list ?? []) {
    if (item.id === id) {
      return item
    }
    const found = findTaskById(item.children, id)
    if (found) {
      return found
    }
  }
  return null
}

function resolveErrorMessage(error) {
  if (error?.response?.data) {
    if (typeof error.response.data === 'string') {
      return error.response.data
    }
    if (error.response.data.message) {
      return error.response.data.message
    }
  }
  return '通信中にエラーが発生しました。'
}
</script>
