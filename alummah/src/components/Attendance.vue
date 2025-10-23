<template>
  <div class="min-h-screen bg-gray-50 p-4">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-800">Take Attendance</h1>
      <p class="text-gray-600">Select students who are present today</p>
      <p class="text-sm text-gray-500 mt-1" v-if="selectedGroup">Class: {{ selectedGroup }}</p>
      <p class="text-sm text-gray-500">Date: {{ currentDate }}</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-8">
      <div class="spinner"></div>
      <span class="ml-2 text-gray-600">Loading students...</span>
    </div>

    <!-- Students List -->
    <div v-else-if="students && students.length > 0" class="space-y-3">
      <div class="flex justify-between items-center mb-4">
        <p class="text-sm text-gray-600">
          Total: {{ students.length }} | Present: {{ presentStudents.length }} | Absent: {{ students.length - presentStudents.length }}
        </p>
        <button
          @click="toggleAllStudents"
          class="px-3 py-1 text-sm bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
        >
          {{ presentStudents.length === students.length ? 'Mark All Absent' : 'Mark All Present' }}
        </button>
      </div>

      <div 
        v-for="student in students" 
        :key="student.student"
        class="bg-white rounded-lg shadow-sm p-4 border-2 transition-colors cursor-pointer"
        :class="presentStudents.includes(student.student) ? 'border-green-500 bg-green-50' : 'border-gray-200'"
        @click="toggleStudentAttendance(student.student)"
      >
        <div class="flex items-center space-x-4">
          <!-- Student Avatar with better fallback -->
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
          
          <div class="flex-1 min-w-0">
            <h3 class="font-medium text-gray-800 truncate">{{ student.student_name }}</h3>
            <div class="flex items-center space-x-4 text-sm text-gray-600">
              <span>Roll No: {{ student.group_roll_number }}</span>
              <span class="text-gray-400">•</span>
              <span class="truncate">{{ student.student }}</span>
            </div>
          </div>
          
          <div class="flex-shrink-0">
            <div class="w-6 h-6 rounded-full border-2 flex items-center justify-center"
              :class="presentStudents.includes(student.student) ? 'bg-green-500 border-green-500' : 'border-gray-300'">
              <CheckIcon v-if="presentStudents.includes(student.student)" class="w-4 h-4 text-white" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- No Students State -->
    <div v-else class="text-center py-8">
      <p class="text-gray-600">No students available for this class</p>
      <button 
        @click="fetchAttendanceData"
        class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
      >
        Try Again
      </button>
    </div>

    <!-- Action Buttons -->
    <div v-if="students.length > 0" class="flex space-x-4 mt-6">
      <button
        @click="handleCancel"
        class="flex-1 px-4 py-3 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors flex items-center justify-center space-x-2"
      >
        <XMarkIcon class="w-5 h-5" />
        <span>Cancel</span>
      </button>

      <button
        @click="handleSubmitAttendance"
        :disabled="submitting"
        class="flex-1 px-4 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <ArrowRightIcon class="w-5 h-5" />
        <span>{{ submitting ? 'Submitting...' : 'Submit' }}</span>
      </button>

      <button
        @click="fetchAttendanceData"
        class="flex-1 px-4 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors flex items-center justify-center space-x-2"
      >
        <ArrowPathIcon class="w-5 h-5" />
        <span>Refresh</span>
      </button>
    </div>

    <!-- Confirmation Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-sm w-full mx-4">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">Confirm Attendance</h3>
        <p class="text-gray-600 mb-2">Present: {{ presentStudents.length }}</p>
        <p class="text-gray-600 mb-6">Absent: {{ students.length - presentStudents.length }}</p>
        <div class="flex space-x-3">
          <button
            @click="showModal = false"
            class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            @click="confirmAttendance"
            class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Confirm
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { createResource } from 'frappe-ui'
import { XMarkIcon, ArrowRightIcon, ArrowPathIcon, CheckIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const props = defineProps({
  selectedGroup: String
})

defineEmits(['back-to-dashboard'])

// Reactive state
const students = ref([])
const presentStudents = ref([])
const loading = ref(true)
const showModal = ref(false)
const submitting = ref(false)

// Computed current date
const currentDate = computed(() => {
  return new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

// Helper functions for profile images
const getProfileImage = (student) => {
  if (student.base64profile && student.base64profile !== 'null') {
    // Handle both data URL and base64 string formats
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
  // Hide the broken image and let the fallback initials show
  event.target.style.display = 'none'
}

// Create resource for fetching attendance records
const attendanceResource = createResource({
  url: 'school.al_ummah.api2.get_student_attendance_records',
  onSuccess(data) {
    console.log('Attendance data loaded:', data)
    return data
  },
  onError(error) {
    console.error('Error fetching attendance:', error)
    alert('Failed to load student data. Please check your connection and try again.')
  }
})

// Create resource for marking attendance
const markAttendanceResource = createResource({
  url: 'school.al_ummah.api2.mark_attendance',
  onSuccess(data) {
    console.log('Attendance marked successfully:', data)
    submitting.value = false
    
    // Handle different response formats
    if (data.status === 'success' || data.message?.includes('successfully')) {
      alert('Success! ' + (data.message || 'Attendance has been marked successfully.'))
      router.push({ name: 'Teacherhome' })
    } else if (data._server_messages) {
      // Handle Frappe server messages
      try {
        const serverMessages = JSON.parse(data._server_messages)
        if (serverMessages.length > 0) {
          const message = JSON.parse(serverMessages[0])
          if (message.message && message.message.includes('successfully')) {
            alert('Success! ' + message.message)
            router.push({ name: 'Teacherhome' })
            return
          }
        }
      } catch (e) {
        console.error('Error parsing server messages:', e)
      }
      // Fallback success
      alert('Success! Attendance has been marked successfully.')
      router.push({ name: 'Teacherhome' })
    } else {
      alert('Error: ' + (data.message || 'There was an issue marking attendance.'))
    }
  },
  onError(error) {
    console.error('Error marking attendance:', error)
    submitting.value = false
    
    if (error.exc_type === 'PermissionError') {
      alert('Permission denied: You do not have permission to mark attendance. Please contact your administrator.')
    } else {
      alert('Failed to submit attendance. Please check your connection and try again.')
    }
  }
})

// Fetch attendance data
const fetchAttendanceData = async () => {
  loading.value = true
  try {
    const group = props.selectedGroup || localStorage.getItem('selected_student_group')
    if (!group) {
      alert('Please select a class first.')
      loading.value = false
      return
    }

    const params = { based_on: 'Batch', student_group: group }
    const attendanceRecords = await attendanceResource.fetch(params)

    if (!attendanceRecords || attendanceRecords.length === 0) {
      alert('No students found for this class.')
      students.value = []
      return
    }

    students.value = attendanceRecords
    // Default all students to present
    presentStudents.value = attendanceRecords.map(student => student.student)
  } catch (error) {
    console.error('Error fetching attendance:', error)
    alert('Failed to load student data.')
  } finally {
    loading.value = false
  }
}

// Toggle all students
const toggleAllStudents = () => {
  if (presentStudents.value.length === students.value.length) {
    // If all are present, mark all absent
    presentStudents.value = []
  } else {
    // If not all are present, mark all present
    presentStudents.value = students.value.map(student => student.student)
  }
}

// Toggle student attendance
const toggleStudentAttendance = (studentId) => {
  const index = presentStudents.value.indexOf(studentId)
  if (index > -1) {
    presentStudents.value.splice(index, 1)
  } else {
    presentStudents.value.push(studentId)
  }
}

// Handle submit attendance
const handleSubmitAttendance = () => {
  if (presentStudents.value.length === 0) {
    alert('Please select at least one student as present.')
    return
  }
  showModal.value = true
}

// Confirm attendance submission
const confirmAttendance = async () => {
  showModal.value = false
  submitting.value = true

  const studentsPresent = students.value
    .filter(student => presentStudents.value.includes(student.student))
    .map(student => ({
      student: student.student,
      student_name: student.student_name,
      group_roll_number: student.group_roll_number,
      disabled: false,
      checked: true,
    }))

  const studentsAbsent = students.value
    .filter(student => !presentStudents.value.includes(student.student))
    .map(student => ({
      student: student.student,
      student_name: student.student_name,
      group_roll_number: student.group_roll_number,
      disabled: false,
      checked: false,
    }))

  const formattedDate = new Date().toISOString().split('T')[0]
  const group = props.selectedGroup || localStorage.getItem('selected_student_group')

  try {
    await markAttendanceResource.submit({
      students_present: JSON.stringify(studentsPresent),
      students_absent: JSON.stringify(studentsAbsent),
      student_group: group,
      date: formattedDate
    })
  } catch (error) {
    console.error('Error submitting attendance:', error)
    submitting.value = false
  }
}

// Handle cancel
const handleCancel = () => {
  router.push({ name: 'Teacherhome' })
}

// Load data on mount
onMounted(() => {
  fetchAttendanceData()
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