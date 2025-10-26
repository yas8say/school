<template>
  <div class="min-h-screen bg-white flex items-center justify-center p-4">
    <div class="w-full max-w-md text-center">
      <!-- Header -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-blue-600 mb-2">OTP Login</h1>
        <p class="text-gray-600">Enter your phone number to receive OTP</p>
      </div>

      <!-- Phone Input -->
      <div class="mb-6 text-left">
        <label for="phoneNumber" class="block text-sm font-medium text-gray-700 mb-2">
          Phone Number
        </label>
        <input
          id="phoneNumber"
          type="tel"
          v-model="phoneNumber"
          placeholder="Enter your phone number"
          :disabled="isPhoneDisabled"
          :class="[
            'w-full px-4 py-3 border border-gray-300 rounded-full focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
            isPhoneDisabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'
          ]"
        />
      </div>

      <!-- Send OTP Button -->
      <button
        @click="handleSendOtp"
        :disabled="isPhoneDisabled || !phoneNumber"
        :class="[
          'w-full py-3 px-4 rounded-full font-medium transition-colors mb-6',
          isPhoneDisabled || !phoneNumber
            ? 'bg-gray-400 cursor-not-allowed text-white'
            : 'bg-blue-600 hover:bg-blue-700 text-white'
        ]"
      >
        {{ isPhoneDisabled ? 'OTP Sent' : 'Send OTP' }}
      </button>

      <!-- OTP Input -->
      <div class="mb-6 text-left" v-if="isPhoneDisabled">
        <label for="otp" class="block text-sm font-medium text-gray-700 mb-2">
          Enter OTP
        </label>
        <input
          id="otp"
          type="text"
          v-model="otp"
          placeholder="Enter OTP"
          class="w-full px-4 py-3 border border-gray-300 rounded-full focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      <!-- Verify OTP Button -->
      <button
        v-if="isPhoneDisabled"
        @click="handleVerifyOtp"
        :disabled="!otp || verifying"
        :class="[
          'w-full py-3 px-4 rounded-full font-medium transition-colors mb-4',
          !otp || verifying
            ? 'bg-gray-400 cursor-not-allowed text-white'
            : 'bg-green-600 hover:bg-green-700 text-white'
        ]"
      >
        {{ verifying ? 'Verifying...' : 'Verify OTP' }}
      </button>

      <!-- Back Button -->
      <button
        @click="handleBack"
        class="w-full py-3 px-4 border border-gray-300 text-gray-700 rounded-full font-medium hover:bg-gray-50 transition-colors"
      >
        Back to Login
      </button>

      <!-- Loading Overlay -->
      <div v-if="loading" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg p-6 flex items-center space-x-3">
          <div class="spinner"></div>
          <span class="text-gray-700">Processing...</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// Get role from route query or default to teacher
const currentRole = ref(route.query.role || 'teacher')

// Reactive state
const phoneNumber = ref('')
const otp = ref('')
const isPhoneDisabled = ref(false)
const loading = ref(false)
const verifying = ref(false)

// Lazy loaded modules
let session = null
let setSelectedLoginRole = null

// Load modules dynamically
const loadModules = async () => {
  try {
    // Load session module
    const sessionModule = await import('@/data/session')
    session = sessionModule.session
    setSelectedLoginRole = sessionModule.setSelectedLoginRole
    
    // Set the selected login role globally
    if (setSelectedLoginRole) {
      setSelectedLoginRole(currentRole.value)
    }
  } catch (error) {
    console.error('Error loading modules:', error)
    showUniversalPopup('info', 'Error', 'Failed to load required modules. Please refresh the page.')
  }
}

// UniversalPopup helper function
function showUniversalPopup(type, title, message) {
  window.dispatchEvent(new CustomEvent('show-api-message-popup', {
    detail: {
      type: type,
      title: title,
      message: message
    }
  }))
}

// Event listeners for OTP verification
const onOtpVerificationSuccess = (event) => {
  console.log('OTP verification success from session:', event.detail)
  verifying.value = false
}

const onOtpVerificationError = (event) => {
  console.log('OTP verification error from session:', event.detail)
  verifying.value = false
  showUniversalPopup('info', 'Verification Failed', 'Failed to verify OTP. Please try again.')
}

// Set up event listeners
const setupEventListeners = () => {
  window.addEventListener('otp-verification-success', onOtpVerificationSuccess)
  window.addEventListener('otp-verification-error', onOtpVerificationError)
}

// Clean up event listeners
const cleanupEventListeners = () => {
  window.removeEventListener('otp-verification-success', onOtpVerificationSuccess)
  window.removeEventListener('otp-verification-error', onOtpVerificationError)
}

// Create resource for send OTP API call only
const sendOtpResource = {
  submit: async (params) => {
    const { createResource } = await import('frappe-ui')
    
    const resource = createResource({
      url: 'school.al_ummah.api2.send_otp_web',
      onSuccess(data) {
        console.log('OTP sent successfully:', data)
        loading.value = false
        if (data.success) {
          showUniversalPopup('info', 'OTP Sent', 'OTP sent successfully! Check your phone.')
          isPhoneDisabled.value = true
        } else {
          showUniversalPopup('info', 'OTP Failed', data.message || 'Failed to send OTP. Please try again.')
        }
      },
      onError(error) {
        console.error('Error sending OTP:', error)
        loading.value = false
        showUniversalPopup('info', 'OTP Failed', 'Failed to send OTP. Please try again.')
      }
    })
    
    return resource.submit(params)
  }
}

// Handle send OTP
const handleSendOtp = async () => {
  if (!phoneNumber.value) {
    showUniversalPopup('info', 'Missing Information', 'Please enter a valid phone number.')
    return
  }

  loading.value = true
  try {
    await sendOtpResource.submit({
      phone: phoneNumber.value,
      role: currentRole.value === 'parent' ? 'Guardian' : 'Instructor'
    })
  } catch (error) {
    console.error('Error in send OTP:', error)
    loading.value = false
    showUniversalPopup('info', 'OTP Failed', 'Failed to send OTP. Please try again.')
  }
}

// Handle verify OTP - now using session.verifyOtp
const handleVerifyOtp = async () => {
  if (!otp.value) {
    showUniversalPopup('info', 'Missing Information', 'Please enter the OTP.')
    return
  }

  verifying.value = true
  try {
    if (session && session.verifyOtp) {
      await session.verifyOtp.submit({
        phone: phoneNumber.value,
        otp: otp.value,
        role: currentRole.value === 'parent' ? 'Guardian' : 'Instructor'
      })
    } else {
      throw new Error('Session module not loaded')
    }
  } catch (error) {
    console.error('Error in verify OTP:', error)
    verifying.value = false
    showUniversalPopup('info', 'Verification Failed', 'Failed to verify OTP. Please try again.')
  }
}

// Watch for OTP verification errors from session
watch(() => {
  if (session) return session.verifyOtp.error
}, (error) => {
  if (error) {
    verifying.value = false
    showUniversalPopup('info', 'Verification Failed', 'Failed to verify OTP. Please check the code and try again.')
  }
})

// Watch for OTP verification success with error message
watch(() => {
  if (session) return session.verifyOtp.data
}, (data) => {
  if (data && data.status !== 'success') {
    verifying.value = false
    const message = data.message || 'OTP verification failed. Please try again.'
    showUniversalPopup('info', 'Verification Failed', message)
  }
})

// Handle back navigation
const handleBack = () => {
  router.push({ name: 'Login' })
}

onMounted(async () => {
  await loadModules()
  setupEventListeners()
})

onUnmounted(() => {
  cleanupEventListeners()
})
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