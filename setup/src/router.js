// router.js
import { createRouter, createWebHistory } from 'vue-router'
import { session } from './data/session'
import { userResource } from '@/data/user'

const routes = [
  // Root path (/setup) redirects to login
  {
    path: '/',
    name: 'Root',
    redirect: '/account/login'
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/pages/Home.vue'),
    redirect: '/home/quick-setup',
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
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
  {
    name: 'Login',
    path: '/account/login',
    component: () => import('@/pages/Login.vue'),
    meta: { requiresAuth: false }
  },
  // Catch-all route - redirect any unknown paths to login
  {
    path: '/:pathMatch(.*)*',
    redirect: '/account/login'
  }
]

const router = createRouter({
  history: createWebHistory('/setup'),
  routes,
})

// Helper function to check admin access
async function checkAdminAccess() {
  // Wait for user resource to load if it's still loading
  if (userResource.loading) {
    await userResource.promise
  }
  
  // Multiple checks for Administrator role
  const isAdmin = 
    session.isAdmin ||
    session.hasRole('Administrator') ||
    (userResource.data?.roles?.includes('Administrator') ?? false)
  
  console.log('Router admin check:', {
    sessionIsAdmin: session.isAdmin,
    sessionUserRole: session.userRole,
    userResourceRoles: userResource.data?.roles,
    finalResult: isAdmin
  })
  
  return isAdmin
}

router.beforeEach(async (to, from, next) => {
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
    user: session.user
  })

  try {
    // Ensure user resource is loaded
    if (isLoggedIn && !userResource.data) {
      await userResource.reload()
    }
  } catch (error) {
    console.error('Failed to load user resource:', error)
  }

  // Public routes (no auth required)
  if (!requiresAuth) {
    if (to.name === 'Login' && isLoggedIn) {
      // Check if logged-in user is admin and redirect accordingly
      const isAdmin = await checkAdminAccess()
      if (isAdmin) {
        next({ name: 'Home' })
      } else {
        // Non-admin users stay on login page with message
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
    const isAdmin = await checkAdminAccess()
    
    if (!isAdmin) {
      console.warn('Access denied: User does not have Administrator privileges')
      
      // Show user-friendly error message
      const event = new CustomEvent('show-api-message-popup', {
        detail: {
          type: 'error',
          title: 'Access Denied',
          message: 'Administrator privileges are required to access this page. Please contact your system administrator if you need access.'
        }
      })
      window.dispatchEvent(event)
      
      // Prevent navigation
      next(false)
      return
    }
  }

  // All checks passed, allow navigation
  next()
})

export default router