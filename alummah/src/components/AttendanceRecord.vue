<template>
  <div class="min-h-screen bg-gray-50 p-4">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-800">Attendance Record</h1>
      <p class="text-gray-600">View student attendance history</p>
      <p class="text-sm text-gray-500 mt-1" v-if="selectedGroup">Class: {{ selectedGroup }}</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-8">
      <div class="spinner"></div>
      <span class="ml-2 text-gray-600">Loading attendance records...</span>
    </div>

    <!-- Students List -->
    <div v-else-if="students && students.length > 0" class="space-y-3">
      <div class="flex justify-between items-center mb-4">
        <p class="text-sm text-gray-600">
          Total Students: {{ students.length }}
        </p>
        <button
          @click="fetchAttendanceData"
          class="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center space-x-2"
        >
          <ArrowPathIcon class="w-4 h-4" />
          <span>Refresh</span>
        </button>
      </div>

      <!-- Student Records -->
      <div 
        v-for="student in students" 
        :key="student.student"
        class="bg-white rounded-lg shadow-sm p-4 border border-gray-200 hover:border-blue-300 transition-colors cursor-pointer"
        @click="viewStudentDetails(student)"
      >
        <div class="flex items-center space-x-4">
          <!-- Student Avatar -->
          <div class="flex-shrink-0">
            <div class="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold text-sm relative overflow-hidden">
              <img
                v-if="student.base64profile && student.base64profile !== 'null'"
                :src="getProfileImage(student)"
                alt="Student"
                class="absolute inset-0 w-full h-full object-cover"
                @error="handleImageError"
              />
              <span v-else class="text-white text-sm font-medium">
                {{ getInitials(student.student_name) }}
              </span>
            </div>
          </div>
          
          <!-- Student Info -->
          <div class="flex-1 min-w-0">
            <h3 class="font-medium text-gray-800 truncate">{{ student.student_name }}</h3>
            <div class="flex items-center space-x-4 text-sm text-gray-600">
              <span>Roll No: {{ student.group_roll_number }}</span>
              <span class="text-gray-400">•</span>
              <span class="truncate text-xs">{{ student.student }}</span>
            </div>
            
            <!-- Attendance Stats -->
            <div class="flex items-center space-x-4 mt-2 text-xs">
              <span class="flex items-center space-x-1 text-green-600">
                <CheckCircleIcon class="w-4 h-4" />
                <span>Present: {{ student.present_count || 0 }}</span>
              </span>
              <span class="flex items-center space-x-1 text-red-600">
                <XCircleIcon class="w-4 h-4" />
                <span>Absent: {{ student.absent_count || 0 }}</span>
              </span>
              <span class="flex items-center space-x-1 text-yellow-600">
                <ClockIcon class="w-4 h-4" />
                <span>Leave: {{ student.leave_count || 0 }}</span>
              </span>
            </div>
          </div>
          
          <!-- View Details Arrow -->
          <div class="flex-shrink-0">
            <ChevronRightIcon class="w-5 h-5 text-gray-400" />
          </div>
        </div>
      </div>
    </div>

    <!-- No Students State -->
    <div v-else class="text-center py-8">
      <div class="bg-white rounded-lg shadow-sm p-8">
        <UserGroupIcon class="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-800 mb-2">No Students Found</h3>
        <p class="text-gray-600 mb-4">No attendance records available for this class.</p>
        <button 
          @click="fetchAttendanceData"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2 mx-auto"
        >
          <ArrowPathIcon class="w-4 h-4" />
          <span>Refresh Data</span>
        </button>
      </div>
    </div>

    <!-- Student Details Modal -->
    <div v-if="selectedStudent && showStudentModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4 max-h-[80vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-800">Student Details</h3>
          <button @click="closeStudentModal" class="text-gray-400 hover:text-gray-600">
            <XMarkIcon class="w-6 h-6" />
          </button>
        </div>
        
        <!-- Student Info in Modal -->
        <div class="flex items-center space-x-4 mb-6">
          <div class="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold text-lg relative overflow-hidden">
            <img
              v-if="selectedStudent.base64profile && selectedStudent.base64profile !== 'null'"
              :src="getProfileImage(selectedStudent)"
              alt="Student"
              class="absolute inset-0 w-full h-full object-cover"
              @error="handleImageError"
            />
            <span v-else class="text-white text-lg font-medium">
              {{ getInitials(selectedStudent.student_name) }}
            </span>
          </div>
          <div>
            <h4 class="font-medium text-gray-800">{{ selectedStudent.student_name }}</h4>
            <p class="text-sm text-gray-600">Roll No: {{ selectedStudent.group_roll_number }}</p>
            <p class="text-xs text-gray-500">{{ selectedStudent.student }}</p>
          </div>
        </div>

        <!-- Detailed Attendance Stats -->
        <div class="grid grid-cols-3 gap-4 mb-6">
          <div class="text-center p-3 bg-green-50 rounded-lg">
            <CheckCircleIcon class="w-8 h-8 text-green-600 mx-auto mb-2" />
            <p class="text-2xl font-bold text-green-600">{{ selectedStudent.present_count || 0 }}</p>
            <p class="text-sm text-green-700">Present</p>
          </div>
          <div class="text-center p-3 bg-red-50 rounded-lg">
            <XCircleIcon class="w-8 h-8 text-red-600 mx-auto mb-2" />
            <p class="text-2xl font-bold text-red-600">{{ selectedStudent.absent_count || 0 }}</p>
            <p class="text-sm text-red-700">Absent</p>
          </div>
          <div class="text-center p-3 bg-yellow-50 rounded-lg">
            <ClockIcon class="w-8 h-8 text-yellow-600 mx-auto mb-2" />
            <p class="text-2xl font-bold text-yellow-600">{{ selectedStudent.leave_count || 0 }}</p>
            <p class="text-sm text-yellow-700">Leave</p>
          </div>
        </div>

        <!-- Contact Info -->
        <div class="border-t pt-4">
          <h5 class="font-medium text-gray-800 mb-2">Contact Information</h5>
          <p class="text-sm text-gray-600" v-if="selectedStudent.mobile">
            📱 {{ selectedStudent.mobile }}
          </p>
          <p class="text-sm text-gray-600" v-if="selectedStudent.address">
            📍 {{ selectedStudent.address }}
          </p>
          <p class="text-sm text-gray-500" v-if="!selectedStudent.mobile && !selectedStudent.address">
            No contact information available
          </p>
        </div>

        <div class="flex space-x-3 mt-6">
          <button
            @click="closeStudentModal"
            class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { createResource } from 'frappe-ui'
