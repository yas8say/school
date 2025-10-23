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
import { ref } from "vue"
import { useRouter } from "vue-router"
import { session, setSelectedLoginRole } from "../data/session" // Import both session and setter
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

// Get the Frappe role based on selected role
const getFrappeRole = () => {
  return currentRole.value === "parent" ? "Guardian" : "Instructor"
}

// Methods
function selectRole(role: string) {
  currentRole.value = role
  showWelcome.value = false
  // Store the selected role globally for navigation
  setSelectedLoginRole(role)
}

function togglePasswordVisibility() {
  passwordVisible.value = !passwordVisible.value
}

function handleLogin() {
  if (!username.value || !password.value) {
    alert("Please fill out all fields")
    return
  }
  
  // Make sure the role is stored before submitting
  setSelectedLoginRole(currentRole.value)
  
  // Use the global session login with role parameter
  session.login.submit({
    email: username.value,
    password: password.value,
    role: getFrappeRole()
  })
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
</script>