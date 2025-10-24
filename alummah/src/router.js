import { userResource } from "@/data/user"
import { createRouter, createWebHistory } from "vue-router"
import { session, selectedLoginRole } from "./data/session"

const routes = [
	{
		path: "/",
		name: "EditStudent",
		component: () => import("@/components/EditStudent.vue"),
	},
	{
		name: "Login",
		path: "/account/login",
		component: () => import("@/pages/Login.vue"),
	},
	{
		name: "Teacherhome",
		path: "/teacher-home",
		component: () => import("@/pages/TeacherHome.vue"),
	},
	{
		name: "Parenthome", 
		path: "/parent-home",
		component: () => import("@/pages/ParentHome.vue"),
	},
	{
		name: "ForgotPassword",
		path: "/forgot-password",
		component: () => import("@/pages/ForgotPassword.vue"),
	},
	{
		name: "OTPLogin",
		path: "/otp-login",
		component: () => import("@/pages/OTPLogin.vue"),
	},
	{
		name: "SignInScreen",
		path: "/google-signin",
		component: () => import("@/pages/SignInScreen.vue"),
	},
	{
		name: "TeacherSignup",
		path: "/teacher/signup",
		component: () => import("@/pages/TeacherSignup.vue"),
	},
	{
		name: "ParentSignup",
		path: "/parent/signup",
		component: () => import("@/pages/ParentSignup.vue"),
	},
	// REMOVED: All the component routes since they're now embedded in TeacherHome/ParentHome
]

const router = createRouter({
	history: createWebHistory("/alummah"),
	routes,
})

// In your router file
// In your router file
router.beforeEach(async (to, from, next) => {
  console.log("Route guard: from", from.name, "to", to.name)
  
  let isLoggedIn = session.isLoggedIn
  let userData = null
  
  try {
    await userResource.promise
    userData = userResource.data
  } catch (error) {
    isLoggedIn = false
  }

  console.log("User is logged in:", isLoggedIn)
  console.log("User data:", userData)

  // Define public routes that don't require authentication
  const publicRoutes = ['Login', 'ForgotPassword', 'OTPLogin', 'SignInScreen', 'TeacherSignup', 'ParentSignup']
  
  if (to.name === "Login" && isLoggedIn) {
    // Check user role and redirect accordingly
    const userRole = userData?.role || ''
    console.log("User role:", userRole)
    
    if (userRole === "Instructor" || userRole === "Guardian") {
      const routeName = selectedLoginRole === "parent" ? "Parenthome" : "Teacherhome"
      console.log("Redirecting to:", routeName, "based on role:", userRole)
      next({ name: routeName })
    } else {
      console.log("User role not Instructor or Guardian, allowing Login page")
      next()
    }
  } else if (!publicRoutes.includes(to.name) && !isLoggedIn) {
    console.log("User not logged in, redirecting to Login")
    next({ name: "Login" })
  } else {
    console.log("Allowing navigation to:", to.name)
    next()
  }
})

export default router