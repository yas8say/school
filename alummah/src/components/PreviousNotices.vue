<template>
  <div class="min-h-screen bg-gray-50 p-4">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-800">Previous Notices</h1>
      <p class="text-gray-600">View all published notices</p>
      <p class="text-sm text-gray-500 mt-1" v-if="selectedGroup">Class: {{ selectedGroup }}</p>
    </div>

    <!-- Loading State -->
    <div v-if="noticesResource.loading" class="flex justify-center items-center py-8">
      <div class="spinner"></div>
      <span class="ml-2 text-gray-600">Loading notices...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="noticesResource.error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
      <p class="text-red-800">Failed to load notices.</p>
      <button @click="fetchNotices" class="mt-2 px-3 py-1 bg-red-600 text-white rounded text-sm">
        Retry
      </button>
    </div>

    <!-- Notices List -->
    <div v-else class="space-y-4">
      <div 
        v-for="(notice, index) in notices" 
        :key="index"
        class="bg-white rounded-lg shadow-sm border border-gray-200 hover:border-blue-300 transition-colors cursor-pointer"
        @click="viewNoticeDetails(notice)"
      >
        <div class="p-6">
          <div class="flex items-start justify-between mb-3">
            <h3 class="text-lg font-semibold text-gray-800 flex-1 pr-4">
              {{ notice.notice_heading || 'No Title' }}
            </h3>
            <span class="text-sm text-gray-500 whitespace-nowrap">
              {{ formatDate(notice.date) }}
            </span>
          </div>
          
          <p class="text-gray-600 line-clamp-2 mb-4">
            {{ notice.notice_message || 'No message content' }}
          </p>
          
          <div class="flex items-center justify-between text-sm text-gray-500">
            <span>By: {{ notice.owner || 'System' }}</span>
            <button
              @click.stop="deleteNotice(notice.name)"
              class="text-red-600 hover:text-red-800 font-medium"
            >
              Delete
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="notices.length === 0" class="text-center py-12">
        <div class="bg-white rounded-lg shadow-sm p-8">
          <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 class="text-lg font-medium text-gray-800 mb-2">No Notices Found</h3>
          <p class="text-gray-600">No notices have been published for this class yet.</p>
        </div>
      </div>
    </div>

    <!-- Notice Details Modal -->
    <div v-if="selectedNotice && showNoticeModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-xl font-bold text-gray-800">{{ selectedNotice.notice_heading }}</h2>
            <button @click="closeNoticeModal" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="mb-4 text-sm text-gray-500">
            <p>Published on: {{ formatDate(selectedNotice.date) }}</p>
            <p>By: {{ selectedNotice.owner || 'System' }}</p>
          </div>

          <div class="prose max-w-none mb-6">
            <p class="text-gray-700 whitespace-pre-wrap">{{ selectedNotice.notice_message }}</p>
          </div>

          <div class="flex space-x-3 pt-4 border-t">
            <button
              @click="deleteNotice(selectedNotice.name)"
              class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 flex items-center space-x-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              <span>Delete Notice</span>
            </button>
            <button
              @click="closeNoticeModal"
              class="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { createResource } from 'frappe-ui'

// Reactive state
const notices = ref([])
const selectedGroup = ref('')
const selectedNotice = ref(null)
const showNoticeModal = ref(false)

// Create resources for API calls
const noticesResource = createResource({
  url: 'school.al_ummah.api2.get_notice_list',
  auto: false,
  onSuccess(data) {
    console.log('Notices loaded:', data)
    notices.value = Array.isArray(data) ? data : []
  },
  onError(error) {
    console.error('Error fetching notices:', error)
    notices.value = []
  }
})

const deleteNoticeResource = createResource({
  url: 'school.al_ummah.api2.delete_notice',
  auto: false,
  onSuccess() {
    console.log('Notice deleted successfully')
    // Refresh the notices list
    fetchNotices()
    closeNoticeModal()
  },
  onError(error) {
    console.error('Error deleting notice:', error)
    alert('Error', 'Failed to delete notice. Please try again.')
  }
})

// Load selected group from localStorage
const loadSelectedGroup = () => {
  try {
    const group = localStorage.getItem('selected_student_group')
    if (group) {
      selectedGroup.value = group
    }
  } catch (error) {
    console.error('Failed to load selected student group:', error)
  }
}

// Fetch notices
const fetchNotices = () => {
  if (!selectedGroup.value) return
  
  const params = {
    student_group: selectedGroup.value
  }
  
  noticesResource.fetch(params)
}

// Format date
const formatDate = (dateString) => {
  if (!dateString) return 'No date'
  
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  } catch (error) {
    return dateString
  }
}

// View notice details
const viewNoticeDetails = (notice) => {
  selectedNotice.value = notice
  showNoticeModal.value = true
}

// Close notice modal
const closeNoticeModal = () => {
  showNoticeModal.value = false
  selectedNotice.value = null
}

// Delete notice
const deleteNotice = (noticeId) => {
  if (!noticeId) {
    alert('Error', 'No notice ID provided')
    return
  }

  if (confirm('Are you sure you want to delete this notice? This action cannot be undone.')) {
    deleteNoticeResource.fetch({ name: noticeId })
  }
}

// Alert function
const alert = (type, message) => {
  if (type === 'Error') {
    window.alert(`Error: ${message}`)
  } else {
    window.alert(message)
  }
}

// Lifecycle
onMounted(() => {
  loadSelectedGroup()
  if (selectedGroup.value) {
    fetchNotices()
  }
})

// Watch for group changes
watch(selectedGroup, (newGroup) => {
  if (newGroup) {
    fetchNotices()
  }
})
</script>

<style scoped>
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>