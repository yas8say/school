<template>
  <div id="app">
    <!-- Global Navigation Buttons -->
    <div v-if="showGlobalButtons" class="global-nav-buttons">
      <!-- Back Button - Only show when useful -->
      <button 
        v-if="showBackButton"
        @click="handleBack"
        class="global-nav-btn global-back-btn"
        :title="backButtonTitle"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        <span class="btn-text">{{ backButtonText }}</span>
      </button>

      <!-- Switch Dashboard Button -->
      <button 
        v-if="showSwitchButton"
        @click="switchDashboard"
        class="global-nav-btn global-switch-btn"
        :title="`Switch to ${targetDashboard} dashboard`"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
        </svg>
        <span class="btn-text">Switch to {{ targetDashboard }}</span>
      </button>
    </div>

    <router-view />
    <UniversalPopup />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import UniversalPopup from '@/components/UniversalPopup.vue'

const router = useRouter()
const route = useRoute()

// Reactive state
const currentRole = ref(localStorage.getItem('selectedLoginRole') || '')
const userRolesData = ref(getUserRolesFromStorage())
const currentRouteName = ref('')

// Computed properties
const userRoles = computed(() => userRolesData.value)

const hasBothRoles = computed(() => {
  return userRoles.value.includes('Instructor') && userRoles.value.includes('Guardian')
})

const targetDashboard = computed(() => {
  return currentRole.value === 'teacher' ? 'Parent' : 'Teacher'
})

const showGlobalButtons = computed(() => {
  // Don't show on login page or public routes
  const publicRoutes = ['Login', 'ForgotPassword', 'OTPLogin', 'SignInScreen', 'TeacherSignup', 'ParentSignup']
  const currentRoute = currentRouteName.value || route.name
  return !publicRoutes.includes(currentRoute) && isUserLoggedIn()
})

const showBackButton = computed(() => {
  // Only show back button on specific pages where it makes sense
  const backButtonRoutes = ['EditStudent', 'AttendanceRecord']
  const currentRoute = currentRouteName.value || route.name
  
  const shouldShow = showGlobalButtons.value && backButtonRoutes.includes(currentRoute)
  
  console.log('🔙 Back Button Check:', {
    currentRoute,
    showGlobalButtons: showGlobalButtons.value,
    isBackRoute: backButtonRoutes.includes(currentRoute),
    shouldShowBack: shouldShow
  })
  
  return shouldShow
})

const showSwitchButton = computed(() => {
  const currentRoute = currentRouteName.value || route.name
  return showGlobalButtons.value && hasBothRoles.value && ['Teacherhome', 'Parenthome'].includes(currentRoute)
})

const backButtonText = computed(() => {
  const currentRoute = currentRouteName.value || route.name
  
  if (currentRoute === 'EditStudent') {
    return 'Back to Attendance'
  } else if (currentRoute === 'AttendanceRecord') {
    return 'Back to Dashboard'
  } else {
    return 'Back'
  }
})

const backButtonTitle = computed(() => {
  const currentRoute = currentRouteName.value || route.name
  
  if (currentRoute === 'EditStudent') {
    return 'Return to Attendance Record'
  } else if (currentRoute === 'AttendanceRecord') {
    return 'Return to Teacher Dashboard'
  } else {
    return 'Go back to previous page'
  }
})

// Helper functions
function getUserRolesFromStorage() {
  try {
    const roles = localStorage.getItem('userRoles')
    return roles ? JSON.parse(roles) : []
  } catch {
    return []
  }
}

function isUserLoggedIn() {
  const cookies = new URLSearchParams(document.cookie.split('; ').join('&'))
  const userId = cookies.get('user_id')
  return userId && userId !== 'Guest' && userId !== 'undefined'
}

// Smart back navigation
const handleBack = () => {
  const currentRoute = currentRouteName.value || route.name
  console.log('Back button clicked from route:', currentRoute)
  
  if (currentRoute === 'EditStudent') {
    // From EditStudent, go back to AttendanceRecord
    router.push({ name: 'AttendanceRecord' })
  } else if (currentRoute === 'AttendanceRecord') {
    // From AttendanceRecord, go back to Teacherhome
    router.push({ name: 'Teacherhome' })
  } else if (window.history.length > 1) {
    // Default browser back
    router.go(-1)
  }
}

const switchDashboard = async () => {
  const newRole = currentRole.value === 'teacher' ? 'parent' : 'teacher'
  
  // Update selected role
  localStorage.setItem('selectedLoginRole', newRole)
  currentRole.value = newRole
  forceUpdate.value++
  
  await nextTick()
  
  // Navigate to the other dashboard
  if (newRole === 'teacher') {
    router.push({ name: 'Teacherhome' })
  } else {
    router.push({ name: 'Parenthome' })
  }
}

// Watch for route changes
watch(
  () => route.name,
  (newRoute) => {
    console.log('🔄 Route changed to:', newRoute)
    currentRouteName.value = newRoute
    currentRole.value = localStorage.getItem('selectedLoginRole') || ''
    userRolesData.value = getUserRolesFromStorage()
    forceUpdate.value++
  },
  { immediate: true }
)

// Force update trigger
const forceUpdate = ref(0)

// Initialize
onMounted(() => {
  currentRole.value = localStorage.getItem('selectedLoginRole') || ''
  userRolesData.value = getUserRolesFromStorage()
  currentRouteName.value = route.name
  
  console.log('🎯 Global navigation initialized', {
    currentRoute: currentRouteName.value,
    currentRole: currentRole.value,
    showBackButton: showBackButton.value,
    showSwitchButton: showSwitchButton.value
  })
})
</script>

<style scoped>
.global-nav-buttons {
  position: fixed;
  top: 20px;
  right: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 40;
}

.global-nav-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  min-width: 140px;
  justify-content: flex-start;
  backdrop-filter: blur(10px);
}

.global-back-btn {
  background: rgba(107, 114, 128, 0.95);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.global-back-btn:hover {
  background: rgba(75, 85, 99, 0.95);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.global-switch-btn {
  background: rgba(59, 130, 246, 0.95);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.global-switch-btn:hover {
  background: rgba(37, 99, 235, 0.95);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

/* Mobile responsive */
@media (max-width: 768px) {
  .global-nav-buttons {
    top: 70px;
    right: 10px;
    gap: 8px;
  }
  
  .global-nav-btn {
    padding: 8px 10px;
    min-width: auto;
    max-width: 160px;
    font-size: 12px;
  }
}

.global-nav-btn {
  animation: slideInStable 0.3s ease-out;
}

@keyframes slideInStable {
  from {
    opacity: 0;
    transform: translateY(-5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>