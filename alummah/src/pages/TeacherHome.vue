<template>
  <div class="flex min-h-screen bg-gray-50 flex-col md:flex-row">
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
      <!-- Teacher Info Card -->
      <div class="flex items-center space-x-4 border-b pb-4">
        <div class="w-16 h-16 rounded-full bg-gray-200 overflow-hidden flex items-center justify-center">
          <img
            v-if="teacher.image"
            :src="`data:image/jpeg;base64,${teacher.image}`"
            alt="Teacher"
            class="object-cover w-full h-full"
          />
          <span v-else class="text-sm text-gray-500">No Image</span>
        </div>
        <div>
          <h2 class="text-xl font-semibold text-gray-800">{{ teacher.name || 'No Name Available' }}</h2>
          <p class="text-sm text-gray-500">Teacher</p>
        </div>
      </div>

      <!-- Class Selection -->
      <div class="space-y-2">
        <label class="block text-sm font-medium text-gray-700">Select Class:</label>
        <select 
          v-model="selectedGroup" 
          @change="handleGroupChange" 
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option v-for="(group, index) in studentGroups" :key="index" :value="group">
            {{ group }}
          </option>
        </select>
      </div>

      <!-- Navigation Buttons -->
      <nav class="space-y-3">
        <router-link 
          :to="{ name: 'Attendance' }" 
          class="block"
          @click="showSidebar = false"
        >
          <button class="w-full text-left px-4 py-3 rounded hover:bg-blue-100 bg-blue-50 text-blue-800 font-medium flex items-center space-x-3">
            <ClipboardDocumentListIcon class="w-5 h-5" />
            <span>Take Attendance</span>
          </button>
        </router-link>

        <router-link 
          :to="{ name: 'AttendanceRecord' }" 
          class="block"
          @click="showSidebar = false"
        >
          <button class="w-full text-left px-4 py-3 rounded hover:bg-green-100 bg-green-50 text-green-800 font-medium flex items-center space-x-3">
            <UserGroupIcon class="w-5 h-5" />
            <span>Student Record</span>
          </button>
        </router-link>

        <router-link 
          :to="{ name: 'CreateNotice' }" 
          class="block"
          @click="showSidebar = false"
        >
          <button class="w-full text-left px-4 py-3 rounded hover:bg-yellow-100 bg-yellow-50 text-yellow-800 font-medium flex items-center space-x-3">
            <PlusCircleIcon class="w-5 h-5" />
            <span>Create Notice</span>
          </button>
        </router-link>

        <router-link 
          :to="{ name: 'PreviousNotices' }" 
          class="block"
          @click="showSidebar = false"
        >
          <button class="w-full text-left px-4 py-3 rounded hover:bg-purple-100 bg-purple-50 text-purple-800 font-medium flex items-center space-x-3">
            <DocumentTextIcon class="w-5 h-5" />
            <span>Previous Notices</span>
          </button>
        </router-link>

        <router-link 
          :to="{ name: 'BrowseLeaveAppeals' }" 
          class="block"
          @click="showSidebar = false"
        >
          <button class="w-full text-left px-4 py-3 rounded hover:bg-indigo-100 bg-indigo-50 text-indigo-800 font-medium flex items-center space-x-3">
            <InboxIcon class="w-5 h-5" />
            <span>Browse Leave Appeals</span>
          </button>
        </router-link>
      </nav>

      <!-- Logout Button -->
      <div class="pt-4 border-t">
        <button
          class="w-full px-4 py-3 rounded bg-red-100 text-red-600 font-medium hover:bg-red-200 flex items-center justify-center space-x-2"
          @click="handleLogout"
        >
          <ArrowRightOnRectangleIcon class="w-5 h-5" />
          <span>Logout</span>
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 p-4 md:p-8 bg-gray-50">
      <!-- Welcome Section -->
      <div class="bg-white rounded-lg shadow-sm p-6 mb-6">
        <h1 class="text-2xl font-bold text-gray-800 mb-2">Welcome, {{ teacher.name || 'Teacher' }}!</h1>
        <p class="text-gray-600">Manage your classroom activities and student records from here.</p>
      </div>

      <!-- Quick Stats Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
        <div class="bg-white rounded-lg shadow-sm p-6 border-l-4 border-blue-500">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Selected Class</p>
              <p class="text-2xl font-bold text-gray-800">{{ selectedGroup || 'None' }}</p>
            </div>
            <UserGroupIcon class="w-8 h-8 text-blue-500" />
          </div>
        </div>

        <div class="bg-white rounded-lg shadow-sm p-6 border-l-4 border-green-500">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Available Classes</p>
              <p class="text-2xl font-bold text-gray-800">{{ studentGroups.length }}</p>
            </div>
            <ClipboardDocumentListIcon class="w-8 h-8 text-green-500" />
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
          <router-link 
            :to="{ name: 'Attendance' }"
            class="flex items-center p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
          >
            <ClipboardDocumentListIcon class="w-6 h-6 text-blue-600 mr-3" />
            <div>
              <h3 class="font-medium text-gray-800">Take Today's Attendance</h3>
              <p class="text-sm text-gray-600">Mark student attendance for today</p>
            </div>
          </router-link>

          <router-link 
            :to="{ name: 'CreateNotice' }"
            class="flex items-center p-4 border border-gray-200 rounded-lg hover:border-yellow-500 hover:bg-yellow-50 transition-colors"
          >
            <PlusCircleIcon class="w-6 h-6 text-yellow-600 mr-3" />
            <div>
              <h3 class="font-medium text-gray-800">Create New Notice</h3>
              <p class="text-sm text-gray-600">Send announcement to students</p>
            </div>
          </router-link>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { session } from '@/data/session'

