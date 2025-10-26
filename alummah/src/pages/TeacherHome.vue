<template>
  <div class="flex min-h-screen bg-gray-50 flex-col md:flex-row">
    <!-- Error State -->
    <div v-if="globalError" class="fixed inset-0 bg-red-50 bg-opacity-90 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg shadow-lg p-6 max-w-md w-full">
        <div class="flex items-center mb-4">
          <div class="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center mr-3">
            <ExclamationTriangleIcon class="w-6 h-6 text-red-600" />
          </div>
          <h3 class="text-lg font-semibold text-red-800">Something went wrong</h3>
        </div>
        <p class="text-gray-600 mb-4">{{ globalError }}</p>
        <div class="flex space-x-3">
          <button 
            @click="retryLoading" 
            class="flex-1 bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 transition-colors"
          >
            Try Again
          </button>
          <button 
            @click="handleLogout" 
            class="flex-1 bg-gray-200 text-gray-800 py-2 px-4 rounded-md hover:bg-gray-300 transition-colors"
          >
            Logout
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-else-if="userDetailsResource.loading && !hasInitialData" class="fixed inset-0 bg-white bg-opacity-80 flex items-center justify-center z-50">
      <div class="text-center">
        <div class="spinner mb-4 mx-auto"></div>
        <p class="text-gray-600">Loading your dashboard...</p>
      </div>
    </div>

    <!-- Main Application -->
    <div v-else class="flex flex-col md:flex-row w-full min-h-screen">
      <!-- Mobile Header -->
      <header class="md:hidden bg-white shadow-sm border-b border-gray-200 p-4 flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 rounded-full bg-gray-200 overflow-hidden flex-shrink-0">
            <img
              v-if="teacher.image"
              :src="`data:image/jpeg;base64,${teacher.image}`"
              alt="Teacher"
              class="object-cover w-full h-full"
              @error="handleImageError"
            />
            <div v-else class="w-full h-full flex items-center justify-center bg-gray-100">
              <UserIcon class="w-5 h-5 text-gray-400" />
            </div>
          </div>
          <div class="min-w-0 flex-1">
            <h2 class="text-sm font-semibold text-gray-800 truncate">{{ teacher.name || 'Teacher' }}</h2>
            <p class="text-xs text-gray-500">Teacher</p>
          </div>
        </div>
        <button
          @click="showSidebar = !showSidebar"
          class="p-2 rounded-md text-gray-600 hover:bg-gray-100 transition-colors"
        >
          <Bars3Icon class="w-6 h-6" />
        </button>
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
          'bg-white shadow-md p-4 md:p-6 space-y-6 md:space-y-8 z-50',
          'fixed md:relative inset-y-0 left-0 transform transition-transform duration-300 ease-in-out',
          'w-72 max-w-full',
          showSidebar ? 'translate-x-0' : '-translate-x-full md:translate-x-0',
          'flex flex-col h-screen md:h-auto'
        ]"
      >
        <!-- Close button for mobile -->
        <div class="flex items-center justify-between md:hidden pb-4 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-800">Menu</h3>
          <button
            @click="showSidebar = false"
            class="p-2 rounded-md text-gray-600 hover:bg-gray-100 transition-colors"
          >
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>

        <!-- Scrollable content -->
        <div class="flex-1 overflow-y-auto space-y-6 md:space-y-8">
          <!-- Teacher Info Card - Hidden on mobile since we have header -->
          <div class="hidden md:flex items-start space-x-4 border-b pb-4">
            <div class="flex-shrink-0 w-16 h-16 rounded-full bg-gray-200 overflow-hidden">
              <img
                v-if="teacher.image"
                :src="`data:image/jpeg;base64,${teacher.image}`"
                alt="Teacher"
                class="object-cover w-full h-full"
                @error="handleImageError"
              />
              <div v-else class="w-full h-full flex items-center justify-center bg-gray-100">
                <UserIcon class="w-6 h-6 text-gray-400" />
              </div>
            </div>
            <div class="min-w-0 flex-1">
              <h2 class="text-xl font-semibold text-gray-800 break-words">{{ teacher.name || 'Loading...' }}</h2>
              <p class="text-sm text-gray-500 mt-1">Teacher</p>
            </div>
          </div>

          <!-- Class Selection -->
          <div class="space-y-2">
            <label class="block text-sm font-medium text-gray-700">Select Class:</label>
            <select 
              v-model="selectedGroup" 
              @change="handleGroupChange" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm md:text-base"
              :disabled="userDetailsResource.loading || !studentGroups.length"
            >
              <option value="" disabled>Select a class</option>
              <option v-for="(group, index) in studentGroups" :key="index" :value="group">
                {{ group }}
              </option>
            </select>
            <p v-if="!studentGroups.length" class="text-sm text-yellow-600">
              No classes available
            </p>
          </div>

          <!-- Navigation Buttons -->
          <div class="space-y-3">
            <h3 class="text-sm font-medium text-gray-700">Navigation</h3>
            <nav class="space-y-2">
              <button
                @click="setActiveView('dashboard')"
                :class="[
                  'w-full text-left px-4 py-3 rounded font-medium flex items-center space-x-3 transition-colors text-sm md:text-base',
                  activeView === 'dashboard' 
                    ? 'bg-blue-100 border border-blue-200 text-blue-800' 
                    : 'bg-blue-50 text-blue-800 hover:bg-blue-100'
                ]"
                :disabled="userDetailsResource.loading"
              >
                <HomeIcon class="w-5 h-5 flex-shrink-0" />
                <span class="truncate">Dashboard</span>
              </button>

              <button
                @click="setActiveView('attendance')"
                :class="[
                  'w-full text-left px-4 py-3 rounded font-medium flex items-center space-x-3 transition-colors text-sm md:text-base',
                  activeView === 'attendance' 
                    ? 'bg-blue-100 border border-blue-200 text-blue-800' 
                    : 'bg-blue-50 text-blue-800 hover:bg-blue-100'
                ]"
                :disabled="!selectedGroup || userDetailsResource.loading"
              >
                <ClipboardDocumentListIcon class="w-5 h-5 flex-shrink-0" />
                <span class="truncate">Take Attendance</span>
              </button>

              <button
                @click="setActiveView('attendance-record')"
                :class="[
                  'w-full text-left px-4 py-3 rounded font-medium flex items-center space-x-3 transition-colors text-sm md:text-base',
                  activeView === 'attendance-record' 
                    ? 'bg-green-100 border border-green-200 text-green-800' 
                    : 'bg-green-50 text-green-800 hover:bg-green-100'
                ]"
                :disabled="!selectedGroup || userDetailsResource.loading"
              >
                <UserGroupIcon class="w-5 h-5 flex-shrink-0" />
                <span class="truncate">Student Record</span>
              </button>

              <button
                @click="setActiveView('create-notice')"
                :class="[
                  'w-full text-left px-4 py-3 rounded font-medium flex items-center space-x-3 transition-colors text-sm md:text-base',
                  activeView === 'create-notice' 
                    ? 'bg-yellow-100 border border-yellow-200 text-yellow-800' 
                    : 'bg-yellow-50 text-yellow-800 hover:bg-yellow-100'
                ]"
                :disabled="!selectedGroup || userDetailsResource.loading"
              >
                <PlusCircleIcon class="w-5 h-5 flex-shrink-0" />
                <span class="truncate">Create Notice</span>
              </button>

              <button
                @click="setActiveView('previous-notices')"
                :class="[
                  'w-full text-left px-4 py-3 rounded font-medium flex items-center space-x-3 transition-colors text-sm md:text-base',
                  activeView === 'previous-notices' 
                    ? 'bg-purple-100 border border-purple-200 text-purple-800' 
                    : 'bg-purple-50 text-purple-800 hover:bg-purple-100'
                ]"
                :disabled="!selectedGroup || userDetailsResource.loading"
              >
                <DocumentTextIcon class="w-5 h-5 flex-shrink-0" />
                <span class="truncate">Previous Notices</span>
              </button>

              <button
                @click="setActiveView('leave-appeals')"
                :class="[
                  'w-full text-left px-4 py-3 rounded font-medium flex items-center space-x-3 transition-colors text-sm md:text-base',
                  activeView === 'leave-appeals' 
                    ? 'bg-indigo-100 border border-indigo-200 text-indigo-800' 
                    : 'bg-indigo-50 text-indigo-800 hover:bg-indigo-100'
                ]"
                :disabled="!selectedGroup || userDetailsResource.loading"
              >
                <InboxIcon class="w-5 h-5 flex-shrink-0" />
                <span class="truncate">Browse Leave Appeals</span>
              </button>
            </nav>
          </div>
        </div>

        <!-- Logout Button -->
        <div class="pt-4 border-t border-gray-200 flex-shrink-0">
          <button
            class="w-full px-4 py-3 rounded bg-red-100 text-red-600 font-medium hover:bg-red-200 flex items-center justify-center space-x-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm md:text-base"
            @click="handleLogout"
            :disabled="userDetailsResource.loading"
          >
            <ArrowRightOnRectangleIcon class="w-5 h-5 flex-shrink-0" />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      <!-- Main Content Area -->
      <main class="flex-1 min-h-screen md:min-h-0 p-4 md:p-6 lg:p-8 bg-gray-50" :class="{ 'opacity-50 pointer-events-none': userDetailsResource.loading }">
        <!-- Dashboard View -->
        <div v-if="activeView === 'dashboard'">
          <!-- Welcome Section -->
          <div class="bg-white rounded-lg shadow-sm p-4 md:p-6 mb-4 md:mb-6">
            <h1 class="text-xl md:text-2xl font-bold text-gray-800 mb-2">Welcome, {{ teacher.name || 'Teacher' }}!</h1>
            <p class="text-gray-600 text-sm md:text-base">Manage your classroom activities and student records from here.</p>
          </div>

          <!-- Quick Stats Grid -->
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6 mb-4 md:mb-6">
            <div class="bg-white rounded-lg shadow-sm p-4 md:p-6 border-l-4 border-blue-500">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-xs md:text-sm font-medium text-gray-600">Selected Class</p>
                  <p class="text-lg md:text-2xl font-bold text-gray-800 truncate">{{ selectedGroup || 'None' }}</p>
                </div>
                <UserGroupIcon class="w-6 h-6 md:w-8 md:h-8 text-blue-500 flex-shrink-0" />
              </div>
            </div>

            <div class="bg-white rounded-lg shadow-sm p-4 md:p-6 border-l-4 border-green-500">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-xs md:text-sm font-medium text-gray-600">Available Classes</p>
                  <p class="text-lg md:text-2xl font-bold text-gray-800">{{ studentGroups.length }}</p>
                </div>
                <ClipboardDocumentListIcon class="w-6 h-6 md:w-8 md:h-8 text-green-500 flex-shrink-0" />
              </div>
            </div>

            <div class="bg-white rounded-lg shadow-sm p-4 md:p-6 border-l-4 border-purple-500">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-xs md:text-sm font-medium text-gray-600">Today's Date</p>
                  <p class="text-lg md:text-2xl font-bold text-gray-800">{{ currentDate }}</p>
                </div>
                <CalendarIcon class="w-6 h-6 md:w-8 md:h-8 text-purple-500 flex-shrink-0" />
              </div>
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="bg-white rounded-lg shadow-sm p-4 md:p-6">
            <h2 class="text-lg font-semibold text-gray-800 mb-4">Quick Actions</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 md:gap-4">
              <button 
                @click="setActiveView('attendance')"
                :disabled="!selectedGroup"
                class="flex items-center p-3 md:p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed text-left"
              >
                <ClipboardDocumentListIcon class="w-5 h-5 md:w-6 md:h-6 text-blue-600 mr-3 flex-shrink-0" />
                <div class="min-w-0 flex-1">
                  <h3 class="font-medium text-gray-800 text-sm md:text-base">Take Today's Attendance</h3>
                  <p class="text-xs md:text-sm text-gray-600 truncate">Mark student attendance for today</p>
                </div>
              </button>

              <button 
                @click="setActiveView('create-notice')"
                :disabled="!selectedGroup"
                class="flex items-center p-3 md:p-4 border border-gray-200 rounded-lg hover:border-yellow-500 hover:bg-yellow-50 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed text-left"
              >
                <PlusCircleIcon class="w-5 h-5 md:w-6 md:h-6 text-yellow-600 mr-3 flex-shrink-0" />
                <div class="min-w-0 flex-1">
                  <h3 class="font-medium text-gray-800 text-sm md:text-base">Create New Notice</h3>
                  <p class="text-xs md:text-sm text-gray-600 truncate">Send announcement to students</p>
                </div>
              </button>
            </div>
            <p v-if="!selectedGroup" class="text-sm text-yellow-600 mt-3">
              Please select a class to access these features
            </p>
          </div>
        </div>

        <!-- Dynamic Component Views -->
        <div v-else class="h-full">
          <component 
            :is="getActiveComponent()" 
            :selected-group="selectedGroup"
            @back-to-dashboard="setActiveView('dashboard')"
            :key="selectedGroup + activeView"
          />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { session } from '@/data/session'
