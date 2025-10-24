<template>
  <div class="min-h-screen bg-gray-50 p-4">
    <div class="max-w-4xl mx-auto">
      <!-- Header -->
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-800">Create Notice</h1>
        <p class="text-gray-600">Send announcements to students and parents</p>
      </div>

      <!-- Notice Form -->
      <div class="bg-white rounded-lg shadow-sm p-6">
        <!-- Title Input -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Notice Title *
          </label>
          <input
            v-model="title"
            type="text"
            placeholder="Enter notice title"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <!-- Message Input -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Notice Message *
          </label>
          <textarea
            v-model="text"
            rows="8"
            placeholder="Enter your notice message here..."
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          ></textarea>
        </div>

        <!-- Selected Class Info -->
        <div class="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <p class="text-sm text-blue-700">
            <span class="font-medium">Selected Class:</span> {{ selectedGroup || 'No class selected' }}
          </p>
        </div>

        <!-- Submit Button -->
        <div class="flex justify-end">
          <button
            @click="handleSubmit"
            :disabled="submitResource.loading"
            class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-300 disabled:cursor-not-allowed flex items-center space-x-2 transition-colors"
          >
            <svg 
              v-if="!submitResource.loading"
              class="w-5 h-5" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <svg 
              v-else
              class="w-5 h-5 animate-spin" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span>{{ submitResource.loading ? 'Publishing...' : 'Publish Notice' }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { createResource } from 'frappe-ui'

// Reactive state
const text = ref('')
const title = ref('')
const selectedGroup = ref('')

// Create resource for submitting notice
const submitResource = createResource({
  url: 'school.al_ummah.api2.submit_notice',
  auto: false,
  onSuccess(data) {
    console.log('Notice submission response:', data)
    
    // Handle different response formats
    if (data.message) {
      // If there's a message field, show it
      showSuccess(data.message)
    } else if (typeof data === 'string' && data.includes('success')) {
      // If the response is a success string
      showSuccess(data)
    } else {
      // Default success message
      showSuccess('Notice published successfully!')
    }
    
    // Clear form
    text.value = ''
    title.value = ''
  },
  onError(error) {
    console.error('Error submitting notice:', error)
    
    // Handle different error formats
    if (error.message) {
      showError(error.message)
    } else if (error.exc_type === 'ValidationError') {
      showError('Validation error: Please check your input data.')
    } else {
      showError('An error occurred while submitting the notice.')
    }
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

// Handle form submission
const handleSubmit = async () => {
  // Validation
  if (!text.value.trim() || !title.value.trim()) {
    showError('Please enter both title and notice message.')
    return
  }

  if (!selectedGroup.value) {
    showError('Student group information is missing.')
    return
  }

  // Prepare data for submission
  const noticeData = {
    notice_heading: title.value.trim(),
    notice_message: text.value.trim(),
    student_group: selectedGroup.value
  }

  console.log('Submitting notice:', noticeData)
  
  // Submit notice
  await submitResource.fetch(noticeData)
}

// Success notification
const showSuccess = (message) => {
  // You can replace this with a proper notification system like vue-toastification
  alert(`✅ Success: ${message}`)
}

// Error notification
const showError = (message) => {
  // You can replace this with a proper notification system like vue-toastification
  alert(`❌ Error: ${message}`)
}

onMounted(() => {
  loadSelectedGroup()
})
</script>