// Import Heroicons
import {
  ClipboardDocumentListIcon,
  UserGroupIcon,
  PlusCircleIcon,
  DocumentTextIcon,
  InboxIcon,
  ArrowRightOnRectangleIcon,
  CalendarIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()

// Reactive state
const teacher = ref({})
const loading = ref(true)
const studentGroups = ref([])
const selectedGroup = ref('')
const showSidebar = ref(false)

// Computed properties
const currentDate = computed(() => {
  return new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

// Load user details from localStorage
const loadUserDetails = async () => {
  try {
    const userDetailsData = localStorage.getItem('user_details')
    if (userDetailsData) {
      const userDetails = JSON.parse(userDetailsData)

      // Update teacher state
      teacher.value = {
        name: userDetails.name,
        image: userDetails.base64profile,
      }

      // Set student groups
      if (userDetails.student_groups?.length) {
        studentGroups.value = userDetails.student_groups
        selectedGroup.value = userDetails.student_groups[0] // Default to first group
        localStorage.setItem('selected_student_group', userDetails.student_groups[0])
      }
    } else {
      alert('No user details found.')
    }
  } catch (error) {
    console.error('Error loading user details:', error)
    alert('Failed to load user details.')
  } finally {
    loading.value = false
  }
}

// Handle group selection change
const handleGroupChange = async () => {
  localStorage.setItem('selected_student_group', selectedGroup.value)
}

// Handle logout
const handleLogout = async () => {
  try {
    // Clear localStorage
    localStorage.removeItem('user_details')
    localStorage.removeItem('user')
    localStorage.removeItem('selected_student_group')
    
    // Logout from session
    await session.logout.submit()
    
    // Redirect to login
    router.push({ name: 'Login' })
  } catch (error) {
    console.error('Logout error:', error)
    // Force redirect even if logout fails
    localStorage.clear()
    router.push({ name: 'Login' })
  }
}

// Load user details on component mount
onMounted(() => {
  loadUserDetails()
})
</script>

<style scoped>
.router-link-active button {
  @apply bg-blue-100 border-blue-200;
}
</style>