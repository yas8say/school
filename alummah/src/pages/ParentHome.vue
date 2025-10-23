<template>
  <div class="flex min-h-screen bg-gray-50 flex-col md:flex-row">
    <!-- Loading State -->
    <div v-if="userDetailsResource.loading" class="fixed inset-0 bg-white bg-opacity-80 flex items-center justify-center z-50">
      <div class="spinner"></div>
    </div>

    <!-- Mobile Toggle -->
    <div class="md:hidden p-4 bg-white shadow">
      <button
        @click="showSidebar = !showSidebar"
        class="px-4 py-2 bg-blue-600 text-white rounded"
      >
        {{ showSidebar ? 'Close Menu' : 'Open Menu' }}
      </button>
    </div>

    <!-- Sidebar -->
    <aside
      :class="[
        'bg-white shadow-md p-6 space-y-8 md:block',
        showSidebar ? 'block' : 'hidden',
        'md:w-72'
      ]"
    >
      <!-- Parent Info Card -->
      <div class="flex items-start space-x-4 border-b pb-4">
        <div class="flex-shrink-0 w-16 h-16 rounded-full bg-gray-200 overflow-hidden">
          <img
            v-if="parent.image"
            :src="`data:image/jpeg;base64,${parent.image}`"
            alt="Parent"
            class="object-cover w-full h-full"
          />
          <div v-else class="w-full h-full flex items-center justify-center">
            <span class="text-sm text-gray-500">No Image</span>
          </div>
        </div>
        <div class="min-w-0 flex-1">
          <h2 class="text-xl font-semibold text-gray-800 break-words">{{ parent.name || 'No Name Available' }}</h2>
          <p class="text-sm text-gray-500 mt-1">Parent</p>
        </div>
      </div>

      <!-- Student Selection -->
      <div class="space-y-2">
        <label class="block text-sm font-medium text-gray-700">Select Child:</label>
        <select 
          v-model="selectedStudent" 
          @change="handleStudentChange" 
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          :disabled="userDetailsResource.loading"
        >
          <option value="" disabled>Select a child</option>
          <option v-for="student in studentList" :key="student.student" :value="student">
            {{ student.student_name || 'Unnamed Student' }}
          </option>
        </select>
      </div>

      <!-- Navigation Buttons -->
      <div class="space-y-3">
        <h3 class="text-sm font-medium text-gray-700">Navigation</h3>
        <nav class="space-y-2">
          <button
            @click="setActiveView('dashboard')"
            :class="[
              'w-full text-left px-4 py-3 rounded font-medium flex items-center space-x-3 transition-colors',
              activeView === 'dashboard' 
                ? 'bg-blue-100 border border-blue-200 text-blue-800' 
                : 'bg-blue-50 text-blue-800 hover:bg-blue-100'
            ]"
          >
            <HomeIcon class="w-5 h-5" />
            <span>Dashboard</span>
          </button>

          <button
            @click="setActiveView('attendance-record')"
            :class="[
              'w-full text-left px-4 py-3 rounded font-medium flex items-center space-x-3 transition-colors',
              activeView === 'attendance-record' 
                ? 'bg-blue-100 border border-blue-200 text-blue-800' 
                : 'bg-blue-50 text-blue-800 hover:bg-blue-100'
            ]"
          >
            <ClipboardDocumentListIcon class="w-5 h-5" />
            <span>Attendance Record</span>
          </button>

          <button
            @click="setActiveView('browse-notices')"
            :class="[
              'w-full text-left px-4 py-3 rounded font-medium flex items-center space-x-3 transition-colors',
              activeView === 'browse-notices' 
                ? 'bg-green-100 border border-green-200 text-green-800' 
                : 'bg-green-50 text-green-800 hover:bg-green-100'
            ]"
          >
            <DocumentTextIcon class="w-5 h-5" />
            <span>Browse Notices</span>
          </button>

          <button
            @click="setActiveView('appeal-leave')"
            :class="[
              'w-full text-left px-4 py-3 rounded font-medium flex items-center space-x-3 transition-colors',
              activeView === 'appeal-leave' 
                ? 'bg-yellow-100 border border-yellow-200 text-yellow-800' 
                : 'bg-yellow-50 text-yellow-800 hover:bg-yellow-100'
            ]"
          >
            <InboxIcon class="w-5 h-5" />
            <span>Appeal Leave</span>
          </button>
        </nav>
      </div>

      <!-- Logout Button -->
      <div class="pt-4 border-t">
        <button
          class="w-full px-4 py-3 rounded bg-red-100 text-red-600 font-medium hover:bg-red-200 flex items-center justify-center space-x-2 transition-colors"
          @click="handleLogout"
          :disabled="userDetailsResource.loading"
        >
          <ArrowRightOnRectangleIcon class="w-5 h-5" />
          <span>Logout</span>
        </button>
      </div>
    </aside>

    <!-- Main Content Area - Dynamic based on active view -->
    <main class="flex-1 p-4 md:p-8 bg-gray-50">
      <!-- Dashboard View -->
      <div v-if="activeView === 'dashboard'">
        <!-- Welcome Section -->
        <div class="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h1 class="text-2xl font-bold text-gray-800 mb-2">Welcome, {{ parent.name || 'Parent' }}!</h1>
          <p class="text-gray-600">Monitor your child's activities and school records from here.</p>
        </div>

        <!-- Quick Stats Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
          <div class="bg-white rounded-lg shadow-sm p-6 border-l-4 border-blue-500">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600">Selected Child</p>
                <p class="text-2xl font-bold text-gray-800">{{ selectedStudent?.student_name || 'None' }}</p>
              </div>
              <UserGroupIcon class="w-8 h-8 text-blue-500" />
            </div>
          </div>

          <div class="bg-white rounded-lg shadow-sm p-6 border-l-4 border-green-500">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600">Available Children</p>
                <p class="text-2xl font-bold text-gray-800">{{ studentList.length }}</p>
              </div>
              <UserGroupIcon class="w-8 h-8 text-green-500" />
            </div>
          </div>

          <div class="bg-white rounded-lg shadow-sm p-6 border-l-4 border-purple-500">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600">Today's Date</p>
                <p class="text-2xl font-bold text-gray-800">{{ currentDate }}</p>
              </div>
              <CalendarIcon class="w-8 h-8 text-purple-500" />
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="bg-white rounded-lg shadow-sm p-6">
          <h2 class="text-lg font-semibold text-gray-800 mb-4">Quick Actions</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button 
              @click="setActiveView('attendance-record')"
              class="flex items-center p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors cursor-pointer"
            >
              <ClipboardDocumentListIcon class="w-6 h-6 text-blue-600 mr-3" />
              <div>
                <h3 class="font-medium text-gray-800">View Attendance Record</h3>
                <p class="text-sm text-gray-600">Check your child's attendance history</p>
              </div>
            </button>

            <button 
              @click="setActiveView('appeal-leave')"
              class="flex items-center p-4 border border-gray-200 rounded-lg hover:border-yellow-500 hover:bg-yellow-50 transition-colors cursor-pointer"
            >
              <InboxIcon class="w-6 h-6 text-yellow-600 mr-3" />
              <div>
                <h3 class="font-medium text-gray-800">Appeal for Leave</h3>
                <p class="text-sm text-gray-600">Submit leave appeal for your child</p>
              </div>
            </button>
          </div>
        </div>
      </div>

      <!-- Attendance Record View -->
      <div v-else-if="activeView === 'attendance-record'">
        <AttendanceRecord 
          :selected-student="selectedStudent"
          @back-to-dashboard="setActiveView('dashboard')"
        />
      </div>

      <!-- Browse Notices View -->
      <div v-else-if="activeView === 'browse-notices'">
        <BrowseNotices 
          :selected-student="selectedStudent"
          @back-to-dashboard="setActiveView('dashboard')"
        />
      </div>

      <!-- Appeal Leave View -->
      <div v-else-if="activeView === 'appeal-leave'">
        <AppealLeave 
          :selected-student="selectedStudent"
          @back-to-dashboard="setActiveView('dashboard')"
        />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { session } from '@/data/session'