import { 
  ArrowPathIcon, 
  ChevronRightIcon, 
  XMarkIcon,
  UserGroupIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon
} from '@heroicons/vue/24/outline'

// Reactive state
const students = ref([])
const loading = ref(true)
const selectedGroup = ref('')
const selectedStudent = ref(null)
const showStudentModal = ref(false)

// Helper functions for profile images
const getProfileImage = (student) => {
  if (student.base64profile && student.base64profile !== 'null') {
    if (student.base64profile.startsWith('data:')) {
      return student.base64profile
    } else {
      return `data:image/jpeg;base64,${student.base64profile}`
    }
  }
  return null
}

const getInitials = (name) => {
  if (!name) return '?'
  return name
    .split(' ')
    .map(part => part.charAt(0))
    .join('')
    .toUpperCase()
    .substring(0, 2)
}

const handleImageError = (event) => {
  event.target.style.display = 'none'
}

// Create resource for fetching attendance records
const attendanceResource = createResource({
  url: 'school.al_ummah.api2.get_student_attendance_records',
  onSuccess(data) {
    console.log('Attendance records loaded:', data)
    return data
  },
  onError(error) {
    console.error('Error fetching attendance records:', error)
    // Fallback to localStorage if API fails
    loadAttendanceDataFromStorage()
  }
})

// Load selected group from localStorage
const loadSelectedGroup = () => {
  try {
    const group = localStorage.getItem('selected_student_group')
    if (group) {
      selectedGroup.value = group
    }
  } catch (error) {
    console.error('Failed to load selected student group:', error)
  }
}

// Fetch attendance data from API
const fetchAttendanceData = async () => {
  if (!selectedGroup.value) return

  loading.value = true
  try {
    const params = {
      based_on: 'Student Group',
      student_group: selectedGroup.value,
    }

    const apiData = await attendanceResource.fetch(params)
    if (apiData && Array.isArray(apiData) && apiData.length > 0) {
      localStorage.setItem('attendance_data', JSON.stringify(apiData))
      students.value = apiData
    }
  } catch (error) {
    console.warn('Failed to fetch data from API:', error)
  } finally {
    loading.value = false
  }
}

// Load attendance data from localStorage
const loadAttendanceDataFromStorage = async () => {
  try {
    const storedData = localStorage.getItem('attendance_data')
    if (storedData) {
      students.value = JSON.parse(storedData)
    }
  } catch (error) {
    console.error('Failed to load attendance data from storage:', error)
  } finally {
    loading.value = false
  }
}

// View student details
const viewStudentDetails = (student) => {
  selectedStudent.value = student
  showStudentModal.value = true
}

// Close student modal
const closeStudentModal = () => {
  showStudentModal.value = false
  selectedStudent.value = null
}

// Lifecycle
onMounted(() => {
  loadSelectedGroup()
  if (selectedGroup.value) {
    loadAttendanceDataFromStorage()
    fetchAttendanceData()
  } else {
    loading.value = false
  }
})

// Watch for group changes
watch(selectedGroup, (newGroup) => {
  if (newGroup) {
    loadAttendanceDataFromStorage()
    fetchAttendanceData()
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