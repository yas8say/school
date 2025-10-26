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
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// Get role from route params or default to teacher
const currentRole = ref(route.query?.role || 'teacher')
const loading = ref(false)

// Lazy loaded modules
let googleAuth = null
let session = null
let setSelectedLoginRole = null

// Load modules dynamically
const loadModules = async () => {
  try {
    // Load session module
    const sessionModule = await import('@/data/session')
    googleAuth = sessionModule.googleAuth
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

// Handle Google credential response directly
const handleGoogleCredentialResponse = async (response) => {
  try {
    loading.value = true
    console.log('Google credential response received', response)
    console.log('Current role:', currentRole.value)
    
    // Convert role to backend format and send to API
    const backendRole = currentRole.value === 'parent' ? 'Guardian' : 'Instructor'
    console.log('Sending role to API:', backendRole)
    
    // Send both id_token and role to the API
    await session.verifyGoogleToken.submit({
      id_token: response.credential,
      role: backendRole  // Send "Instructor" or "Guardian" to backend
    })
    
  } catch (error) {
    console.error('Error handling credential response:', error)
    loading.value = false
    showUniversalPopup('info', 'Sign-In Failed', 'Failed to process Google sign in. Please try again.')
  }
}

// Watch for Google auth errors from session
watch(() => {
  if (session) return session.verifyGoogleToken.error
}, (error) => {
  if (error) {
    loading.value = false
    console.log('Google auth error from session:', error)
    if (error.message && (error.message.includes('CSRF') || error.message.includes('session'))) {
      showUniversalPopup('csrf', 'Session Conflict', 'It seems you\'re already logged in. Please logout from other sessions to continue.')
    } else {
      const message = error.message || 'Failed to verify Google token. Please try again.'
      showUniversalPopup('info', 'Google Sign-In Failed', message)
    }
  }
})

// Watch for Google auth success with error message
watch(() => {
  if (session) return session.verifyGoogleToken.data
}, (data) => {
  if (data && !data.success) {
    loading.value = false
    console.log('Google auth failed with data:', data)
    const message = data.error || 'Google authentication failed. Please try again.'
    showUniversalPopup('info', 'Authentication Failed', message)
  }
})

// Watch for Google auth loading state
watch(() => {
  if (session) return session.verifyGoogleToken.loading
}, (isLoading) => {
  loading.value = isLoading
})

// Initialize Google Sign-In
const initializeGoogleSignIn = async () => {
  await loadModules()
  
  if (googleAuth && window.google) {
    try {
      // Initialize Google Sign-In with direct callback
      window.google.accounts.id.initialize({
        client_id: googleAuth.CLIENT_ID,
        callback: handleGoogleCredentialResponse,
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
      showUniversalPopup('info', 'Initialization Error', 'Failed to initialize Google Sign-In. Please refresh the page.')
    }
  } else {
    // Load Google script first
    try {
      await googleAuth.loadScript()
      
      // Initialize Google button after script loads
      setTimeout(() => {
        if (window.google) {
          window.google.accounts.id.initialize({
            client_id: googleAuth.CLIENT_ID,
            callback: handleGoogleCredentialResponse,
            auto_select: false,
            cancel_on_tap_outside: true,
            ux_mode: 'popup'
          })

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
        } else {
          showUniversalPopup('info', 'Load Error', 'Google Sign-In failed to load. Please check your connection.')
        }
      }, 500)
      
    } catch (error) {
      console.error('Failed to load Google Sign-In:', error)
      showUniversalPopup('info', 'Load Error', 'Failed to load Google Sign-In. Please check your connection.')
    }
  }
}

onMounted(async () => {
  // Initialize Google Sign-In
  await initializeGoogleSignIn()
})

onUnmounted(() => {
  // Clean up any Google Sign-In instances
  if (window.google && window.google.accounts && window.google.accounts.id) {
    window.google.accounts.id.cancel()
  }
})
</script>

<style scoped>
/* Custom styles if needed */
</style>