import { createResource } from 'frappe-ui'

// Import Heroicons
import {
  HomeIcon,
  ClipboardDocumentListIcon,
  UserGroupIcon,
  DocumentTextIcon,
  InboxIcon,
  ArrowRightOnRectangleIcon,
  CalendarIcon
} from '@heroicons/vue/24/outline'

// Import Components
import AttendanceRecord from '@/components/AttendanceRecord.vue'
import BrowseNotices from '@/components/BrowseNotices.vue'
import AppealLeave from '@/components/AppealLeave.vue'

const router = useRouter()

// Reactive state
const parent = ref({})
const studentList = ref([])
const selectedStudent = ref(null)
const showSidebar = ref(false)
const activeView = ref('dashboard') // Default to dashboard

// Set active view function
const setActiveView = (view) => {
  activeView.value = view
  if (window.innerWidth < 768) {
    showSidebar.value = false
  }
}

// Get current user and role
const currentUser = session.user
const currentRole = 'parent'

// Create resource for API call
const userDetailsResource = createResource({
  url: 'school.al_ummah.api2.get_user_details',
  params: { 
    role: currentRole,
    username: currentUser
  },
  auto: true,
  onSuccess(data) {
    console.log('Parent user details loaded:', data)
    
    if (data && data.user_details) {
      parent.value = {
        name: data.user_details.name,
        image: data.user_details.base64profile,
        address: data.user_details.address
      }

      if (data.user_details.student_list?.length) {
        studentList.value = data.user_details.student_list
        selectedStudent.value = data.user_details.student_list[0]
        localStorage.setItem('selected_student', JSON.stringify(data.user_details.student_list[0]))
        localStorage.setItem('selected_student_group', data.user_details.student_list[0]?.student_group || '')
      }

      localStorage.setItem('user_details', JSON.stringify(data.user_details))
    }
  },
  onError(error) {
    console.error('Error loading parent user details:', error)
    loadUserDetailsFromLocalStorage()
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
    const userDetailsData = localStorage.getItem('user_details')
    if (userDetailsData) {
      const userDetails = JSON.parse(userDetailsData)
      parent.value = {
        name: userDetails.name,
        image: userDetails.base64profile,
        address: userDetails.address
      }
      if (userDetails.student_list?.length) {
        studentList.value = userDetails.student_list
        const savedStudent = localStorage.getItem('selected_student')
        if (savedStudent) {
          selectedStudent.value = JSON.parse(savedStudent)
        } else {
          selectedStudent.value = userDetails.student_list[0]
        }
      }
    }
  } catch (error) {
    console.error('Error loading from localStorage:', error)
  }
}

// Handle student selection change
const handleStudentChange = async () => {
  if (selectedStudent.value) {
    localStorage.setItem('selected_student', JSON.stringify(selectedStudent.value))
    localStorage.setItem('selected_student_group', selectedStudent.value.student_group || '')
  }
}

// Handle logout
const handleLogout = async () => {
  try {
    localStorage.removeItem('user_details')
    localStorage.removeItem('user')
    localStorage.removeItem('selected_student')
    localStorage.removeItem('selected_student_group')
    await session.logout.submit()
    router.push({ name: 'Login' })
  } catch (error) {
    console.error('Logout error:', error)
    localStorage.clear()
    router.push({ name: 'Login' })
  }
}

onMounted(() => {
  if (!userDetailsResource.data) {
    userDetailsResource.reload()
  }
})

watch(() => userDetailsResource.loading, (loading) => {
  if (!loading && userDetailsResource.data) {
    console.log('Parent data loaded successfully')
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
</style>