<template>
  <div class="min-h-screen bg-gray-50 p-4">
    <!-- Header -->
    <div class="mb-6">
      <div class="flex justify-between items-start">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">Remove Courses from Students</h1>
          <p class="text-gray-600" v-if="programInfo.program_name">
            Remove courses from students in {{ programInfo.program_name }}
          </p>
          <p class="text-sm text-gray-500 mt-1" v-if="selectedGroup">Current Class: {{ selectedGroup }}</p>
          <p class="text-sm text-gray-500">Total Students: {{ students.length }}</p>
          <p class="text-sm text-gray-500" v-if="programInfo.program_name">
            Program: {{ programInfo.program_name }}
          </p>
        </div>
        
        <!-- Selection Stats -->
        <div class="text-right">
          <p class="text-sm font-medium text-gray-600">
            {{ currentActionType === 'global' ? 'Global Selection' : 'Individual Selection' }}
          </p>
          <p class="text-2xl font-bold text-red-600">{{ totalSelectedCoursesCount }}</p>
          <p class="text-xs text-gray-500">
            {{ totalSelectedStudentsCount }} students, {{ totalSelectedCoursesCount }} courses
          </p>
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
      <span class="ml-2 text-gray-600">Loading students and courses...</span>
    </div>

    <!-- Error State - No Program -->
    <div v-else-if="!programInfo.program" class="text-center py-8">
      <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-6 max-w-md mx-auto">
        <ExclamationTriangleIcon class="w-12 h-12 text-yellow-500 mx-auto mb-4" />
        <h3 class="text-lg font-semibold text-yellow-800 mb-2">No Program Found</h3>
        <p class="text-yellow-700 mb-4">
          The selected student group is not associated with any program. 
          Course removal is only available for student groups with assigned programs.
        </p>
      </div>
    </div>

    <!-- Error State - No Courses -->
    <div v-else-if="availableCourses.length === 0" class="text-center py-8">
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-6 max-w-md mx-auto">
        <InformationCircleIcon class="w-12 h-12 text-blue-500 mx-auto mb-4" />
        <h3 class="text-lg font-semibold text-blue-800 mb-2">No Courses Available</h3>
        <p class="text-blue-700 mb-4">
          There are no courses assigned to this program. 
          Please add courses to the program before using this feature.
        </p>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="space-y-6">
      <!-- Global Course Selection -->
      <div class="bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">Remove Courses from All Students</h2>
        <p class="text-sm text-gray-600 mb-4">Select courses to remove from all students in this class:</p>
        
        <!-- Course Selection Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mb-4">
          <div 
            v-for="course in availableCourses" 
            :key="course.course"
            class="flex items-center p-3 border border-gray-300 rounded-lg cursor-pointer hover:border-blue-500 transition-colors"
            :class="globalSelectedCourses.includes(course.course) ? 'bg-blue-50 border-blue-500' : 'bg-white'"
            @click="toggleGlobalCourse(course.course)"
          >
            <div class="flex items-center space-x-3 flex-1">
              <div class="w-4 h-4 rounded border-2 flex items-center justify-center flex-shrink-0"
                  :class="globalSelectedCourses.includes(course.course) ? 'bg-blue-500 border-blue-500' : 'border-gray-300'">
                <CheckIcon v-if="globalSelectedCourses.includes(course.course)" class="w-3 h-3 text-white" />
              </div>
              <div class="flex-1 min-w-0">
                <h3 class="font-medium text-gray-800 text-sm">{{ course.course_name }}</h3>
                <p class="text-xs text-gray-500">{{ course.course }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Global Action Buttons -->
        <div class="flex space-x-3">
          <button
            @click="selectAllGlobalCourses"
            class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors text-sm"
          >
            Select All Courses
          </button>
          <button
            @click="clearAllGlobalCourses"
            class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors text-sm"
          >
            Clear All
          </button>
        </div>
      </div>

      <!-- Individual Student Course Management -->
      <div class="bg-white rounded-lg shadow-sm p-4">
        <h2 class="text-lg font-semibold text-gray-800 mb-3">Student Course Selections</h2>
        <p class="text-sm text-gray-600 mb-3">Select courses to remove from individual students:</p>

        <!-- Student List with Course Selection -->
        <div class="space-y-3">
          <div 
            v-for="student in students" 
            :key="student.student"
            class="border border-gray-200 rounded-lg p-3 hover:border-gray-300 transition-colors"
          >
            <!-- Student Header -->
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center space-x-3">
                <div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold text-xs relative overflow-hidden">
                  <img
                    v-if="student.img_url"
                    :src="getProfileImageUrl(student.img_url)"
                    alt="Student"
                    class="absolute inset-0 w-full h-full object-cover"
                    @error="handleImageError"
                  />
                  <span v-else class="text-white text-xs font-medium">
                    {{ getInitials(student.student_name) }}
                  </span>
                </div>
                <div class="min-w-0">
                  <h3 class="font-medium text-gray-800 text-sm leading-tight">{{ student.student_name }}</h3>
                  <p class="text-xs text-gray-500">Roll No: {{ student.group_roll_number }}</p>
                </div>
              </div>
              <div class="text-right">
                <p class="text-xs font-medium" 
                   :class="getStudentSelectedCourses(student.student).length > 0 ? 'text-red-600' : 'text-gray-500'">
                  {{ getStudentSelectedCourses(student.student).length }} selected
                </p>
              </div>
            </div>

            <!-- Course Selection for Student - Single Row -->
            <div class="flex flex-wrap gap-1">
              <div 
                v-for="course in student.courses" 
                :key="course.course"
                class="flex items-center px-2 py-1 border border-gray-200 rounded cursor-pointer hover:border-red-300 transition-colors text-xs"
                :class="getStudentSelectedCourses(student.student).includes(course.course) ? 'bg-red-50 border-red-500' : 'bg-white'"
                @click="toggleStudentCourse(student.student, course.course)"
              >
                <div class="flex items-center space-x-1">
                  <div class="w-3 h-3 rounded border flex items-center justify-center flex-shrink-0"
                      :class="getStudentSelectedCourses(student.student).includes(course.course) ? 'bg-red-500 border-red-500' : 'border-gray-300'">
                    <MinusIcon v-if="getStudentSelectedCourses(student.student).includes(course.course)" class="w-2 h-2 text-white" />
                  </div>
                  <span class="text-gray-800 whitespace-nowrap">{{ course.course_name }}</span>
                </div>
              </div>
              
              <!-- Show message if student has no courses -->
              <div v-if="student.courses.length === 0" class="text-xs text-gray-500 italic px-2 py-1">
                No courses enrolled
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Action Button -->
      <div class="bg-white rounded-lg shadow-sm p-6">
        <div class="flex justify-between items-center">
          <div>
            <h3 class="text-lg font-semibold text-gray-800">Remove Selected Courses</h3>
            <p class="text-sm text-gray-600">
              {{ getActionDescription }}
            </p>
          </div>
          <button
            @click="handleRemoveCourses"
            :disabled="!canRemoveCourses || submitting"
            :class="[
              'px-6 py-3 text-white rounded-lg font-medium transition-colors text-sm',
              !canRemoveCourses || submitting
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-red-600 hover:bg-red-700'
            ]"
          >
            {{ getRemoveButtonText }}
          </button>
        </div>
      </div>
    </div>

    <!-- Confirmation Modal -->
    <ConfirmationModal
      v-if="showModal"
      mode="remove-courses"
      :selected-courses="currentActionCourses"
      :affected-students="currentActionStudents"
      :action-type="currentActionType"
      :available-courses="availableCourses"
      @confirm="confirmRemoveCourses"
      @cancel="showModal = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { createResource } from 'frappe-ui'
