<template>
  <div class="min-h-screen bg-gray-50 p-4">
    <!-- Header -->
    <div class="mb-6">
      <div class="flex justify-between items-start">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">Promote Students</h1>
          <p class="text-gray-600">Select students to promote to next academic year</p>
          <p class="text-sm text-gray-500 mt-1" v-if="selectedGroup">Current Class: {{ selectedGroup }}</p>
          <p class="text-sm text-gray-500">Date: {{ currentDate }}</p>
        </div>
        
        <!-- Mode Picker -->
        <div class="flex flex-col items-end space-y-2">
          <div class="bg-white rounded-lg border border-gray-300 p-1 flex">
            <button
              @click="setMode('attendance')"
              class="px-3 py-1 text-sm font-medium rounded-md transition-colors text-gray-600 hover:text-gray-800"
            >
              Take Attendance
            </button>
            <button
              @click="setMode('promotion')"
              class="px-3 py-1 text-sm font-medium rounded-md transition-colors bg-green-600 text-white"
            >
              Promote Students
            </button>
          </div>
          
          <!-- Promotion Info -->
          <div v-if="studentGroupInfo.success" 
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
          <div v-if="!studentGroupInfo.success && studentGroupInfo.message" 
               class="text-sm bg-red-50 px-3 py-2 rounded-lg border border-red-200 max-w-xs">
            <div class="font-semibold text-red-800 mb-1">Cannot Promote:</div>
            <div class="text-red-700">{{ studentGroupInfo.message }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast Message -->
    <ToastMessage
      :show="toast.show"
      :type="toast.type"
      :title="toast.title"
      :message="toast.message"
      @close="toast.show = false"
    />

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-8">
      <div class="spinner"></div>
      <span class="ml-2 text-gray-600">Loading students...</span>
    </div>

    <!-- Student List -->
    <StudentList
      v-else
      :students="students"
      :selected-students="selectedStudents"
      mode="promotion"
      :available-students="students"
      :promotion-info="promotionInfoText"
      :selected-group="selectedGroup"
      @student-toggle="toggleStudent"
      @toggle-all="toggleAllStudents"
      @reload="fetchPromotionData"
    >
      <template #header-stats>
        Total: {{ students.length }} | 
        Selected for Promotion: {{ selectedStudents.length }} |
        Not Selected: {{ students.length - selectedStudents.length }}
        <span v-if="studentGroupInfo.success" class="ml-2 text-green-600 font-semibold">
          → To: {{ studentGroupInfo.next_group }}
        </span>
      </template>
    </StudentList>

    <!-- Action Buttons -->
    <ActionButtons
      v-if="students.length > 0"
      mode="promotion"
      :submitting="submitting"
      :can-submit="canSubmit"
      @cancel="handleCancel"
      @submit="handleSubmit"
    />

    <!-- Confirmation Modal -->
    <ConfirmationModal
      v-if="showModal"
      mode="promotion"
      :selected-students="selectedStudents"
      :total-students="students.length"
      :student-group-info="studentGroupInfo"
      @confirm="confirmAction"
      @cancel="showModal = false"
    />

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
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { createResource } from 'frappe-ui'
import { XMarkIcon } from '@heroicons/vue/24/outline'

// Components
import StudentList from './StudentList.vue'
import ToastMessage from './ToastMessage.vue'
import ActionButtons from './ActionButtons.vue'
import ConfirmationModal from './ConfirmationModal.vue'

const router = useRouter()

// Get group from query params or localStorage
const selectedGroup = ref(router.currentRoute.value.query.group || localStorage.getItem('selected_student_group'))

// Reactive state
const students = ref([])
const selectedStudents = ref([])
const loading = ref(true)
const showModal = ref(false)
const showPermissionModal = ref(false)
const submitting = ref(false)
const studentGroupInfo = ref({
  success: false,
  allowed: false,
  message: '',
  current_group: '',
  next_group: '',
  next_academic_year: '',
  next_program: '',
  group_exists: false
})

// Toast notification
const toast = ref({
  show: false,
  type: 'success',
  title: '',
  message: ''
})

// Computed properties
const currentDate = computed(() => {
  return new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

const canSubmit = computed(() => {
  return selectedStudents.value.length > 0 && 
         studentGroupInfo.value.success && 
         studentGroupInfo.value.allowed &&
         studentGroupInfo.value.group_exists
})

const promotionInfoText = computed(() => {
  if (studentGroupInfo.value.success) {
    return `→ ${studentGroupInfo.value.next_group} (${studentGroupInfo.value.next_program})`
  }
  return ''
})

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

const promoteStudentsResource = createResource({
  url: 'school.al_ummah.api6.promote_students',
  onSuccess(data) {
    console.log('Students promoted successfully:', data)
    submitting.value = false
    
    if (data.success === false) {
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

// Helper functions
const showToast = (type, title, message) => {
  toast.value = {
    show: true,
    type,
    title,
    message
  }
  setTimeout(() => {
    toast.value.show = false
  }, 5000)
}

const handleSuccessResponse = (data, defaultMessage) => {
  if (data.success === true || data.status === 'success' || data.message?.includes('successfully')) {
    const successMessage = data.message || defaultMessage
    showToast('success', 'Success!', successMessage)
    setTimeout(() => {
      router.push({ name: 'Teacherhome' })
    }, 2000)
  } else {
    showToast('success', 'Success!', defaultMessage)
    setTimeout(() => {
      router.push({ name: 'Teacherhome' })
    }, 2000)
  }
}

const handleErrorResponse = (error, operationType) => {
  if (error.exc_type === 'PermissionError') {
    showToast('error', 'Permission Denied', `You do not have permission to ${operationType === 'attendance' ? 'mark attendance' : 'promote students'}. Please contact your administrator.`)
  } else if (error.messages && error.messages.length > 0) {
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

// Fetch promotion data
const fetchPromotionData = async () => {
  loading.value = true
  try {
    if (!selectedGroup.value) {
      showToast('error', 'Selection Required', 'Please select a class first.')
      loading.value = false
      return
    }

    // Fetch student group info first
    await fetchStudentGroupInfo(selectedGroup.value)

    if (!studentGroupInfo.value.allowed) {
      showPermissionModal.value = true
      loading.value = false
      return
    }

    // Fetch students
    const params = { based_on: 'Batch', student_group: selectedGroup.value }
    const response = await attendanceResource.fetch(params)

    // Handle both old (array) and new (object) response formats
    let studentList = []
    
    if (Array.isArray(response)) {
      // Old format - response is directly the student array
      studentList = response
    } else if (response && response.students) {
      // New format - response is an object with students property
      studentList = response.students
    } else {
      // Invalid response
      showToast('error', 'No Students', 'No students found for this class.')
      students.value = []
      return
    }

    if (!studentList || studentList.length === 0) {
      showToast('error', 'No Students', 'No students found for this class.')
      students.value = []
      return
    }

    students.value = studentList
    
  } catch (error) {
    console.error('Error fetching promotion data:', error)
    showToast('error', 'Load Failed', 'Failed to load student data.')
  } finally {
    loading.value = false
  }
}

// Toggle student selection
const toggleStudent = (studentId) => {
  const index = selectedStudents.value.indexOf(studentId)
  if (index > -1) {
    selectedStudents.value.splice(index, 1)
  } else {
    selectedStudents.value.push(studentId)
  }
}

// Toggle all students
const toggleAllStudents = () => {
  if (selectedStudents.value.length === students.value.length) {
    selectedStudents.value = []
  } else {
    selectedStudents.value = students.value.map(student => student.student)
  }
}

// Mode management
const setMode = (newMode) => {
  if (newMode === 'attendance') {
    router.push({ name: 'AttendancePage' })
  }
}

// Handle submit
const handleSubmit = () => {
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

  showModal.value = true
}

// Confirm action
const confirmAction = async () => {
  showModal.value = false
  submitting.value = true

  const studentsToPromote = students.value
    .filter(student => selectedStudents.value.includes(student.student))
    .map(student => ({
      student: student.student,
      student_name: student.student_name,
      current_academic_year: student.academic_year,
      group_roll_number: student.group_roll_number,
      current_group: selectedGroup.value,
      next_group: studentGroupInfo.value.next_group
    }))

  try {
    await promoteStudentsResource.submit({
      students: JSON.stringify(studentsToPromote),
      student_group: selectedGroup.value,
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
  fetchPromotionData()
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