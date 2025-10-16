// router.js
import { createRouter, createWebHistory } from 'vue-router'
import { session } from './data/session'
import { userResource } from '@/data/user'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/pages/Home.vue'),
    redirect: '/quick-setup',
    children: [
      {
        path: 'quick-setup', // removed leading slash
        name: 'QuickSetup',
        component: () => import('@/pages/QuickSetup.vue'),
      },
      {
        path: 'upload-students',
        name: 'UploadStudents',
        component: () => import('@/pages/UploadStudents.vue'),
      },
      {
        path: 'add-student',
        name: 'AddStudent',
        component: () => import('@/pages/AddStudent.vue'),
      },
      {
        path: 'upload-instructors',
        name: 'UploadInstructors',
        component: () => import('@/pages/UploadInstructors.vue'),
      },
      {
        path: 'add-instructor',
        name: 'AddInstructor',
        component: () => import('@/pages/AddInstructor.vue'),
      },
    ]
  },
  {
    name: 'Login',
    path: '/account/login',
    component: () => import('@/pages/Login.vue'),
  },
]


let router = createRouter({
  history: createWebHistory('/setup'),
  routes,
})

router.beforeEach(async (to, from, next) => {
  let isLoggedIn = session.isLoggedIn
  try {
    await userResource.promise
  } catch (error) {
    isLoggedIn = false
  }

  if (to.name === 'Login' && isLoggedIn) {
    next({ name: 'Home' })
  } else if (to.name !== 'Login' && !isLoggedIn) {
    next({ name: 'Login' })
  } else {
    next()
  }
})

export default router