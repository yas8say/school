<template>
  <div class="flex min-h-screen bg-gray-50 flex-col md:flex-row">
    <!-- Mobile Header with Toggle -->
    <header class="md:hidden bg-white shadow-sm border-b">
      <div class="flex items-center justify-between p-4">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 rounded-full bg-blue-100 overflow-hidden flex-shrink-0">
            <img
              :src="adminImage"
              alt="Admin"
              class="object-cover w-full h-full"
            />
          </div>
          <div>
            <h1 class="text-lg font-semibold text-gray-800 truncate max-w-[150px]">{{ admin.name || 'Admin' }}</h1>
            <p class="text-xs text-gray-500">Administrator</p>
          </div>
        </div>
        <button
          @click="showSidebar = !showSidebar"
          class="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors"
          :aria-expanded="showSidebar"
          aria-label="Toggle menu"
        >
          <svg 
            class="w-6 h-6 text-gray-600" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              v-if="!showSidebar"
              stroke-linecap="round" 
              stroke-linejoin="round" 
              stroke-width="2" 
              d="M4 6h16M4 12h16M4 18h16" 
            />
            <path 
              v-else
              stroke-linecap="round" 
              stroke-linejoin="round" 
              stroke-width="2" 
              d="M6 18L18 6M6 6l12 12" 
            />
          </svg>
        </button>
      </div>
    </header>

    <!-- Sidebar Overlay for Mobile -->
    <div 
      v-if="showSidebar"
      class="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
      @click="showSidebar = false"
    ></div>

    <!-- Sidebar -->
    <aside
      :class="[
        'fixed md:static inset-y-0 left-0 z-50',
        'bg-white shadow-xl md:shadow-md p-6 space-y-8',
        'transform transition-transform duration-300 ease-in-out md:transform-none',
        'w-80 max-w-full md:w-72 flex flex-col',
        showSidebar ? 'translate-x-0' : '-translate-x-full md:translate-x-0',
        'md:block'
      ]"
    >
      <!-- Close button for mobile -->
      <div class="flex items-center justify-between md:hidden pb-4 border-b">
        <h2 class="text-lg font-semibold text-gray-800">Menu</h2>
        <button
          @click="showSidebar = false"
          class="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors"
          aria-label="Close menu"
        >
          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Admin Info Card -->
      <div class="flex items-start space-x-4 border-b pb-6">
        <div class="flex-shrink-0 w-16 h-16 rounded-full bg-gradient-to-br from-blue-100 to-blue-200 overflow-hidden border-2 border-white shadow-sm">
          <img
            :src="adminImage"
            alt="Admin"
            class="object-cover w-full h-full"
          />
        </div>
        <div class="min-w-0 flex-1">
          <h2 class="text-lg font-semibold text-gray-800 break-words leading-tight">{{ admin.name || 'No Name Available' }}</h2>
          <p class="text-sm text-gray-500 mt-1 flex items-center">
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            Administrator
          </p>
        </div>
      </div>

      <!-- Navigation Section -->
      <div class="space-y-6 flex-1 overflow-y-auto">
        <div class="space-y-3">
          <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Navigation</h3>
          <nav class="space-y-2">
            <router-link 
              v-for="nav in navigation"
              :key="nav.to"
              :to="nav.to" 
              class="block"
              @click="showSidebar = false"
            >
              <button
                :class="[
                  'w-full text-left px-4 py-3 rounded-xl font-medium flex items-center space-x-3 transition-all duration-200',
                  'group relative overflow-hidden',
                  route.path === nav.to 
                    ? nav.activeClasses
                    : nav.inactiveClasses
                ]"
              >
                <div class="flex items-center space-x-3 flex-1">
                  <div :class="['p-2 rounded-lg transition-colors', route.path === nav.to ? 'bg-white bg-opacity-20' : 'bg-white bg-opacity-50 group-hover:bg-opacity-70']">
                    <component :is="nav.icon" class="w-5 h-5" />
                  </div>
                  <span class="font-medium">{{ nav.label }}</span>
                </div>
                <div v-if="route.path === nav.to" class="w-1.5 h-1.5 rounded-full bg-current opacity-60"></div>
              </button>
            </router-link>
          </nav>
        </div>
      </div>

      <!-- Logout Button -->
      <div class="pt-4 border-t border-gray-100">
        <button
          class="w-full px-4 py-3 rounded-xl bg-red-50 text-red-600 font-medium hover:bg-red-100 flex items-center justify-center space-x-2 transition-all duration-200 group"
          @click="logout"
        >
          <svg class="w-5 h-5 transform group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          <span>Logout</span>
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 min-h-screen p-4 md:p-6 lg:p-8 bg-gray-50 overflow-auto">
      <div class="max-w-7xl mx-auto">
        <!-- Breadcrumb for larger screens -->
        <nav class="hidden md:flex items-center space-x-2 text-sm text-gray-500 mb-6">
          <router-link to="/home" class="hover:text-gray-700 transition-colors">Home</router-link>
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
          <span class="text-gray-800 font-medium capitalize">{{ currentPageTitle }}</span>
        </nav>

        <!-- Page Title for Mobile -->
        <div class="md:hidden mb-6">
          <h1 class="text-2xl font-bold text-gray-800 capitalize">{{ currentPageTitle }}</h1>
          <p class="text-gray-500 text-sm mt-1">Manage your school administration</p>
        </div>

        <!-- Router View Container -->
        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <router-view />
        </div>

        <!-- Mobile Bottom Navigation -->
        <div class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-3 md:hidden z-30">
          <div class="flex justify-around items-center">
            <router-link
              v-for="nav in mobileNavigation"
              :key="nav.to"
              :to="nav.to"
              :class="[
                'flex flex-col items-center p-2 rounded-lg transition-colors',
                route.path === nav.to ? 'text-blue-600 bg-blue-50' : 'text-gray-500 hover:text-gray-700'
              ]"
            >
              <component :is="nav.icon" class="w-6 h-6" />
              <span class="text-xs mt-1">{{ nav.label }}</span>
            </router-link>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { session } from '../data/session'

