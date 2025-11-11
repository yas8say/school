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
              <div><strong>Fee Structures:</strong> {{ processingDetails.fee_structures }}</div>
              <div><strong>Student Groups:</strong> {{ processingDetails.student_groups }}</div>
              <div><strong>Total Students:</strong> {{ processingDetails.total_students }}</div>
              <div><strong>Total Schedules:</strong> {{ processingDetails.schedule_count }}</div>
            </div>
          </div>
          
          <div>
            <div class="spinner"></div>
            Creating fee schedules and invoices...
          </div>
        </div>
      </div>

<!-- Student List Modal - Fullscreen with Scroll -->
<div v-if="showStudentList" class="modal-overlay fullscreen-modal">
  <div class="modal-content fullscreen-content scrollable-content">
    <StudentList
      :student-group="selectedStudentGroup"
      :fee-structures="selectedStructures"
      :initial-selected-students="getInitialSelections(selectedStudentGroup)"
      @save="handleStudentListSave"
      @close="showStudentList = false"
      @selection-change="handleStudentListSelectionChange"
    />
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
          </div>

            <!-- Add the note here -->
        <div v-if="formData.selected_class && feeSchedulesCount > 0" class="info-note">
          <div class="note-icon">ℹ️</div>
          <div class="note-content">
            <strong>Note:</strong> This program already has <strong>{{ feeSchedulesCount }}</strong> 
            fee schedule{{ feeSchedulesCount > 1 ? 's' : '' }} created for the current academic year.
            Creating new schedules will add to the existing ones.
          </div>
        </div>
        </div>
        

        <!-- Fee Structures Table -->
        <div v-if="formData.selected_class && feeStructuresList.length" class="form-section">
          <h3 class="section-title">Select Fee Structures</h3>
          <div class="selection-controls">
            <button @click="selectAllStructures" class="secondary-button small" :disabled="processing">
              Select All
            </button>
            <button @click="deselectAllStructures" class="secondary-button small" :disabled="processing">
              Deselect All
            </button>
            <span class="selection-count">
              {{ selectedStructuresCount }} of {{ feeStructuresList.length }} selected
            </span>
          </div>
          <div class="table-container-wrapper">
            <table class="preview-table fee-structures-table">
              <thead>
                <tr>
                  <th width="60px">
                    <div class="header-label">Select</div>
                  </th>
                  <th>
                    <div class="header-label">Fee Structure</div>
                  </th>
                  <th>
                    <div class="header-label">Fee Plan</div>
                  </th>
                  <th>
                    <div class="header-label">Total Amount</div>
                  </th>
                  <th width="80px">
                    <div class="header-label">Actions</div>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="structure in feeStructuresList" :key="structure.name" 
                    :class="{ 'selected-row': structure.selected }">
                  <td class="status-cell">
                    <input 
                      type="checkbox" 
                      v-model="structure.selected"
                      :disabled="processing"
                      class="custom-checkbox"
                      @change="onStructureSelectionChange(structure)"
                    />
                  </td>
                  <td>
                    <div class="fee-structure-info">
                      <div class="fee-structure-name">{{ structure.name }}</div>
                      <div class="fee-structure-meta">
                        {{ structure.program }} • {{ structure.academic_year }}
                        <span v-if="structure.academic_term">• {{ structure.academic_term }}</span>
                      </div>
                    </div>
                  </td>
                  <td>
                    <select 
                      v-model="structure.selected_fee_plan"
                      class="table-select"
                      :disabled="processing || !structure.selected"
                      @change="onFeePlanChange(structure)"
                    >
                      <option value="">Select Plan</option>
                      <option 
                        v-for="plan in feePlans" 
                        :key="plan.value" 
                        :value="plan.value"
                      >
                        {{ plan.label }}
                      </option>
                    </select>
                  </td>
                  <td>
                    <div class="total-amount">
                      ₹{{ structure.total_amount?.toLocaleString() }}
                    </div>
                  </td>
                  <td class="actions">
                    <button 
                      class="details-button"
                      :class="{ 'expanded': expandedStructures[structure.name] }"
                      @click="toggleStructureDetails(structure.name)"
                      :disabled="processing"
                    >
                      <span class="icon">▼</span>
                      Details
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Expanded Fee Structure Details -->
          <div v-for="structure in feeStructuresList" :key="structure.name + '_details'">
            <div v-if="expandedStructures[structure.name]" class="fee-structure-expanded-details">
              <!-- Fee Structure Details -->
              <div class="fee-structure-details-section">
                <h4 class="subsection-title">Fee Structure Details - {{ structure.name }}</h4>
                <div class="details-grid">
                  <div class="detail-item">
                    <span class="label">Total Amount:</span>
                    <span class="value">₹{{ structure.total_amount?.toLocaleString() }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">Academic Year:</span>
                    <span class="value">{{ structure.academic_year }}</span>
                  </div>
                  <div v-if="structure.academic_term" class="detail-item">
                    <span class="label">Academic Term:</span>
                    <span class="value">{{ structure.academic_term }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">Selected Fee Plan:</span>
                    <span class="value">{{ getFeePlanLabel(structure.selected_fee_plan) || 'Not selected' }}</span>
                  </div>
                </div>

                <!-- Components Breakdown -->
                <div v-if="structure.components && structure.components.length" class="components-section">
                  <h5 class="subsubsection-title">Fee Components</h5>
                  <div class="components-table">
                    <table>
                      <thead>
                        <tr>
                          <th>Fee Category</th>
                          <th>Amount</th>
                          <th>Discount</th>
                          <th>Total</th>
                          <th>Installment Calculation</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="component in structure.components" :key="component.fees_category">
                          <td>{{ component.fees_category }}</td>
                          <td>₹{{ component.amount?.toLocaleString() }}</td>
                          <td>{{ component.discount }}%</td>
                          <td>₹{{ component.total?.toLocaleString() }}</td>
                          <td class="installment-calculation">
                            <span v-if="structure.selected_fee_plan && structure.selected_fee_plan !== 'Annually'">
                              ₹{{ component.total?.toLocaleString() }} ÷ {{ getInstallmentCount(structure.selected_fee_plan) }} months = 
                              ₹{{ calculateInstallmentAmount(component.total, structure.selected_fee_plan)?.toLocaleString() }}
                            </span>
                            <span v-else class="text-muted">Full amount</span>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>

              <!-- Fee Schedule Distribution -->
              <div v-if="structure.selected_fee_plan && structure.feeSchedules && structure.feeSchedules.length" class="form-section">
                <h4 class="subsection-title">Fee Schedule Distribution - {{ structure.name }}</h4>
                <div class="schedule-controls">
                  <button @click="selectAllSchedules(structure)" class="secondary-button small" :disabled="processing">
                    Select All
                  </button>
                  <button @click="deselectAllSchedules(structure)" class="secondary-button small" :disabled="processing">
                    Deselect All
                  </button>
                  <span class="selection-count">
                    {{ getSelectedSchedulesCount(structure) }} of {{ structure.feeSchedules.length }} schedules selected
                  </span>
                </div>
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
                        <th>
                          <div class="header-label">Description</div>
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(schedule, index) in structure.feeSchedules" :key="index">
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
                      <td class="schedule-description">
                        {{ getScheduleDescription(structure.selected_fee_plan, index, schedule.due_date) }}
                      </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Student Groups Selection -->
        <div v-if="selectedStructuresCount > 0 && studentGroupsList.length" class="form-section">
          <h3 class="section-title">Select Student Groups</h3>
          <div class="selection-controls">
            <button @click="selectAllGroups" class="secondary-button small" :disabled="processing">
              Select All
            </button>
            <button @click="deselectAllGroups" class="secondary-button small" :disabled="processing">
              Deselect All
            </button>
            <span class="selection-count">
              {{ selectedStudentGroups.length }} of {{ studentGroupsList.length }} groups selected
            </span>
          </div>
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
                  <th>
                    <div class="header-label">Selected Students</div>
                  </th>
                  <th width="100px">
                    <div class="header-label">Actions</div>
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
                  <td>
                    {{ getSelectedStudentsCount(group) }} / {{ group.total_students }}
                    <span v-if="getSelectedStudentsCount(group) < group.total_students" class="exceptions-badge">
                      ({{ group.total_students - getSelectedStudentsCount(group) }} excluded)
                    </span>
                  </td>
                  <td class="actions">
                    <button 
                      @click="openStudentList(group)"
                      class="edit-button"
                      :disabled="processing"
                    >
                      Edit Students
                    </button>
                  </td>
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
            <div class="stat-item">
              <span class="stat-label">Excluded Students</span>
              <span class="stat-value warning">{{ getTotalExcludedStudents() }}</span>
            </div>
          </div>
        </div>

        <!-- Summary Section -->
        <div v-if="isFormValid" class="summary-section">
          <h3 class="section-title">Summary</h3>
          
          <!-- Main Summary Grid -->
          <div class="summary-grid">
            <div class="summary-item">
              <span class="label">Class:</span>
              <span class="value">{{ getClassName(formData.selected_class) }}</span>
            </div>
            <div class="summary-item">
              <span class="label">Fee Structures:</span>
              <span class="value">{{ selectedStructuresCount }} structures</span>
            </div>
            <div class="summary-item">
              <span class="label">Student Groups:</span>
              <span class="value">{{ selectedStudentGroups.length }} groups</span>
            </div>
            <div class="summary-item">
              <span class="label">Total Students:</span>
              <span class="value">{{ getTotalStudents() }}</span>
            </div>
            <div class="summary-item">
              <span class="label">Excluded Students:</span>
              <span class="value">{{ getTotalExcludedStudents() }}</span>
            </div>
            <div class="summary-item">
              <span class="label">Total Schedules:</span>
              <span class="value">{{ getTotalSchedulesCount() }}</span>
            </div>
            <div class="summary-item highlight">
              <span class="label">Total Amount:</span>
              <span class="value">₹{{ getTotalAmount()?.toLocaleString() }}</span>
            </div>
          </div>
          
          <!-- Selected Structures within Summary -->
          <div class="selected-structures-in-summary">
            <h4 class="subsection-title">Selected Fee Structures</h4>
            <div class="structures-summary-grid">
              <div v-for="structure in selectedStructures" :key="structure.name" class="structure-summary-card">
                <div class="structure-summary-header">
                  <div class="structure-name-plan">
                    <h5 class="structure-title">{{ structure.name }}</h5>
                    <span class="fee-plan-tag">{{ getFeePlanLabel(structure.selected_fee_plan) }}</span>
                  </div>
                  <div class="structure-amounts">
                    <span class="total-amount">₹{{ structure.total_amount?.toLocaleString() }}</span>
                    <span class="schedule-count">{{ getSelectedSchedulesCount(structure) }} schedules</span>
                  </div>
                </div>
                
                <div class="structure-components-summary">
                  <div v-for="component in structure.components" :key="component.fees_category" class="component-summary">
                    <span class="component-name">{{ component.fees_category }}</span>
                    <span class="component-breakdown">
                      ₹{{ component.total?.toLocaleString() }}
                      <span v-if="structure.selected_fee_plan && structure.selected_fee_plan !== 'Annually'">
                        (₹{{ calculateInstallmentAmount(component.total, structure.selected_fee_plan)?.toLocaleString() }} × {{ getInstallmentCount(structure.selected_fee_plan) }})
                      </span>
                    </span>
                  </div>
                </div>
                
                <!-- Schedule Preview -->
                <div v-if="structure.feeSchedules && structure.feeSchedules.filter(s => s.selected).length > 0" class="schedule-preview">
                  <div class="schedule-preview-title">Schedule:</div>
                  <div class="schedule-dates">
                    <span v-for="(schedule, index) in structure.feeSchedules.filter(s => s.selected).slice(0, 3)" 
                          :key="index" class="schedule-date-tag">
                      {{ formatScheduleDate(schedule.due_date) }}
                    </span>
                    <span v-if="structure.feeSchedules.filter(s => s.selected).length > 3" class="more-schedules">
                      +{{ structure.feeSchedules.filter(s => s.selected).length - 3 }} more
                    </span>
                  </div>
                </div>
              </div>
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
              {{ processing ? 'Processing...' : `Create Fee Schedules for ${selectedStructuresCount} Structures` }}
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

        <div v-for="structureResult in results.structure_results" :key="structureResult.fee_structure" class="form-section">
          <h3 class="section-title">Fee Schedules Created - {{ structureResult.fee_structure }}</h3>
          <div class="table-container-wrapper">
            <table class="preview-table">
              <thead>
                <tr>
                  <th>Fee Schedule</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="schedule in structureResult.fee_schedules" :key="schedule">
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

<!-- Simplified Invoice Results Summary with Direct Links -->
<div class="form-section">
  <h3 class="section-title">Invoice Results Summary</h3>
  <div class="table-container-wrapper">
    <table class="preview-table">
      <thead>
        <tr>
          <th>Fee Schedule</th>
          <th>Students Processed</th>
          <th>Created Documents</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="invoiceResult in results.invoice_results" :key="invoiceResult.fee_schedule">
          <td>{{ invoiceResult.fee_schedule }}</td>
          <td>
            {{ invoiceResult.result.created_count }}/{{ invoiceResult.result.total_students }}
          </td>
          <td>
            <div v-if="invoiceResult.result.submitted_invoices && invoiceResult.result.submitted_invoices.length > 0" class="document-links">
              <strong>Invoices:</strong>
              <div v-for="invoice in invoiceResult.result.submitted_invoices.slice(0, 3)" :key="invoice" class="document-link">
                <a :href="`/app/sales-invoice/${invoice}`" target="_blank" class="link">
                  {{ invoice }}
                </a>
              </div>
              <div v-if="invoiceResult.result.submitted_invoices.length > 3" class="more-documents">
                +{{ invoiceResult.result.submitted_invoices.length - 3 }} more invoices
              </div>
            </div>
            
            <div v-if="invoiceResult.result.submitted_orders && invoiceResult.result.submitted_orders.length > 0" class="document-links">
              <strong>Orders:</strong>
              <div v-for="order in invoiceResult.result.submitted_orders.slice(0, 3)" :key="order" class="document-link">
                <a :href="`/app/sales-order/${order}`" target="_blank" class="link">
                  {{ order }}
                </a>
              </div>
              <div v-if="invoiceResult.result.submitted_orders.length > 3" class="more-documents">
                +{{ invoiceResult.result.submitted_orders.length - 3 }} more orders
              </div>
            </div>
            
            <div v-if="!invoiceResult.result.submitted_invoices && !invoiceResult.result.submitted_orders">
              No documents created
            </div>
          </td>
          <td class="actions">
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
import StudentList from '../components/StudentList.vue';
import '@/styles/form.css';

export default {
  name: 'FeeScheduleCreator',
  
  components: {
    StudentList
  },
  
  setup() {
    // Reactive state
    const processing = ref(false);
    const errorMessage = ref('');
    const successMessage = ref('');
    const results = ref(null);
    const processingDetails = ref(null);
    const expandedStructures = ref({});
    const showStudentList = ref(false);
    const selectedStudentGroup = ref(null);

        
    // Store student exceptions in format: { groupName: { studentId: [excludedCategories] } }
    const studentExceptions = ref({});

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
      student_group: ''
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
        // Initialize fee plan and schedules for each structure
        if (data && data.success && data.fee_structures) {
          data.fee_structures.forEach(structure => {
            structure.selected = false;
            structure.selected_fee_plan = extractFeePlanFromName(structure.name) || '';
            structure.feeSchedules = [];
            if (structure.selected_fee_plan) {
              calculateFeeSchedulesForStructure(structure);
            }
          });
        }
      },
      onError: (err) => {
        errorMessage.value = err.messages?.[0] || 'Failed to load fee structures';
        console.error('Error loading fee structures:', err);
      }
    });

    const studentGroupsResource = createResource({
      url: 'school.al_ummah.api5.get_student_groups',
      onSuccess: (data) => {
        console.log('Student groups loaded:', data);
        // Add selected property to each group and initialize exceptions
        if (data && data.success && data.student_groups) {
          data.student_groups.forEach(group => {
            group.selected = true;
            // Initialize empty exceptions for each group
            if (!studentExceptions.value[group.name]) {
              studentExceptions.value[group.name] = {};
            }
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
    const feeSchedulesCount = computed(() => {
      if (feeStructuresResource.data && feeStructuresResource.data.success) {
        return feeStructuresResource.data.fee_schedules_count || 0;
      }
      return 0;
    });
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

    const selectedStructures = computed(() => {
      return feeStructuresList.value.filter(structure => 
        structure.selected && structure.selected_fee_plan && structure.feeSchedules && structure.feeSchedules.length > 0
      );
    });

    const selectedStructuresCount = computed(() => {
      return selectedStructures.value.length;
    });

    const selectedStudentGroups = computed(() => {
      return studentGroupsList.value.filter(group => group.selected);
    });

    const isFormValid = computed(() => {
      return formData.value.selected_class && 
             selectedStructuresCount.value > 0 &&
             selectedStudentGroups.value.length > 0;
    });

    // Methods
    // Add these to your methods section
function showInvoiceLinks(documents, documentType) {
  currentDocumentLinks.value = documents;
  currentDocumentType.value = documentType;
  showInvoiceLinksModal.value = true;
}

function closeInvoiceLinksModal() {
  showInvoiceLinksModal.value = false;
  currentDocumentLinks.value = [];
  currentDocumentType.value = '';
}

function getDocumentUrl(documentName, documentType) {
  const doctype = documentType.toLowerCase().replace(' ', '-');
  return `/app/${doctype}/${documentName}`;
}
    function extractFeePlanFromName(structureName) {
      const name = structureName.toLowerCase();
      if (name.includes('monthly')) return 'Monthly';
      if (name.includes('quarterly')) return 'Quarterly';
      if (name.includes('semi-annually') || name.includes('semi annually')) return 'Semi-Annually';
      if (name.includes('annually') || name.includes('annual')) return 'Annually';
      if (name.includes('term') || name.includes('term-wise')) return 'Term-Wise';
      return '';
    }

    function getInstallmentCount(feePlan) {
      const planConfig = {
        'Monthly': 12,
        'Quarterly': 4,
        'Semi-Annually': 2,
        'Annually': 1,
        'Term-Wise': 3
      };
      return planConfig[feePlan] || 1;
    }

    function calculateInstallmentAmount(amount, feePlan) {
      const installmentCount = getInstallmentCount(feePlan);
      return parseFloat((amount / installmentCount).toFixed(2));
    }

    function calculateFeeSchedulesForStructure(structure) {
      if (!structure.selected_fee_plan) return;

      const totalAmount = structure.total_amount;
      const feePlan = structure.selected_fee_plan;
      
      const distribution = getDistributionForFeePlan(feePlan, totalAmount);
      structure.feeSchedules = distribution.map(item => ({
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

    function getScheduleDescription(feePlan, index, dueDate = null) {
      // If we have a due date, use it to generate description
      if (dueDate) {
        const date = new Date(dueDate);
        const monthName = date.toLocaleDateString('en-US', { month: 'long' });
        const year = date.getFullYear();
        
        const descriptions = {
          'Monthly': `${monthName} ${year}`,
          'Quarterly': `Quarter ${Math.floor(index / 3) + 1} - ${monthName} ${year}`,
          'Semi-Annually': index === 0 ? `First Half - ${monthName} ${year}` : `Second Half - ${monthName} ${year}`,
          'Annually': `Annual Fee - ${year}`,
          'Term-Wise': `Term ${index + 1} - ${monthName} ${year}`
        };
        return descriptions[feePlan] || `${monthName} ${year} - Installment ${index + 1}`;
      }
      
      // Fallback to static descriptions if no due date
      const monthNames = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
      ];
      
      const staticDescriptions = {
        'Monthly': monthNames[index] || `Month ${index + 1}`,
        'Quarterly': `Quarter ${index + 1}`,
        'Semi-Annually': index === 0 ? 'First Half' : 'Second Half',
        'Annually': 'Annual Fee',
        'Term-Wise': `Term ${index + 1}`
      };
      return staticDescriptions[feePlan] || `Installment ${index + 1}`;
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

    function formatScheduleDate(dateString) {
      if (!dateString) return 'Not set';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        year: 'numeric'
      });
    }

    function onClassChange() {
      formData.value.student_group = '';
      results.value = null;
      successMessage.value = '';
      errorMessage.value = '';
      expandedStructures.value = {};
      studentExceptions.value = {}; // Reset exceptions when class changes

      if (formData.value.selected_class) {
        feeStructuresResource.update({
          params: { program: formData.value.selected_class }
        });
        feeStructuresResource.reload();
      } else {
        feeStructuresResource.data = null;
      }
    }

    function onStructureSelectionChange(structure) {
      if (!structure.selected) {
        // Clear fee plan and schedules when deselected
        structure.selected_fee_plan = '';
        structure.feeSchedules = [];
      } else if (structure.selected && !structure.selected_fee_plan) {
        // Auto-select fee plan if not already selected
        structure.selected_fee_plan = extractFeePlanFromName(structure.name) || '';
        if (structure.selected_fee_plan) {
          calculateFeeSchedulesForStructure(structure);
        }
      }

      // Load student groups when first structure is selected
      if (selectedStructuresCount.value > 0 && !studentGroupsResource.data) {
        loadStudentGroups();
      }
    }

    function onFeePlanChange(structure) {
      if (structure.selected_fee_plan) {
        calculateFeeSchedulesForStructure(structure);
      } else {
        structure.feeSchedules = [];
      }
    }

    function loadStudentGroups() {
      if (formData.value.selected_class) {
        studentGroupsResource.update({
          params: { program: formData.value.selected_class }
        });
        studentGroupsResource.reload();
      }
    }

    function toggleStructureDetails(structureName) {
      expandedStructures.value = {
        ...expandedStructures.value,
        [structureName]: !expandedStructures.value[structureName]
      };
    }

    function selectAllStructures() {
      feeStructuresList.value.forEach(structure => {
        structure.selected = true;
        if (!structure.selected_fee_plan) {
          structure.selected_fee_plan = extractFeePlanFromName(structure.name) || '';
          if (structure.selected_fee_plan) {
            calculateFeeSchedulesForStructure(structure);
          }
        }
      });
      
      // Load student groups after selecting all structures
      if (selectedStructuresCount.value > 0) {
        loadStudentGroups();
      }
    }

    function deselectAllStructures() {
      feeStructuresList.value.forEach(structure => {
        structure.selected = false;
        structure.selected_fee_plan = '';
        structure.feeSchedules = [];
      });
    }

    function selectAllGroups() {
      studentGroupsList.value.forEach(group => {
        group.selected = true;
      });
    }

    function deselectAllGroups() {
      studentGroupsList.value.forEach(group => {
        group.selected = false;
      });
    }

    function selectAllSchedules(structure) {
      if (structure.feeSchedules) {
        structure.feeSchedules.forEach(schedule => {
          schedule.selected = true;
        });
      }
    }

    function deselectAllSchedules(structure) {
      if (structure.feeSchedules) {
        structure.feeSchedules.forEach(schedule => {
          schedule.selected = false;
        });
      }
    }

    function getClassName(className) {
      const cls = classesList.value.find(c => c.name === className);
      return cls ? (cls.program_name || cls.name) : className;
    }

    function getFeePlanLabel(planValue) {
      const plan = feePlans.value.find(p => p.value === planValue);
      return plan ? plan.label : planValue;
    }

    function getSelectedSchedulesCount(structure) {
      if (structure.feeSchedules) {
        return structure.feeSchedules.filter(s => s.selected).length;
      }
      return 0;
    }

    function getTotalSchedulesCount() {
      return selectedStructures.value.reduce((total, structure) => {
        return total + getSelectedSchedulesCount(structure);
      }, 0);
    }

    // Student Fee Category Selection Methods
    function getAllFeeCategories() {
      const allCategories = [];
      selectedStructures.value.forEach(structure => {
        if (structure.components) {
          structure.components.forEach(component => {
            if (!allCategories.includes(component.fees_category)) {
              allCategories.push(component.fees_category);
            }
          });
        }
      });
      return allCategories;
    }

    function getSelectedStudentsCount(group) {
      const totalStudents = group.total_students || 0;
      const groupExceptions = studentExceptions.value[group.name] || {};
      const allCategories = getAllFeeCategories();
      
      if (allCategories.length === 0) return totalStudents;
      
      // Count students who have all categories excluded (completely excluded)
      const completelyExcludedStudents = Object.keys(groupExceptions).filter(studentId => {
        const excludedCategories = groupExceptions[studentId] || [];
        return excludedCategories.length === allCategories.length;
      }).length;
      
      return totalStudents - completelyExcludedStudents;
    }

    function getTotalStudents() {
      return selectedStudentGroups.value.reduce((total, group) => {
        return total + getSelectedStudentsCount(group);
      }, 0);
    }

    // ADD THE MISSING FUNCTION
    function getTotalExcludedStudents() {
      let totalExcluded = 0;
      selectedStudentGroups.value.forEach(group => {
        const totalStudents = group.total_students || 0;
        const selectedStudents = getSelectedStudentsCount(group);
        totalExcluded += (totalStudents - selectedStudents);
      });
      return totalExcluded;
    }

    function hasFeeCategoryExceptions(group) {
      const groupExceptions = studentExceptions.value[group.name];
      return groupExceptions && Object.keys(groupExceptions).length > 0;
    }

    function getExcludedCategoriesCount(group) {
      const groupExceptions = studentExceptions.value[group.name];
      if (!groupExceptions) return 0;
      
      let total = 0;
      Object.values(groupExceptions).forEach(categories => {
        total += categories.length;
      });
      return total;
    }

    function getTotalExcludedCategories() {
      let total = 0;
      selectedStudentGroups.value.forEach(group => {
        const groupExceptions = studentExceptions.value[group.name];
        if (groupExceptions) {
          Object.values(groupExceptions).forEach(categories => {
            total += categories.length;
          });
        }
      });
      return total;
    }

    function getTotalAmount() {
      return selectedStructures.value.reduce((total, structure) => {
        return total + (structure.total_amount || 0);
      }, 0);
    }

    // Student List Modal Methods
    function getInitialSelections(group) {
      if (!group) return {};
      
      const initialSelections = {};
      const allCategories = getAllFeeCategories();
      
      group.students?.forEach(student => {
        const studentId = student.student;
        const groupExceptions = studentExceptions.value[group.name] || {};
        const excludedCategories = groupExceptions[studentId] || [];
        
        // Calculate selected categories (all categories minus excluded ones)
        const selectedCategories = allCategories.filter(cat => 
          !excludedCategories.includes(cat)
        );
        
        initialSelections[studentId] = selectedCategories;
      });
      
      return initialSelections;
    }

    function openStudentList(group) {
      selectedStudentGroup.value = group;
      showStudentList.value = true;
    }

    function handleStudentListSave(exceptions) {
      if (selectedStudentGroup.value) {
        const groupName = selectedStudentGroup.value.name;
        
        // Store exceptions in the format: { groupName: { studentId: [excludedCategories] } }
        studentExceptions.value[groupName] = exceptions;
        
        console.log(`Saved fee category exceptions for ${groupName}:`, exceptions);
      }
      
      showStudentList.value = false;
    }

    function handleStudentListSelectionChange(selectedStudents) {
      // This can be used for real-time updates if needed
      console.log('Selection changed:', selectedStudents);
    }

    function createFeeSchedulesAndInvoices() {
      if (!isFormValid.value) return;
      
      processing.value = true;
      errorMessage.value = '';
      successMessage.value = '';
      results.value = null;

      const structureData = selectedStructures.value.map(structure => ({
        fee_structure_name: structure.name,
        fee_plan: structure.selected_fee_plan,
        due_dates: structure.feeSchedules
          .filter(s => s.selected)
          .map(s => s.due_date)
      }));

      const selectedGroups = selectedStudentGroups.value.map(g => g.name);
      
      // Prepare student exceptions data with fee categories
      const student_exceptions = {};
      selectedStudentGroups.value.forEach(group => {
        const groupExceptions = studentExceptions.value[group.name];
        if (groupExceptions && Object.keys(groupExceptions).length > 0) {
          student_exceptions[group.name] = groupExceptions;
        }
      });

      processingDetails.value = {
        class: getClassName(formData.value.selected_class),
        fee_structures: selectedStructures.value.map(s => s.name).join(', '),
        student_groups: selectedGroups.join(', '),
        total_students: getTotalStudents(),
        schedule_count: getTotalSchedulesCount(),
        excluded_categories: getTotalExcludedCategories()
      };

      createFeeSchedulesResource.submit({
        fee_structures: structureData,
        student_groups: selectedGroups,
        student_exceptions: student_exceptions
      });
    }

    function resetForm() {
      formData.value = {
        selected_class: '',
        student_group: ''
      };
      results.value = null;
      errorMessage.value = '';
      successMessage.value = '';
      processingDetails.value = null;
      expandedStructures.value = {};
      studentExceptions.value = {}; // Clear exceptions
      showStudentList.value = false;
      selectedStudentGroup.value = null;
      
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
      expandedStructures,
      showStudentList,
      selectedStudentGroup,
      classesResource,
      feeStructuresResource,
      studentGroupsResource,
      createFeeSchedulesResource,
      classesList,
      feeStructuresList,
      studentGroupsList,
      selectedStructures,
      selectedStructuresCount,
      selectedStudentGroups,
      isFormValid,
      feeSchedulesCount,
      onClassChange,
      onStructureSelectionChange,
      onFeePlanChange,
      toggleStructureDetails,
      selectAllStructures,
      deselectAllStructures,
      selectAllGroups,
      deselectAllGroups,
      selectAllSchedules,
      deselectAllSchedules,
      extractFeePlanFromName,
      getInstallmentCount,
      calculateInstallmentAmount,
      getScheduleDescription,
      getClassName,
      getFeePlanLabel,
      getSelectedSchedulesCount,
      getTotalSchedulesCount,
      getTotalStudents,
      getTotalExcludedStudents, // ADD THIS TO RETURN OBJECT
      getTotalExcludedCategories,
      getSelectedStudentsCount,
      getExcludedCategoriesCount,
      hasFeeCategoryExceptions,
      getTotalAmount,
      formatScheduleDate,
      openStudentList,
      handleStudentListSave,
      handleStudentListSelectionChange,
      getInitialSelections,
      createFeeSchedulesAndInvoices,
      resetForm
    };
  }
};
</script>

<style scoped>
/* Selection Controls */
.selection-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 0.375rem;
  border: 1px solid #e2e8f0;
}

.selection-count {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
  margin-left: auto;
}

.secondary-button.small {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}

.schedule-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 1rem;
}

/* Fee Structures Table */
.fee-structures-table {
  margin-bottom: 1rem;
}

.selected-row {
  background-color: #f0f9ff !important;
  border-left: 4px solid #3b82f6;
}

.fee-structure-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.fee-structure-name {
  font-weight: 600;
  color: #1f2937;
}

.fee-structure-meta {
  font-size: 0.875rem;
  color: #6b7280;
}

.total-amount {
  font-weight: 600;
  color: #059669;
  font-size: 1.1rem;
}

.table-select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background: white;
  font-size: 0.875rem;
}

.table-select:disabled {
  background-color: #f9fafb;
  color: #6b7280;
  cursor: not-allowed;
}

/* Enhanced Details Button */
.details-button {
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-weight: 500;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
  width: 100px; /* Fixed width for consistency */
}

.details-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #1d4ed8, #1e40af);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.4);
}

.details-button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.details-button .icon {
  font-size: 0.75rem;
  transition: transform 0.3s ease;
}

.details-button.expanded .icon {
  transform: rotate(180deg);
}
/* Expanded Details */
.fee-structure-expanded-details {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-top: none;
  border-radius: 0 0 0.5rem 0.5rem;
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.fee-structure-details-section {
  margin-bottom: 1.5rem;
}

.subsection-title {
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 1rem;
}

.subsubsection-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #4b5563;
  margin-bottom: 0.75rem;
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
  margin-top: 1rem;
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
  font-size: 0.875rem;
}

.components-table th {
  background: #f8fafc;
  font-weight: 600;
  color: #374151;
}

.components-table tr:last-child td {
  border-bottom: none;
}

.installment-calculation {
  font-size: 0.8rem;
  color: #6b7280;
  font-family: monospace;
}

.text-muted {
  color: #9ca3af;
}

/* Schedule Description */
.schedule-description {
  font-size: 0.875rem;
  color: #6b7280;
  font-style: italic;
}

/* Enhanced Summary Section */
.summary-section {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
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

.summary-item.highlight {
  background: #f0f9ff;
  border-radius: 0.5rem;
  padding: 0.75rem;
  border: 1px solid #bae6fd;
}

.summary-item.highlight .value {
  color: #0369a1;
  font-size: 1.1rem;
}

/* Selected Structures in Summary */
.selected-structures-in-summary {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.structures-summary-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.structure-summary-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1.25rem;
  transition: all 0.3s ease;
}

.structure-summary-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
}

.structure-summary-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.structure-name-plan {
  flex: 1;
}

.structure-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #1f2937;
}

.fee-plan-tag {
  background: #dbeafe;
  color: #1e40af;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.structure-amounts {
  text-align: right;
}

.total-amount {
  display: block;
  font-size: 1.25rem;
  font-weight: 700;
  color: #059669;
}

.schedule-count {
  display: block;
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.structure-components-summary {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.component-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f3f4f6;
}

.component-summary:last-child {
  border-bottom: none;
}

.component-name {
  font-size: 0.875rem;
  color: #374151;
  font-weight: 500;
}

.component-breakdown {
  font-size: 0.8rem;
  color: #6b7280;
  text-align: right;
  font-family: monospace;
}

/* Schedule Preview */
.schedule-preview {
  padding-top: 0.75rem;
  border-top: 1px solid #f1f5f9;
}

.schedule-preview-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
}

.schedule-dates {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.schedule-date-tag {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  color: #475569;
}

.more-schedules {
  background: #f1f5f9;
  color: #64748b;
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-style: italic;
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
  .selection-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }

  .selection-count {
    margin-left: 0;
    text-align: center;
  }

  .details-grid {
    grid-template-columns: 1fr;
  }
  
  .summary-grid {
    grid-template-columns: 1fr;
  }
  
  .structures-summary-grid {
    grid-template-columns: 1fr;
  }
  
  .components-table {
    overflow-x: auto;
  }
  
  .components-table table {
    min-width: 600px;
  }
  
  .fee-structure-info {
    min-width: 200px;
  }

  .structure-summary-header {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .structure-amounts {
    text-align: left;
    width: 100%;
  }
  
  .component-summary {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .schedule-dates {
    gap: 0.375rem;
  }
}
/* Student List Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 1000px;
  max-height: 90vh;
  overflow: hidden;
}

/* Edit Button */
.edit-button {
  padding: 0.375rem 0.75rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.edit-button:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-1px);
}

.edit-button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  transform: none;
}

/* Exceptions Badge */
.exceptions-badge {
  background: #fef3c7;
  color: #92400e;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  margin-left: 0.5rem;
}

/* Warning stat value */
.stat-value.warning {
  color: #d97706;
}

/* Responsive adjustments for student groups table */
@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    margin: 1rem;
  }
  
  /* Adjust student groups table for mobile */
  .preview-table th:nth-child(4),
  .preview-table td:nth-child(4),
  .preview-table th:nth-child(5),
  .preview-table td:nth-child(5) {
    display: none;
  }
}
.document-links {
  margin: 0.5rem 0;
}