import { 
  CheckIcon, 
  MinusIcon, 
  ExclamationTriangleIcon,
  InformationCircleIcon 
} from '@heroicons/vue/24/outline'

// Components
import ToastMessage from './ToastMessage.vue'
import ConfirmationModal from './ConfirmationModal.vue'

const router = useRouter()
const props = defineProps({
  selectedGroup: String
})

// Reactive state
const students = ref([])
const availableCourses = ref([])
const programInfo = ref({
  program: null,
  program_name: null
})
const loading = ref(true)
const showModal = ref(false)
const submitting = ref(false)

// Course selection state
const globalSelectedCourses = ref([])
const studentCourseSelections = ref({})

// Current action state for confirmation modal
const currentActionCourses = ref([])
const currentActionStudents = ref([])
const currentActionType = ref('global') // 'global' or 'individual'

// Toast notification
const toast = ref({
  show: false,
  type: 'success',
  title: '',
  message: ''
})

// Computed properties
const hasGlobalSelections = computed(() => {
  return globalSelectedCourses.value.length > 0
})

const hasIndividualSelections = computed(() => {
  return Object.values(studentCourseSelections.value).some(courses => courses.length > 0)
})

const totalSelectedStudentsCount = computed(() => {
  if (currentActionType.value === 'global') {
    return students.value.length
  } else {
    return Object.entries(studentCourseSelections.value).filter(([_, courses]) => courses.length > 0).length
  }
})

const totalSelectedCoursesCount = computed(() => {
  if (currentActionType.value === 'global') {
    return globalSelectedCourses.value.length
  } else {
    let count = 0
    Object.values(studentCourseSelections.value).forEach(courses => {
      count += courses.length
    })
    return count
  }
})

