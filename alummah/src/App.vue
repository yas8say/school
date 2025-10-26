<template>
  <div id="app">
    <router-view />
    <UniversalPopup />
  </div>
</template>

<script setup>
import UniversalPopup from '@/components/UniversalPopup.vue' // Renamed from CSRFErrorPopup
</script>