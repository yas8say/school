<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <!-- Welcome Screen -->
      <div v-if="showWelcome">
        <!-- Header -->
        <div class="text-center mb-8">
          <div class="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l9-5-9-5-9 5 9 5z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l9-5-9-5-9 5 9 5z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14v6l9-5-9-5-9 5 9 5z" />
            </svg>
          </div>
          <h1 class="text-2xl font-bold text-gray-900 mb-2">School Portal</h1>
          <p class="text-gray-600">Select your role to continue</p>
        </div>

        <!-- Role Selection Card -->
        <Card class="w-full shadow-lg border-0">
          <template #title>
            <div class="text-center">
              <h2 class="text-xl font-semibold text-gray-800">Login as</h2>
              <p class="text-sm text-gray-600 mt-1">Choose your role to sign in</p>
            </div>
          </template>

          <div class="space-y-4">
            <!-- Parent Role -->
            <div 
              class="border-2 border-gray-200 rounded-lg p-4 cursor-pointer transition-all duration-200 hover:border-blue-500 hover:bg-blue-50"
              @click="selectRole('parent')"
            >
              <div class="flex items-center space-x-4">
                <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                  <img :src="parentImage" alt="Parent" class="w-8 h-8 object-contain" />
                </div>
                <div>
                  <h3 class="font-semibold text-gray-800">Parent</h3>
                  <p class="text-sm text-gray-600">Access student progress and information</p>
                </div>
              </div>
            </div>

            <!-- Teacher Role -->
            <div 
              class="border-2 border-gray-200 rounded-lg p-4 cursor-pointer transition-all duration-200 hover:border-green-500 hover:bg-green-50"
              @click="selectRole('teacher')"
            >
              <div class="flex items-center space-x-4">
                <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                  <img :src="teacherImage" alt="Teacher" class="w-8 h-8 object-contain" />
                </div>
                <div>
                  <h3 class="font-semibold text-gray-800">Teacher</h3>
                  <p class="text-sm text-gray-600">Manage classes and student records</p>
                </div>
              </div>
            </div>
          </div>

          <template #footer>
            <div class="text-center text-sm text-gray-500 pt-4 border-t">
              <p>Need help? Contact school administration</p>
            </div>
          </template>
        </Card>
      </div>

      <!-- Login Form -->
      <div v-else>
        <!-- Header -->
        <div class="text-center mb-8">
          <div class="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <h1 class="text-2xl font-bold text-gray-900 mb-2">{{ currentRole === 'teacher' ? 'Teacher' : 'Parent' }} Portal</h1>
          <p class="text-gray-600">Sign in to access your account</p>
        </div>

        <!-- Login Card -->
        <Card class="w-full shadow-lg border-0">
          <template #title>
            <div class="text-center">
              <h2 class="text-xl font-semibold text-gray-800">Welcome Back</h2>
              <p class="text-sm text-gray-600 mt-1">Sign in as {{ currentRole }}</p>
            </div>
          </template>

          <form class="space-y-4" @submit.prevent="handleLogin">
            <!-- Username Field -->
            <div class="space-y-2">
              <label class="block text-sm font-medium text-gray-700">
                User ID
                <span class="text-red-500 ml-1">*</span>
              </label>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <input
                  required
                  id="username"
                  type="text"
                  placeholder="johndoe@email.com"
                  class="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-500 transition-colors"
                  :class="{ 
                    'border-red-300 focus:border-red-500 focus:ring-red-200': loginError,
                    'border-gray-300 focus:border-blue-500 focus:ring-blue-200': !loginError
                  }"
                  autocomplete="username"
                  v-model="username"
                  @input="clearError"
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
                  {{ passwordVisible ? 'Hide' : 'Show' }}
                </button>
              </div>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <input
                  required
                  id="password"
                  :type="passwordVisible ? 'text' : 'password'"
                  placeholder="••••••"
                  class="w-full pl-10 pr-10 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-500 transition-colors"
                  :class="{ 
                    'border-red-300 focus:border-red-500 focus:ring-red-200': loginError,
                    'border-gray-300 focus:border-blue-500 focus:ring-blue-200': !loginError
                  }"
                  autocomplete="current-password"
                  v-model="password"
                  @input="clearError"
                />
                <div class="absolute inset-y-0 right-0 pr-3 flex items-center">
                  <button
                    type="button"
                    @click="togglePasswordVisibility"
                    class="text-gray-400 hover:text-gray-500 focus:outline-none"
                  >
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path v-if="passwordVisible" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
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
                  <h3 class="text-red-800 font-medium text-sm mb-1">Login Failed</h3>
                  <p class="text-red-700 text-sm">{{ loginError }}</p>
                </div>
              </div>
            </div>

            <!-- Login Button -->
            <button 
              type="submit"
              :disabled="session.login.loading"
              class="w-full bg-blue-600 hover:bg-blue-700 text-white py-2.5 px-4 rounded-md transition-colors flex items-center justify-center gap-2 font-medium"
              :class="{
                'opacity-50 cursor-not-allowed': (!username || !password) && !session.login.loading,
                'bg-blue-600 hover:bg-blue-700': username && password && !session.login.loading,
                'bg-blue-400 cursor-wait': session.login.loading
              }"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" v-if="!session.login.loading">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
              </svg>
              <span v-if="session.login.loading">Signing In...</span>
              <span v-else>Sign in as {{ currentRole }}</span>
            </button>

            <!-- Back and Forgot Password -->
            <div class="flex items-center justify-between pt-2">
              <button 
                type="button" 
                @click="showWelcome = true"
                class="text-blue-600 hover:text-blue-500 font-medium text-sm"
              >
                ← Back to role selection
              </button>
              <button 
                type="button" 
                @click="navigateTo('ForgotPassword')"
                class="text-blue-600 hover:text-blue-500 font-medium text-sm"
              >
                Forgot password?
              </button>
            </div>

            <!-- Alternative Login Options -->
            <div class="border-t pt-4 space-y-3">
              <button 
                type="button" 
                @click="navigateTo('OTPLogin')"
                class="w-full border border-gray-300 text-gray-700 hover:bg-gray-50 py-2.5 px-4 rounded-md transition-colors flex items-center justify-center gap-2 font-medium"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                Login with OTP
              </button>

              <button 
                type="button" 
                @click="navigateTo('SignInScreen')"
                class="w-full border border-gray-300 text-gray-700 hover:bg-gray-50 py-2.5 px-4 rounded-md transition-colors flex items-center justify-center gap-2 font-medium"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                </svg>
                Login with Google
              </button>
            </div>

            <!-- Sign Up Section -->
            <div class="text-center pt-4 border-t">
              <button 
                type="button" 
                @click="navigateToSignup"
                class="text-green-600 hover:text-green-500 font-medium text-sm"
              >
                Don't have an account? Sign up here
              </button>
            </div>
          </form>

          <template #footer>
            <div class="text-center text-sm text-gray-500">
              <p>Having trouble signing in? Contact school administration</p>
            </div>
          </template>
        </Card>
      </div>

      <!-- Version Info -->
      <div class="text-center mt-6">
        <p class="text-xs text-gray-500">School Management System v1.0</p>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, onUnmounted, watch } from "vue"
