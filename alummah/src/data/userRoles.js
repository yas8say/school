import { createResource } from "frappe-ui"
import { reactive } from "vue"

export const userRolesStore = reactive({
  roles: [],
  isLoading: false,
  isLoaded: false,
  error: null
})

export const userRolesResource = createResource({
  url: "school.al_ummah.api2.get_user_roles",
  auto: false,
  onSuccess(data) {
    const rolesArray = Array.isArray(data) ? data : []
    
    userRolesStore.roles = rolesArray
    userRolesStore.isLoading = false
    userRolesStore.isLoaded = true
    userRolesStore.error = null
    
    localStorage.setItem('userRoles', JSON.stringify(rolesArray))
  },
  onError(error) {
    userRolesStore.isLoading = false
    userRolesStore.error = error
    // Fallback to stored roles
    const storedRoles = localStorage.getItem('userRoles')
    if (storedRoles) {
      try {
        userRolesStore.roles = JSON.parse(storedRoles)
        userRolesStore.isLoaded = true
      } catch (e) {
        userRolesStore.roles = []
      }
    }
  }
})

// Export the fetch function properly
export const fetchUserRoles = async () => {
  if (userRolesStore.isLoading) return
  
  userRolesStore.isLoading = true
  userRolesStore.error = null
  
  try {
    await userRolesResource.fetch()
  } catch (error) {
    console.error("Error in fetchUserRoles:", error)
  }
}

export const hasRole = (roleName) => {
  return userRolesStore.roles.includes(roleName)
}

export const isInstructor = () => {
  return hasRole('Instructor')
}

export const isGuardian = () => {
  return hasRole('Guardian')
}

// Initialize from localStorage
export const initializeUserRoles = () => {
  const storedRoles = localStorage.getItem('userRoles')
  if (storedRoles) {
    try {
      const parsedRoles = JSON.parse(storedRoles)
      userRolesStore.roles = Array.isArray(parsedRoles) ? parsedRoles : []
      userRolesStore.isLoaded = true
    } catch (e) {
      userRolesStore.roles = []
    }
  }
}

// Initialize on import
initializeUserRoles()