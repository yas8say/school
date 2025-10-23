<template>
  <div class="bg-white rounded-lg shadow-sm p-6">
    <div class="flex items-center mb-4">
      <button 
        @click="$emit('back-to-dashboard')"
        class="flex items-center space-x-2 text-blue-600 hover:text-blue-800 mr-4"
      >
        <ArrowLeftIcon class="w-5 h-5" />
        <span>Back to Dashboard</span>
      </button>
      <h1 class="text-2xl font-bold text-gray-800">{{ pageTitle }}</h1>
    </div>
    <p class="text-gray-600 mb-4">For class: {{ selectedGroup || 'Not selected' }}</p>
    <div class="mt-4 p-4 bg-yellow-100 border border-yellow-400 text-yellow-700 rounded">
      {{ pageTitle }} functionality is under development.
    </div>
  </div>
</template>

<script setup>
import { ArrowLeftIcon } from '@heroicons/vue/24/outline'
import { computed } from 'vue'

defineProps({
  selectedGroup: String
})

defineEmits(['back-to-dashboard'])

const pageTitle = computed(() => {
  const titles = {
    'Attendance': 'Take Attendance',
    'AttendanceRecord': 'Student Attendance Record',
    'CreateNotice': 'Create Notice', 
    'PreviousNotices': 'Previous Notices',
    'LeaveAppeals': 'Browse Leave Appeals'
  }
  return titles['LeaveAppeals'] || 'LeaveAppeals'
})
</script>
