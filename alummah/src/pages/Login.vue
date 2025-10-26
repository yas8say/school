<template>
  <div v-if="showWelcome" class="container">
    <div class="welcome-section">
      <h1 class="heading">Login as</h1>
      <div class="role-selection">
        <div class="role-card" @click="selectRole('parent')">
          <img :src="parentImage" alt="Parent" class="role-image" />
          <span class="role-title">A parent</span>
        </div>
        <div class="role-card" @click="selectRole('teacher')">
          <img :src="teacherImage" alt="Teacher" class="role-image" />
          <span class="role-title">A teacher</span>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="container">
    <form class="login-form" @submit.prevent="handleLogin">
      <h2 class="form-title">Login as {{ currentRole }}</h2>
      
      <div class="form-group">
        <label for="username">User ID</label>
        <input
          id="username"
          type="text"
          v-model="username"
          placeholder="johndoe@email.com"
          required
        />
      </div>

      <div class="form-group">
        <label for="password">Password</label>
        <div class="password-container">
          <input
            id="password"
            :type="passwordVisible ? 'text' : 'password'"
            v-model="password"
            placeholder="••••••"
            required
          />
          <button
            type="button"
            class="password-toggle"
            @click="togglePasswordVisibility"
          >
            <span v-if="passwordVisible">👁️</span>
            <span v-else>👁️‍🗨️</span>
          </button>
        </div>
      </div>

      <button type="submit" class="login-btn" :disabled="session.login.loading">
        {{ session.login.loading ? 'Logging in...' : `Sign in as ${currentRole}` }}
      </button>

      <div class="form-actions">
        <button type="button" class="secondary-btn" @click="showWelcome = true">
          Back
        </button>
        <button type="button" class="text-btn" @click="navigateTo('ForgotPassword')">
          Forgot password?
        </button>
      </div>

      <div class="alternative-options">
        <button type="button" class="outline-btn" @click="navigateTo('OTPLogin')">
          Login with OTP
        </button>
        <button type="button" class="outline-btn" @click="navigateTo('SignInScreen')">
          Login with Google
        </button>
      </div>

      <div class="signup-section">
        <button type="button" class="success-btn" @click="navigateToSignup">
          Don't have an account? Sign up here
        </button>
      </div>
    </form>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, onUnmounted, watch } from "vue"
import { useRouter } from "vue-router"
import { session, setSelectedLoginRole } from "../data/session"
import '@/styles/form.css';
import parentImage from "../assets/parent.png"
import teacherImage from "../assets/teacher.png"

const router = useRouter()

// Reactive state
const showWelcome = ref(true)
const currentRole = ref("")
const username = ref("")
const password = ref("")
const passwordVisible = ref(false)

// Methods
function selectRole(role: string) {
  currentRole.value = role
  showWelcome.value = false
  setSelectedLoginRole(role)
}

function togglePasswordVisibility() {
  passwordVisible.value = !passwordVisible.value
}

function handleLogin() {
  if (!username.value || !password.value) {
    showUniversalPopup('info', 'Missing Information', 'Please fill out all fields')
    return
  }
  
  setSelectedLoginRole(currentRole.value)
  
  session.login.submit({
    email: username.value,
    password: password.value,
    role: getFrappeRole()
  })
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

// UniversalPopup helper function
function showUniversalPopup(type: string, title: string, message: string) {
  window.dispatchEvent(new CustomEvent('show-api-message-popup', {
    detail: {
      type: type,
      title: title,
      message: message
    }
  }))
}

// Watch for login errors
watch(() => session.login.error, (error) => {
  if (error) {
    if (error.message && (error.message.includes('CSRF') || error.message.includes('session'))) {
      showUniversalPopup('csrf', 'Session Conflict', 'It seems you\'re already logged in. Please logout from other sessions to continue.')
    } else {
      const message = error.message || "Login failed. Please check your credentials and try again."
      showUniversalPopup('info', 'Login Failed', message)
    }
  }
})

// Watch for login success with error message (when status is not success)
watch(() => session.login.data, (data) => {
  if (data && !data.status === "success") {
    const message = data.message || "Login failed. Please try again."
    showUniversalPopup('info', 'Login Information', message)
  }
})

// Reset form when component mounts
const resetForm = () => {
  username.value = ""
  password.value = ""
  session.login.reset()
}

onMounted(() => {
  resetForm()
})

onUnmounted(() => {
  resetForm()
})
</script>