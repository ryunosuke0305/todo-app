<template>
  <div>
    <div
      class="offcanvas offcanvas-start"
      tabindex="-1"
      id="globalNavigation"
      aria-labelledby="globalNavigationLabel"
    >
      <div class="offcanvas-header">
        <h5 class="offcanvas-title" id="globalNavigationLabel">メニュー</h5>
        <button
          type="button"
          class="btn-close"
          data-bs-dismiss="offcanvas"
          aria-label="閉じる"
        ></button>
      </div>
      <div class="offcanvas-body">
        <nav class="nav flex-column gap-1">
          <span class="text-uppercase text-muted small">ナビゲーション</span>
          <a class="nav-link disabled" href="#" aria-disabled="true">ダッシュボード（準備中）</a>
          <a class="nav-link disabled" href="#" aria-disabled="true">レポート（準備中）</a>
          <a class="nav-link disabled" href="#" aria-disabled="true">設定（準備中）</a>
        </nav>
      </div>
    </div>

    <div
      class="modal fade"
      id="taskModal"
      tabindex="-1"
      aria-labelledby="taskModalLabel"
      aria-hidden="true"
      ref="taskModal"
    >
      <div class="modal-dialog modal-lg modal-dialog-scrollable">
        <div class="modal-content">
          <form @submit.prevent="handleSubmit">
            <div class="modal-header">
              <h5 class="modal-title" id="taskModalLabel">
                {{ isEditing ? 'タスクを更新' : 'タスクを登録' }}
                <span v-if="isEditing" class="badge bg-warning text-dark ms-2">編集中</span>
              </h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="閉じる"></button>
            </div>
            <div class="modal-body">
              <div v-if="formError" class="alert alert-danger" role="alert">
                {{ formError }}
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
                  @click="clearParent"
                >
                  親タスク解除
                </button>
              </div>
              <div class="row g-3">
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
              </div>
            </div>
            <div class="modal-footer">
              <button
                type="button"
                class="btn btn-outline-secondary"
                data-bs-dismiss="modal"
              >
                キャンセル
              </button>
              <button type="submit" class="btn btn-primary">
                {{ isEditing ? '更新する' : '追加する' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <header class="border-bottom bg-light">
      <div class="container py-3 d-flex align-items-center gap-3">
        <button
          class="btn btn-outline-secondary d-flex align-items-center"
          type="button"
          data-bs-toggle="offcanvas"
          data-bs-target="#globalNavigation"
          aria-controls="globalNavigation"
        >
          <span class="me-2" aria-hidden="true">&#9776;</span>
          メニュー
        </button>
        <div>
          <h1 class="h4 mb-1">タスク管理</h1>
          <p class="text-muted mb-0 small">API を通じてタスクの登録・更新・削除が行えます。</p>
        </div>
        <div class="ms-auto">
          <button type="button" class="btn btn-primary" @click="openCreateModal()">
            新規タスク
          </button>
        </div>
      </div>
    </header>

    <main class="container py-4">
      <section v-if="globalError" class="mb-4">
        <div class="alert alert-danger" role="alert">
          {{ globalError }}
        </div>
      </section>
      <section>
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h2 class="h5 mb-0">タスク一覧</h2>
          <button
            type="button"
            class="btn btn-outline-success btn-sm"
            @click="openCreateModal()"
          >
            新規タスク
          </button>
        </div>
        <TaskList
          :tasks="tasks"
          @edit="openEditModal"
          @delete="handleDelete"
          @add-child="handleAddChild"
        />
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import axios from 'axios'
import { Modal } from 'bootstrap'
import TaskList from './components/TaskList.vue'

const tasks = ref([])
const isEditing = ref(false)
const editingId = ref(null)
const globalError = ref('')
const formError = ref('')
const formTask = reactive(createDefaultTask())
const taskModal = ref(null)
let modalInstance = null

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
  const defaults = createDefaultTask()
  Object.assign(formTask, defaults)
  formTask.parent_id = parentId

  if (parentId) {
    const parent = findTaskById(tasks.value, parentId)
    if (parent) {
      formTask.start_date = parent.start_date ?? defaults.start_date
      formTask.due_date = parent.due_date ?? defaults.due_date
    }
  }

  isEditing.value = false
  editingId.value = null
}

function showModal() {
  modalInstance?.show()
}

function hideModal() {
  modalInstance?.hide()
}

function handleModalHidden() {
  resetForm()
  formError.value = ''
}

async function loadTasks() {
  try {
    const response = await axios.get('/api/tasks')
    tasks.value = response.data.tasks ?? []
    globalError.value = ''
  } catch (error) {
    globalError.value = resolveErrorMessage(error)
  }
}

onMounted(() => {
  if (taskModal.value) {
    modalInstance = new Modal(taskModal.value, { backdrop: 'static' })
    taskModal.value.addEventListener('hidden.bs.modal', handleModalHidden)
  }

  loadTasks()
})

onBeforeUnmount(() => {
  if (taskModal.value) {
    taskModal.value.removeEventListener('hidden.bs.modal', handleModalHidden)
  }
  modalInstance?.dispose()
})

function openCreateModal(parentId = null) {
  resetForm(parentId)
  formError.value = ''
  showModal()
}

function openEditModal(task) {
  if (!task?.id) {
    return
  }

  const defaults = createDefaultTask()
  isEditing.value = true
  editingId.value = task.id
  formError.value = ''

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

  showModal()
}

function clearParent() {
  formTask.parent_id = null
}

async function handleSubmit() {
  const trimmedTitle = formTask.title.trim()
  if (!trimmedTitle) {
    formError.value = 'タイトルを入力してください。'
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
    hideModal()
  } catch (error) {
    formError.value = resolveErrorMessage(error)
  }
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
      hideModal()
    }
    await loadTasks()
  } catch (error) {
    globalError.value = resolveErrorMessage(error)
  }
}

function handleAddChild(task) {
  openCreateModal(task?.id ?? null)
}

const parentTitle = computed(() => {
  if (!formTask.parent_id) {
    return ''
  }
  const parent = findTaskById(tasks.value, formTask.parent_id)
  return parent ? parent.title : ''
})

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
