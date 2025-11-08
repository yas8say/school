<template>
  <div class="enrollment-container">
    <div class="scroll-view-content">
      <!-- Header -->
      <div class="header">
        <h1 class="title">Create Fee Schedules & Invoices</h1>
        <p class="subtitle">Generate fee schedules and sales invoices for students</p>
      </div>

<!-- Processing Modal -->
<div v-if="processing" class="modal-overlay">
  <div class="loading-modal">
    <div class="loading-spinner"></div>
    <h3 class="loading-title">Processing Fee Schedules & Invoices</h3>
    <p class="loading-description">
      Please wait while we create fee schedules and generate invoices for all students.
      This may take a few minutes depending on the number of students.
    </p>
    
    <div v-if="processingDetails">
      <h4>Processing Details</h4>
      <div>
        <div><strong>Fee Structure:</strong> {{ processingDetails.fee_structure }}</div>
        <div><strong>Student Groups:</strong> {{ processingDetails.student_groups }}</div>
        <div><strong>Fee Plan:</strong> {{ processingDetails.fee_plan }}</div>
        <div><strong>Total Students:</strong> {{ processingDetails.total_students }}</div>
        <div><strong>Schedule Count:</strong> {{ processingDetails.schedule_count }}</div>
      </div>
    </div>
    
    <div>
      <div class="spinner"></div>
      Creating fee schedules and invoices...
    </div>
  </div>
