<template>
  <div v-if="show" 
       :class="[
         'fixed top-4 right-4 z-50 max-w-sm p-4 rounded-lg shadow-lg border-l-4 transition-all duration-300',
         type === 'success' 
           ? 'bg-green-50 border-green-500 text-green-800' 
           : 'bg-red-50 border-red-500 text-red-800'
       ]">
    <div class="flex items-start">
      <div class="flex-shrink-0">
        <CheckCircleIcon v-if="type === 'success'" class="w-5 h-5 text-green-500" />
        <XCircleIcon v-else class="w-5 h-5 text-red-500" />
      </div>
      <div class="ml-3 flex-1">
        <p class="text-sm font-medium">{{ title }}</p>
        <p class="text-sm mt-1">{{ message }}</p>
      </div>
      <button @click="$emit('close')" class="ml-4 flex-shrink-0 text-gray-400 hover:text-gray-600">
        <XMarkIcon class="w-4 h-4" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { CheckCircleIcon, XCircleIcon, XMarkIcon } from '@heroicons/vue/24/outline'

defineProps({
  show: Boolean,
  type: {
    type: String,
    default: 'success'
  },
  title: String,
  message: String
})

defineEmits(['close'])
</script>