const canRemoveCourses = computed(() => {
  return hasGlobalSelections.value || hasIndividualSelections.value
})

const getActionDescription = computed(() => {
  if (hasGlobalSelections.value && hasIndividualSelections.value) {
    return `Removing ${globalSelectedCourses.value.length} courses from all students and individual selections from ${totalSelectedStudentsCount.value - students.value.length} students`
  } else if (hasGlobalSelections.value) {
    return `Removing ${globalSelectedCourses.value.length} courses from all ${students.value.length} students`
  } else if (hasIndividualSelections.value) {
    return `Removing selected courses from ${totalSelectedStudentsCount.value} students`
  } else {
    return 'Select courses to remove from students'
  }
})

const getRemoveButtonText = computed(() => {
  if (submitting.value) {
    return 'Removing Courses...'
  }
  
  if (hasGlobalSelections.value && hasIndividualSelections.value) {
    return `Remove Courses (${totalSelectedCoursesCount.value} from ${totalSelectedStudentsCount.value} students)`
  } else if (hasGlobalSelections.value) {
    return `Remove from All Students (${globalSelectedCourses.value.length})`
  } else if (hasIndividualSelections.value) {
    return `Remove from ${totalSelectedStudentsCount.value} Students (${totalSelectedCoursesCount.value})`
  } else {
    return 'Remove Courses'
  }
})

// Watch for global course selection changes and update all students
watch(globalSelectedCourses, (newGlobalSelection) => {
  // Update all students with the global selection, but only for courses they have
  students.value.forEach(student => {
    const studentCourseCodes = student.courses.map(c => c.course)
    // Only include global selections that this student actually has
    studentCourseSelections.value[student.student] = newGlobalSelection.filter(
      course => studentCourseCodes.includes(course)
    )
  })
}, { deep: true })

// API Resources
const attendanceResource = createResource({
  url: 'school.al_ummah.api2.get_student_attendance_records',
  onSuccess(data) {
    console.log('Student and course data loaded:', data)
    return data
  },
  onError(error) {
    console.error('Error fetching student data:', error)
    showToast('error', 'Load Failed', 'Failed to load student and course data. Please check your connection and try again.')
  }
})

