// data/session.js
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

// Optional: Add a helper to clear all auth data consistently
export function clearAuthData() {
  session.user = null
  localStorage.removeItem('selectedLoginRole')
  localStorage.removeItem('userRoles')
  localStorage.removeItem('user')
  localStorage.removeItem('session_id')
  localStorage.removeItem('logout_clicked_timestamp') // Add this for consistency
}

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
		async onSuccess(data) {
			console.log("Login successful:", data)
			
			if (data && data.status === "success") {
				userResource.reload()
				session.user = sessionUser()
				session.login.reset()
				
				// Store user roles if available
				if (data.roles) {
					localStorage.setItem('userRoles', JSON.stringify(data.roles))
				}
				
				// Emit success event - let router handle redirection
				window.dispatchEvent(new CustomEvent('login-success', {
					detail: data
				}))
				
			} else {
				const message = data.message || "Login failed. Please try again."
				// Error will be handled by component
				console.warn("Login failed:", message)
			}
		},
		onError(error) {
			console.error("Login failed:", error)
			// Error will be handled by component
		}
	}),
	
	// OTP Verification and Session Creation
	verifyOtp: createResource({
		url: "school.al_ummah.api2.verify_otp_and_create_session",
		makeParams({ phone, otp, role }) {
			return {
				phone: phone,
				otp: otp,
				role: role || "Instructor"
			}
		},
		async onSuccess(data) {
			console.log('OTP verified successfully:', data)
			
			if (data.status === 'success') {
				console.log('OTP login successful, session created on backend')
				
				// Store user info
				localStorage.setItem('user', JSON.stringify({
					username: data.user,
					role: data.role || 'teacher',
					roles: data.roles
				}))
				
				// Store user roles
				if (data.roles) {
					localStorage.setItem('userRoles', JSON.stringify(data.roles))
				}
				
				// Update session user
				session.user = sessionUser()
				
				// Reload user resource
				if (userResource) {
					userResource.reload()
				}
				
				// Emit success event - let router handle redirection
				window.dispatchEvent(new CustomEvent('otp-verification-success', {
					detail: data
				}))
				
			} else {
				const message = data.message || 'OTP verification failed. Please try again.'
				// Error will be handled by component
				console.warn("OTP verification failed:", message)
			}
		},
		onError(error) {
			console.error('Error verifying OTP:', error)
			// Error will be handled by component
		}
	}),
	
	// Google Sign-In Verification and Session Creation
	verifyGoogleToken: createResource({
		url: "school.al_ummah.api2.verify_google_token_and_create_session",
		makeParams({ id_token, role }) {
			return {
				id_token: id_token,
				role: role || "Instructor"
			}
		},
		async onSuccess(data) {
			console.log('Google token verified successfully:', data)
			
			if (data.success) {
				console.log('Google authentication successful, session created on backend')
				
				// Store user info
				localStorage.setItem('user', JSON.stringify({
					username: data.user,
					email: data.email,
					role: data.role || 'teacher',
					roles: data.roles
				}))

				// Store user roles
				if (data.roles) {
					localStorage.setItem('userRoles', JSON.stringify(data.roles))
				}

				// Store session info
				if (data.sid) {
					localStorage.setItem('session_id', data.sid)
				}

				// Update session user
				session.user = sessionUser()
				
				// Reload user resource
				if (userResource) {
					userResource.reload()
				}
				
				// Emit success event - let router handle redirection
				window.dispatchEvent(new CustomEvent('google-auth-success', {
					detail: data
				}))
				
			} else {
				const message = data.error || 'Google authentication failed. Please try again.'
				// Error will be handled by component
				console.warn("Google authentication failed:", message)
			}
		},
		onError(error) {
			console.error('Error verifying Google token:', error)
			// Error will be handled by component
		}
	}),
	

	// Then update logout to use it:
	logout: createResource({
	url: "logout",
	onSuccess() {
		userResource.reset()
		session.user = sessionUser()
		clearAuthData()
	},
	onError(error) {
		console.error("Logout failed:", error)
		// Fallback - clear everything
		session.user = null
		clearAuthData()
	}
	}),
	user: sessionUser(),
	isLoggedIn: computed(() => !!session.user),
})

// Export function to set the selected role
export function setSelectedLoginRole(role) {
	localStorage.setItem('selectedLoginRole', role)
	console.log("Role saved to localStorage:", role)
}

// Helper to get selected role
export function getSelectedLoginRole() {
	return localStorage.getItem('selectedLoginRole') || ''
}

// Google Sign-In utility functions
export const googleAuth = {
	// Your web client ID
	CLIENT_ID: "619580422153-9o7kvuuocsjfqejuv2jrud3h986t5prc.apps.googleusercontent.com",
	
	// Initialize Google Sign-In
	initialize: (buttonElementId, role = 'teacher') => {
		if (typeof window === 'undefined' || !window.google) {
			console.log('Google API not loaded yet')
			return false
		}

		try {
			window.google.accounts.id.initialize({
				client_id: googleAuth.CLIENT_ID,
				callback: (response) => googleAuth.handleCredentialResponse(response, role),
				auto_select: false,
				cancel_on_tap_outside: true,
				ux_mode: 'popup'
			})

			// Render Google button
			window.google.accounts.id.renderButton(
				document.getElementById(buttonElementId),
				{ 
					theme: 'outline', 
					size: 'large',
					width: 280,
					text: 'signin_with',
					shape: 'pill',
					logo_alignment: 'center'
				}
			)

			console.log('Google Sign-In initialized successfully')
			return true

		} catch (error) {
			console.error('Error initializing Google Sign-In:', error)
			return false
		}
	},
	
	// Handle credential response from Google
	handleCredentialResponse: async (response, role) => {
		try {
			console.log('Google credential response received', response)
			console.log('Current role:', role)
			
			// Convert role to backend format and send to API
			const backendRole = role === 'parent' ? 'Guardian' : 'Instructor'
			console.log('Sending role to API:', backendRole)
			
			// Send both id_token and role to the API
			await session.verifyGoogleToken.submit({
				id_token: response.credential,
				role: backendRole  // Send "Instructor" or "Guardian" to backend
			})
			
		} catch (error) {
			console.error('Error handling credential response:', error)
			// Error will be handled by component
		}
	},
	
	// Load Google API script
	loadScript: () => {
		return new Promise((resolve, reject) => {
			if (document.getElementById('google-js-sdk')) {
				resolve()
				return
			}

			const script = document.createElement('script')
			script.id = 'google-js-sdk'
			script.src = 'https://accounts.google.com/gsi/client'
			script.async = true
			script.defer = true
			script.onload = () => {
				setTimeout(() => {
					resolve()
				}, 100)
			}
			script.onerror = () => {
				console.error('Failed to load Google Sign-In script')
				reject(new Error('Failed to load Google Sign-In'))
			}
			document.head.appendChild(script)
		})
	}
}