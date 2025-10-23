<template>
  <div class="min-h-screen bg-white flex items-center justify-center p-4">
    <div class="w-full max-w-md text-center">
      <!-- Header -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-blue-600 mb-2">Reset your password</h1>
      </div>

      <!-- Email Input -->
      <div class="mb-6 text-left">
        <input
          type="email"
          v-model="email"
          placeholder="Enter your email"
          class="w-full px-6 py-4 bg-gray-100 text-gray-800 rounded-full focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
          :disabled="loading"
        />
      </div>

      <!-- Reset Password Button -->
      <button
        @click="handleResetPassword"
        :disabled="!email || loading"
        :class="[
          'w-full py-4 px-6 rounded-full font-medium transition-colors',
          !email || loading
            ? 'bg-gray-400 cursor-not-allowed text-white'
            : 'bg-blue-600 hover:bg-blue-700 text-white'
        ]"
      >
        {{ loading ? 'Sending...' : 'Reset Password' }}
      </button>

      <!-- Success Message -->
      <div v-if="successMessage" class="mt-4 p-3 bg-green-100 text-green-700 rounded-lg">
        {{ successMessage }}
      </div>

      <!-- Error Message -->
      <div v-if="errorMessage" class="mt-4 p-3 bg-red-100 text-red-700 rounded-lg">
        {{ errorMessage }}
      </div>

      <!-- Loading Overlay -->
      <div v-if="loading" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg p-6 flex items-center space-x-3">
          <div class="spinner"></div>
          <span class="text-gray-700">Sending reset instructions...</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { createResource } from 'frappe-ui'

const email = ref('')
const loading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

// Create resource for reset password API call
const resetPasswordResource = createResource({
  url: 'frappe.core.doctype.user.user.reset_password',
  onSuccess(data) {
    console.log('Reset password API response:', data)
    loading.value = false
    
    // If we get here, the API call was successful (HTTP 200)
    // The Frappe reset_password endpoint typically returns a message directly
    if (data && data.message) {
      successMessage.value = data.message
      errorMessage.value = ''
    } else {
      // Default success message if no specific message is returned
      successMessage.value = 'Password reset instructions have been sent to your email.'
      errorMessage.value = ''
    }
  },
  onError(error) {
    console.error('Error sending reset password email:', error)
    loading.value = false
    
    // Handle different types of errors
    if (error && error.exc) {
      try {
        // Try to parse the exception message from Frappe
        const errorData = JSON.parse(error.exc)
        errorMessage.value = errorData._error_message || 'Failed to send reset email. Please try again.'
      } catch (e) {
        errorMessage.value = error.message || 'Failed to send reset email. Please try again.'
      }
    } else if (error && error.message) {
      errorMessage.value = error.message
    } else {
      errorMessage.value = 'Failed to send reset email. Please try again.'
    }
    
    successMessage.value = ''
  }
})

// Handle reset password
const handleResetPassword = async () => {
  if (!email.value) {
    errorMessage.value = 'Please enter your email.'
    return
  }

  // Clear previous messages
  successMessage.value = ''
  errorMessage.value = ''
  
  loading.value = true
  try {
    await resetPasswordResource.submit({
      user: email.value
    })
  } catch (error) {
    console.error('Error in reset password:', error)
    loading.value = false
    errorMessage.value = 'An unexpected error occurred. Please try again.'
  }
}
</script>

<style scoped>
.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #e5e7eb;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>