const removeCoursesResource = createResource({
  url: 'school.al_ummah.api2.remove_courses_from_students',
  onSuccess(data) {
    console.log('Courses removed successfully:', data)
    submitting.value = false
    handleSuccessResponse(data, 'Courses removed successfully!')
  },
  onError(error) {
    console.error('Error removing courses:', error)
    submitting.value = false
    handleErrorResponse(error, 'remove courses')
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
    // Refresh data after successful removal
    setTimeout(() => {
      fetchStudentData()
    }, 2000)
  } else {
    showToast('success', 'Success!', defaultMessage)
    setTimeout(() => {
      fetchStudentData()
    }, 2000)
  }
}

const handleErrorResponse = (error, operationType) => {
  if (error.exc_type === 'PermissionError') {
    showToast('error', 'Permission Denied', `You do not have permission to ${operationType}. Please contact your administrator.`)
  } else if (error.messages && error.messages.length > 0) {
    showToast('error', 'Operation Failed', error.messages[0])
  } else if (error.message) {
    showToast('error', 'Operation Failed', error.message)
  } else {
    showToast('error', 'Operation Failed', `Failed to ${operationType}. Please check your connection and try again.`)
  }
}

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

// Fetch student and course data
const fetchStudentData = async () => {
  loading.value = true
  try {
    const group = props.selectedGroup || localStorage.getItem('selected_student_group')
    if (!group) {
      showToast('error', 'Selection Required', 'Please select a class first.')
      loading.value = false
      return
    }

    const params = { 
      based_on: 'Batch', 
      student_group: group,
      get_courses: true
    }    
    const response = await attendanceResource.fetch(params)

    // Handle both response formats
    let studentList = []
    if (Array.isArray(response)) {
      studentList = response
    } else if (response && response.students) {
      studentList = response.students
      programInfo.value = {
        program: response.program,
        program_name: response.program_name
      }
      availableCourses.value = response.courses || []
    }

    if (!studentList || studentList.length === 0) {
      showToast('error', 'No Students', 'No students found for this class.')
      students.value = []
      availableCourses.value = []
      return
    }

    students.value = studentList

    // Initialize student course selections
    initializeStudentSelections()

    console.log('Loaded data:', {
      program: programInfo.value,
      students: students.value.length,
      courses: availableCourses.value.length
    })
    
  } catch (error) {
    console.error('Error fetching student data:', error)
    showToast('error', 'Load Failed', 'Failed to load student data.')
  } finally {
    loading.value = false
  }
}

// Initialize student course selections
const initializeStudentSelections = () => {
  studentCourseSelections.value = {}
  students.value.forEach(student => {
    studentCourseSelections.value[student.student] = []
  })
}

// Get selected courses for a student
const getStudentSelectedCourses = (studentId) => {
  return studentCourseSelections.value[studentId] || []
}

// Global course selection
const toggleGlobalCourse = (courseId) => {
  const index = globalSelectedCourses.value.indexOf(courseId)
  if (index > -1) {
    globalSelectedCourses.value.splice(index, 1)
  } else {
    globalSelectedCourses.value.push(courseId)
  }
}

const selectAllGlobalCourses = () => {
  globalSelectedCourses.value = availableCourses.value.map(course => course.course)
}

const clearAllGlobalCourses = () => {
  globalSelectedCourses.value = []
}

// Individual student course selection
const toggleStudentCourse = (studentId, courseId) => {
  const student = students.value.find(s => s.student === studentId)
  if (!student) return
  
  // Check if student actually has this course
  const studentHasCourse = student.courses.some(c => c.course === courseId)
  if (!studentHasCourse) return
  
  if (!studentCourseSelections.value[studentId]) {
    studentCourseSelections.value[studentId] = []
  }
  
  const index = studentCourseSelections.value[studentId].indexOf(courseId)
  if (index > -1) {
    studentCourseSelections.value[studentId].splice(index, 1)
  } else {
    studentCourseSelections.value[studentId].push(courseId)
  }
}

// Main remove courses handler
const handleRemoveCourses = () => {
  if (!canRemoveCourses.value) {
    showToast('error', 'Selection Required', 'Please select courses to remove.')
    return
  }

  // Determine action type and prepare data
  if (hasGlobalSelections.value && hasIndividualSelections.value) {
    // Combined action - global + individual
    currentActionType.value = 'combined'
    
    // Get all unique courses from both global and individual selections
    const allCourses = new Set([...globalSelectedCourses.value])
    Object.values(studentCourseSelections.value).forEach(courses => {
      courses.forEach(course => allCourses.add(course))
    })
    currentActionCourses.value = Array.from(allCourses)
    
    // All students are affected in combined mode
    currentActionStudents.value = students.value.map(student => student.student)
    
  } else if (hasGlobalSelections.value) {
    // Global action only
    currentActionType.value = 'global'
    currentActionCourses.value = globalSelectedCourses.value
    currentActionStudents.value = students.value.map(student => student.student)
    
  } else {
    // Individual action only
    currentActionType.value = 'individual'
    
    // Get all unique courses from individual selections
    const allCourses = new Set()
    Object.values(studentCourseSelections.value).forEach(courses => {
      courses.forEach(course => allCourses.add(course))
    })
    currentActionCourses.value = Array.from(allCourses)
    
    // Get students with selections
    currentActionStudents.value = Object.entries(studentCourseSelections.value)
      .filter(([_, courses]) => courses.length > 0)
      .map(([studentId]) => studentId)
  }

  showModal.value = true
}

// Confirm and execute course removal
const confirmRemoveCourses = async () => {
  showModal.value = false
  submitting.value = true

  try {
    let studentsToUpdate = []

    if (currentActionType.value === 'global' || currentActionType.value === 'combined') {
      // For global and combined actions, remove selected courses from all students
      studentsToUpdate = students.value.map(student => ({
        student: student.student,
        student_name: student.student_name,
        courses: currentActionCourses.value
      }))
    } else {
      // For individual action, remove only from selected students
      studentsToUpdate = currentActionStudents.value.map(studentId => {
        const student = students.value.find(s => s.student === studentId)
        return {
          student: studentId,
          student_name: student?.student_name || 'Unknown',
          courses: studentCourseSelections.value[studentId] || []
        }
      })
    }

    console.log('Removing courses:', {
      actionType: currentActionType.value,
      students: studentsToUpdate,
      program: programInfo.value
    })

    await removeCoursesResource.submit({
      students: JSON.stringify(studentsToUpdate),
      program_id: programInfo.value.program,
      student_group: props.selectedGroup || localStorage.getItem('selected_student_group')
    })

    // Reset selections after successful removal
    clearAllSelections()

  } catch (error) {
    console.error('Error in course removal:', error)
    submitting.value = false
  }
}

// Clear all selections
const clearAllSelections = () => {
  globalSelectedCourses.value = []
  students.value.forEach(student => {
    studentCourseSelections.value[student.student] = []
  })
}

// Load data on mount
onMounted(() => {
  fetchStudentData()
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