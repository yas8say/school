import { userResource } from "@/data/user"
import { createRouter, createWebHistory } from "vue-router"
import { session, selectedLoginRole } from "./data/session"

const routes = [
	{
		path: "/",
		name: "Home",
		component: () => import("@/pages/Home.vue"),
	},
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
  try {
    await userResource.promise
  } catch (error) {
    isLoggedIn = false
  }

  console.log("User is logged in:", isLoggedIn)

  // Define public routes that don't require authentication
  const publicRoutes = ['Login', 'ForgotPassword', 'OTPLogin', 'SignInScreen', 'TeacherSignup', 'ParentSignup']
  
  if (to.name === "Login" && isLoggedIn) {
    // Redirect to appropriate home based on selectedLoginRole
    const routeName = selectedLoginRole === "parent" ? "Parenthome" : "Teacherhome"
    console.log("Redirecting to:", routeName)
    next({ name: routeName })
  } else if (!publicRoutes.includes(to.name) && !isLoggedIn) {
    console.log("User not logged in, redirecting to Login")
    next({ name: "Login" })
  } else if (to.name === "Home" && isLoggedIn) {
    // Redirect home to appropriate dashboard
    const routeName = selectedLoginRole === "parent" ? "Parenthome" : "Teacherhome"
    console.log("Redirecting home to:", routeName)
    next({ name: routeName })
  } else {
    console.log("Allowing navigation to:", to.name)
    next()
  }
})

export default router