</div>

      <!-- Main Form -->
      <div class="form-card">
        <h2 class="form-title">Fee Schedule Configuration</h2>

        <!-- Messages -->
        <div v-if="errorMessage" class="message error">
          <strong>Error:</strong> {{ errorMessage }}
        </div>

        <div v-if="successMessage" class="message success">
          <strong>Success:</strong> {{ successMessage }}
        </div>

        <div class="form-section">
          <h3 class="section-title">Basic Information</h3>
          <div class="form-grid">
            <!-- Class Selection -->
            <div class="form-group required">
              <label>Class/Program</label>
              <select 
                v-model="formData.selected_class" 
                class="picker"
                :disabled="classesResource.loading || processing"
                @change="onClassChange"
              >
                <option value="">Select Class/Program</option>
                <option 
                  v-for="cls in classesList" 
                  :key="cls.name" 
                  :value="cls.name"
                >
                  {{ cls.program_name || cls.name }}
                </option>
              </select>
              <span v-if="classesResource.loading" class="field-hint">Loading classes...</span>
            </div>

            <!-- Fee Structure Selection -->
            <div class="form-group required">
              <label>Fee Structure</label>
              <select 
                v-model="formData.fee_structure" 
                class="picker"
                :disabled="!formData.selected_class || feeStructuresResource.loading || processing"
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
              <span v-if="feeStructuresResource.loading" class="field-hint">Loading fee structures...</span>
              <span v-if="!formData.selected_class" class="field-hint">Select a class first</span>
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
        </div>

        <!-- Fee Structure Details -->
        <div v-if="formData.fee_structure && selectedFeeStructure" class="fee-structure-details-section">
          <h3 class="section-title">Fee Structure Details</h3>
          <div class="details-grid">
            <div class="detail-item">
              <span class="label">Total Amount:</span>
              <span class="value">₹{{ selectedFeeStructure.total_amount?.toLocaleString() }}</span>
            </div>
            <div class="detail-item">
              <span class="label">Academic Year:</span>
              <span class="value">{{ selectedFeeStructure.academic_year }}</span>
            </div>
            <div v-if="selectedFeeStructure.academic_term" class="detail-item">
              <span class="label">Academic Term:</span>
              <span class="value">{{ selectedFeeStructure.academic_term }}</span>
            </div>
          </div>

          <!-- Components Breakdown -->
          <div v-if="selectedFeeStructure.components && selectedFeeStructure.components.length" class="components-section">
            <h4 class="subsection-title">Fee Components</h4>
            <div class="components-table">
              <table>
                <thead>
                  <tr>
                    <th>Fee Category</th>
                    <th>Amount</th>
                    <th>Discount</th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="component in selectedFeeStructure.components" :key="component.fees_category">
                    <td>{{ component.fees_category }}</td>
                    <td>₹{{ component.amount?.toLocaleString() }}</td>
                    <td>{{ component.discount }}%</td>
                    <td>₹{{ component.total?.toLocaleString() }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Fee Schedule Distribution -->
        <div v-if="formData.fee_plan && feeSchedules.length" class="form-section">
          <h3 class="section-title">Fee Schedule Distribution</h3>
          <div class="table-container-wrapper">
            <table class="preview-table">
              <thead>
                <tr>
                  <th width="60px">
                    <div class="header-label">Select</div>
                  </th>
                  <th>
                    <div class="header-label">Due Date</div>
                  </th>
                  <th>
                    <div class="header-label">Amount</div>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(schedule, index) in feeSchedules" :key="index">
                  <td class="status-cell">
                    <input 
                      type="checkbox" 
                      v-model="schedule.selected"
                      :disabled="processing"
                      class="custom-checkbox"
                    />
                  </td>
                  <td>
                    <input
                      type="date"
                      v-model="schedule.due_date"
                      :disabled="processing"
                      class="table-input"
                    />
                  </td>
                  <td>₹{{ schedule.amount?.toLocaleString() }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Student Groups Selection -->
        <div v-if="formData.fee_structure && studentGroupsList.length" class="form-section">
          <h3 class="section-title">Select Student Groups</h3>
          <div class="table-container-wrapper">
            <table class="preview-table">
              <thead>
                <tr>
                  <th width="60px">
                    <div class="header-label">Select</div>
                  </th>
                  <th>
                    <div class="header-label">Student Group</div>
                  </th>
                  <th>
                    <div class="header-label">Total Students</div>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="group in studentGroupsList" :key="group.name">
                  <td class="status-cell">
                    <input 
                      type="checkbox" 
                      v-model="group.selected"
                      :disabled="processing"
                      class="custom-checkbox"
                    />
                  </td>
                  <td>{{ group.name }}</td>
                  <td>{{ group.total_students }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-if="selectedStudentGroups.length > 0" class="summary-stats">
            <div class="stat-item">
              <span class="stat-label">Selected Groups</span>
              <span class="stat-value info">{{ selectedStudentGroups.length }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Total Students</span>
              <span class="stat-value valid">{{ getTotalStudents() }}</span>
            </div>
          </div>
        </div>

        <!-- Summary Section -->
        <div v-if="isFormValid" class="summary-section">
          <h3 class="section-title">Summary</h3>
          <div class="summary-grid">
            <div class="summary-item">
              <span class="label">Class:</span>
              <span class="value">{{ getClassName(formData.selected_class) }}</span>
            </div>
            <div class="summary-item">
              <span class="label">Fee Structure:</span>
              <span class="value">{{ getFeeStructureName(formData.fee_structure) }}</span>
            </div>
            <div class="summary-item">
              <span class="label">Fee Plan:</span>
              <span class="value">{{ getFeePlanLabel(formData.fee_plan) }}</span>
            </div>
            <div class="summary-item">
              <span class="label">Total Schedules:</span>
              <span class="value">{{ feeSchedules.filter(s => s.selected).length }}</span>
            </div>
            <div class="summary-item">
              <span class="label">Student Groups:</span>
              <span class="value">{{ selectedStudentGroups.length }} groups</span>
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
            class="enroll-button"
            :disabled="!isFormValid || processing"
          >
            <span class="button-content">
              <span v-if="processing" class="spinner"></span>
              {{ processing ? 'Processing...' : 'Create Fee Schedules & Invoices' }}
            </span>
          </button>

          <button 
            @click="resetForm" 
            class="reset-button"
            :disabled="processing"
          >
            Reset Form
          </button>
        </div>
      </div>

      <!-- Results Section -->
      <div v-if="results && results.success" class="form-card summary-card">
        <h2 class="form-title">Creation Results</h2>
        
        <div class="message success">
          <strong>Successfully Created!</strong> {{ results.message }}
        </div>

        <div class="form-section">
          <h3 class="section-title">Fee Schedules Created</h3>
          <div class="table-container-wrapper">
            <table class="preview-table">
              <thead>
                <tr>
                  <th>Fee Schedule</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="schedule in results.fee_schedules" :key="schedule">
                  <td>{{ schedule }}</td>
                  <td class="actions">
                    <a 
                      :href="`/app/fee-schedule/${schedule}`" 
                      target="_blank" 
                      class="primary-button"
                      style="padding: 0.5rem 1rem; font-size: 0.9rem; text-decoration: none; display: inline-block;"
                    >
                      View
                    </a>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="form-section">
          <h3 class="section-title">Invoice Results</h3>
          <div class="table-container-wrapper">
            <table class="preview-table">
              <thead>
                <tr>
                  <th>Fee Schedule</th>
                  <th>Students Processed</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="invoiceResult in results.invoice_results" :key="invoiceResult.fee_schedule">
                  <td>{{ invoiceResult.fee_schedule }}</td>
                  <td>
                    {{ invoiceResult.result.created_count }}/{{ invoiceResult.result.total_students }}
                  </td>
                  <td class="status-cell">
                    <span class="status-badge success" v-if="invoiceResult.result.success">Success</span>
                    <span class="status-badge error" v-else>Failed</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="form-actions">
          <button @click="resetForm" class="success-button">
            Create Another
          </button>
          <button @click="results = null" class="secondary-button">
            Close Results
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { createResource } from 'frappe-ui';
import { ref, computed, onMounted, watch } from 'vue';
import '@/styles/form.css';

export default {
  name: 'FeeScheduleCreator',
  
  setup() {
    // Reactive state
    const processing = ref(false);
    const errorMessage = ref('');
    const successMessage = ref('');
    const results = ref(null);
    const processingDetails = ref(null);
    const feeSchedules = ref([]);

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
      selected_class: '',
      fee_structure: '',
      student_group: '',
      fee_plan: ''
    });

    // API Resources
    const classesResource = createResource({
      url: 'school.al_ummah.api3.get_classes',
      auto: true,
      onSuccess: (data) => {
        console.log('Classes loaded:', data);
      },
      onError: (err) => {
        errorMessage.value = err.messages?.[0] || 'Failed to load classes';
        console.error('Error loading classes:', err);
      }
    });

    const feeStructuresResource = createResource({
      url: 'school.al_ummah.api5.get_fee_structures_for_selection',
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
        // Add selected property to each group
        if (data && data.success && data.student_groups) {
          data.student_groups.forEach(group => {
            group.selected = true;
          });
        }
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
    const classesList = computed(() => {
      return classesResource.data || [];
    });

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

    const selectedFeeStructure = computed(() => {
      if (formData.value.fee_structure && feeStructuresList.value.length) {
        return feeStructuresList.value.find(s => s.name === formData.value.fee_structure);
      }
      return null;
    });

    const selectedStudentGroups = computed(() => {
      return studentGroupsList.value.filter(group => group.selected);
    });

    const isFormValid = computed(() => {
      return formData.value.selected_class && 
             formData.value.fee_structure && 
             formData.value.fee_plan &&
             feeSchedules.value.length > 0 &&
             selectedStudentGroups.value.length > 0;
    });

    // Watchers
    watch(() => formData.value.fee_plan, (newPlan) => {
      if (newPlan && selectedFeeStructure.value) {
        calculateFeeSchedules();
      }
    });

    watch(() => formData.value.fee_structure, (newStructure) => {
      if (newStructure && formData.value.fee_plan) {
        calculateFeeSchedules();
      }
    });

    // Methods
    function onClassChange() {
      formData.value.fee_structure = '';
      formData.value.student_group = '';
      formData.value.fee_plan = '';
      results.value = null;
      successMessage.value = '';
      errorMessage.value = '';
      feeSchedules.value = [];

      if (formData.value.selected_class) {
        feeStructuresResource.update({
          params: { program: formData.value.selected_class }
        });
        feeStructuresResource.reload();
      } else {
        feeStructuresResource.data = null;
      }
    }

    function onFeeStructureChange() {
      formData.value.student_group = '';
      formData.value.fee_plan = '';
      results.value = null;
      successMessage.value = '';
      errorMessage.value = '';
      feeSchedules.value = [];

      if (formData.value.fee_structure) {
        studentGroupsResource.update({
          params: { fee_structure_name: formData.value.fee_structure }
        });
        studentGroupsResource.reload();
      } else {
        studentGroupsResource.data = null;
      }
    }

    function calculateFeeSchedules() {
      if (!selectedFeeStructure.value || !formData.value.fee_plan) return;

      const totalAmount = selectedFeeStructure.value.total_amount;
      const feePlan = formData.value.fee_plan;
      
      const distribution = getDistributionForFeePlan(feePlan, totalAmount);
      feeSchedules.value = distribution.map(item => ({
        ...item,
        selected: true,
        due_date: item.due_date || getDefaultDueDate()
      }));
    }

    function getDistributionForFeePlan(feePlan, totalAmount) {
      const today = new Date();
      const distributions = [];

      const planConfig = {
        'Monthly': { frequency: 12, gap: 1 },
        'Quarterly': { frequency: 4, gap: 3 },
        'Semi-Annually': { frequency: 2, gap: 6 },
        'Annually': { frequency: 1, gap: 12 },
        'Term-Wise': { frequency: 3, gap: 4 }
      };

      const config = planConfig[feePlan];
      if (!config) return [];

      const installmentAmount = totalAmount / config.frequency;

      for (let i = 1; i <= config.frequency; i++) {
        const dueDate = new Date(today);
        dueDate.setMonth(today.getMonth() + (config.gap * i));
        
        distributions.push({
          due_date: formatDate(dueDate),
          amount: parseFloat(installmentAmount.toFixed(2))
        });
      }

      return distributions;
    }

    function getDefaultDueDate() {
      const today = new Date();
      today.setDate(today.getDate() + 30);
      return formatDate(today);
    }

    function formatDate(date) {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    }

    function getClassName(className) {
      const cls = classesList.value.find(c => c.name === className);
      return cls ? (cls.program_name || cls.name) : className;
    }

    function getFeeStructureName(structureName) {
      const structure = feeStructuresList.value.find(s => s.name === structureName);
      if (structure) {
        let displayName = structure.name;
        if (structure.program) {
          displayName += ` - ${structure.program}`;
        }
        if (structure.academic_year) {
          displayName += ` (${structure.academic_year})`;
        }
        return displayName;
      }
      return structureName;
    }

    function getFeePlanLabel(planValue) {
      const plan = feePlans.value.find(p => p.value === planValue);
      return plan ? plan.label : planValue;
    }

    function getTotalStudents() {
      return selectedStudentGroups.value.reduce((total, group) => {
        return total + (group.total_students || 0);
      }, 0);
    }

    function createFeeSchedulesAndInvoices() {
      if (!isFormValid.value) return;
      
      processing.value = true;
      errorMessage.value = '';
      successMessage.value = '';
      results.value = null;

      const selectedSchedules = feeSchedules.value.filter(s => s.selected);
      const selectedGroups = selectedStudentGroups.value.map(g => g.name);
      const dueDates = selectedSchedules.map(s => s.due_date);

      processingDetails.value = {
        class: getClassName(formData.value.selected_class),
        fee_structure: getFeeStructureName(formData.value.fee_structure),
        student_groups: selectedGroups.join(', '),
        fee_plan: getFeePlanLabel(formData.value.fee_plan),
        total_students: getTotalStudents(),
        schedule_count: selectedSchedules.length
      };

      createFeeSchedulesResource.submit({
        fee_structure_name: formData.value.fee_structure,
        student_groups: selectedGroups,
        fee_plan: formData.value.fee_plan,
        due_dates: dueDates
      });
    }

    function resetForm() {
      formData.value = {
        selected_class: '',
        fee_structure: '',
        student_group: '',
        fee_plan: ''
      };
      results.value = null;
      errorMessage.value = '';
      successMessage.value = '';
      processingDetails.value = null;
      feeSchedules.value = [];
      
      feeStructuresResource.data = null;
      studentGroupsResource.data = null;
    }

    onMounted(() => {
      console.log('Fee Schedule Creator mounted');
    });

    return {
      processing,
      errorMessage,
      successMessage,
      results,
      feePlans,
      formData,
      processingDetails,
      feeSchedules,
      classesResource,
      feeStructuresResource,
      studentGroupsResource,
      createFeeSchedulesResource,
      classesList,
      feeStructuresList,
      studentGroupsList,
      isFormValid,
      selectedFeeStructure,
      selectedStudentGroups,
      onClassChange,
      onFeeStructureChange,
      getClassName,
      getFeeStructureName,
      getFeePlanLabel,
      getTotalStudents,
      createFeeSchedulesAndInvoices,
      resetForm
    };
  }
};
</script>

<style scoped>
/* Fee Structure Details */
.fee-structure-details-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: white;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

.detail-item .label {
  font-weight: 500;
  color: #374151;
}

.detail-item .value {
  font-weight: 600;
  color: #1f2937;
}

/* Components Section */
.components-section {
  margin-top: 1.5rem;
}

.subsection-title {
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 1rem;
}

.components-table {
  background: white;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.components-table table {
  width: 100%;
  border-collapse: collapse;
}

.components-table th,
.components-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.components-table th {
  background: #f8fafc;
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
}

.components-table tr:last-child td {
  border-bottom: none;
}

/* Summary Section */
.summary-section {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
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

/* Checkbox styling */
.custom-checkbox {
  width: 1rem;
  height: 1rem;
  border-radius: 0.25rem;
  border: 1px solid #d1d5db;
  cursor: pointer;
}

.custom-checkbox:checked {
  background-color: #3b82f6;
  border-color: #3b82f6;
}

.custom-checkbox:disabled {
  background-color: #f3f4f6;
  border-color: #d1d5db;
  cursor: not-allowed;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .details-grid {
    grid-template-columns: 1fr;
  }
  
  .summary-grid {
    grid-template-columns: 1fr;
  }
  
  .components-table {
    overflow-x: auto;
  }
  
  .components-table table {
    min-width: 500px;
  }
}
</style>