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
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
  }
  </style>