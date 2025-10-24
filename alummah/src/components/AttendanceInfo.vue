<template>
  <div class="min-h-screen bg-gray-50 p-4">
    <!-- Loading State -->
    <div v-if="studentResource.loading" class="flex justify-center items-center py-8">
      <div class="spinner"></div>
      <span class="ml-2 text-gray-600">Loading student details...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="studentResource.error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
      <p class="text-red-800 font-medium mb-2">Failed to load student details</p>
      <p class="text-red-700 text-sm">{{ studentResource.error.message }}</p>
      <button @click="loadStudentDetails" class="mt-2 px-3 py-1 bg-red-600 text-white rounded text-sm">
        Retry
      </button>
    </div>

    <!-- Student Details -->
    <div v-else-if="student && student.student" class="bg-white rounded-lg shadow-sm">
      <!-- Header Section -->
      <div class="bg-gradient-to-r from-blue-500 to-purple-600 rounded-t-lg p-6">
        <div class="flex items-center space-x-4">
          <div class="flex-shrink-0">
            <img 
              :src="profileImage" 
              alt="Student" 
              class="w-20 h-20 rounded-full border-4 border-white object-cover"
              @error="handleImageError"
            />
          </div>
          <div class="flex-1 text-white">
            <h1 class="text-2xl font-bold">{{ student.student_name || student.name || 'Unknown Student' }}</h1>
            <p class="text-blue-100">Student ID: {{ student.student }}</p>
            <p class="text-blue-100" v-if="student.group_roll_no">Roll No: {{ student.group_roll_no }}</p>
            <p class="text-blue-100">Class: {{ student.student_group }}</p>
            <p class="text-blue-100">Today: {{ student.status || 'No Record' }}</p>
          </div>
        </div>
      </div>

      <!-- Contact Information -->
      <div class="p-6">
        <div class="space-y-4 mb-6">
          <!-- Phone -->
          <div 
            v-if="student.mobile"
            class="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors"
            @click="callStudent"
          >
            <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
              </svg>
            </div>
            <div>
              <p class="text-sm text-gray-600">Phone</p>
              <p class="font-medium text-gray-800">{{ student.mobile }}</p>
            </div>
          </div>

          <!-- Address -->
          <div 
            v-if="student.address"
            class="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg"
          >
            <div class="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
              <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <div class="flex-1">
              <p class="text-sm text-gray-600">Address</p>
              <p class="font-medium text-gray-800">{{ student.address }}</p>
            </div>
          </div>
        </div>

        <!-- Attendance Statistics -->
        <div class="bg-gray-50 rounded-lg p-6">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">Attendance Summary</h3>
          <div class="grid grid-cols-3 gap-4">
            <div class="text-center bg-green-50 rounded-lg p-4 border border-green-200">
              <p class="text-2xl font-bold text-green-600">{{ student.present_count || 0 }}</p>
              <p class="text-sm text-green-700 font-medium">Present</p>
            </div>
            <div class="text-center bg-red-50 rounded-lg p-4 border border-red-200">
              <p class="text-2xl font-bold text-red-600">{{ student.absent_count || 0 }}</p>
              <p class="text-sm text-red-700 font-medium">Absent</p>
            </div>
            <div class="text-center bg-yellow-50 rounded-lg p-4 border border-yellow-200">
              <p class="text-2xl font-bold text-yellow-600">{{ student.leave_count || 0 }}</p>
              <p class="text-sm text-yellow-700 font-medium">Leave</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- No Student Data -->
    <div v-else class="text-center py-8">
      <div class="bg-white rounded-lg shadow-sm p-8">
        <h3 class="text-lg font-medium text-gray-800 mb-2">No Student Data</h3>
        <p class="text-gray-600 mb-4">Unable to load student information.</p>
        <button 
          @click="loadStudentDetails"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Try Again
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { createResource } from 'frappe-ui'

// Reactive state
const student = ref({})

// Create resource for fetching student details
const studentResource = createResource({
  url: 'school.al_ummah.api2.get_student_app_data',
  auto: false,
  onSuccess(data) {
    if (data && data.student) {
      student.value = data
    } else if (data && data.error) {
      throw new Error(data.error)
    } else {
      throw new Error('No student data received')
    }
  },
  onError(error) {
    console.error('Error fetching student details:', error)
    student.value = {}
  }
})

// Computed property for profile image
const profileImage = computed(() => {
  if (student.value.base64profile) {
    return `data:image/jpeg;base64,${student.value.base64profile}`
  }
  return 'https://via.placeholder.com/150?text=Student'
})

// Handle image loading errors
const handleImageError = (event) => {
  event.target.src = 'https://via.placeholder.com/150?text=Student'
}

// Make phone call
const callStudent = () => {
  if (student.value.mobile) {
    window.open(`tel:${student.value.mobile}`, '_self')
  }
}

// Load student details
const loadStudentDetails = async () => {
  try {
    // Get student ID from localStorage
    let studentId = localStorage.getItem('selected_student')
    
    // If it's a stringified object, parse it and extract the student ID
    if (studentId && studentId.startsWith('{')) {
      try {
        const studentData = JSON.parse(studentId)
        studentId = studentData.student || studentData.name
      } catch (e) {
        console.error('Error parsing student data:', e)
      }
    }
    
    if (!studentId) {
      throw new Error('No student ID found')
    }
    
    // Make API call with just the student ID string
    await studentResource.fetch({ studentID: studentId })
    
  } catch (error) {
    console.error('Error loading student details:', error)
  }
}

onMounted(() => {
  loadStudentDetails()
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