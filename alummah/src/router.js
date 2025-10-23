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
	// New routes for teacher navigation
	{
		name: "Attendance",
		path: "/attendance",
		component: () => import("@/pages/Attendance.vue"),
	},
	{
		name: "AttendanceRecord",
		path: "/attendance-record", 
		component: () => import("@/pages/AttendanceRecord.vue"),
	},
	{
		name: "CreateNotice",
		path: "/create-notice",
		component: () => import("@/pages/CreateNotice.vue"),
	},
	{
		name: "PreviousNotices",
		path: "/previous-notices",
		component: () => import("@/pages/PreviousNotices.vue"),
	},
	{
		name: "BrowseLeaveAppeals",
		path: "/browse-leave-appeals",
		component: () => import("@/pages/BrowseLeaveAppeals.vue"),
	},
	{
		name: "AppealLeave", 
		path: "/appeal-leave",
		component: () => import("@/pages/AppealLeave.vue"),
	},
]

const router = createRouter({
	history: createWebHistory("/alummah"),
	routes,
})

router.beforeEach(async (to, from, next) => {
	let isLoggedIn = session.isLoggedIn
	try {
		await userResource.promise
	} catch (error) {
		isLoggedIn = false
	}

	if (to.name === "Login" && isLoggedIn) {
		// Redirect to appropriate home based on selectedLoginRole
		const routeName = selectedLoginRole === "parent" ? "Parenthome" : "Teacherhome"
		next({ name: routeName })
	} else if (to.name !== "Login" && !isLoggedIn) {
		next({ name: "Login" })
	} else if (to.name === "Home" && isLoggedIn) {
		// Redirect home to appropriate dashboard
		const routeName = selectedLoginRole === "parent" ? "Parenthome" : "Teacherhome"
		next({ name: routeName })
	} else {
		next()
	}
})

export default router