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
import { useRouter } from 'vue-router'

const router = useRouter()

const showPopup = ref(false)
const popupType = ref('info') // 'info', 'csrf', 'role'
const popupTitle = ref('')
const popupMessage = ref('')
const loggingOut = ref(false)

const showUniversalPopup = (type, title, message) => {
  popupType.value = type
  popupTitle.value = title
  popupMessage.value = message
  showPopup.value = true
}

const closePopup = () => {
  showPopup.value = false
  loggingOut.value = false
}

const forceLogout = async () => {
  // Save logout timestamp to localStorage
  localStorage.setItem('logout_clicked_timestamp', Date.now().toString())
  
  loggingOut.value = true
  try {
    // Get current origin and remove any port
    const currentOrigin = window.location.origin
    const url = new URL(currentOrigin)
    
    // Remove port from origin (keep protocol and hostname only)
    const cleanOrigin = `${url.protocol}//${url.hostname}`
    
    // Build the Vue app login URL without port
    const vueLoginUrl = `${cleanOrigin}/setup/account/login`
    
    console.log('Logout redirect:', {
      currentOrigin,
      cleanOrigin, 
      vueLoginUrl
    })
    
    // Redirect to Frappe's logout page with cleaned Vue app login URL
    window.location.href = `/logout?redirect-to=${encodeURIComponent(vueLoginUrl)}`
    
  } catch (error) {
    console.error('Logout failed:', error)
    // Fallback - redirect directly to login without port
    const url = new URL(window.location.origin)
    const cleanOrigin = `${url.protocol}//${url.hostname}`
    window.location.href = `${cleanOrigin}/setup/account/login`
  } finally {
    loggingOut.value = false
    showPopup.value = false
  }
}

// Listen for custom events from anywhere in the app
const handlePopupEvent = (event) => {
  const { type, title, message } = event.detail
  showUniversalPopup(type, title, message)
}

onMounted(() => {
  window.addEventListener('show-universal-popup', handlePopupEvent)
})

onUnmounted(() => {
  window.removeEventListener('show-universal-popup', handlePopupEvent)
})

// Expose methods for programmatic use
defineExpose({
  showUniversalPopup,
  closePopup
})
</script>

<style scoped>
.spinner-small {
  @apply w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin;
}
</style>