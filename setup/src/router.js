// router.js
import { createRouter, createWebHistory } from 'vue-router'
import { session } from './data/session'
import { userResource } from '@/data/user'

const routes = [
  {
    path: '/',
    name: 'Root',
    redirect: { name: 'Login' }
  },
  {
    name: 'Login',
    path: '/account/login',
    component: () => import('@/pages/Login.vue'),
    meta: { requiresAuth: false }
  },
  // Home dashboard with nested routes - ADMIN ONLY
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/pages/Home.vue'),
    redirect: '/home/quick-setup',
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: 'fee-schedule',
        name: 'Fee Schedule',
        component: () => import('@/pages/FeeSchedule.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'fee-payments',
        name: 'Fee Payments',
        component: () => import('@/pages/FeePayments.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'quick-setup',
        name: 'QuickSetup',
        component: () => import('@/pages/QuickSetup.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'upload-students',
        name: 'UploadStudents',
        component: () => import('@/pages/UploadStudents.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'add-student',
        name: 'AddStudent',
        component: () => import('@/pages/AddStudent.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'upload-instructors',
        name: 'UploadInstructors',
        component: () => import('@/pages/UploadInstructors.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'add-instructor',
        name: 'AddInstructor',
        component: () => import('@/pages/AddInstructor.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'admin-settings',
        name: 'AdminSettings',
        component: () => import('@/pages/AdminSettings.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
    ]
  },
  // Catch-all route
  {
    path: '/:pathMatch(.*)*',
    redirect: '/account/login'
  }
]

const router = createRouter({
  history: createWebHistory('/setup'),
  routes,
})

// Helper function to show universal popup
function showUniversalPopup(type, title, message) {
  const event = new CustomEvent('show-universal-popup', {
    detail: { type, title, message }
  })
  window.dispatchEvent(event)
}

// Check if logout was recently clicked (within last 5 seconds)
function wasLogoutRecentlyClicked() {
  const logoutTimestamp = localStorage.getItem('logout_clicked_timestamp')
  if (!logoutTimestamp) return false
  
  const now = Date.now()
  const timeDiff = now - parseInt(logoutTimestamp)
  return timeDiff < 5000 // 5 seconds
}

// Clear old logout timestamp (only if it's expired)
function clearExpiredLogoutTimestamp() {
  const logoutTimestamp = localStorage.getItem('logout_clicked_timestamp')
  if (!logoutTimestamp) return
  
  const now = Date.now()
  const timeDiff = now - parseInt(logoutTimestamp)
  
  // Only clear if it's older than 5 seconds
  if (timeDiff > 5000) {
    localStorage.removeItem('logout_clicked_timestamp')
  }
}

// Show error via UniversalPopup (with logout timestamp check)
function showError(type, title, message) {
  // Don't show role error popup if logout was recently clicked
  if (type === 'role' && wasLogoutRecentlyClicked()) {
    console.log('Suppressing role error popup - logout was recently clicked')
    return
  }
  
  showUniversalPopup(type, title, message)
}

// Check if user has Administrator role
function hasAdministratorRole() {
  // Use session's isAdministrator method
  return session.isAdministrator()
}

// Check if user has valid role for this application (Administrator only)
function hasValidRole() {
  return hasAdministratorRole()
}

// Handle successful authentication redirection for Admin
function handleAuthSuccessRedirect() {
  if (hasAdministratorRole()) {
    return { name: 'Home' }
  } else {
    // No admin role - but don't show popup if logout was recent
    if (!wasLogoutRecentlyClicked()) {
      showError(
        'role', 
        'Access Restricted', 
        'Your account does not have Administrator privileges required to access this portal.'
      )
    }
    return { name: 'Login' }
  }
}

router.beforeEach(async (to, from, next) => {
  // Clear expired logout timestamp on every navigation
  clearExpiredLogoutTimestamp()
  
  const isLoggedIn = session.isLoggedIn
  const requiresAuth = to.meta.requiresAuth
  const requiresAdmin = to.meta.requiresAdmin
  
  console.log('Navigation guard:', {
    to: to.name,
    path: to.path,
    fullPath: to.fullPath,
    requiresAuth,
    requiresAdmin,
    isLoggedIn,
    hasAdministratorRole: hasAdministratorRole(),
    wasLogoutRecentlyClicked: wasLogoutRecentlyClicked()
  })

  try {
    // Ensure user resource is loaded if user is logged in
    if (isLoggedIn && !userResource.data) {
      await userResource.reload()
    }
  } catch (error) {
    console.error('Failed to load user resource:', error)
  }

  // Public routes (no auth required)
  if (!requiresAuth) {
    if (to.name === 'Login' && isLoggedIn) {
      // Check if logged-in user is admin
      const isAdmin = hasAdministratorRole()
      console.log('Login page access - User logged in:', {
        isLoggedIn,
        isAdmin,
        wasLogoutRecentlyClicked: wasLogoutRecentlyClicked()
      })
      
      if (isAdmin) {
        // Redirect admin users to home dashboard
        console.log('Redirecting admin user to Home')
        next({ name: 'Home' })
      } else {
        // Non-admin users stay on login page with message
        console.log('Non-admin user staying on login page')
        showError(
          'role',
          'Access Information',
          'You are logged in but do not have Administrator privileges. This portal is for administrators only.'
        )
        next()
      }
    } else {
      next()
    }
    return
  }

  // Check authentication
  if (!isLoggedIn) {
    console.log('User not logged in, redirecting to login')
    next({ name: 'Login' })
    return
  }

  // Check admin privileges for admin-only routes
  if (requiresAdmin) {
    const isAdmin = hasAdministratorRole()
    
    if (!isAdmin) {
      console.warn('Access denied: User does not have Administrator privileges')
      
      showError(
        'role',
        'Access Denied',
        'Administrator privileges are required to access this portal. Please logout and contact your system administrator.'
      )
      
      // Prevent navigation - let the user decide to logout via popup
      next(false)
      return
    }
  }

  // All checks passed, allow navigation
  console.log('Navigation allowed to:', to.name)
  next()
})

export default router