import { createResource } from 'frappe-ui'

// Import Heroicons
import {
  HomeIcon,
  ClipboardDocumentListIcon,
  UserGroupIcon,
  PlusCircleIcon,
  DocumentTextIcon,
  InboxIcon,
  ArrowRightOnRectangleIcon,
  CalendarIcon,
  ExclamationTriangleIcon,
  Bars3Icon,
  UserIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'

// Import Components
import Attendance from '@/components/Attendance.vue'
import AttendanceRecord from '@/components/AttendanceRecord.vue'
import CreateNotice from '@/components/CreateNotice.vue'
import PreviousNotices from '@/components/PreviousNotices.vue'
import LeaveAppeals from '@/components/LeaveAppeals.vue'

const router = useRouter()

// Reactive state
const teacher = ref({})
const studentGroups = ref([])
const selectedGroup = ref('')
const showSidebar = ref(false)
const activeView = ref('dashboard')
const globalError = ref(null)
const hasInitialData = ref(false)

// Component mapping
const componentMap = {
  'attendance': Attendance,
  'attendance-record': AttendanceRecord,
  'create-notice': CreateNotice,
  'previous-notices': PreviousNotices,
  'leave-appeals': LeaveAppeals
}

const getActiveComponent = () => componentMap[activeView.value] || null

// Set active view function
const setActiveView = (view) => {
  if (userDetailsResource.loading) return
  
  activeView.value = view
  if (window.innerWidth < 768) {
    showSidebar.value = false
  }
}

// Get current user and role
const currentUser = session.user
const currentRole = 'teacher'

// Initialize with localStorage data first for better UX
const initializeFromLocalStorage = () => {
  try {
    const userDetailsData = localStorage.getItem('user_details')
    const savedGroup = localStorage.getItem('selected_student_group')
    
    if (userDetailsData) {
      const userDetails = JSON.parse(userDetailsData)
      teacher.value = {
        name: userDetails.name,
        image: userDetails.base64profile,
      }
      if (userDetails.student_groups?.length) {
        studentGroups.value = userDetails.student_groups
        selectedGroup.value = savedGroup || userDetails.student_groups[0]
        hasInitialData.value = true
      }
    }
  } catch (error) {
    console.warn('Error loading from localStorage:', error)
  }
}

// Create resource for API call with better error handling
const userDetailsResource = createResource({
  url: 'school.al_ummah.api2.get_user_details',
  params: { 
    role: currentRole,
    username: currentUser
  },
  auto: false,
  onSuccess(data) {
    console.log('User details loaded:', data)
    globalError.value = null
    
    try {
      if (data && data.user_details) {
        teacher.value = {
          name: data.user_details.name,
          image: data.user_details.base64profile,
        }

        if (data.user_details.student_groups?.length) {
          studentGroups.value = data.user_details.student_groups
          selectedGroup.value = data.user_details.student_groups[0]
          localStorage.setItem('selected_student_group', data.user_details.student_groups[0])
        }

        localStorage.setItem('user_details', JSON.stringify(data.user_details))
        hasInitialData.value = true
      } else {
        globalError.value = 'No user data received from server'
      }
    } catch (error) {
      console.error('Error processing user data:', error)
      globalError.value = 'Error processing user data'
    }
  },
  onError(error) {
    console.error('Error loading user details:', error)
    globalError.value = 'Failed to load user data. Please try again.'
    
    // If we don't have any data from localStorage, show error
    if (!hasInitialData.value) {
      loadUserDetailsFromLocalStorage()
    }
  }
})

// Computed properties
const currentDate = computed(() => {
  return new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

// Fallback to localStorage if API fails
const loadUserDetailsFromLocalStorage = () => {
  try {
    initializeFromLocalStorage()
    if (teacher.value.name || studentGroups.value.length) {
      hasInitialData.value = true
      globalError.value = null
    }
  } catch (error) {
    console.error('Error loading from localStorage:', error)
    globalError.value = 'Unable to load user data. Please refresh the page.'
  }
}

// Handle group selection change
const handleGroupChange = async () => {
  if (selectedGroup.value) {
    localStorage.setItem('selected_student_group', selectedGroup.value)
  }
}

// Handle image loading errors
const handleImageError = (event) => {
  event.target.style.display = 'none'
  const nextSibling = event.target.nextElementSibling
  if (nextSibling) {
    nextSibling.style.display = 'flex'
  }
}

// Retry loading data
const retryLoading = () => {
  globalError.value = null
  hasInitialData.value = false
  userDetailsResource.reload()
}

// Handle logout
const handleLogout = async () => {
  try {
    localStorage.removeItem('user_details')
    localStorage.removeItem('user')
    localStorage.removeItem('selected_student_group')
    await session.logout.submit()
    router.push({ name: 'Login' })
  } catch (error) {
    console.error('Logout error:', error)
    localStorage.clear()
    router.push({ name: 'Login' })
  }
}

// Handle window resize
const handleResize = () => {
  if (window.innerWidth >= 768) {
    showSidebar.value = false
  }
}

onMounted(() => {
  // Load from localStorage first for immediate UI
  initializeFromLocalStorage()
  
  // Add resize listener
  window.addEventListener('resize', handleResize)
  
  // Then try to fetch fresh data with error handling
  setTimeout(() => {
    userDetailsResource.reload().catch(error => {
      console.error('Failed to reload user details:', error)
      globalError.value = 'Network error. Please check your connection.'
    })
  }, 100)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

// Watch for loading state changes
watch(() => userDetailsResource.loading, (loading) => {
  if (!loading && userDetailsResource.data) {
    console.log('Data loaded successfully')
  }
})

// Auto-hide sidebar when view changes on mobile
watch(() => activeView.value, () => {
  if (window.innerWidth < 768) {
    showSidebar.value = false
  }
})
</script>

<style scoped>
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Improved responsive design */
@media (max-width: 768px) {
  .flex.min-h-screen {
    min-height: 100vh;
  }
  
  main {
    min-height: calc(100vh - 80px);
  }
}

/* Ensure proper scrolling on mobile */
aside {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e0 #f7fafc;
}

aside::-webkit-scrollbar {
  width: 6px;
}

aside::-webkit-scrollbar-track {
  background: #f7fafc;
}

aside::-webkit-scrollbar-thumb {
  background-color: #cbd5e0;
  border-radius: 3px;
}
</style>