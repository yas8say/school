<template>
  <div class="min-h-screen bg-gray-50 p-4">
    <!-- Header -->
    <div class="mb-6">
      <div class="flex justify-between items-start">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">{{ mode === 'attendance' ? 'Take Attendance' : 'Promote Students' }}</h1>
          <p class="text-gray-600">{{ mode === 'attendance' ? 'Select students who are present today' : 'Select students to promote to next academic year' }}</p>
          <p class="text-sm text-gray-500 mt-1" v-if="selectedGroup">Current Class: {{ selectedGroup }}</p>
          <p class="text-sm text-gray-500">Date: {{ currentDate }}</p>
        </div>
        
        <!-- Mode Picker -->
        <div class="flex flex-col items-end space-y-2">
          <div class="bg-white rounded-lg border border-gray-300 p-1 flex">
            <button
              @click="setMode('attendance')"
              :class="[
                'px-3 py-1 text-sm font-medium rounded-md transition-colors',
                mode === 'attendance' 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-600 hover:text-gray-800'
              ]"
            >
              Take Attendance
            </button>
            <button
              @click="setMode('promotion')"
              :class="[
                'px-3 py-1 text-sm font-medium rounded-md transition-colors',
                mode === 'promotion' 
                  ? 'bg-green-600 text-white' 
                  : 'text-gray-600 hover:text-gray-800'
              ]"
            >
              Promote Students
            </button>
          </div>
          
          <!-- Promotion Info -->
          <div v-if="mode === 'promotion' && studentGroupInfo.success" 
               class="text-sm bg-green-50 px-3 py-2 rounded-lg border border-green-200 max-w-xs">
            <div class="font-semibold text-green-800 mb-1">Promotion Details:</div>
            <div class="text-green-700">
              <div>From: <span class="font-medium">{{ selectedGroup }}</span></div>
              <div>To: <span class="font-medium">{{ studentGroupInfo.next_group }}</span></div>
              <div>Program: <span class="font-medium">{{ studentGroupInfo.next_program }}</span></div>
              <div>Academic Year: <span class="font-medium">{{ studentGroupInfo.next_academic_year }}</span></div>
            </div>
          </div>

          <!-- Promotion Error -->
          <div v-if="mode === 'promotion' && !studentGroupInfo.success && studentGroupInfo.message" 
               class="text-sm bg-red-50 px-3 py-2 rounded-lg border border-red-200 max-w-xs">
            <div class="font-semibold text-red-800 mb-1">Cannot Promote:</div>
            <div class="text-red-700">{{ studentGroupInfo.message }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Success/Error Toast Messages -->
    <div v-if="toast.show" 
         :class="[
           'fixed top-4 right-4 z-50 max-w-sm p-4 rounded-lg shadow-lg border-l-4 transition-all duration-300',
           toast.type === 'success' 
             ? 'bg-green-50 border-green-500 text-green-800' 
             : 'bg-red-50 border-red-500 text-red-800'
         ]">
      <div class="flex items-start">
        <div class="flex-shrink-0">
          <CheckCircleIcon v-if="toast.type === 'success'" class="w-5 h-5 text-green-500" />
          <XCircleIcon v-else class="w-5 h-5 text-red-500" />
        </div>
        <div class="ml-3 flex-1">
          <p class="text-sm font-medium">{{ toast.title }}</p>
          <p class="text-sm mt-1">{{ toast.message }}</p>
        </div>
        <button @click="toast.show = false" class="ml-4 flex-shrink-0 text-gray-400 hover:text-gray-600">
          <XMarkIcon class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-8">
      <div class="spinner"></div>
      <span class="ml-2 text-gray-600">Loading students...</span>
    </div>

    <!-- Students List -->
    <div v-else-if="students && students.length > 0" class="space-y-3">
      <div class="flex justify-between items-center mb-4">
        <p class="text-sm text-gray-600" v-if="mode === 'attendance'">
          Total: {{ students.length }} | 
          To Mark Present: {{ presentStudents.length }} | 
          To Mark Absent: {{ availableStudents.length - presentStudents.length }} |
          Already Marked: {{ markedStudentsCount }}
        </p>
        <p class="text-sm text-gray-600" v-else>
          Total: {{ students.length }} | 
          Selected for Promotion: {{ selectedStudents.length }} |
          Not Selected: {{ students.length - selectedStudents.length }}
          <span v-if="studentGroupInfo.success" class="ml-2 text-green-600 font-semibold">
            → To: {{ studentGroupInfo.next_group }}
          </span>
        </p>
        
        <button
          @click="toggleAllStudents"
          class="px-3 py-1 text-sm bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
          :disabled="mode === 'attendance' ? allStudentsMarked : false"
        >
          <span v-if="mode === 'attendance'">
            {{ presentStudents.length === availableStudents.length ? 'Mark All Absent' : 'Mark All Present' }}
          </span>
          <span v-else>
            {{ selectedStudents.length === students.length ? 'Deselect All' : 'Select All' }}
          </span>
        </button>
      </div>

      <!-- Already Marked Students (Only for attendance mode) -->
      <template v-if="mode === 'attendance'">
        <div 
          v-for="student in markedStudents" 
          :key="student.student"
          class="bg-gray-100 rounded-lg shadow-sm p-4 border-2 border-gray-300 cursor-not-allowed"
        >
          <div class="flex items-center space-x-4">
            <!-- Student Avatar -->
            <div class="flex-shrink-0">
              <div class="w-12 h-12 rounded-full flex items-center justify-center text-white font-semibold text-sm relative overflow-hidden"
                   :class="student.present === 1 ? 'bg-gradient-to-br from-green-400 to-green-500' : 'bg-gradient-to-br from-yellow-400 to-yellow-500'">
                <img
                  v-if="student.img_url"
                  :src="getProfileImageUrl(student.img_url)"
                  alt="Student"
                  class="absolute inset-0 w-full h-full object-cover opacity-70"
                  @error="handleImageError"
                  loading="lazy"
                />
                <span v-else class="text-white text-sm font-medium opacity-70">
                  {{ getInitials(student.student_name) }}
                </span>
              </div>
            </div>
            
            <div class="flex-1 min-w-0">
              <h3 class="font-medium text-gray-500 truncate">{{ student.student_name }}</h3>
              <div class="flex items-center space-x-4 text-sm text-gray-500">
                <span>Roll No: {{ student.group_roll_number }}</span>
                <span class="text-gray-400">•</span>
                <span class="truncate">{{ student.student }}</span>
              </div>
              <div class="flex items-center space-x-2 mt-1">
                <CheckIcon v-if="student.present === 1" class="w-4 h-4 text-green-500" />
                <ClockIcon v-if="student.on_leave === 1" class="w-4 h-4 text-yellow-500" />
                <span class="text-xs font-medium" :class="student.present === 1 ? 'text-green-600' : 'text-yellow-600'">
                  {{ student.present === 1 ? 'Already Marked Present' : 'On Leave' }}
                </span>
              </div>
            </div>
            
            <div class="flex-shrink-0">
              <div class="w-6 h-6 rounded-full border-2 flex items-center justify-center"
                   :class="student.present === 1 ? 'bg-green-500 border-green-500' : 'bg-yellow-500 border-yellow-500'">
                <CheckIcon v-if="student.present === 1" class="w-4 h-4 text-white" />
                <MinusIcon v-if="student.on_leave === 1" class="w-4 h-4 text-white" />
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Available Students (For both modes) -->
      <div 
        v-for="student in (mode === 'attendance' ? availableStudents : students)" 
        :key="student.student"
        class="bg-white rounded-lg shadow-sm p-4 border-2 transition-colors cursor-pointer hover:border-blue-300"
        :class="getStudentCardClass(student)"
        @click="toggleStudent(student.student)"
      >
        <div class="flex items-center space-x-4">
          <!-- Student Avatar -->
          <div class="flex-shrink-0">
            <div class="w-12 h-12 rounded-full flex items-center justify-center text-white font-semibold text-sm relative overflow-hidden"
                :class="mode === 'attendance' ? 'bg-gradient-to-br from-blue-500 to-purple-600' : 'bg-gradient-to-br from-green-500 to-green-600'">
              <img
                v-if="student.img_url"
                :src="getProfileImageUrl(student.img_url)"
                alt="Student"
                class="absolute inset-0 w-full h-full object-cover"
                @error="handleImageError"
                loading="lazy"
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
            <div v-if="mode === 'promotion'" class="mt-1">
              <span class="text-xs text-gray-500">
                Current Year: {{ extractAcademicYear(selectedGroup) }}
              </span>
              <span v-if="studentGroupInfo.success && isStudentSelected(student)" 
                    class="ml-2 text-xs text-green-600 font-semibold">
                → {{ studentGroupInfo.next_group }} ({{ studentGroupInfo.next_program }})
              </span>
            </div>
          </div>
          
          <div class="flex-shrink-0">
            <div class="w-6 h-6 rounded-full border-2 flex items-center justify-center"
              :class="getCheckboxClass(student)">
              <CheckIcon v-if="isStudentSelected(student)" class="w-4 h-4 text-white" />
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
        @click="handleSubmit"
        :disabled="submitting || !canSubmit"
        :class="[
          'flex-1 px-4 py-3 text-white rounded-lg font-medium transition-colors flex items-center justify-center space-x-2',
          submitting || !canSubmit 
            ? 'bg-gray-400 cursor-not-allowed' 
            : mode === 'attendance' 
              ? 'bg-blue-600 hover:bg-blue-700' 
              : 'bg-green-600 hover:bg-green-700'
        ]"
      >
        <ArrowRightIcon class="w-5 h-5" />
        <span>{{ getSubmitButtonText }}</span>
      </button>
    </div>

    <!-- Confirmation Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">
          {{ mode === 'attendance' ? 'Confirm Attendance' : 'Confirm Promotion' }}
        </h3>
        
        <template v-if="mode === 'attendance'">
          <div class="space-y-2 mb-4">
            <div class="flex justify-between">
              <span class="text-gray-600">To Mark Present:</span>
              <span class="font-semibold">{{ presentStudents.length }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">To Mark Absent:</span>
              <span class="font-semibold">{{ availableStudents.length - presentStudents.length }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Already Marked:</span>
              <span class="font-semibold">{{ markedStudentsCount }}</span>
            </div>
          </div>
          <div class="text-sm text-gray-500 bg-blue-50 p-3 rounded mb-4">
            Note: Students already marked as "Present" or "On Leave" will not be included in this attendance submission.
          </div>
        </template>
        
        <template v-else>
          <div class="space-y-3 mb-4">
            <div class="flex justify-between">
              <span class="text-gray-600">Students to Promote:</span>
              <span class="font-semibold text-green-600">{{ selectedStudents.length }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Not Promoting:</span>
              <span class="font-semibold">{{ students.length - selectedStudents.length }}</span>
            </div>
            <div class="border-t pt-3">
              <div class="text-sm text-gray-600 mb-2">Promotion Details:</div>
              <div class="grid grid-cols-2 gap-2 text-sm">
                <div class="text-gray-500">From:</div>
                <div class="font-medium">{{ selectedGroup }}</div>
                <div class="text-gray-500">To:</div>
                <div class="font-medium text-green-600">{{ studentGroupInfo.next_group }}</div>
                <div class="text-gray-500">Program:</div>
                <div class="font-medium">{{ studentGroupInfo.next_program }}</div>
                <div class="text-gray-500">Academic Year:</div>
                <div class="font-medium">{{ studentGroupInfo.next_academic_year }}</div>
              </div>
            </div>
          </div>
          <div v-if="!studentGroupInfo.group_exists" class="text-sm bg-yellow-50 p-3 rounded mb-4 border border-yellow-200">
            <div class="flex items-start">
              <ExclamationTriangleIcon class="w-5 h-5 text-yellow-600 mr-2 mt-0.5 flex-shrink-0" />
              <div>
                <p class="font-medium text-yellow-800">Target Group Not Found</p>
                <p class="text-yellow-700 mt-1">
                  The student group <span class="font-semibold">{{ studentGroupInfo.next_group }}</span> 
                  does not exist in the system yet. Please contact administrator.
                </p>
              </div>
            </div>
          </div>
        </template>
        
        <div class="flex space-x-3">
          <button
            @click="showModal = false"
            class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="confirmAction"
            :class="[
              'flex-1 px-4 py-2 text-white rounded-lg font-medium transition-colors',
              mode === 'attendance' 
                ? 'bg-blue-600 hover:bg-blue-700' 
                : 'bg-green-600 hover:bg-green-700'
            ]"
            :disabled="mode === 'promotion' && !studentGroupInfo.group_exists"
          >
            {{ mode === 'attendance' ? 'Confirm Attendance' : 'Promote Students' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Permission Error Modal -->
    <div v-if="showPermissionModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-sm w-full mx-4">
        <div class="text-center">
          <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <XMarkIcon class="w-6 h-6 text-red-600" />
          </div>
          <h3 class="text-lg font-semibold text-gray-800 mb-2">Permission Denied</h3>
          <p class="text-gray-600 mb-4">
            You are not allowed to promote students. Please contact your administrator to enable this feature.
          </p>
          <button
            @click="showPermissionModal = false"
            class="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            OK
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { createResource } from 'frappe-ui'
import { 
  XMarkIcon, 
  ArrowRightIcon, 
  CheckIcon,
  ClockIcon,
  MinusIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const props = defineProps({
  selectedGroup: String
})

defineEmits(['back-to-dashboard'])

// Reactive state
const students = ref([])
const presentStudents = ref([])
const selectedStudents = ref([])
const loading = ref(true)
const showModal = ref(false)
const showPermissionModal = ref(false)
const submitting = ref(false)
const mode = ref('attendance') // 'attendance' or 'promotion'
const studentGroupInfo = ref({
  success: false,
  allowed: false,
  message: '',
  current_group: '',
  next_group: '',
  next_academic_year: '',
  next_program: '', // Added next_program field
  group_exists: false
})

// Toast notification
const toast = ref({
  show: false,
  type: 'success', // 'success' or 'error'
  title: '',
  message: ''
})

// Computed properties
const extractAcademicYear = (groupName) => {
  if (!groupName) return 'N/A'
  const match = groupName.match(/\(([^)]+)\)/) // Extract content between parentheses
  return match ? match[1] : 'N/A'
}

const currentDate = computed(() => {
  return new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

// Separate marked (present = 1 OR on_leave = 1) and available students (both = 0)
const markedStudents = computed(() => {
  return students.value.filter(student => student.present === 1 || student.on_leave === 1)
})

const availableStudents = computed(() => {
  return students.value.filter(student => student.present === 0 && student.on_leave === 0)
})

const markedStudentsCount = computed(() => {
  return markedStudents.value.length
})

const allStudentsMarked = computed(() => {
  return availableStudents.value.length === 0
})

const canSubmit = computed(() => {
  if (mode.value === 'attendance') {
    return availableStudents.value.length > 0
  } else {
    return selectedStudents.value.length > 0 && 
           studentGroupInfo.value.success && 
           studentGroupInfo.value.allowed &&
           studentGroupInfo.value.group_exists
  }
})

const getSubmitButtonText = computed(() => {
  if (submitting.value) {
    return mode.value === 'attendance' ? 'Submitting...' : 'Promoting...'
  }
  return mode.value === 'attendance' ? 'Submit' : 'Promote Students'
})

// Helper functions
const getProfileImageUrl = (imgUrl) => {
  if (!imgUrl) return null
  if (imgUrl.startsWith('http') || imgUrl.startsWith('//')) {
    return imgUrl
  }
  if (imgUrl.startsWith('/')) {
    return window.location.origin + imgUrl
  }
  const baseUrl = window.location.origin
  return `${baseUrl}/${imgUrl.replace(/^\//, '')}`
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

const getStudentCardClass = (student) => {
  if (mode.value === 'attendance') {
    return presentStudents.value.includes(student.student) ? 'border-green-500 bg-green-50' : 'border-gray-200'
  } else {
    return selectedStudents.value.includes(student.student) ? 'border-green-500 bg-green-50' : 'border-gray-200'
  }
}

const getCheckboxClass = (student) => {
  if (mode.value === 'attendance') {
    return presentStudents.value.includes(student.student) ? 'bg-green-500 border-green-500' : 'border-gray-300'
  } else {
    return selectedStudents.value.includes(student.student) ? 'bg-green-500 border-green-500' : 'border-gray-300'
  }
}

const isStudentSelected = (student) => {
  if (mode.value === 'attendance') {
    return presentStudents.value.includes(student.student)
  } else {
    return selectedStudents.value.includes(student.student)
  }
}

// Toast notification function
const showToast = (type, title, message) => {
  toast.value = {
    show: true,
    type,
    title,
    message
  }
  // Auto hide after 5 seconds
  setTimeout(() => {
    toast.value.show = false
  }, 5000)
}

// Watch for selected group changes
watch(() => props.selectedGroup, (newGroup) => {
  if (newGroup && mode.value === 'promotion') {
    fetchStudentGroupInfo(newGroup)
  }
})

// Mode management
const setMode = async (newMode) => {
  if (newMode === 'promotion') {
    const group = props.selectedGroup || localStorage.getItem('selected_student_group')
    if (!group) {
      showToast('error', 'Selection Required', 'Please select a class first.')
      return
    }
    
    // Fetch student group info to check permissions and get next group
    await fetchStudentGroupInfo(group)
    
    if (!studentGroupInfo.value.allowed) {
      showPermissionModal.value = true
      return
    }
    
    mode.value = newMode
    // Reset selection for promotion mode
    selectedStudents.value = []
  } else {
    mode.value = newMode
  }
}

// API Resources
const attendanceResource = createResource({
  url: 'school.al_ummah.api2.get_student_attendance_records',
  onSuccess(data) {
    console.log('Attendance data loaded:', data)
    return data
  },
  onError(error) {
    console.error('Error fetching attendance:', error)
    showToast('error', 'Load Failed', 'Failed to load student data. Please check your connection and try again.')
  }
})

const markAttendanceResource = createResource({
  url: 'school.al_ummah.api2.mark_attendance',
  onSuccess(data) {
    console.log('Attendance marked successfully:', data)
    submitting.value = false
    handleSuccessResponse(data, 'Attendance marked successfully!')
  },
  onError(error) {
    console.error('Error marking attendance:', error)
    submitting.value = false
    handleErrorResponse(error, 'attendance')
  }
})

const promoteStudentsResource = createResource({
  url: 'school.al_ummah.api6.promote_students',
  onSuccess(data) {
    console.log('Students promoted successfully:', data)
    submitting.value = false
    
    // Check if the response indicates success
    if (data.success === false) {
      // Handle backend success: false with message
      handleErrorResponse({ message: data.message }, 'promotion')
    } else {
      handleSuccessResponse(data, 'Students promoted successfully!')
    }
  },
  onError(error) {
    console.error('Error promoting students:', error)
    submitting.value = false
    handleErrorResponse(error, 'promotion')
  }
})

const studentGroupResource = createResource({
  url: 'school.al_ummah.api3.fetch_student_group',
  onSuccess(data) {
    console.log('Student group info loaded:', data)
    studentGroupInfo.value = data
    return data
  },
  onError(error) {
    console.error('Error fetching student group info:', error)
    studentGroupInfo.value = {
      success: false,
      allowed: false,
      message: 'Failed to load promotion information'
    }
  }
})

// Helper functions for API responses
const handleSuccessResponse = (data, defaultMessage) => {
  console.log('Success response data:', data) // Debug log
  
  // Check for success in different response formats
  if (data.success === true || data.status === 'success' || data.message?.includes('successfully')) {
    const successMessage = data.message || defaultMessage
    showToast('success', 'Success!', successMessage)
    setTimeout(() => {
      router.push({ name: 'Teacherhome' })
    }, 2000)
  } else if (data._server_messages) {
    try {
      const serverMessages = JSON.parse(data._server_messages)
      if (serverMessages.length > 0) {
        const message = JSON.parse(serverMessages[0])
        if (message.message) {
          showToast('success', 'Success!', message.message)
          setTimeout(() => {
            router.push({ name: 'Teacherhome' })
          }, 2000)
          return
        }
      }
    } catch (e) {
      console.error('Error parsing server messages:', e)
    }
    showToast('success', 'Success!', defaultMessage)
    setTimeout(() => {
      router.push({ name: 'Teacherhome' })
    }, 2000)
  } else {
    // If no clear success indicator but we got a 200 response
    showToast('success', 'Success!', defaultMessage)
    setTimeout(() => {
      router.push({ name: 'Teacherhome' })
    }, 2000)
  }
}

const handleErrorResponse = (error, operationType) => {
  console.error('Error response:', error) // Debug log
  
  if (error.exc_type === 'PermissionError') {
    showToast('error', 'Permission Denied', `You do not have permission to ${operationType === 'attendance' ? 'mark attendance' : 'promote students'}. Please contact your administrator.`)
  } else if (error.messages && error.messages.length > 0) {
    // Handle Frappe UI error format
    showToast('error', 'Operation Failed', error.messages[0])
  } else if (error.message) {
    showToast('error', 'Operation Failed', error.message)
  } else {
    showToast('error', 'Operation Failed', `Failed to ${operationType === 'attendance' ? 'submit attendance' : 'promote students'}. Please check your connection and try again.`)
  }
}

// Fetch student group info
const fetchStudentGroupInfo = async (groupName) => {
  try {
    await studentGroupResource.submit({
      current_group_name: groupName
    })
  } catch (error) {
    console.error('Error fetching student group info:', error)
  }
}

// Fetch attendance data
const fetchAttendanceData = async () => {
  loading.value = true
  try {
    const group = props.selectedGroup || localStorage.getItem('selected_student_group')
    if (!group) {
      showToast('error', 'Selection Required', 'Please select a class first.')
      loading.value = false
      return
    }

    const params = { based_on: 'Batch', student_group: group }
    const attendanceRecords = await attendanceResource.fetch(params)

    if (!attendanceRecords || attendanceRecords.length === 0) {
      showToast('error', 'No Students', 'No students found for this class.')
      students.value = []
      return
    }

    students.value = attendanceRecords
    // Default all available students to present (excluding already marked students)
    presentStudents.value = availableStudents.value.map(student => student.student)
    
    console.log('Loaded students:', {
      total: students.value.length,
      alreadyMarked: markedStudents.value.length,
      available: availableStudents.value.length
    })
  } catch (error) {
    console.error('Error fetching attendance:', error)
    showToast('error', 'Load Failed', 'Failed to load student data.')
  } finally {
    loading.value = false
  }
}

// Toggle all students
const toggleAllStudents = () => {
  if (mode.value === 'attendance') {
    if (allStudentsMarked.value) return
    if (presentStudents.value.length === availableStudents.value.length) {
      presentStudents.value = []
    } else {
      presentStudents.value = availableStudents.value.map(student => student.student)
    }
  } else {
    if (selectedStudents.value.length === students.value.length) {
      selectedStudents.value = []
    } else {
      selectedStudents.value = students.value.map(student => student.student)
    }
  }
}

// Toggle student selection
const toggleStudent = (studentId) => {
  if (mode.value === 'attendance') {
    const student = students.value.find(s => s.student === studentId)
    if (student && (student.present === 1 || student.on_leave === 1)) {
      return
    }
    
    const index = presentStudents.value.indexOf(studentId)
    if (index > -1) {
      presentStudents.value.splice(index, 1)
    } else {
      presentStudents.value.push(studentId)
    }
  } else {
    const index = selectedStudents.value.indexOf(studentId)
    if (index > -1) {
      selectedStudents.value.splice(index, 1)
    } else {
      selectedStudents.value.push(studentId)
    }
  }
}

// Handle submit
const handleSubmit = () => {
  if (mode.value === 'promotion') {
    if (!studentGroupInfo.value.allowed) {
      showPermissionModal.value = true
      return
    }
    
    if (!studentGroupInfo.value.success) {
      showToast('error', 'Cannot Promote', studentGroupInfo.value.message || 'Unknown error')
      return
    }
    
    if (selectedStudents.value.length === 0) {
      showToast('error', 'Selection Required', 'Please select at least one student to promote.')
      return
    }
  }

  if (mode.value === 'attendance' && presentStudents.value.length === 0) {
    showToast('error', 'Selection Required', 'Please select at least one student as present.')
    return
  }

  showModal.value = true
}

// Confirm action
const confirmAction = async () => {
  showModal.value = false
  submitting.value = true

  if (mode.value === 'attendance') {
    await submitAttendance()
  } else {
    await submitPromotion()
  }
}

// Submit attendance
const submitAttendance = async () => {
  const studentsPresent = availableStudents.value
    .filter(student => presentStudents.value.includes(student.student))
    .map(student => ({
      student: student.student,
      student_name: student.student_name,
      group_roll_number: student.group_roll_number,
      disabled: false,
      checked: true,
    }))

  const studentsAbsent = availableStudents.value
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

// Submit promotion
const submitPromotion = async () => {
  const studentsToPromote = students.value
    .filter(student => selectedStudents.value.includes(student.student))
    .map(student => ({
      student: student.student,
      student_name: student.student_name,
      current_academic_year: student.academic_year,
      group_roll_number: student.group_roll_number,
      current_group: props.selectedGroup,
      next_group: studentGroupInfo.value.next_group
    }))

  console.log('Students to promote:', studentsToPromote)
  console.log('Promotion details:', {
    student_group: props.selectedGroup,
    next_academic_year: studentGroupInfo.value.next_academic_year,
    next_student_group: studentGroupInfo.value.next_group,
    next_program: studentGroupInfo.value.next_program
  })

  const group = props.selectedGroup || localStorage.getItem('selected_student_group')

  try {
    await promoteStudentsResource.submit({
      students: JSON.stringify(studentsToPromote),
      student_group: group,
      next_academic_year: studentGroupInfo.value.next_academic_year,
      next_student_group: studentGroupInfo.value.next_group,
      next_program: studentGroupInfo.value.next_program
    })
  } catch (error) {
    console.error('Error promoting students:', error)
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