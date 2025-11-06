<template>
  <div class="fee-schedule-container" :class="{ 'blurred': processing }">
    <div class="header">
      <h1 class="title">Create Fee Schedules & Invoices</h1>
      <p class="subtitle">Generate fee schedules and sales invoices for students</p>
    </div>

    <!-- Processing Modal -->
    <div v-if="processing" class="processing-modal-overlay">
      <div class="processing-modal">
        <div class="processing-spinner"></div>
        <h3 class="processing-title">Processing Fee Schedules & Invoices</h3>
        <p class="processing-description">
          Please wait while we create fee schedules and generate invoices for all students.
          This may take a few minutes depending on the number of students.
        </p>
        <div class="processing-details" v-if="processingDetails">
          <div class="detail-item">
            <span class="detail-label">Fee Structure:</span>
            <span class="detail-value">{{ processingDetails.fee_structure }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Student Group:</span>
            <span class="detail-value">{{ processingDetails.student_group }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Fee Plan:</span>
            <span class="detail-value">{{ processingDetails.fee_plan }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Total Students:</span>
            <span class="detail-value">{{ processingDetails.total_students }}</span>
          </div>
        </div>
        <div class="processing-status">
          <div class="status-spinner"></div>
          <span class="status-text">Creating fee schedules and invoices...</span>
        </div>
      </div>
    </div>

    <!-- Main Form -->
    <div class="form-card">
      <h2 class="form-title">Fee Schedule Configuration</h2>

      <!-- Error Message -->
      <div v-if="errorMessage" class="message error">
        <div class="message-icon">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div class="message-content">
          <strong>Error:</strong> {{ errorMessage }}
        </div>
        <button @click="errorMessage = ''" class="message-close">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Success Message -->
      <div v-if="successMessage" class="message success">
        <div class="message-icon">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div class="message-content">
          <strong>Success:</strong> {{ successMessage }}
        </div>
        <button @click="successMessage = ''" class="message-close">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="form-grid">
        <!-- Fee Structure Selection -->
        <div class="form-group required">
          <label>Fee Structure</label>
          <select 
            v-model="formData.fee_structure" 
            class="picker"
            :disabled="feeStructuresResource.loading || processing"
            @change="onFeeStructureChange"
          >
            <option value="">Select Fee Structure</option>
            <option 
              v-for="structure in feeStructuresList" 
              :key="structure.name" 
              :value="structure.name"
            >
              {{ structure.name }} - {{ structure.program }} ({{ structure.academic_year }})
            </option>
          </select>
          <span v-if="feeStructuresResource.loading" class="loading-text">Loading fee structures...</span>
        </div>

        <!-- Student Group Selection -->
        <div class="form-group required">
          <label>Student Group</label>
          <select 
            v-model="formData.student_group" 
            class="picker"
            :disabled="!formData.fee_structure || studentGroupsResource.loading || processing"
          >
            <option value="">Select Student Group</option>
            <option 
              v-for="group in studentGroupsList" 
              :key="group.name" 
              :value="group.name"
            >
              {{ group.name }} - {{ group.total_students }} students
            </option>
          </select>
          <span v-if="studentGroupsResource.loading" class="loading-text">Loading student groups...</span>
          <span v-if="!formData.fee_structure" class="hint-text">Select a fee structure first</span>
        </div>

        <!-- Fee Plan Selection -->
        <div class="form-group required">
          <label>Fee Plan</label>
          <select 
            v-model="formData.fee_plan" 
            class="picker"
            :disabled="processing"
          >
            <option value="">Select Fee Plan</option>
            <option 
              v-for="plan in feePlans" 
              :key="plan.value" 
              :value="plan.value"
            >
              {{ plan.label }}
            </option>
          </select>
        </div>
      </div>

      <!-- Summary Section -->
      <div v-if="formData.fee_structure && formData.student_group && formData.fee_plan" class="summary-section">
        <h3 class="section-title">Summary</h3>
        <div class="summary-grid">
          <div class="summary-item">
            <span class="label">Fee Structure:</span>
            <span class="value">{{ getFeeStructureName(formData.fee_structure) }}</span>
          </div>
          <div class="summary-item">
            <span class="label">Student Group:</span>
            <span class="value">{{ getStudentGroupName(formData.student_group) }}</span>
          </div>
          <div class="summary-item">
            <span class="label">Fee Plan:</span>
            <span class="value">{{ getFeePlanLabel(formData.fee_plan) }}</span>
          </div>
          <div class="summary-item">
            <span class="label">Total Students:</span>
            <span class="value">{{ getTotalStudents() }}</span>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="form-actions">
        <button 
          @click="createFeeSchedulesAndInvoices" 
          class="primary-button"
          :disabled="!isFormValid || processing"
        >
          <span class="button-content">
            <svg v-if="!processing" class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            <span v-if="processing" class="spinner"></span>
            {{ processing ? 'Processing...' : 'Create Fee Schedules & Invoices' }}
          </span>
        </button>

        <button 
          @click="resetForm" 
          class="secondary-button"
          :disabled="processing"
        >
          Reset Form
        </button>
      </div>
    </div>

    <!-- Results Section -->
    <div v-if="results && results.success" class="form-card results-card">
      <h2 class="form-title">Creation Results</h2>
      
      <div class="success-banner">
        <div class="success-icon">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div class="success-content">
          <h3>Successfully Created!</h3>
          <p>{{ results.message }}</p>
        </div>
      </div>

      <div class="results-details">
        <div class="result-section">
          <h4>Fee Schedules Created</h4>
          <div class="result-list">
            <div 
              v-for="schedule in results.fee_schedules" 
              :key="schedule" 
              class="result-item"
            >
              <span class="result-badge">Fee Schedule</span>
              <span class="result-name">{{ schedule }}</span>
              <a 
                :href="`/app/fee-schedule/${schedule}`" 
                target="_blank" 
                class="view-link"
              >
                View
              </a>
            </div>
          </div>
        </div>

        <div class="result-section">
          <h4>Invoice Results</h4>
          <div class="result-list">
            <div 
              v-for="invoiceResult in results.invoice_results" 
              :key="invoiceResult.fee_schedule" 
              class="result-item"
            >
              <span class="result-badge">Invoices</span>
              <span class="result-name">{{ invoiceResult.fee_schedule }}</span>
              <span class="result-count">
                {{ invoiceResult.result.created_count }}/{{ invoiceResult.result.total_students }} students
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { createResource } from 'frappe-ui';
import { ref, computed, onMounted } from 'vue';

export default {
  name: 'FeeScheduleCreator',
  
  setup() {
    // Reactive state
    const processing = ref(false);
    const errorMessage = ref('');
    const successMessage = ref('');
    const results = ref(null);
    const processingDetails = ref(null);

    // Fee plans defined in frontend
    const feePlans = ref([
      { value: 'Monthly', label: 'Monthly' },
      { value: 'Quarterly', label: 'Quarterly' },
      { value: 'Semi-Annually', label: 'Semi-Annually' },
      { value: 'Annually', label: 'Annually' },
      { value: 'Term-Wise', label: 'Term-Wise' }
    ]);

    // Form data
    const formData = ref({
      fee_structure: '',
      student_group: '',
      fee_plan: ''
    });

    // API Resources
    const feeStructuresResource = createResource({
      url: 'school.al_ummah.api5.get_fee_structures_for_selection',
      auto: true,
      onSuccess: (data) => {
        console.log('Fee structures loaded:', data);
      },
      onError: (err) => {
        errorMessage.value = err.messages?.[0] || 'Failed to load fee structures';
        console.error('Error loading fee structures:', err);
      }
    });

    const studentGroupsResource = createResource({
      url: 'school.al_ummah.api5.get_student_groups_for_fee_structure',
      onSuccess: (data) => {
        console.log('Student groups loaded:', data);
      },
      onError: (err) => {
        errorMessage.value = err.messages?.[0] || 'Failed to load student groups';
        console.error('Error loading student groups:', err);
      }
    });

    const createFeeSchedulesResource = createResource({
      url: 'school.al_ummah.api5.create_and_submit_fee_schedules_with_invoices',
      method: 'POST',
      onSuccess: (data) => {
        processing.value = false;
        processingDetails.value = null;
        results.value = data;
        successMessage.value = data.message;
        errorMessage.value = '';
        console.log('Fee schedules and invoices created:', data);
      },
      onError: (err) => {
        processing.value = false;
        processingDetails.value = null;
        errorMessage.value = err.messages?.[0] || 'Failed to create fee schedules and invoices';
        console.error('Error creating fee schedules:', err);
      }
    });

    // Computed properties
    const feeStructuresList = computed(() => {
      if (feeStructuresResource.data && feeStructuresResource.data.success) {
        return feeStructuresResource.data.fee_structures;
      }
      return [];
    });

    const studentGroupsList = computed(() => {
      if (studentGroupsResource.data && studentGroupsResource.data.success) {
        return studentGroupsResource.data.student_groups;
      }
      return [];
    });

    const isFormValid = computed(() => {
      return formData.value.fee_structure && 
             formData.value.student_group && 
             formData.value.fee_plan;
    });

    // Methods
    function onFeeStructureChange() {
      // Reset student group when fee structure changes
      formData.value.student_group = '';
      results.value = null;
      successMessage.value = '';
      errorMessage.value = '';

      if (formData.value.fee_structure) {
        // Load student groups for selected fee structure
        studentGroupsResource.update({
          params: { fee_structure_name: formData.value.fee_structure }
        });
        studentGroupsResource.reload();
      }
    }

    function getFeeStructureName(structureName) {
      const structure = feeStructuresList.value.find(s => s.name === structureName);
      return structure ? `${structure.name} - ${structure.program} (${structure.academic_year})` : structureName;
    }

    function getStudentGroupName(groupName) {
      const group = studentGroupsList.value.find(g => g.name === groupName);
      return group ? group.name : groupName;
    }

    function getFeePlanLabel(planValue) {
      const plan = feePlans.value.find(p => p.value === planValue);
      return plan ? plan.label : planValue;
    }

    function getTotalStudents() {
      const group = studentGroupsList.value.find(g => g.name === formData.value.student_group);
      return group ? group.total_students : 0;
    }

    function createFeeSchedulesAndInvoices() {
      if (!isFormValid.value) return;
      
      processing.value = true;
      errorMessage.value = '';
      successMessage.value = '';
      results.value = null;

      // Set processing details for the modal
      processingDetails.value = {
        fee_structure: getFeeStructureName(formData.value.fee_structure),
        student_group: getStudentGroupName(formData.value.student_group),
        fee_plan: getFeePlanLabel(formData.value.fee_plan),
        total_students: getTotalStudents()
      };

      createFeeSchedulesResource.submit({
        fee_structure_name: formData.value.fee_structure,
        student_group_name: formData.value.student_group,
        fee_plan: formData.value.fee_plan
      });
    }

    function resetForm() {
      formData.value = {
        fee_structure: '',
        student_group: '',
        fee_plan: ''
      };
      results.value = null;
      errorMessage.value = '';
      successMessage.value = '';
      processingDetails.value = null;
    }

    // Lifecycle
    onMounted(() => {
      console.log('Fee Schedule Creator mounted');
    });

    return {
      // State
      processing,
      errorMessage,
      successMessage,
      results,
      feePlans,
      formData,
      processingDetails,
      
      // Resources
      feeStructuresResource,
      studentGroupsResource,
      createFeeSchedulesResource,
      
      // Computed
      feeStructuresList,
      studentGroupsList,
      isFormValid,
      
      // Methods
      onFeeStructureChange,
      getFeeStructureName,
      getStudentGroupName,
      getFeePlanLabel,
      getTotalStudents,
      createFeeSchedulesAndInvoices,
      resetForm
    };
  }
};
</script>

<style scoped>
.fee-schedule-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem;
  transition: all 0.3s ease;
}

.fee-schedule-container.blurred {
  filter: blur(2px);
  pointer-events: none;
  user-select: none;
}

.header {
  text-align: center;
  margin-bottom: 2rem;
}

.title {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.subtitle {
  font-size: 1.125rem;
  color: #6b7280;
}

.form-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
}

.form-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1.5rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.required label::after {
  content: " *";
  color: #ef4444;
}

.form-group label {
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.picker {
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
  background: white;
  cursor: pointer;
  width: 100%;
}

.picker:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.picker:disabled {
  background-color: #f9fafb;
  cursor: not-allowed;
  opacity: 0.6;
}

.loading-text {
  font-size: 0.75rem;
  color: #6b7280;
  font-style: italic;
  margin-top: 0.25rem;
}

.hint-text {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.summary-section {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.section-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 1rem;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.summary-item .label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.summary-item .value {
  font-size: 1rem;
  color: #1f2937;
  font-weight: 600;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.primary-button, .secondary-button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-width: 120px;
}

.primary-button {
  background: #10b981;
  color: white;
}

.primary-button:hover:not(:disabled) {
  background: #059669;
  transform: translateY(-1px);
}

.primary-button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  transform: none;
}

.secondary-button {
  background: #6b7280;
  color: white;
}

.secondary-button:hover:not(:disabled) {
  background: #4b5563;
  transform: translateY(-1px);
}

.secondary-button:disabled {
  background: #d1d5db;
  cursor: not-allowed;
  transform: none;
}

.button-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.spinner {
  display: inline-block;
  width: 1rem;
  height: 1rem;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.icon {
  width: 1.25rem;
  height: 1.25rem;
}

/* Message Styles */
.message {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  font-weight: 500;
}

.message.error {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.message.success {
  background: #f0fdf4;
  color: #16a34a;
  border: 1px solid #bbf7d0;
}

.message-icon {
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.message-icon .icon {
  width: 1.25rem;
  height: 1.25rem;
}

.message-content {
  flex: 1;
}

.message-close {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  color: inherit;
  opacity: 0.7;
}

.message-close:hover {
  opacity: 1;
  background: rgba(0, 0, 0, 0.1);
}

/* Processing Modal */
.processing-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.processing-modal {
  background: white;
  padding: 2.5rem;
  border-radius: 16px;
  text-align: center;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.processing-spinner {
  width: 4rem;
  height: 4rem;
  border: 4px solid #e5e7eb;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1.5s linear infinite;
  margin: 0 auto 1.5rem;
}

.processing-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.processing-description {
  color: #6b7280;
  line-height: 1.6;
  margin-bottom: 2rem;
}

.processing-details {
  background: #f8fafc;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  text-align: left;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #e5e7eb;
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-label {
  font-weight: 500;
  color: #374151;
}

.detail-value {
  font-weight: 600;
  color: #1f2937;
}

.processing-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 1rem;
  background: #f0f9ff;
  border-radius: 8px;
  border: 1px solid #bae6fd;
}

.status-spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid transparent;
  border-top: 2px solid #0ea5e9;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.status-text {
  color: #0369a1;
  font-weight: 500;
}

/* Results Section */
.results-card {
  border: 2px solid #10b981;
  animation: resultsSlideIn 0.5s ease-out;
}

@keyframes resultsSlideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.success-banner {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: #f0fdf4;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.success-icon {
  width: 3rem;
  height: 3rem;
  background: #d1fae5;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.success-icon .icon {
  width: 1.5rem;
  height: 1.5rem;
  color: #10b981;
}

.success-content h3 {
  margin: 0 0 0.25rem 0;
  color: #065f46;
  font-size: 1.25rem;
}

.success-content p {
  margin: 0;
  color: #047857;
}

.results-details {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.result-section h4 {
  margin: 0 0 1rem 0;
  color: #374151;
  font-size: 1.125rem;
}

.result-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.result-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.result-badge {
  background: #e0e7ff;
  color: #3730a3;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.result-name {
  flex: 1;
  color: #374151;
  font-weight: 500;
}

.result-count {
  color: #6b7280;
  font-size: 0.875rem;
}

.view-link {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.875rem;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  border: 1px solid #3b82f6;
  transition: all 0.2s;
}

.view-link:hover {
  background: #3b82f6;
  color: white;
  text-decoration: none;
}

/* Responsive Design */
@media (max-width: 768px) {
  .fee-schedule-container {
    padding: 1rem;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .summary-grid {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .success-banner {
    flex-direction: column;
    text-align: center;
  }
  
  .processing-modal {
    padding: 1.5rem;
    margin: 1rem;
  }
  
  .processing-details {
    padding: 1rem;
  }
  
  .detail-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .message {
    flex-direction: column;
    text-align: center;
    gap: 0.5rem;
  }
  
  .message-close {
    align-self: flex-end;
  }
}
</style>