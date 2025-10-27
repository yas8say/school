// router.js (simplified version)
import { createRouter, createWebHistory } from 'vue-router'
import { session } from './data/session'
import { userResource } from '@/data/user'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/pages/Home.vue'),
    redirect: '/quick-setup',
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
]

const router = createRouter({
  history: createWebHistory('/setup'),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const isLoggedIn = session.isLoggedIn
  const isAdmin = session.isAdmin
  
  try {
    await userResource.promise
  } catch (error) {
    // User resource failed to load
  }

  // Public routes
  if (!to.meta.requiresAuth) {
    if (to.name === 'Login' && isLoggedIn && isAdmin) {
      next({ name: 'Home' })
    } else {
      next()
    }
    return
  }

  // Check authentication
  if (!isLoggedIn) {
    next({ name: 'Login' })
    return
  }

  // Check admin privileges
  if (to.meta.requiresAdmin && !isAdmin) {
    // Show alert and prevent navigation
    alert('Access Denied: Administrator privileges required.')
    next(false)
    return
  }

  next()
})

export default router