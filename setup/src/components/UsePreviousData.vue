<template>
  <div class="card">
    <h3 class="section-title">Use Previous Data</h3>
    
    <div v-if="loading" class="loading">Loading previous data...</div>
    <div v-else>
      <!-- Success Message -->
      <div 
        v-if="showSuccessMessage" 
        class="success-message"
      >
        ✓ Previous data from {{ usedPreviousYear }} has been successfully loaded
      </div>

      <div class="field">
        <select v-model="selectedPreviousData">
          <option :value="null">Select a year</option>
          <option 
            v-for="(data, index) in previousDataList" 
            :key="index"
            :value="data"
          >
            {{ data.academicYear }}
          </option>
        </select>
      </div>

      <button 
        @click="handleUsePreviousData"
        :disabled="!selectedPreviousData"
      >
        Use Previous Data
      </button>
      
      <div class="switch-container">
        <label>Don't create classes</label>
        <input 
          type="checkbox" 
          v-model="dontCreateClasses"
          @change="updateDontCreateClasses"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  props: {
    values: Object,
    previousDataList: Array
  },
  emits: ['update-field', 'use-previous-data'],
  setup(props, { emit }) {
    const loading = ref(false)
    const selectedPreviousData = ref(null)
    const dontCreateClasses = ref(props.values.dontCreateClasses || false)
    const showSuccessMessage = ref(false)
    const usedPreviousYear = ref('')

    const handleUsePreviousData = () => {
      if (!selectedPreviousData.value) {
        console.warn('No data selected');
        return;
      }
      
      loading.value = true
      
      // Emit the event to parent
      emit('use-previous-data', selectedPreviousData.value);
      
      // Set success message
      usedPreviousYear.value = selectedPreviousData.value.academicYear
      showSuccessMessage.value = true
      loading.value = false
      
      // Hide message after 5 seconds
      setTimeout(() => {
        showSuccessMessage.value = false
      }, 5000)
    };

    const updateDontCreateClasses = () => {
      emit('update-field', { field: 'dontCreateClasses', value: dontCreateClasses.value })
    };

    return {
      loading,
      selectedPreviousData,
      dontCreateClasses,
      showSuccessMessage,
      usedPreviousYear,
      handleUsePreviousData,
      updateDontCreateClasses
    }
  }
}
</script>

<style scoped>
.success-message {
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
  background-color: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #166534;
  border-radius: 0.375rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.loading {
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
  background-color: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #1e40af;
  border-radius: 0.375rem;
}

.card {
  padding: 1.5rem;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.section-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.field {
  margin-bottom: 1rem;
}

.field select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
}

button {
  padding: 0.5rem 1rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
}

button:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

.switch-container {
  margin-top: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
</style>