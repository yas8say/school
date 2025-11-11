<template>
  <div class="space-y-3">
    <!-- Header Stats -->
    <div class="flex justify-between items-center mb-4">
      <p class="text-sm text-gray-600">
        <slot name="header-stats">
          Total: {{ students.length }}
        </slot>
      </p>
      
      <button
        @click="$emit('toggle-all')"
        class="px-3 py-1 text-sm bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
        :disabled="disabled"
      >
        <slot name="toggle-button-text">
          {{ isAllSelected ? 'Deselect All' : 'Select All' }}
        </slot>
      </button>
    </div>

    <!-- Already Marked Students (for attendance) -->
    <template v-if="showMarkedStudents && markedStudents.length > 0">
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

    <!-- Available Students -->
    <div 
      v-for="student in availableStudents" 
      :key="student.student"
      class="bg-white rounded-lg shadow-sm p-4 border-2 transition-colors cursor-pointer hover:border-blue-300"
      :class="getStudentCardClass(student)"
      @click="$emit('student-toggle', student.student)"
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
            <span v-if="promotionInfo && isStudentSelected(student)" 
                  class="ml-2 text-xs text-green-600 font-semibold">
              {{ promotionInfo }}
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

    <!-- Empty State -->
    <div v-if="students.length === 0" class="text-center py-8">
      <p class="text-gray-600">No students available</p>
      <slot name="empty-state-action">
        <button 
          @click="$emit('reload')"
          class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Try Again
        </button>
      </slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { CheckIcon, ClockIcon, MinusIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  students: {
    type: Array,
    default: () => []
  },
  selectedStudents: {
    type: Array,
    default: () => []
  },
  mode: {
    type: String,
    default: 'attendance'
  },
  showMarkedStudents: {
    type: Boolean,
    default: false
  },
  markedStudents: {
    type: Array,
    default: () => []
  },
  availableStudents: {
    type: Array,
    default: () => []
  },
  disabled: {
    type: Boolean,
    default: false
  },
  promotionInfo: {
    type: String,
    default: ''
  },
  selectedGroup: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['student-toggle', 'toggle-all', 'reload'])

const isAllSelected = computed(() => {
  return props.selectedStudents.length === props.availableStudents.length
})

const isStudentSelected = (student) => {
  return props.selectedStudents.includes(student.student)
}

const getStudentCardClass = (student) => {
  if (isStudentSelected(student)) {
    return 'border-green-500 bg-green-50'
  }
  return 'border-gray-200'
}

const getCheckboxClass = (student) => {
  return isStudentSelected(student) 
    ? 'bg-green-500 border-green-500' 
    : 'border-gray-300'
}

const extractAcademicYear = (groupName) => {
  if (!groupName) return 'N/A'
  const match = groupName.match(/\(([^)]+)\)/)
  return match ? match[1] : 'N/A'
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
</script>