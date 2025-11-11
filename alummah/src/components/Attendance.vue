<template>
  <div class="min-h-screen bg-gray-50 p-4">
    <!-- Header -->
    <div class="mb-6">
      <div class="flex justify-between items-start">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">Take Attendance</h1>
          <p class="text-gray-600">Select students who are present today</p>
          <p class="text-sm text-gray-500 mt-1" v-if="selectedGroup">Current Class: {{ selectedGroup }}</p>
          <p class="text-sm text-gray-500">Date: {{ currentDate }}</p>
        </div>
        
        <!-- Back Button -->
        <button
          @click="handleBack"
          class="px-4 py-2 bg-gray-600 text-white rounded-lg font-medium hover:bg-gray-700 transition-colors flex items-center space-x-2"
        >
          <ArrowLeftIcon class="w-5 h-5" />
          <span>Back to Dashboard</span>
        </button>
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
      :selected-students="presentStudents"
      mode="attendance"
      :show-marked-students="true"
      :marked-students="markedStudents"
      :available-students="availableStudents"
      :disabled="allStudentsMarked"
      @student-toggle="toggleStudent"
      @toggle-all="toggleAllStudents"
      @reload="fetchAttendanceData"
    >
      <template #header-stats>
        Total: {{ students.length }} | 
        To Mark Present: {{ presentStudents.length }} | 
        To Mark Absent: {{ availableStudents.length - presentStudents.length }} |
        Already Marked: {{ markedStudentsCount }}
      </template>
      
      <template #toggle-button-text>
        {{ presentStudents.length === availableStudents.length ? 'Mark All Absent' : 'Mark All Present' }}
      </template>
    </StudentList>

    <!-- Action Buttons -->
    <ActionButtons
      v-if="students.length > 0"
      mode="attendance"
      :submitting="submitting"
      :can-submit="canSubmit"
      @cancel="handleCancel"
      @submit="handleSubmit"
    />

    <!-- Confirmation Modal -->
    <ConfirmationModal
      v-if="showModal"
      mode="attendance"
      :present-students="presentStudents"
      :available-students="availableStudents"
      :marked-students-count="markedStudentsCount"
      @confirm="confirmAction"
      @cancel="showModal = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { createResource } from 'frappe-ui'
import { ArrowLeftIcon } from '@heroicons/vue/24/outline'

// Components
import StudentList from './StudentList.vue'
import ToastMessage from './ToastMessage.vue'
import ActionButtons from './ActionButtons.vue'
import ConfirmationModal from './ConfirmationModal.vue'

const router = useRouter()
const props = defineProps({
  selectedGroup: String
})

// Reactive state
const students = ref([])
const presentStudents = ref([])
const loading = ref(true)
const showModal = ref(false)
const submitting = ref(false)

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
  return availableStudents.value.length > 0
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
    // Default all available students to present
    presentStudents.value = availableStudents.value.map(student => student.student)
    
  } catch (error) {
    console.error('Error fetching attendance:', error)
    showToast('error', 'Load Failed', 'Failed to load student data.')
  } finally {
    loading.value = false
  }
}

// Toggle all students
const toggleAllStudents = () => {
  if (allStudentsMarked.value) return
  if (presentStudents.value.length === availableStudents.value.length) {
    presentStudents.value = []
  } else {
    presentStudents.value = availableStudents.value.map(student => student.student)
  }
}

// Toggle student selection
const toggleStudent = (studentId) => {
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
}

// Handle back to dashboard
const handleBack = () => {
  router.push({ name: 'Teacherhome' })
}

// Handle submit
const handleSubmit = () => {
  if (presentStudents.value.length === 0) {
    showToast('error', 'Selection Required', 'Please select at least one student as present.')
    return
  }
  showModal.value = true
}

// Confirm action
const confirmAction = async () => {
  showModal.value = false
  submitting.value = true

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