// Icons (you can replace these with your actual icon components)
const QuickSetupIcon = {
  template: `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>`
}

const UploadIcon = {
  template: `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>`
}

const AddUserIcon = {
  template: `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" /></svg>`
}

const SettingsIcon = {
  template: `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>`
}

const route = useRoute()
const router = useRouter()

const admin = ref({
  name: 'Admin User',
  role: 'Admin',
  image: null
})

const showSidebar = ref(false)

// Navigation configuration
const navigation = [
  {
    to: '/home/quick-setup',
    label: 'Quick Setup',
    icon: QuickSetupIcon,
    activeClasses: 'bg-blue-500 text-white shadow-lg shadow-blue-200',
    inactiveClasses: 'bg-blue-50 text-blue-700 hover:bg-blue-100 hover:text-blue-800 hover:shadow-md'
  },
  {
    to: '/home/upload-students',
    label: 'Upload Students',
    icon: UploadIcon,
    activeClasses: 'bg-blue-500 text-white shadow-lg shadow-blue-200',
    inactiveClasses: 'bg-blue-50 text-blue-700 hover:bg-blue-100 hover:text-blue-800 hover:shadow-md'
  },
  {
    to: '/home/add-student',
    label: 'Add Student',
    icon: AddUserIcon,
    activeClasses: 'bg-green-500 text-white shadow-lg shadow-green-200',
    inactiveClasses: 'bg-green-50 text-green-700 hover:bg-green-100 hover:text-green-800 hover:shadow-md'
  },
  {
    to: '/home/upload-instructors',
    label: 'Upload Instructors',
    icon: UploadIcon,
    activeClasses: 'bg-yellow-500 text-white shadow-lg shadow-yellow-200',
    inactiveClasses: 'bg-yellow-50 text-yellow-700 hover:bg-yellow-100 hover:text-yellow-800 hover:shadow-md'
  },
  {
    to: '/home/add-instructor',
    label: 'Add Instructor',
    icon: AddUserIcon,
    activeClasses: 'bg-purple-500 text-white shadow-lg shadow-purple-200',
    inactiveClasses: 'bg-purple-50 text-purple-700 hover:bg-purple-100 hover:text-purple-800 hover:shadow-md'
  },
  {
    to: '/home/admin-settings',
    label: 'Admin Settings',
    icon: SettingsIcon,
    activeClasses: 'bg-gray-500 text-white shadow-lg shadow-gray-200',
    inactiveClasses: 'bg-gray-50 text-gray-700 hover:bg-gray-100 hover:text-gray-800 hover:shadow-md'
  }
]

// Mobile navigation (simplified for bottom bar)
const mobileNavigation = [
  { to: '/home/quick-setup', label: 'Setup', icon: QuickSetupIcon },
  { to: '/home/upload-students', label: 'Upload', icon: UploadIcon },
  { to: '/home/add-student', label: 'Add', icon: AddUserIcon },
  { to: '/home/admin-settings', label: 'Settings', icon: SettingsIcon }
]

// Computed property to handle the image source
const adminImage = computed(() => {
  if (admin.value.image) {
    return `data:image/jpeg;base64,${admin.value.image}`
  }
  return new URL('../assets/admin.png', import.meta.url).href
})

// Current page title for display
const currentPageTitle = computed(() => {
  const path = route.path
  if (path.includes('quick-setup')) return 'Quick Setup'
  if (path.includes('upload-students')) return 'Upload Students'
  if (path.includes('add-student')) return 'Add Student'
  if (path.includes('upload-instructors')) return 'Upload Instructors'
  if (path.includes('add-instructor')) return 'Add Instructor'
  if (path.includes('admin-settings')) return 'Admin Settings'
  return 'Dashboard'
})

const logout = async () => {
  try {
    await session.logout.submit()
    router.push('/account/login')
  } catch (error) {
    console.error('Logout error:', error)
  }
}

// Close sidebar when clicking outside on mobile
const handleClickOutside = (event) => {
  if (showSidebar.value && !event.target.closest('aside') && !event.target.closest('header')) {
    showSidebar.value = false
  }
}

// Handle escape key to close sidebar
const handleEscapeKey = (event) => {
  if (event.key === 'Escape' && showSidebar.value) {
    showSidebar.value = false
  }
}

// Handle window resize
const handleResize = () => {
  if (window.innerWidth >= 768) {
    showSidebar.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  document.addEventListener('keydown', handleEscapeKey)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('keydown', handleEscapeKey)
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
/* Smooth scrolling for sidebar */
aside {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e0 transparent;
}

aside::-webkit-scrollbar {
  width: 4px;
}

aside::-webkit-scrollbar-track {
  background: transparent;
}

aside::-webkit-scrollbar-thumb {
  background-color: #cbd5e0;
  border-radius: 2px;
}

aside::-webkit-scrollbar-thumb:hover {
  background-color: #a0aec0;
}

/* Ensure proper spacing for mobile bottom nav */
main {
  padding-bottom: 80px; /* Space for bottom navigation */
}

@media (min-width: 768px) {
  main {
    padding-bottom: 2rem; /* Reset for desktop */
  }
}

/* Improved focus styles for accessibility */
button:focus-visible,
a:focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Smooth transitions */
* {
  transition-property: color, background-color, border-color, transform, opacity;
  transition-duration: 200ms;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}
</style>