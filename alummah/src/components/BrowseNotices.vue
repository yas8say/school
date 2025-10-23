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
    <p class="text-gray-600 mb-4" v-if="selectedStudent">
      For child: {{ selectedStudent.student_name }} ({{ selectedStudent.student_group || 'No class' }})
    </p>
    <div class="mt-4 p-4 bg-yellow-100 border border-yellow-400 text-yellow-700 rounded">
      {{ pageTitle }} functionality is under development.
    </div>
  </div>
</template>

<script setup>
import { ArrowLeftIcon } from '@heroicons/vue/24/outline'
import { computed } from 'vue'

defineProps({
  selectedStudent: Object
})

defineEmits(['back-to-dashboard'])

const pageTitle = computed(() => {
  const titles = {
    'BrowseNotices': 'Browse Notices',
    'AppealLeave': 'Appeal Leave'
  }
  return titles['BrowseNotices'] || 'BrowseNotices'
})
</script>
