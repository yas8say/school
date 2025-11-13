<template>
  <div class="toast-container" v-if="toasts.length > 0">
    <div 
      v-for="toast in toasts" 
      :key="toast.id"
      :class="['toast', toast.type]"
    >
      <div class="toast-content">
        <div class="toast-icon">
          <span v-if="toast.type === 'success'">✅</span>
          <span v-else-if="toast.type === 'error'">❌</span>
          <span v-else-if="toast.type === 'warning'">⚠️</span>
          <span v-else>ℹ️</span>
        </div>
        <div class="toast-message">
          <p>{{ toast.message }}</p>
          <div v-if="toast.actions && toast.actions.length" class="toast-actions">
            <a
              v-for="action in toast.actions"
              :key="action.label"
              :href="action.url"
              :target="action.target || '_self'"
              :class="['toast-action', action.type || 'primary']"
              @click="handleActionClick(toast.id, action)"
            >
              {{ action.label }}
            </a>
          </div>
        </div>
        <button @click="removeToast(toast.id)" class="toast-close">
          ×
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const toasts = ref([])
let toastId = 0

const emit = defineEmits(['action-click'])

const showToast = (message, type = 'success', duration = 8000000, actions = []) => {
  const id = toastId++
  const toast = {
    id,
    message,
    type,
    actions,
    duration
  }
  
  toasts.value.push(toast)
  
  if (duration > 0) {
    setTimeout(() => {
      removeToast(id)
    }, duration)
  }
  
  return id
}

const removeToast = (id) => {
  toasts.value = toasts.value.filter(toast => toast.id !== id)
}

const handleActionClick = (toastId, action) => {
  if (action.onClick) {
    action.onClick()
  }
  emit('action-click', { toastId, action })
  
  // Remove toast if action should close it
  if (action.closeOnClick !== false) {
    removeToast(toastId)
  }
}

// Make methods available to parent component
defineExpose({
  showToast,
  removeToast
})
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  max-width: 400px;
}

.toast {
  background: white;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  border-left: 4px solid;
  margin-bottom: 10px;
  animation: slideIn 0.3s ease-out;
}

.toast.success {
  border-left-color: #10b981;
}

.toast.error {
  border-left-color: #ef4444;
}

.toast.warning {
  border-left-color: #f59e0b;
}

.toast.info {
  border-left-color: #3b82f6;
}

.toast-content {
  display: flex;
  align-items: flex-start;
  padding: 1rem;
  gap: 0.75rem;
}

.toast-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.toast-message {
  flex: 1;
  min-width: 0;
}

.toast-message p {
  margin: 0 0 0.75rem 0;
  color: #1f2937;
  font-weight: 500;
  line-height: 1.5;
  white-space: pre-line;
}

.toast-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.toast-action {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 500;
  font-size: 0.875rem;
  transition: all 0.2s;
  border: none;
  cursor: pointer;
}

.toast-action.primary {
  background: #10b981;
  color: white;
}

.toast-action.primary:hover {
  background: #059669;
}

.toast-action.secondary {
  background: #6b7280;
  color: white;
}

.toast-action.secondary:hover {
  background: #4b5563;
}

.toast-action.link {
  background: transparent;
  color: #10b981;
  text-decoration: underline;
  padding: 0.5rem 0;
}

.toast-close {
  background: none;
  border: none;
  font-size: 1.25rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background-color 0.2s;
  flex-shrink: 0;
}

.toast-close:hover {
  background: #e5e7eb;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Responsive */
@media (max-width: 768px) {
  .toast-container {
    top: 10px;
    right: 10px;
    left: 10px;
    max-width: none;
  }
  
  .toast-content {
    padding: 0.75rem;
  }
  
  .toast-actions {
    flex-direction: column;
  }
  
  .toast-action {
    justify-content: center;
  }
}
</style>