.document-link {
  margin: 0.25rem 0;
}

.link {
  color: #3b82f6;
  text-decoration: none;
  font-size: 0.875rem;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.link:hover {
  text-decoration: underline;
}

.more-documents {
  font-size: 0.8rem;
  color: #6b7280;
  font-style: italic;
  margin-top: 0.25rem;
}
/* Fullscreen Modal Styles */
.fullscreen-modal {
  padding: 0 !important;
  align-items: stretch !important;
}

.fullscreen-content {
  width: 100% !important;
  max-width: none !important;
  height: 100% !important;
  max-height: none !important;
  border-radius: 0 !important;
  margin: 0 !important;
}

/* Fullscreen Modal with Scroll */
.fullscreen-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: stretch;
  justify-content: stretch;
  z-index: 1000;
  padding: 0 !important;
  margin: 0 !important;
  overflow: hidden !important;
}

.fullscreen-content {
  width: 100vw !important;
  height: 100vh !important;
  max-width: none !important;
  max-height: none !important;
  border-radius: 0 !important;
  margin: 0 !important;
  background: white;
  position: relative;
}

.scrollable-content {
  overflow-y: auto !important;
  overflow-x: hidden !important;
}

/* Ensure StudentList fills the container */
.scrollable-content > * {
  min-height: 100%;
  width: 100%;
}

/* Optional: Add some padding for better appearance */
.scrollable-content {
  padding: 0;
}
/* Info Note Styling */
.info-note {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 0.5rem;
  margin: 1rem 0;
}

.info-note .note-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.info-note .note-content {
  flex: 1;
  color: #0369a1;
  font-size: 0.875rem;
  line-height: 1.4;
}

.info-note .note-content strong {
  color: #075985;
}
</style>