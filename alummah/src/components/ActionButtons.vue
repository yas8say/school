<template>
  <div class="flex space-x-4 mt-6">
    <button
      @click="$emit('cancel')"
      class="flex-1 px-4 py-3 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors flex items-center justify-center space-x-2"
    >
      <XMarkIcon class="w-5 h-5" />
      <span>Cancel</span>
    </button>

    <button
      @click="$emit('submit')"
      :disabled="submitting || !canSubmit"
      :class="[
        'flex-1 px-4 py-3 text-white rounded-lg font-medium transition-colors flex items-center justify-center space-x-2',
        submitting || !canSubmit 
          ? 'bg-gray-400 cursor-not-allowed' 
          : mode === 'attendance' 
            ? 'bg-blue-600 hover:bg-blue-700' 
            : 'bg-green-600 hover:bg-green-700'
      ]"
    >
      <ArrowRightIcon class="w-5 h-5" />
      <span>{{ submitButtonText }}</span>
    </button>
  </div>
</template>

<script setup>
import { XMarkIcon, ArrowRightIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  mode: {
    type: String,
    default: 'attendance'
  },
  submitting: {
    type: Boolean,
    default: false
  },
  canSubmit: {
    type: Boolean,
    default: false
  }
})

defineEmits(['cancel', 'submit'])

const submitButtonText = props.submitting 
  ? (props.mode === 'attendance' ? 'Submitting...' : 'Promoting...')
  : (props.mode === 'attendance' ? 'Submit' : 'Promote Students')
</script>