import { createRouter, createWebHistory } from "vue-router"

const routes = [
	{
		path: "/",
		name: "Home",
		redirect: { name: "Login" }
	},
	{
		name: "Login",
		path: "/account/login",
		component: () => import("@/pages/Login.vue"),
		meta: { requiresAuth: false }
	},
	{
		name: "Teacherhome",
		path: "/teacher-home",
		component: () => import("@/pages/TeacherHome.vue"),
		meta: { requiresAuth: true, requiredRole: 'instructor' }
	},
	{
		name: "Parenthome", 
		path: "/parent-home",
		component: () => import("@/pages/ParentHome.vue"),
		meta: { requiresAuth: true, requiredRole: 'guardian' }
	},
	{
		name: "ForgotPassword",
		path: "/forgot-password",
		component: () => import("@/pages/ForgotPassword.vue"),
		meta: { requiresAuth: false }
	},
	{
		name: "OTPLogin",
		path: "/otp-login",
		component: () => import("@/pages/OTPLogin.vue"),
		meta: { requiresAuth: false }
	},
	{
		name: "SignInScreen",
		path: "/google-signin",
		component: () => import("@/pages/SignInScreen.vue"),
		meta: { requiresAuth: false }
	},
	{
		name: "TeacherSignup",
		path: "/teacher/signup",
		component: () => import("@/pages/TeacherSignup.vue"),
		meta: { requiresAuth: false }
	},
	{
		name: "ParentSignup",
		path: "/parent/signup",
		component: () => import("@/pages/ParentSignup.vue"),
		meta: { requiresAuth: false }
	},
]

const router = createRouter({
	history: createWebHistory("/alummah"),
	routes,
})

// Simple session check function
function isUserLoggedIn() {
	const cookies = new URLSearchParams(document.cookie.split("; ").join("&"))
	const userId = cookies.get("user_id")
	return userId && userId !== "Guest" && userId !== "undefined"
}

// Get user roles from localStorage
function getUserRoles() {
	try {
		const roles = localStorage.getItem('userRoles')
		return roles ? JSON.parse(roles) : []
	} catch {
		return []
	}
}

// Check if user has specific role
function hasRole(roleName) {
	const roles = getUserRoles()
	return roles.includes(roleName)
}

// Check if user has valid roles for this application
function hasValidRoles() {
	const roles = getUserRoles()
	return hasRole('Instructor') || hasRole('Guardian')
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

// Show error via UniversalPopup
function showError(type, title, message) {
	// Don't show role error popup if logout was recently clicked
	if (type === 'role' && wasLogoutRecentlyClicked()) {
		return
	}
	
	window.dispatchEvent(new CustomEvent('show-api-message-popup', {
		detail: {
			type: type || 'info',
			title: title || 'Information',
			message: message
		}
	}))
}

// Handle successful authentication redirection
function handleAuthSuccessRedirect() {
	const selectedRole = localStorage.getItem('selectedLoginRole')
	const userRoles = getUserRoles()
	
	// Role-based routing logic
	if (selectedRole === 'teacher' && hasRole('Instructor')) {
		return { name: "Teacherhome" }
	} else if (selectedRole === 'parent' && hasRole('Guardian')) {
		return { name: "Parenthome" }
	} else {
		// Auto-detect role if selection doesn't match actual roles
		if (hasRole('Instructor')) {
			localStorage.setItem('selectedLoginRole', 'teacher')
			return { name: "Teacherhome" }
		} else if (hasRole('Guardian')) {
			localStorage.setItem('selectedLoginRole', 'parent')
			return { name: "Parenthome" }
		} else {
			// No valid roles - but don't show popup if logout was recent
			if (!wasLogoutRecentlyClicked()) {
				showError('role', 'Access Restricted', 'Your account does not have the required permissions (Instructor or Guardian role) to access this application.')
			}
			return { name: "Login" }
		}
	}
}

// Listen for authentication success events
window.addEventListener('login-success', () => {
	const redirectTo = handleAuthSuccessRedirect()
	router.replace(redirectTo)
})

window.addEventListener('otp-verification-success', () => {
	const redirectTo = handleAuthSuccessRedirect()
	router.replace(redirectTo)
})

window.addEventListener('google-auth-success', () => {
	const redirectTo = handleAuthSuccessRedirect()
	router.replace(redirectTo)
})

router.beforeEach(async (to, from, next) => {
  // Clear expired logout timestamp on every navigation
  clearExpiredLogoutTimestamp()
  
  const isLoggedIn = isUserLoggedIn()
  
  // Define public routes that should always be accessible
  const alwaysPublicRoutes = ['ForgotPassword', 'OTPLogin', 'SignInScreen', 'TeacherSignup', 'ParentSignup']
  
  // Login is special - we want to redirect if already logged in, but allow access if not
  const loginRoute = 'Login'
  
  // Always allow access to these public routes regardless of login status
  if (alwaysPublicRoutes.includes(to.name)) {
    next()
    return
  }
  
  // Handle login route specifically
  if (to.name === loginRoute) {
    if (isLoggedIn) {
      // Check if user has valid roles for this application
      if (hasValidRoles()) {
        const redirectTo = handleAuthSuccessRedirect()
        next(redirectTo)
      } else {
        // User is logged in but doesn't have required roles
        // Don't show role error if logout was recent
        if (!wasLogoutRecentlyClicked()) {
          showError('role', 'Access Restricted', 'Your account does not have the required permissions (Instructor or Guardian role) to access this application.')
        }
        next()
      }
    } else {
      next()
    }
    return
  }
  
  // Auth required but not logged in
  if (!isLoggedIn) {
    next({ name: "Login" })
    return
  }
  
  // User is logged in - check if they have valid roles for this application
  const selectedRole = localStorage.getItem('selectedLoginRole')
  const userRoles = getUserRoles()
  
  // Check if user has valid roles for this application
  if (!hasValidRoles()) {
    // Don't show role error if logout was recent
    if (!wasLogoutRecentlyClicked()) {
      showError('role', 'Access Restricted', 'Your account does not have the required permissions (Instructor or Guardian role) to access this application.')
    }
    next({ name: "Login" })
    return
  }
  
  // Role-based routing logic for protected routes
  if (to.meta.requiredRole) {
    const requiredRole = to.meta.requiredRole
    
    if (requiredRole === 'instructor' && selectedRole === 'teacher' && hasRole('Instructor')) {
      next() // Allow access to teacher home
    } else if (requiredRole === 'guardian' && selectedRole === 'parent' && hasRole('Guardian')) {
      next() // Allow access to parent home
    } else {
      // Redirect to appropriate home based on actual roles
      const redirectTo = handleAuthSuccessRedirect()
      next(redirectTo)
    }
    return
  }
  
  // For all other authenticated routes without specific role requirements, allow access
  next()
})

export default router