import { useRouter } from "vue-router"
import { session, setSelectedLoginRole } from "../data/session"
import parentImage from "../assets/parent.png"
import teacherImage from "../assets/teacher.png"

const router = useRouter()

// Reactive state
const showWelcome = ref(true)
const currentRole = ref("")
const username = ref("")
const password = ref("")
const passwordVisible = ref(false)
const loginError = ref("")

// Methods
function selectRole(role: string) {
  currentRole.value = role
  showWelcome.value = false
  setSelectedLoginRole(role)
}

function togglePasswordVisibility() {
  passwordVisible.value = !passwordVisible.value
}

function clearError() {
  loginError.value = ""
}

async function handleLogin() {
  // Use the reactive values directly
  console.log('Login attempt values:', { 
    username: username.value, 
    password: password.value,
    usernameLength: username.value?.length,
    passwordLength: password.value?.length
  })
  
  if (!username.value || !password.value) {
    loginError.value = 'Please fill out all fields'
    console.log('Validation failed - empty fields')
    return
  }
  
  // Clear any previous errors
  loginError.value = ""
  console.log('Proceeding with login...')
  
  setSelectedLoginRole(currentRole.value)
  
  try {
    console.log('Submitting login with:', {
      email: username.value,
      password: '***', // Don't log actual password
      role: getFrappeRole()
    })
    
    await session.login.submit({
      email: username.value,
      password: password.value,
      role: getFrappeRole()
    })
    
    console.log('Login successful!')
    
  } catch (error) {
    console.error('Login error details:', error)
    
    // Handle specific error types
    if (error.message && error.message.includes('AuthenticationError')) {
      loginError.value = 'Invalid username or password. Please check your credentials and try again.'
    } else if (error.message && error.message.includes('CSRF') || error.message.includes('session')) {
      loginError.value = 'Session error. Please try refreshing the page.'
    } else {
      loginError.value = 'Login failed. Please check your credentials and try again.'
    }
  }
}

function getFrappeRole() {
  return currentRole.value === "parent" ? "Guardian" : "Instructor"
}

function navigateTo(routeName: string) {
  router.push({ 
    name: routeName, 
    query: { role: currentRole.value } 
  })
}

function navigateToSignup() {
  const routeName = currentRole.value === "teacher" ? "TeacherSignup" : "ParentSignup"
  router.push({ 
    name: routeName, 
    query: { role: currentRole.value } 
  })
}

// Watch for login errors (backup error handling)
watch(() => session.login.error, (error) => {
  if (error && !loginError.value) {
    console.error('Session login error:', error)
    if (error.message && error.message.includes('AuthenticationError')) {
      loginError.value = 'Invalid username or password. Please check your credentials and try again.'
    } else if (error.message && (error.message.includes('CSRF') || error.message.includes('session'))) {
      loginError.value = 'Session error. Please try refreshing the page.'
    } else {
      loginError.value = error.message || "Login failed. Please check your credentials and try again."
    }
  }
})

// Reset form when component mounts
const resetForm = () => {
  username.value = ""
  password.value = ""
  loginError.value = ""
  session.login.reset()
}

onMounted(() => {
  resetForm()
})

onUnmounted(() => {
  resetForm()
})
</script>