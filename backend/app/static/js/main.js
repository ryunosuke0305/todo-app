/* global bootstrap, Vue */
(function () {
  'use strict';

  const { createApp, ref, reactive, computed, onMounted, onBeforeUnmount } = Vue;

  const defaultForm = () => {
    const today = new Date().toISOString().slice(0, 10);
    return {
      title: '',
      detail: '',
      assignee: '',
      owner: '',
      start_date: today,
      due_date: today,
      status: '未着手',
      priority: '中',
      effort: '中'
    };
  };

  const resolveStatusClass = (status) => {
    if (status === '完了') return 'bg-success';
    if (status === '作業中') return 'bg-primary';
    return 'bg-secondary';
  };

  const resolveErrorMessage = (error) => {
    if (!error) {
      return '通信中にエラーが発生しました。';
    }
    if (error instanceof Error) {
      return error.message;
    }
    if (typeof error === 'object' && error.message) {
      return error.message;
    }
    return '通信中にエラーが発生しました。';
  };

  const findTaskById = (tasks, id) => {
    for (const task of tasks ?? []) {
      if (String(task.id) === String(id)) {
        return task;
      }
      const child = findTaskById(task.children, id);
      if (child) {
        return child;
      }
    }
    return null;
  };

  const TaskItem = {
    name: 'TaskItem',
    props: {
      task: {
        type: Object,
        required: true
      }
    },
    emits: ['edit', 'add-child', 'delete'],
    setup(props, { emit }) {
      const childTasks = computed(() =>
        Array.isArray(props.task.children) ? props.task.children : []
      );
      const hasChildren = computed(() => childTasks.value.length > 0);
      const badgeClass = computed(() => resolveStatusClass(props.task.status));

      const handleEdit = () => emit('edit', props.task);
      const handleAddChild = () => emit('add-child', props.task);
      const handleDelete = () => emit('delete', props.task);

      return {
        childTasks,
        hasChildren,
        badgeClass,
        handleEdit,
        handleAddChild,
        handleDelete
      };
    },
    template: `
      <div class="list-group-item" :data-task-id="task.id">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <strong>{{ task.title }}</strong>
            <small class="ms-2 text-muted">{{ task.assignee }} / {{ task.owner }}</small>
          </div>
          <span class="badge" :class="badgeClass">{{ task.status }}</span>
        </div>
        <p class="mb-1 text-muted">{{ task.detail }}</p>
        <ul class="list-inline small mb-0">
          <li class="list-inline-item">優先度: {{ task.priority }}</li>
          <li class="list-inline-item">作業量: {{ task.effort }}</li>
          <li class="list-inline-item">期間: {{ task.start_date }} ~ {{ task.due_date }}</li>
        </ul>
        <div class="mt-3 d-flex flex-wrap gap-2">
          <button type="button" class="btn btn-sm btn-outline-primary" @click="handleEdit">編集</button>
          <button type="button" class="btn btn-sm btn-outline-secondary" @click="handleAddChild">子タスク追加</button>
          <button type="button" class="btn btn-sm btn-outline-danger" @click="handleDelete">削除</button>
        </div>
        <div v-if="hasChildren" class="mt-3 ms-3 border-start ps-3">
          <task-item
            v-for="child in childTasks"
            :key="child.id"
            :task="child"
            @edit="$emit('edit', $event)"
            @add-child="$emit('add-child', $event)"
            @delete="$emit('delete', $event)"
          ></task-item>
        </div>
      </div>
    `
  };

  createApp({
    components: {
      TaskItem
    },
    setup() {
      const tasks = ref([]);
      const loading = ref(false);
      const globalError = ref('');
      const formError = ref('');
      const submitting = ref(false);
      const editingId = ref(null);
      const parentId = ref(null);
      const parentTitle = ref('');
      const form = reactive(defaultForm());
      const modalElement = ref(null);
      let modalInstance = null;

      const isEditing = computed(() => editingId.value !== null);
      const modalTitle = computed(() => (isEditing.value ? 'タスクを更新' : 'タスクを登録'));
      const submitLabel = computed(() => (isEditing.value ? '更新する' : '追加する'));
      const parentLabel = computed(() => parentTitle.value || parentId.value || '');

      const refreshParentTitle = () => {
        if (!parentId.value) {
          parentTitle.value = '';
          return;
        }
        const parent = findTaskById(tasks.value, parentId.value);
        parentTitle.value = parent ? parent.title ?? '' : '';
      };

      const resetForm = (nextParentId = null) => {
        Object.assign(form, defaultForm());
        editingId.value = null;
        parentId.value = nextParentId ?? null;
        formError.value = '';
        parentTitle.value = '';

        if (parentId.value) {
          const parent = findTaskById(tasks.value, parentId.value);
          if (parent) {
            parentTitle.value = parent.title ?? '';
            form.start_date = parent.start_date ?? form.start_date;
            form.due_date = parent.due_date ?? form.due_date;
          }
        }
      };

      const loadTasks = async () => {
        loading.value = true;
        try {
          const response = await fetch('/api/tasks');
          if (!response.ok) {
            throw new Error('タスクを取得できませんでした。');
          }
          const data = await response.json();
          tasks.value = Array.isArray(data.tasks) ? data.tasks : [];
          globalError.value = '';
          refreshParentTitle();
        } catch (error) {
          tasks.value = [];
          globalError.value = resolveErrorMessage(error);
        } finally {
          loading.value = false;
        }
      };

      const showModal = () => {
        if (modalInstance) {
          modalInstance.show();
        }
      };

      const hideModal = () => {
        if (modalInstance) {
          modalInstance.hide();
        }
      };

      const openCreate = () => {
        resetForm(null);
        showModal();
      };

      const openCreateFromTask = (task) => {
        if (!task) {
          resetForm(null);
        } else {
          resetForm(task.id);
        }
        showModal();
      };

      const openEdit = (task) => {
        if (!task) {
          return;
        }
        editingId.value = task.id;
        form.title = task.title ?? '';
        form.detail = task.detail ?? '';
        form.assignee = task.assignee ?? '';
        form.owner = task.owner ?? '';
        form.start_date = task.start_date ?? defaultForm().start_date;
        form.due_date = task.due_date ?? defaultForm().due_date;
        form.status = task.status ?? '未着手';
        form.priority = task.priority ?? '中';
        form.effort = task.effort ?? '中';
        parentId.value = task.parent_id ?? null;
        formError.value = '';
        refreshParentTitle();
        showModal();
      };

      const clearParent = () => {
        parentId.value = null;
        parentTitle.value = '';
        if (!isEditing.value) {
          const defaults = defaultForm();
          form.start_date = defaults.start_date;
          form.due_date = defaults.due_date;
        }
      };

      const handleSubmit = async () => {
        if (!form.title || !form.title.trim()) {
          formError.value = 'タイトルを入力してください。';
          return;
        }

        submitting.value = true;
        try {
          const payload = {
            title: form.title.trim(),
            detail: form.detail ?? '',
            assignee: form.assignee ?? '',
            owner: form.owner ?? '',
            start_date: form.start_date,
            due_date: form.due_date,
            status: form.status,
            priority: form.priority,
            effort: form.effort,
            parent_id: parentId.value ?? null
          };

          const method = isEditing.value ? 'PUT' : 'POST';
          const endpoint = isEditing.value ? `/api/tasks/${editingId.value}` : '/api/tasks';

          const response = await fetch(endpoint, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });

          if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const message = errorData.message || 'タスクの保存中にエラーが発生しました。';
            throw new Error(message);
          }

          await loadTasks();
          hideModal();
        } catch (error) {
          formError.value = resolveErrorMessage(error);
        } finally {
          submitting.value = false;
        }
      };

      const deleteTask = async (task) => {
        if (!task) {
          return;
        }
        if (!window.confirm(`「${task.title ?? ''}」を削除しますか？`)) {
          return;
        }
        try {
          const response = await fetch(`/api/tasks/${task.id}`, { method: 'DELETE' });
          if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const message = errorData.message || 'タスクの削除中にエラーが発生しました。';
            throw new Error(message);
          }
          await loadTasks();
        } catch (error) {
          globalError.value = resolveErrorMessage(error);
        }
      };

      const handleModalHidden = () => {
        resetForm(null);
      };

      onMounted(() => {
        if (modalElement.value) {
          modalInstance = new bootstrap.Modal(modalElement.value, { backdrop: 'static' });
          modalElement.value.addEventListener('hidden.bs.modal', handleModalHidden);
        }
        loadTasks();
      });

      onBeforeUnmount(() => {
        if (modalElement.value) {
          modalElement.value.removeEventListener('hidden.bs.modal', handleModalHidden);
        }
        if (modalInstance && typeof modalInstance.dispose === 'function') {
          modalInstance.dispose();
        }
      });

      return {
        tasks,
        loading,
        globalError,
        formError,
        submitting,
        isEditing,
        modalTitle,
        submitLabel,
        parentId,
        parentTitle,
        parentLabel,
        form,
        modalElement,
        openCreate,
        openCreateFromTask,
        openEdit,
        clearParent,
        handleSubmit,
        deleteTask
      };
    }
  }).mount('#app');
})();
