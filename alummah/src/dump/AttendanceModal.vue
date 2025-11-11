<template>
  <div v-if="visible" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-6 max-w-sm w-full mx-4">
      <h3 class="text-lg font-semibold text-gray-800 mb-4">Confirm Attendance</h3>
      <p class="text-gray-600 mb-2">Present: {{ presentStudents.length }}</p>
      <p class="text-gray-600 mb-6">Absent: {{ totalStudents - presentStudents.length }}</p>
      <div class="flex space-x-3">
        <button
          @click="$emit('cancel')"
          class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          @click="$emit('confirm')"
          class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Confirm
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  visible: Boolean,
  presentStudents: Array,
  totalStudents: Number
})

defineEmits(['confirm', 'cancel'])
</script>