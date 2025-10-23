<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">{{ pageTitle }}</h1>
    <div class="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded">
      <p>{{ pageName }} functionality is under development.</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const pageName = 'AppealLeave'
const pageTitle = computed(() => {
  const titles = {
    'Studentinfo2': 'Student Information',
    'AppealLeave': 'Appeal Leave'
  }
  return titles[pageName] || pageName
})
</script>
