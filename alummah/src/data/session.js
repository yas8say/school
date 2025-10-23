import router from "@/router"
import { createResource } from "frappe-ui"
import { computed, reactive } from "vue"

import { userResource } from "./user"

export function sessionUser() {
	const cookies = new URLSearchParams(document.cookie.split("; ").join("&"))
	let _sessionUser = cookies.get("user_id")
	if (_sessionUser === "Guest") {
		_sessionUser = null
	}
	return _sessionUser
}

// Store the selected role globally so it can be accessed in onSuccess
export let selectedLoginRole = ""  // Add export here

export const session = reactive({
	login: createResource({
		url: "school.al_ummah.api2.login",
		makeParams({ email, password, role }) {
			return {
				usr: email,
				pwd: password,
				role: role || "System User"
			}
		},
		onSuccess(data) {
			console.log("Login successful:", data)
			
			if (data && data.status === "success") {
				userResource.reload()
				session.user = sessionUser()
				session.login.reset()
				
				// Use the selected role from the login card, not the API response
				const routeName = selectedLoginRole === "parent" ? "Parenthome" : "Teacherhome"
				console.log("Redirecting based on selected role:", selectedLoginRole, "→", routeName)
				router.replace({ name: routeName })
			} else {
				// Fallback to default route if custom logic fails
				router.replace(data.default_route || "/")
			}
		},
		onError(error) {
			console.error("Login failed:", error)
			alert("Login failed. Please check your credentials and try again.")
		}
	}),
	logout: createResource({
		url: "logout",
		onSuccess() {
			userResource.reset()
			session.user = sessionUser()
			// Clear the selected role on logout
			selectedLoginRole = ""
			router.replace({ name: "Login" })
		},
		onError(error) {
			console.error("Logout failed:", error)
			// Still redirect to login even if logout API fails
			session.user = null
			selectedLoginRole = ""
			router.replace({ name: "Login" })
		}
	}),
	user: sessionUser(),
	isLoggedIn: computed(() => !!session.user),
})

// Export function to set the selected role
export function setSelectedLoginRole(role) {
	selectedLoginRole = role
}