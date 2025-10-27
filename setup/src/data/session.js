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

// Get user role from localStorage or userResource
export function getUserRole() {
  // First check localStorage (for backward compatibility)
  const storedRole = localStorage.getItem('userRole')
  if (storedRole) {
    return storedRole
  }
  
  // Then check userResource if available
  if (userResource?.data?.roles?.length) {
    const roles = userResource.data.roles
    if (roles.includes('Administrator')) {
      return 'Administrator'
    }
    // Return the first role as fallback
    return roles[0] || null
  }
  
  return null
}

// Set user role in localStorage
export function setUserRole(role) {
  localStorage.setItem('userRole', role)
}

// Clear user role from localStorage
export function clearUserRole() {
  localStorage.removeItem('userRole')
}

// Check if user has specific role
export function hasRole(roleName) {
  // Check localStorage first
  const storedRole = localStorage.getItem('userRole')
  if (storedRole === roleName) {
    return true
  }
  
  // Check userResource roles array
  if (userResource?.data?.roles?.includes(roleName)) {
    return true
  }
  
  return false
}

// Check if user has Administrator role
export function isAdministrator() {
  return hasRole('Administrator')
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
      console.log('Login success data:', data)
      
      // Store user role from API response
      if (data.roles && data.roles.includes('Administrator')) {
        setUserRole('Administrator')
        console.log('✅ User has Administrator role')
      } else if (data.roles && data.roles.length > 0) {
        // Store the first role as fallback
        setUserRole(data.roles[0])
        console.log('ℹ️ User role set to:', data.roles[0])
      } else {
        console.warn('⚠️ No roles found in login response')
      }
      
      // Reload user resource to get fresh data
      userResource.reload().then(() => {
        console.log('User resource reloaded:', userResource.data)
      })
      
      session.user = sessionUser()
      session.userRole = getUserRole()
      session.login.reset()
      
      // Redirect to home
      router.replace('/')
    },
    onError(error) {
      console.error('Login error:', error)
      // Clear any existing role on login error
      clearUserRole()
      session.userRole = null
      throw error
    },
  }),
  logout: createResource({
    url: 'logout',
    onSuccess() {
      console.log('Logout successful')
      // Clear user role on logout
      clearUserRole()
      userResource.reset()
      session.user = sessionUser()
      session.userRole = null
      router.replace({ name: 'Login' })
    },
    onError(error) {
      console.error('Logout error:', error)
      // Still clear role even if logout fails
      clearUserRole()
      session.userRole = null
    },
  }),
  user: sessionUser(),
  userRole: getUserRole(), // Initialize from localStorage or userResource
  isLoggedIn: computed(() => !!session.user),
  isAdmin: computed(() => {
    // Multiple ways to check for Administrator role
    const isAdmin = 
      session.userRole === 'Administrator' ||
      hasRole('Administrator') ||
      (userResource?.data?.roles?.includes('Administrator') ?? false)
    
    console.log('Admin check:', {
      userRole: session.userRole,
      hasRole: hasRole('Administrator'),
      userResourceRoles: userResource?.data?.roles,
      finalResult: isAdmin
    })
    
    return isAdmin
  }),
  
  // Additional helper methods
  hasRole: (roleName) => hasRole(roleName),
  isAdministrator: () => isAdministrator(),
  
  // Get all user roles
  getRoles: computed(() => {
    if (userResource?.data?.roles) {
      return userResource.data.roles
    }
    return session.userRole ? [session.userRole] : []
  })
})