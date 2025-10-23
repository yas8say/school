<template>
  <div 
    class="bg-white rounded-lg shadow-sm p-4 border-2 transition-colors cursor-pointer"
    :class="isPresent ? 'border-green-500 bg-green-50' : 'border-gray-200'"
    @click="$emit('toggle-attendance', student.student)"
  >
    <div class="flex items-center space-x-4">
      <div class="w-12 h-12 rounded-full bg-gray-200 overflow-hidden flex items-center justify-center">
        <img
          v-if="student.base64profile"
          :src="`data:image/jpeg;base64,${student.base64profile}`"
          alt="Student"
          class="object-cover w-full h-full"
        />
        <span v-else class="text-xs text-gray-500">No Image</span>
      </div>
      <div class="flex-1">
        <h3 class="font-medium text-gray-800">{{ student.student_name }}</h3>
        <p class="text-sm text-gray-600">Roll No: {{ student.group_roll_number }}</p>
      </div>
      <div class="w-6 h-6 rounded-full border-2 flex items-center justify-center"
        :class="isPresent ? 'bg-green-500 border-green-500' : 'border-gray-300'">
        <CheckIcon v-if="isPresent" class="w-4 h-4 text-white" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { CheckIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  student: Object,
  presentStudents: Array
})

defineEmits(['toggle-attendance'])

const isPresent = computed(() => props.presentStudents.includes(props.student.student))
</script>