<template>
  <div class="min-h-screen bg-gray-50 p-3 sm:p-4 md:p-6">
    <!-- Header -->
    <div class="mb-4 sm:mb-6">
      <h1 class="text-xl sm:text-2xl font-bold text-gray-800">Attendance Record</h1>
      <p class="text-sm sm:text-base text-gray-600">View student attendance history</p>
      <p class="text-xs sm:text-sm text-gray-500 mt-1" v-if="selectedGroup">Class: {{ selectedGroup }}</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-6 sm:py-8">
      <div class="spinner"></div>
      <span class="ml-2 text-sm sm:text-base text-gray-600">Loading attendance records...</span>
    </div>

    <!-- Students List -->
    <div v-else-if="students && students.length > 0" class="space-y-3">
      <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 mb-4">
        <p class="text-sm text-gray-600">
          Total Students: {{ students.length }}
        </p>
        <button
          @click="fetchAttendanceData"
          class="px-3 py-2 sm:py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center justify-center sm:justify-start space-x-2 w-full sm:w-auto"
        >
          <ArrowPathIcon class="w-4 h-4" />
          <span>Refresh</span>
        </button>
      </div>

      <!-- Student Records -->
      <div 
        v-for="student in students" 
        :key="student.student"
        class="bg-white rounded-lg shadow-sm p-3 sm:p-4 border border-gray-200 hover:border-blue-300 transition-colors"
      >
        <div class="flex items-center space-x-3 sm:space-x-4">
          <!-- Student Avatar -->
          <div class="flex-shrink-0 cursor-pointer" @click="viewStudentDetails(student)">
            <div class="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold text-xs sm:text-sm relative overflow-hidden">
              <img
                v-if="student.img_url"
                :src="getProfileImageUrl(student.img_url)"
                alt="Student"
                class="absolute inset-0 w-full h-full object-cover"
                @error="handleImageError"
                loading="lazy"
              />
              <span v-else class="text-white text-xs sm:text-sm font-medium">
                {{ getInitials(student.student_name) }}
              </span>
            </div>
          </div>
          
          <!-- Student Info -->
          <div class="flex-1 min-w-0 cursor-pointer" @click="viewStudentDetails(student)">
            <h3 class="font-medium text-gray-800 truncate text-sm sm:text-base">{{ student.student_name }}</h3>
            <div class="flex flex-col sm:flex-row sm:items-center space-y-1 sm:space-y-0 sm:space-x-4 text-xs sm:text-sm text-gray-600 mt-1">
              <span>Roll No: {{ student.group_roll_number }}</span>
              <span class="hidden sm:inline text-gray-400">•</span>
              <span class="truncate text-xs">ID: {{ student.student }}</span>
            </div>
            
            <!-- Attendance Stats -->
            <div class="flex items-center flex-wrap gap-2 sm:gap-4 mt-2 text-xs">
              <span class="flex items-center space-x-1 text-green-600">
                <CheckCircleIcon class="w-3 h-3 sm:w-4 sm:h-4" />
                <span>Present: {{ student.present_count || 0 }}</span>
              </span>
              <span class="flex items-center space-x-1 text-red-600">
                <XCircleIcon class="w-3 h-3 sm:w-4 sm:h-4" />
                <span>Absent: {{ student.absent_count || 0 }}</span>
              </span>
              <span class="flex items-center space-x-1 text-yellow-600">
                <ClockIcon class="w-3 h-3 sm:w-4 sm:h-4" />
                <span>Leave: {{ student.leave_count || 0 }}</span>
              </span>
            </div>
          </div>
          
          <!-- Action Buttons -->
          <div class="flex-shrink-0 flex items-center space-x-1 sm:space-x-2">
            <!-- Edit Button -->
            <button
              @click.stop="editStudent(student)"
              class="p-1.5 sm:p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
              title="Edit Student"
            >
              <PencilSquareIcon class="w-4 h-4 sm:w-5 sm:h-5" />
            </button>
            
            <!-- View Details Arrow -->
            <div class="cursor-pointer" @click.stop="viewStudentDetails(student)">
              <ChevronRightIcon class="w-4 h-4 sm:w-5 sm:h-5 text-gray-400" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- No Students State -->
    <div v-else class="text-center py-6 sm:py-8">
      <div class="bg-white rounded-lg shadow-sm p-6 sm:p-8">
        <UserGroupIcon class="w-12 h-12 sm:w-16 sm:h-16 text-gray-300 mx-auto mb-3 sm:mb-4" />
        <h3 class="text-base sm:text-lg font-medium text-gray-800 mb-2">No Students Found</h3>
        <p class="text-sm text-gray-600 mb-4">No attendance records available for this class.</p>
        <button 
          @click="fetchAttendanceData"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center space-x-2 mx-auto w-full sm:w-auto"
        >
          <ArrowPathIcon class="w-4 h-4" />
          <span>Refresh Data</span>
        </button>
      </div>
    </div>

    <!-- Student Details Modal -->
    <div v-if="selectedStudent && showStudentModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-3 sm:p-4">
      <div class="bg-white rounded-lg p-4 sm:p-6 w-full max-w-sm sm:max-w-md mx-auto max-h-[90vh] sm:max-h-[80vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-800">Student Details</h3>
          <button @click="closeStudentModal" class="text-gray-400 hover:text-gray-600">
            <XMarkIcon class="w-5 h-5 sm:w-6 sm:h-6" />
          </button>
        </div>
        
        <!-- Student Info in Modal -->
        <div class="flex items-center space-x-3 sm:space-x-4 mb-4 sm:mb-6">
          <div class="w-12 h-12 sm:w-16 sm:h-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold text-base sm:text-lg relative overflow-hidden">
            <img
              v-if="selectedStudent.img_url"
              :src="getProfileImageUrl(selectedStudent.img_url)"
              alt="Student"
              class="absolute inset-0 w-full h-full object-cover"
              @error="handleImageError"
              loading="lazy"
            />
            <span v-else class="text-white text-base sm:text-lg font-medium">
              {{ getInitials(selectedStudent.student_name) }}
            </span>
          </div>
          <div class="min-w-0 flex-1">
            <h4 class="font-medium text-gray-800 text-sm sm:text-base truncate">{{ selectedStudent.student_name }}</h4>
            <p class="text-xs sm:text-sm text-gray-600">Roll No: {{ selectedStudent.group_roll_number }}</p>
            <p class="text-xs text-gray-500 truncate">ID: {{ selectedStudent.student }}</p>
          </div>
        </div>

        <!-- Detailed Attendance Stats -->
        <div class="grid grid-cols-3 gap-2 sm:gap-4 mb-4 sm:mb-6">
          <div class="text-center p-2 sm:p-3 bg-green-50 rounded-lg">
            <CheckCircleIcon class="w-6 h-6 sm:w-8 sm:h-8 text-green-600 mx-auto mb-1 sm:mb-2" />
            <p class="text-xl sm:text-2xl font-bold text-green-600">{{ selectedStudent.present_count || 0 }}</p>
            <p class="text-xs sm:text-sm text-green-700">Present</p>
          </div>
          <div class="text-center p-2 sm:p-3 bg-red-50 rounded-lg">
            <XCircleIcon class="w-6 h-6 sm:w-8 sm:h-8 text-red-600 mx-auto mb-1 sm:mb-2" />
            <p class="text-xl sm:text-2xl font-bold text-red-600">{{ selectedStudent.absent_count || 0 }}</p>
            <p class="text-xs sm:text-sm text-red-700">Absent</p>
          </div>
          <div class="text-center p-2 sm:p-3 bg-yellow-50 rounded-lg">
            <ClockIcon class="w-6 h-6 sm:w-8 sm:h-8 text-yellow-600 mx-auto mb-1 sm:mb-2" />
            <p class="text-xl sm:text-2xl font-bold text-yellow-600">{{ selectedStudent.leave_count || 0 }}</p>
            <p class="text-xs sm:text-sm text-yellow-700">Leave</p>
          </div>
        </div>

        <!-- Contact Info -->
        <div class="border-t pt-3 sm:pt-4">
          <h5 class="font-medium text-gray-800 mb-2 sm:mb-3 text-sm sm:text-base">Contact Information</h5>
          
          <!-- Loading State for Guardian Numbers -->
          <div v-if="loadingGuardianNumbers" class="text-center py-3 sm:py-4">
            <div class="spinner-small mx-auto mb-2"></div>
            <p class="text-xs sm:text-sm text-gray-500">Loading guardian information...</p>
          </div>
          
          <!-- Student Mobile Number -->
          <div v-if="selectedStudent.mobile" class="mb-2 sm:mb-3">
            <p class="text-xs text-gray-500 mb-1 sm:mb-2 font-medium uppercase tracking-wide">Student Mobile</p>
            <a 
              :href="`tel:${selectedStudent.mobile}`"
              class="flex items-center justify-between text-sm text-blue-700 hover:text-blue-900 hover:bg-blue-50 p-2 rounded-lg transition-all duration-200 cursor-pointer border border-blue-100"
            >
              <div class="flex items-center space-x-2 sm:space-x-3 min-w-0 flex-1">
                <div class="w-7 h-7 sm:w-8 sm:h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <PhoneIcon class="w-3 h-3 sm:w-4 sm:h-4 text-blue-600" />
                </div>
                <div class="min-w-0 flex-1">
                  <span class="font-semibold block text-gray-800 truncate text-xs sm:text-sm">Student</span>
                  <span class="text-gray-600 text-xs">{{ formatPhoneNumber(selectedStudent.mobile) }}</span>
                </div>
              </div>
              <PhoneIcon class="w-3 h-3 sm:w-4 sm:h-4 text-blue-600 flex-shrink-0" />
            </a>
          </div>

          <!-- Guardian Mobile Numbers -->
          <div v-if="!loadingGuardianNumbers && guardianNumbers.length > 0" class="space-y-2">
            <p class="text-xs text-gray-500 mb-1 sm:mb-2 font-medium uppercase tracking-wide">Guardian Contacts</p>
            
            <!-- Guardian List -->
            <div 
              v-for="(guardian, index) in guardianNumbers" 
              :key="index"
            >
              <a 
                :href="`tel:${guardian.mobile_number}`"
                class="flex items-center justify-between text-sm hover:bg-gray-50 p-2 rounded-lg transition-all duration-200 cursor-pointer border"
                :class="getGuardianCardClass(index)"
              >
                <div class="flex items-center space-x-2 sm:space-x-3 min-w-0 flex-1">
                  <div class="w-7 h-7 sm:w-8 sm:h-8 rounded-full flex items-center justify-center flex-shrink-0" :class="getGuardianIconClass(index)">
                    <UserIcon class="w-3 h-3 sm:w-4 sm:h-4" :class="getGuardianIconColor(index)" />
                  </div>
                  <div class="min-w-0 flex-1">
                    <span class="font-semibold block text-gray-800 truncate text-xs sm:text-sm">{{ guardian.guardian_name }}</span>
                    <span class="text-gray-600 text-xs">{{ formatPhoneNumber(guardian.mobile_number) }}</span>
                  </div>
                </div>
                <PhoneIcon class="w-3 h-3 sm:w-4 sm:h-4 flex-shrink-0" :class="getGuardianActionColor(index)" />
              </a>
            </div>
          </div>

          <!-- Fallback to existing guardian data if API returns empty -->
          <div v-if="!loadingGuardianNumbers && guardianNumbers.length === 0 && (selectedStudent.guardian_number || selectedStudent.parent_mobile)" class="space-y-2">
            <p class="text-xs text-gray-500 mb-1 sm:mb-2 font-medium uppercase tracking-wide">Guardian Contact</p>
            <a 
              :href="`tel:${selectedStudent.guardian_number || selectedStudent.parent_mobile}`"
              class="flex items-center justify-between text-sm text-green-700 hover:text-green-900 hover:bg-green-50 p-2 rounded-lg transition-all duration-200 cursor-pointer border border-green-100"
            >
              <div class="flex items-center space-x-2 sm:space-x-3 min-w-0 flex-1">
                <div class="w-7 h-7 sm:w-8 sm:h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <UserIcon class="w-3 h-3 sm:w-4 sm:h-4 text-green-600" />
                </div>
                <div class="min-w-0 flex-1">
                  <span class="font-semibold block text-gray-800 truncate text-xs sm:text-sm">{{ getGuardianName(selectedStudent) }}</span>
                  <span class="text-gray-600 text-xs">{{ formatPhoneNumber(selectedStudent.guardian_number || selectedStudent.parent_mobile) }}</span>
                </div>
              </div>
              <PhoneIcon class="w-3 h-3 sm:w-4 sm:h-4 text-green-600 flex-shrink-0" />
            </a>
          </div>

          <!-- Address -->
          <div v-if="selectedStudent.address" class="mt-3 sm:mt-4 pt-3 sm:pt-4 border-t">
            <p class="text-xs text-gray-500 mb-1 sm:mb-2 font-medium uppercase tracking-wide">Address</p>
            <div class="flex items-start space-x-2 sm:space-x-3 text-sm text-gray-600 p-2 bg-gray-50 rounded-lg">
              <MapPinIcon class="w-3 h-3 sm:w-4 sm:h-4 text-gray-400 mt-0.5 flex-shrink-0" />
              <span class="leading-relaxed text-xs break-words">{{ selectedStudent.address }}</span>
            </div>
          </div>

          <!-- No Contact Information -->
          <div v-if="!selectedStudent.mobile && guardianNumbers.length === 0 && !selectedStudent.address && !loadingGuardianNumbers" class="text-center py-3 sm:py-4">
            <UserIcon class="w-6 h-6 sm:w-8 sm:h-8 text-gray-300 mx-auto mb-2" />
            <p class="text-xs sm:text-sm text-gray-500">No contact information available</p>
          </div>
        </div>

        <div class="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3 mt-4 sm:mt-6">
          <button
            @click="editStudent(selectedStudent)"
            class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center space-x-2 transition-colors text-sm sm:text-base"
          >
            <PencilSquareIcon class="w-3 h-3 sm:w-4 sm:h-4" />
            <span>Edit Student</span>
          </button>
          <button
            @click="closeStudentModal"
            class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm sm:text-base"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { createResource } from 'frappe-ui'
