<template>
  <!-- Universal Popup for CSRF errors and API messages -->
  <div v-if="showPopup" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-6 max-w-sm w-full mx-4">
      <div class="text-center">
        <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full mb-4" 
             :class="popupType === 'csrf' ? 'bg-red-100' : popupType === 'role' ? 'bg-yellow-100' : 'bg-blue-100'">
          <svg v-if="popupType === 'csrf'" class="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"/>
          </svg>
          <svg v-else-if="popupType === 'role'" class="h-6 w-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"/>
          </svg>
          <svg v-else class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-800 mb-2">{{ popupTitle }}</h3>
        <p class="text-gray-600 mb-4">
          {{ popupMessage }}
        </p>
        <div class="flex space-x-3">
          <button
            v-if="popupType === 'info'"
            @click="closePopup"
            class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            OK
          </button>
          <template v-else-if="popupType === 'role'">
            <button
              @click="closePopup"
              class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              @click="forceLogout"
              class="flex-1 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 flex items-center justify-center space-x-2"
              :disabled="loggingOut"
            >
              <span v-if="loggingOut">
                <div class="spinner-small"></div>
              </span>
              <span>{{ loggingOut ? 'Logging out...' : 'Logout' }}</span>
            </button>
          </template>
          <template v-else>
            <button
              @click="closePopup"
              class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              @click="forceLogout"
              class="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center justify-center space-x-2"
              :disabled="loggingOut"
            >
              <span v-if="loggingOut">
                <div class="spinner-small"></div>
              </span>
              <span>{{ loggingOut ? 'Logging out...' : 'Logout' }}</span>
            </button>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const showPopup = ref(false)
const loggingOut = ref(false)
const popupType = ref('csrf') // 'csrf', 'info', or 'role'
const popupTitle = ref('')
const popupMessage = ref('')

// Handle different types of popups
const handlePopup = (event) => {
  const { type, title, message } = event.detail || {}
  
  popupType.value = type || 'csrf'
  popupTitle.value = title || 'Session Conflict'
  popupMessage.value = message || 'It seems you\'re already logged in. Please logout from other session to continue.'
  
  showPopup.value = true
}

const closePopup = () => {
  showPopup.value = false
  resetPopup()
}

const resetPopup = () => {
  popupType.value = 'csrf'
  popupTitle.value = ''
  popupMessage.value = ''
}

const forceLogout = async () => {
  // Save logout timestamp to localStorage
  localStorage.setItem('logout_clicked_timestamp', Date.now().toString())
  
  loggingOut.value = true
  try {
    // Redirect to Frappe's logout page with our Vue app's login URL as parameter
    const vueLoginUrl = `${window.location.origin}/alummah/account/login`
    window.location.href = `/logout?redirect-to=${encodeURIComponent(vueLoginUrl)}`
    
  } catch (error) {
    console.error('Logout failed:', error)
    // Fallback
    window.location.href = '/alummah/account/login'
  } finally {
    loggingOut.value = false
    showPopup.value = false
  }
}

// Event listeners
onMounted(() => {
  window.addEventListener('show-api-message-popup', handlePopup)
})

onUnmounted(() => {
  window.removeEventListener('show-api-message-popup', handlePopup)
})
</script>

<style scoped>
.spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>