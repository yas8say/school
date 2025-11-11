<template>
  <div class="flex items-center space-x-4">
    <!-- Student Avatar -->
    <div class="flex-shrink-0">
      <div class="w-12 h-12 rounded-full flex items-center justify-center text-white font-semibold text-sm relative overflow-hidden"
          :class="avatarClass">
        <img
          v-if="student.img_url"
          :src="getProfileImageUrl(student.img_url)"
          alt="Student"
          class="absolute inset-0 w-full h-full object-cover"
          :class="{ 'opacity-70': disabled }"
          @error="handleImageError"
          loading="lazy"
        />
        <span v-else class="text-white text-sm font-medium" :class="{ 'opacity-70': disabled }">
          {{ getInitials(student.student_name) }}
        </span>
      </div>
    </div>
    
    <!-- Student Info -->
    <div class="flex-1 min-w-0">
      <h3 class="font-medium text-gray-800 truncate" :class="{ 'text-gray-500': disabled }">
        {{ student.student_name }}
      </h3>
      <div class="flex items-center space-x-4 text-sm" :class="disabled ? 'text-gray-500' : 'text-gray-600'">
        <span>Roll No: {{ student.group_roll_number }}</span>
        <span class="text-gray-400">•</span>
        <span class="truncate">{{ student.student }}</span>
      </div>
      
      <!-- Status for marked students -->
      <div v-if="showStatus" class="flex items-center space-x-2 mt-1">
        <CheckIcon v-if="student.present === 1" class="w-4 h-4 text-green-500" />
        <ClockIcon v-if="student.on_leave === 1" class="w-4 h-4 text-yellow-500" />
        <span class="text-xs font-medium" :class="getStatusClass(student)">
          {{ getStatusText(student) }}
        </span>
      </div>
      
      <!-- Additional Info Slot -->
      <div v-if="additionalInfo" class="mt-1">
        <span class="text-xs" :class="disabled ? 'text-gray-500' : 'text-gray-600'">
          {{ additionalInfo }}
        </span>
      </div>
      
      <!-- Promotion Info -->
      <div v-if="mode === 'promotion' && selected && promotionInfo" class="mt-1">
        <span class="text-xs text-green-600 font-semibold">
          {{ promotionInfo }}
        </span>
      </div>
    </div>
    
    <!-- Checkbox -->
    <div v-if="!disabled" class="flex-shrink-0">
      <div class="w-6 h-6 rounded-full border-2 flex items-center justify-center"
        :class="checkboxClass">
        <CheckIcon v-if="selected" class="w-4 h-4 text-white" />
      </div>
    </div>
    
    <!-- Status Icon for disabled cards -->
    <div v-else class="flex-shrink-0">
      <div class="w-6 h-6 rounded-full border-2 flex items-center justify-center"
          :class="statusIconClass">
        <CheckIcon v-if="student.present === 1" class="w-4 h-4 text-white" />
        <MinusIcon v-if="student.on_leave === 1" class="w-4 h-4 text-white" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { CheckIcon, ClockIcon, MinusIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  student: {
    type: Object,
    required: true
  },
  selected: {
    type: Boolean,
    default: false
  },
  mode: {
    type: String,
    default: 'attendance'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  showStatus: {
    type: Boolean,
    default: false
  },
  additionalInfo: {
    type: String,
    default: null
  },
  promotionInfo: {
    type: String,
    default: null
  }
})

const avatarClass = computed(() => {
  if (props.disabled) {
    return props.student.present === 1 
      ? 'bg-gradient-to-br from-green-400 to-green-500' 
      : 'bg-gradient-to-br from-yellow-400 to-yellow-500'
  }
  return props.mode === 'attendance' 
    ? 'bg-gradient-to-br from-blue-500 to-purple-600' 
    : 'bg-gradient-to-br from-green-500 to-green-600'
})

const checkboxClass = computed(() => {
  return props.selected 
    ? 'bg-green-500 border-green-500' 
    : 'border-gray-300'
})

const statusIconClass = computed(() => {
  return props.student.present === 1 
    ? 'bg-green-500 border-green-500' 
    : 'bg-yellow-500 border-yellow-500'
})

const getStatusClass = (student) => {
  if (student.present === 1) return 'text-green-600'
  if (student.on_leave === 1) return 'text-yellow-600'
  return 'text-gray-600'
}

const getStatusText = (student) => {
  if (student.present === 1) return 'Already Marked Present'
  if (student.on_leave === 1) return 'On Leave'
  return 'Available'
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