import { 
  ArrowPathIcon, 
  ChevronRightIcon, 
  XMarkIcon,
  UserGroupIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  PencilSquareIcon,
  PhoneIcon,
  UserIcon,
  MapPinIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()

// Reactive state
const students = ref([])
const loading = ref(true)
const selectedGroup = ref('')
const selectedStudent = ref(null)
const showStudentModal = ref(false)
const guardianNumbers = ref([])
const loadingGuardianNumbers = ref(false)

// Helper function to get guardian name
const getGuardianName = (student) => {
  if (student.guardian_name) return student.guardian_name
  if (student.parent_name) return student.parent_name
  return 'Guardian'
}

// Format phone number for better display
const formatPhoneNumber = (phone) => {
  if (!phone) return ''
  // Remove any non-digit characters
  const cleaned = phone.replace(/\D/g, '')
  // Format as XXX-XXX-XXXX
  if (cleaned.length === 10) {
    return cleaned.replace(/(\d{3})(\d{3})(\d{4})/, '$1-$2-$3')
  }
  return phone
}

// Styling functions for different guardians
const getGuardianCardClass = (index) => {
  const classes = [
    'text-green-700 hover:text-green-900 border-green-100',
    'text-purple-700 hover:text-purple-900 border-purple-100', 
    'text-orange-700 hover:text-orange-900 border-orange-100',
    'text-indigo-700 hover:text-indigo-900 border-indigo-100',
    'text-pink-700 hover:text-pink-900 border-pink-100'
  ]
  return classes[index % classes.length]
}

const getGuardianIconClass = (index) => {
  const classes = [
    'bg-green-100',
    'bg-purple-100',
    'bg-orange-100',
    'bg-indigo-100',
    'bg-pink-100'
  ]
  return classes[index % classes.length]
}

const getGuardianIconColor = (index) => {
  const classes = [
    'text-green-600',
    'text-purple-600',
    'text-orange-600',
    'text-indigo-600',
    'text-pink-600'
  ]
  return classes[index % classes.length]
}

const getGuardianActionColor = (index) => {
  const classes = [
    'text-green-600',
    'text-purple-600',
    'text-orange-600',
    'text-indigo-600',
    'text-pink-600'
  ]
  return classes[index % classes.length]
}

// Helper functions for profile images
const getProfileImageUrl = (imgUrl) => {
  if (!imgUrl) return null
  
  // If URL is already absolute, use it directly
  if (imgUrl.startsWith('http') || imgUrl.startsWith('//')) {
    return imgUrl
  }
  
  // If URL starts with /, prepend current origin
  if (imgUrl.startsWith('/')) {
    return window.location.origin + imgUrl
  }
  
  // For relative URLs, construct full URL
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

// Create resource for fetching guardian numbers
const guardianResource = createResource({
  url: 'school.al_ummah.api2.get_guardian_numbers',
  makeParams({ student_id }) {
    return {
      student_id: student_id
    }
  },
  onSuccess(data) {
    return data
  },
  onError(error) {
    console.error('Error fetching guardian numbers:', error)
    return null
  }
})

// Fetch guardian numbers
const fetchGuardianNumbers = async (studentId) => {
  if (!studentId) return
  
  loadingGuardianNumbers.value = true
  guardianNumbers.value = []
  
  try {
    const params = {
      student_id: studentId
    }
    
    const apiData = await guardianResource.fetch(params)
    
    if (apiData && Array.isArray(apiData)) {
      guardianNumbers.value = apiData
    } else {
      console.warn('Invalid API response format:', apiData)
    }
  } catch (error) {
    console.warn('Failed to fetch guardian numbers:', error)
  } finally {
    loadingGuardianNumbers.value = false
  }
}

// Edit student function
const editStudent = (student) => {
  // Prepare complete student data with all fields
  const studentData = {
    // Student ID (primary identifier)
    student_id: student.student,
    
    // Basic info
    student_name: student.student_name,
    group_roll_number: student.group_roll_number,
    student_group: selectedGroup.value,
    
    // Personal Details
    'First Name': student.first_name || student.student_name?.split(' ')[0] || '',
    'Middle Name': student.middle_name || student.student_name?.split(' ')[1] || '',
    'Last Name': student.last_name || student.student_name?.split(' ')[2] || '',
    'Student Date of Birth': student.date_of_birth || student.student_date_of_birth || '',
    'GR Number': student.name || student.group_roll_number || '',
    
    // Contact Information
    'Email Address': student.email || student.email_address || '',
    'Phone Number': student.mobile || student.phone_number || '',
    
    // Guardian Information
    'Guardian Name': student.guardian_name || student.parent_name || '',
    'Guardian Number': student.guardian_number || student.parent_mobile || '',
    'Guardian Name 2': student.guardian_name_2 || '',
    'Guardian Number 2': student.guardian_number_2 || '',
    'Guardian Name 3': student.guardian_name_3 || '',
    'Guardian Number 3': student.guardian_number_3 || '',
    'Relation': student.relation || '',
    'Guardian Date of Birth': student.guardian_date_of_birth || '',
    'Guardian Email': student.guardian_email || '',
    'Guardian Occupation': student.guardian_occupation || '',
    'Guardian Designation': student.guardian_designation || '',
    'Guardian Work Address': student.guardian_work_address || '',
    'Guardian Education': student.guardian_education || '',
    
    // Address
    address: student.address || '',
    
    // Profile image URL
    img_url: student.img_url || '',
    
    // Attendance stats
    present_count: student.present_count || 0,
    absent_count: student.absent_count || 0,
    leave_count: student.leave_count || 0,
    
    // Additional fields from API
    gender: student.gender || '',
    date_of_birth: student.date_of_birth || '',
    parent_name: student.parent_name || '',
    parent_mobile: student.parent_mobile || '',
    
    // Include all original data
    ...student
  }

  // Navigate to EditStudent page with complete student data
  router.push({
    name: 'EditStudent',
    query: {
      studentId: student.student, // Send student ID as separate parameter for easy access
      studentData: encodeURIComponent(JSON.stringify(studentData))
    }
  })
}

// Create resource for fetching attendance records
const attendanceResource = createResource({
  url: 'school.al_ummah.api2.get_student_attendance_records',
  makeParams({ based_on, student_group, calculate_count_data }) {
    return {
      based_on,
      student_group,
      calculate_count_data: calculate_count_data || true  // Default to true
    }
  },
  onSuccess(data) {
    return data
  },
  onError(error) {
    console.error('Error fetching attendance records:', error)
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
      calculate_count_data: true  // Add this flag
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
const viewStudentDetails = async (student) => {
  selectedStudent.value = student
  showStudentModal.value = true
  // Fetch guardian numbers when modal opens
  await fetchGuardianNumbers(student.student)
}

// Close student modal
const closeStudentModal = () => {
  showStudentModal.value = false
  selectedStudent.value = null
  guardianNumbers.value = [] // Reset guardian numbers when modal closes
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

.spinner-small {
  width: 20px;
  height: 20px;
  border: 2px solid #e5e7eb;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Style for clickable phone links */
a[href^="tel:"] {
  text-decoration: none;
  display: block;
}

a[href^="tel:"]:hover {
  text-decoration: none;
}

/* Responsive text sizing */
@media (max-width: 640px) {
  .text-responsive {
    font-size: 0.875rem;
  }
}
</style>