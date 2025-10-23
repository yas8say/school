<template>
  <div class="min-h-screen bg-white flex items-center justify-center p-4">
    <div class="w-full max-w-md text-center">
      <!-- Title -->
      <h1 class="text-3xl font-bold text-blue-600 mb-6">Login</h1>
      
      <!-- Google Sign In Button -->
      <div id="googleSignInButton" class="flex justify-center"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { createResource } from 'frappe-ui'

const router = useRouter()
const route = useRoute()

// Get role from route params or default to teacher
const currentRole = ref(route.query?.role || 'teacher')
const loading = ref(false)

// Your web client ID
const GOOGLE_CLIENT_ID_WEB = "619580422153-9o7kvuuocsjfqejuv2jrud3h986t5prc.apps.googleusercontent.com"

// Create resource for API calls - updated to match backend endpoint
const verifyTokenResource = createResource({
  url: 'school.al_ummah.api2.verify_google_token_and_create_session',
  onSuccess(data) {
    console.log('Token verified successfully:', data)
    handleTokenVerificationSuccess(data)
  },
  onError(error) {
    console.error('Error verifying token:', error)
    loading.value = false
    alert(error?.message || 'Failed to verify Google token. Please try again.')
  }
})

// Initialize Google Sign-In
const initializeGoogleSignIn = () => {
  if (typeof window === 'undefined' || !window.google) {
    console.log('Google API not loaded yet')
    return
  }

  try {
    window.google.accounts.id.initialize({
      client_id: GOOGLE_CLIENT_ID_WEB,
      callback: handleCredentialResponse,
      auto_select: false,
      cancel_on_tap_outside: true,
      ux_mode: 'popup'
    })

    // Render Google button
    window.google.accounts.id.renderButton(
      document.getElementById('googleSignInButton'),
      { 
        theme: 'outline', 
        size: 'large',
        width: 280,
        text: 'signin_with',
        shape: 'pill',
        logo_alignment: 'center'
      }
    )

    console.log('Google Sign-In initialized successfully')

  } catch (error) {
    console.error('Error initializing Google Sign-In:', error)
  }
}

// Handle credential response from Google
const handleCredentialResponse = async (response) => {
  try {
    loading.value = true
    console.log('Google credential response received', response)
    console.log('Current role:', currentRole.value)
    
    // Convert role to backend format and send to API
    const backendRole = currentRole.value === 'parent' ? 'Guardian' : 'Instructor'
    console.log('Sending role to API:', backendRole)
    
    // Send both id_token and role to the API - matches backend parameters
    await verifyTokenResource.submit({
      id_token: response.credential,
      role: backendRole  // Send "Instructor" or "Guardian" to backend
    })
    
  } catch (error) {
    console.error('Error handling credential response:', error)
    loading.value = false
    alert('Failed to process Google sign in.')
  }
}

// Handle token verification success - simplified for session-based auth
const handleTokenVerificationSuccess = async (data) => {
  try {
    if (data.success) {
      console.log('Google authentication successful:', data)
      
      // Store user info in localStorage
      localStorage.setItem('user', JSON.stringify({
        username: data.user,
        email: data.email,
        role: currentRole.value,  // Store frontend role (teacher/parent)
        roles: data.roles
      }))

      // Store session info
      if (data.sid) {
        localStorage.setItem('session_id', data.sid)
      }

      // Since we're using session-based authentication, we need to update
      // the Frappe UI session state to recognize we're logged in
      try {
        // Import session to update the state
        const { session } = await import('@/data/session')
        session.user = data.user
        session.isLoggedIn = true
        
        // Navigate to appropriate home based on frontend role
        const routeName = currentRole.value === 'parent' ? 'Parenthome' : 'Teacherhome'
        console.log('Navigating to:', routeName)
        router.replace({ name: routeName })
        
      } catch (sessionError) {
        console.error('Error updating session:', sessionError)
        // Fallback: navigate directly
        const routeName = currentRole.value === 'parent' ? 'Parenthome' : 'Teacherhome'
        router.replace({ name: routeName })
      }
      
    } else {
      alert(data.error || 'Authentication failed. Please try again.')
      loading.value = false
    }
  } catch (error) {
    console.error('Error in token verification process:', error)
    alert('Failed to complete login process. Please try again.')
    loading.value = false
  }
}

// Load Google API script
const loadGoogleScript = () => {
  return new Promise((resolve, reject) => {
    if (document.getElementById('google-js-sdk')) {
      resolve()
      return
    }

    const script = document.createElement('script')
    script.id = 'google-js-sdk'
    script.src = 'https://accounts.google.com/gsi/client'
    script.async = true
    script.defer = true
    script.onload = () => {
      setTimeout(() => {
        initializeGoogleSignIn()
        resolve()
      }, 100)
    }
    script.onerror = () => {
      console.error('Failed to load Google Sign-In script')
      reject(new Error('Failed to load Google Sign-In'))
    }
    document.head.appendChild(script)
  })
}

onMounted(async () => {
  // Check if already logged in
  const userData = localStorage.getItem('user')
  if (userData) {
    const user = JSON.parse(userData)
    if (user.role) {
      router.replace({ name: user.role === 'parent' ? 'Parenthome' : 'Teacherhome' })
      return
    }
  }
  
  // Load Google Sign-In
  try {
    await loadGoogleScript()
  } catch (error) {
    console.error('Failed to load Google Sign-In:', error)
  }
})
</script>

<style scoped>
/* Custom styles if needed */
</style>