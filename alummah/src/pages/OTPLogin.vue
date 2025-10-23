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
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { createResource } from 'frappe-ui'
import { session, setSelectedLoginRole } from "@/data/session"

const router = useRouter()
const route = useRoute()

// Get role from route query or default to teacher
const currentRole = ref(route.query.role || 'teacher')

// Set the selected login role globally (like regular login does)
setSelectedLoginRole(currentRole.value)

// Reactive state
const phoneNumber = ref('')
const otp = ref('')
const isPhoneDisabled = ref(false)
const loading = ref(false)
const verifying = ref(false)

// Create resources for API calls
const sendOtpResource = createResource({
  url: 'school.al_ummah.api2.send_otp_web',
  onSuccess(data) {
    console.log('OTP sent successfully:', data)
    loading.value = false
    if (data.success) {
      alert('OTP sent successfully! Check your phone.')
      isPhoneDisabled.value = true
    } else {
      alert(data.message || 'Failed to send OTP. Please try again.')
    }
  },
  onError(error) {
    console.error('Error sending OTP:', error)
    loading.value = false
    alert('Failed to send OTP. Please try again.')
  }
})

const verifyOtpResource = createResource({
  url: 'school.al_ummah.api2.verify_otp_and_create_session',
  onSuccess(data) {
    console.log('OTP verified successfully:', data)
    handleOtpVerificationSuccess(data)
  },
  onError(error) {
    console.error('Error verifying OTP:', error)
    verifying.value = false
    alert('Failed to verify OTP. Please check the code and try again.')
  }
})

// Handle send OTP
const handleSendOtp = async () => {
  if (!phoneNumber.value) {
    alert('Please enter a valid phone number.')
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
  }
}

// Handle verify OTP
const handleVerifyOtp = async () => {
  if (!otp.value) {
    alert('Please enter the OTP.')
    return
  }

  verifying.value = true
  try {
    await verifyOtpResource.submit({
      phone: phoneNumber.value,
      otp: otp.value,
      role: currentRole.value === 'parent' ? 'Guardian' : 'Instructor'
    })
  } catch (error) {
    console.error('Error in verify OTP:', error)
    verifying.value = false
  }
}

// Handle OTP verification success - mimic the same flow as regular login
const handleOtpVerificationSuccess = async (data) => {
  try {
    if (data.status === 'success') {
      console.log('OTP login successful, session created on backend')
      
      // Store user info
      localStorage.setItem('user', JSON.stringify({
        username: data.user,
        role: currentRole.value,
        roles: data.roles
      }))
      
      // 2. Update session user (like session.login.onSuccess does)
      session.user = data.user
      
      // 3. Use the same navigation logic as regular login
      const routeName = currentRole.value === 'parent' ? 'Parenthome' : 'Teacherhome'
      console.log('Redirecting based on selected role:', currentRole.value, '→', routeName)
      router.replace({ name: routeName })
      
    } else {
      alert('OTP verification failed. Please try again.')
      verifying.value = false
    }
  } catch (error) {
    console.error('Error in OTP verification process:', error)
    alert('Failed to complete login process. Please try again.')
    verifying.value = false
  }
}

// Handle back navigation
const handleBack = () => {
  router.push({ name: 'Login' })
}

// Check if user is already logged in - use same logic as regular login
onMounted(() => {
  if (session.isLoggedIn) {
    const routeName = currentRole.value === 'parent' ? 'Parenthome' : 'Teacherhome'
    router.replace({ name: routeName })
  }
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