// session.js
import router from '@/router'
import { computed, reactive } from 'vue'
import { createResource } from 'frappe-ui'

import { userResource } from './user'

export function sessionUser() {
  const cookies = new URLSearchParams(document.cookie.split('; ').join('&'))
  let _sessionUser = cookies.get('user_id')
  if (_sessionUser === 'Guest') {
    _sessionUser = null
  }
  return _sessionUser
}

// Get user role from localStorage
export function getUserRole() {
  return localStorage.getItem('userRole')
}

// Set user role in localStorage
export function setUserRole(role) {
  localStorage.setItem('userRole', role)
}

// Clear user role from localStorage
export function clearUserRole() {
  localStorage.removeItem('userRole')
}

export const session = reactive({
  login: createResource({
    url: 'school.al_ummah.api2.admin_login',
    makeParams({ email, password }) {
      return {
        usr: email,
        pwd: password,
      }
    },
    onSuccess(data) {
      // Store user role from API response
      if (data.roles && data.roles.includes('Administrator')) {
        setUserRole('Administrator')
      }
      
      userResource.reload()
      session.user = sessionUser()
      session.userRole = getUserRole()
      session.login.reset()
      
      // Redirect to home
      router.replace('/')
    },
    onError(error) {
      // Clear any existing role on login error
      clearUserRole()
      session.userRole = null
      throw error
    },
  }),
  logout: createResource({
    url: 'logout',
    onSuccess() {
      // Clear user role on logout
      clearUserRole()
      userResource.reset()
      session.user = sessionUser()
      session.userRole = null
      router.replace({ name: 'Login' })
    },
    onError() {
      // Still clear role even if logout fails
      clearUserRole()
      session.userRole = null
    },
  }),
  user: sessionUser(),
  userRole: getUserRole(), // Initialize from localStorage
  isLoggedIn: computed(() => !!session.user),
  isAdmin: computed(() => session.userRole === 'Administrator'),
})