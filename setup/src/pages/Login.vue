<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <!-- Header -->
      <div class="text-center mb-8">
        <div class="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 mb-2">Admin Portal</h1>
        <p class="text-gray-600">Sign in to manage your school system</p>
      </div>

      <!-- Login Card -->
      <Card class="w-full shadow-lg border-0">
        <template #title>
          <div class="text-center">
            <h2 class="text-xl font-semibold text-gray-800">Welcome Back</h2>
            <p class="text-sm text-gray-600 mt-1">Enter your credentials to continue</p>
          </div>
        </template>

        <form class="space-y-4" @submit.prevent="submit">
          <!-- Username Field -->
          <div class="space-y-2">
            <label class="block text-sm font-medium text-gray-700">
              Username
              <span class="text-red-500 ml-1">*</span>
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <Input
                required
                name="username"
                type="text"
                placeholder="Enter your username"
                class="pl-10 w-full pr-10"
                :class="{ 
                  'border-red-300 focus:border-red-500 focus:ring-red-200': loginError,
                  'border-gray-300 focus:border-blue-500 focus:ring-blue-200': !loginError
                }"
                autocomplete="username"
                v-model="username"
                @input="clearError"
                @focus="clearError"
              />
            </div>
          </div>

          <!-- Password Field -->
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <label class="block text-sm font-medium text-gray-700">
                Password
                <span class="text-red-500 ml-1">*</span>
              </label>
              <button 
                type="button" 
                @click="togglePasswordVisibility"
                class="text-sm text-blue-600 hover:text-blue-500 font-medium"
              >
                {{ showPassword ? 'Hide' : 'Show' }}
              </button>
            </div>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <Input
                required
                name="password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="Enter your password"
                class="pl-10 w-full pr-10"
                :class="{ 
                  'border-red-300 focus:border-red-500 focus:ring-red-200': loginError,
                  'border-gray-300 focus:border-blue-500 focus:ring-blue-200': !loginError
                }"
                autocomplete="current-password"
                v-model="password"
                @input="clearError"
                @focus="clearError"
              />
              <div class="absolute inset-y-0 right-0 pr-3 flex items-center">
                <button
                  type="button"
                  @click="togglePasswordVisibility"
                  class="text-gray-400 hover:text-gray-500 focus:outline-none"
                >
                  <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path v-if="showPassword" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                    <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="loginError" class="bg-red-50 border border-red-200 rounded-md p-4 transition-all duration-300">
            <div class="flex items-start">
              <svg class="w-5 h-5 text-red-400 mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div class="flex-1">
                <h3 class="text-red-800 font-medium text-sm mb-1">Access Denied</h3>
                <p class="text-red-700 text-sm">{{ loginError }}</p>
                <div v-if="isPermissionError" class="mt-2 text-xs text-red-600">
                  <p>This portal requires <strong>Administrator</strong> privileges.</p>
                  <p class="mt-1">Please contact your system administrator if you need access.</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Login Button -->
          <Button 
            :loading="session.login.loading" 
            variant="solid"
            class="w-full bg-blue-600 hover:bg-blue-700 text-white py-2.5 transition-colors"
            :disabled="!username || !password || session.login.loading"
            :class="{ 
              'bg-red-600 hover:bg-red-700': loginError && !session.login.loading,
              'bg-blue-600 hover:bg-blue-700': !loginError
            }"
          >
            <template #prefix>
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
              </svg>
            </template>
            <span v-if="session.login.loading">Signing In...</span>
            <span v-else>Sign In</span>
          </Button>
        </form>

        <!-- Footer -->
        <template #footer>
          <div class="text-center text-sm text-gray-500 pt-4 border-t">
            <p>Having trouble signing in? Contact system administrator</p>
          </div>
        </template>
      </Card>

      <!-- Version Info -->
      <div class="text-center mt-6">
        <p class="text-xs text-gray-500">School Management System v1.0</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { session } from '../data/session'

const username = ref('')
const password = ref('')
const showPassword = ref(false)
const loginError = ref('')

// Computed property to check if it's a permission error
const isPermissionError = computed(() => {
  return loginError.value.toLowerCase().includes('permission') || 
         loginError.value.toLowerCase().includes('administrator') ||
         loginError.value.toLowerCase().includes('access denied') ||
         loginError.value.toLowerCase().includes('role')
})

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}

const clearError = () => {
  if (loginError.value) {
    loginError.value = ''
  }
}

const submit = async (e) => {
  loginError.value = ''
  
  if (!username.value || !password.value) {
    loginError.value = 'Please fill in all fields'
    return
  }

  try {
    const formData = new FormData(e.target)
    await session.login.submit({
      email: formData.get('username'),
      password: formData.get('password'),
    })
  } catch (error) {
    // Handle different types of errors
    if (error.message && error.message.includes('PermissionError')) {
      loginError.value = 'Administrator privileges required. Your account does not have access to the admin portal.'
    } else if (error.message && error.message.includes('AuthenticationError')) {
      loginError.value = 'Invalid username or password. Please check your credentials.'
    } else if (error.message) {
      // Extract clean error message from Frappe response
      try {
        const errorData = JSON.parse(error.message)
        const serverMessage = JSON.parse(errorData._server_messages?.[0] || '{}')
        loginError.value = serverMessage.message || 'Login failed. Please try again.'
      } catch {
        loginError.value = error.message || 'Login failed. Please try again.'
      }
    } else {
      loginError.value = 'Login failed. Please check your credentials and try again.'
    }
    
    // Clear password on error for security
    password.value = ''
  }
}
</script>

<style scoped>
/* Custom focus styles */
:deep(input:focus) {
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

:deep(input.border-red-300:focus) {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

/* Smooth transitions for error states */
:deep(input) {
  transition: all 0.2s ease-in-out;
}

/* Ensure consistent input heights */
:deep(.input-container) {
  min-height: 42px;
}

/* Button loading state */
:deep(.btn--loading) {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>