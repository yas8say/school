<template>
  <div class="app-container">
    <MultiStepForm />
  </div>
</template>

<script>
import MultiStepForm from '../components/MultiStepForm.vue';

export default {
  components: {
    MultiStepForm
  }
}
</script>

<style>
/* Global styles can go here */
.app-container {
  width: 100%;
  margin: 0;
  padding: 0;
  min-height: 100vh;
  background: #f8fafc;
}
</style>