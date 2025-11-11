<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
      <h3 class="text-lg font-semibold text-gray-800 mb-4">
        {{ getModalTitle }}
      </h3>
      
      <!-- Remove Courses Mode -->
      <template v-if="mode === 'remove-courses'">
        <div class="space-y-3 mb-4">
          <div class="flex justify-between">
            <span class="text-gray-600">Courses to Remove:</span>
            <span class="font-semibold text-red-600">{{ selectedCourses.length }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Affected Students:</span>
            <span class="font-semibold">{{ affectedStudents.length }}</span>
          </div>
          
          <!-- Course List -->
          <div v-if="selectedCourses.length > 0" class="mt-3">
            <p class="text-sm font-medium text-gray-700 mb-2">Selected Courses:</p>
            <div class="max-h-32 overflow-y-auto space-y-1 border border-gray-200 rounded p-2">
              <div 
                v-for="courseId in selectedCourses" 
                :key="courseId"
                class="text-sm text-gray-600 bg-gray-50 px-2 py-1 rounded flex items-center justify-between"
              >
                <span>{{ getCourseName(courseId) }}</span>
                <span class="text-xs text-gray-500">{{ courseId }}</span>
              </div>
            </div>
          </div>

          <!-- Action Type Info -->
          <div class="text-sm text-blue-600 bg-blue-50 p-3 rounded border border-blue-200">
            <p class="font-medium">
              {{ actionType === 'global' ? 'Global Removal' : 'Individual Removal' }}
            </p>
            <p class="mt-1">
              {{ actionType === 'global' 
                ? 'This will remove the selected courses from ALL students in the class.' 
                : 'This will remove courses from specific students only.' 
              }}
            </p>
          </div>

          <!-- Warning -->
          <div class="text-sm text-yellow-600 bg-yellow-50 p-3 rounded border border-yellow-200">
            <p class="font-medium">Warning</p>
            <p class="mt-1">
              This action cannot be undone. Students will lose access to the selected courses.
            </p>
          </div>
        </div>
      </template>
      
      <!-- ... existing attendance and promotion modes ... -->
      
      <div class="flex space-x-3 pt-4 border-t border-gray-200">
        <button
          @click="$emit('cancel')"
          class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
        >
          Cancel
        </button>
        <button
          @click="$emit('confirm')"
          :class="[
            'flex-1 px-4 py-2 text-white rounded-lg font-medium transition-colors',
            getConfirmButtonClass
          ]"
        >
          {{ getConfirmButtonText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  mode: {
    type: String,
    default: 'attendance'
  },
  // ... existing props ...
  // Add new props for remove-courses mode
  selectedCourses: {
    type: Array,
    default: () => []
  },
  affectedStudents: {
    type: Array,
    default: () => []
  },
  actionType: {
    type: String,
    default: 'global'
  },
  availableCourses: {
    type: Array,
    default: () => []
  }
})

defineEmits(['confirm', 'cancel'])

const getModalTitle = computed(() => {
  switch (props.mode) {
    case 'remove-courses':
      return 'Confirm Course Removal'
    case 'attendance':
      return 'Confirm Attendance'
    case 'promotion':
      return 'Confirm Promotion'
    default:
      return 'Confirm Action'
  }
})

const getConfirmButtonClass = computed(() => {
  switch (props.mode) {
    case 'remove-courses':
      return 'bg-red-600 hover:bg-red-700'
    case 'attendance':
      return 'bg-blue-600 hover:bg-blue-700'
    case 'promotion':
      return 'bg-green-600 hover:bg-green-700'
    default:
      return 'bg-blue-600 hover:bg-blue-700'
  }
})

const getConfirmButtonText = computed(() => {
  switch (props.mode) {
    case 'remove-courses':
      return 'Remove Courses'
    case 'attendance':
      return 'Confirm Attendance'
    case 'promotion':
      return 'Promote Students'
    default:
      return 'Confirm'
  }
})

const getCourseName = (courseId) => {
  const course = props.availableCourses.find(c => c.course === courseId)
  return course ? course.course_name : courseId
}
</script>