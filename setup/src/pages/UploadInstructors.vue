<template>
  <div class="enrollment-container">
    <div class="scroll-view-content">
      <div class="header">
        <h1 class="title">Teacher Enrollment</h1>
      </div>

      <!-- File Upload Section -->
      <div class="form-card">
        <h2 class="form-title">Upload Teacher Data</h2>
        <div class="form-section">
          <div v-if="fileSelected" class="file-selected">
            <span>Selected file: {{ fileSelected.name }}</span>
            <button @click="removeFile" class="remove-file-btn">×</button>
          </div>
          <button class="secondary-button" @click="handleFileSelection">
            <span class="button-content">
              {{ fileSelected ? 'Change File' : 'Upload File 📤' }}
            </span>
          </button>

          <!-- Enroll Teachers Button -->
          <div class="enroll-button-section">
            <button 
              class="enroll-button" 
              @click="handleEnrollTeachers"
              :disabled="processing || !fileSelected"
            >
              <span class="button-content">
                <span v-if="processing" class="spinner"></span>
                {{ processing ? 'Processing...' : 'Enroll Teachers' }}
              </span>
            </button>
          </div>

          <!-- Main Message Display -->
          <div v-if="message" :class="['message', message.type]">
            {{ message.text }}
          </div>
        </div>
      </div>

      <!-- Enrollment Summary Card - SEPARATE CARD with ALL Results -->
      <div v-if="enrollmentSummary.total_processed > 0" class="form-card summary-card">
        <h2 class="form-title">Enrollment Summary</h2>
        <div class="summary-stats">
          <div class="stat-item">
            <span class="stat-label">Total Processed</span>
            <span class="stat-value">{{ enrollmentSummary.total_processed }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Successful</span>
            <span class="stat-value valid">{{ enrollmentSummary.successful }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Failed</span>
            <span class="stat-value warning">{{ enrollmentSummary.failed }}</span>
          </div>
        </div>

        <!-- Successfully Enrolled inside Summary Card -->
        <div v-if="enrolledTeachers.length > 0" class="success-details">
          <h4 class="section-title">Successfully Enrolled ({{ enrolledTeachers.length }})</h4>
          <div class="results-list">
            <div v-for="(teacher, index) in enrolledTeachers" :key="index" class="success-message">
              <span class="status-badge success">Success</span> {{ teacher }}
            </div>
          </div>
        </div>

        <!-- Enrollment Errors inside Summary Card -->
        <div v-if="failedEnrollments.length > 0" class="error-details">
          <h4 class="section-title">Enrollment Errors ({{ failedEnrollments.length }})</h4>
          <div class="results-list">
            <div v-for="(failure, index) in failedEnrollments" :key="index" class="error-message">
              <div class="error-student">
                <strong>{{ failure.instructor_data['First Name'] }} {{ failure.instructor_data['Middle Name'] }} {{ failure.instructor_data['Last Name'] }}</strong>
                <span class="student-details">(Email: {{ failure.instructor_data['Email'] }}, Mobile: {{ failure.instructor_data['Mobile'] }})</span>
              </div>
              <div class="error-text">
                <span class="status-badge error">Error</span> {{ failure.error }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- File Preview with Class/Division Selection and Mapping Pickers -->
      <div v-if="fileSelected && previewData.length > 0" class="form-card preview-card">
        <h2 class="form-title">File Preview (First 100 rows)</h2>
        
        <!-- Summary Stats -->
        <div class="summary-stats">
          <div class="stat-item">
            <span class="stat-label">Total Rows:</span>
            <span class="stat-value">{{ previewData.length }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Ready to Enroll:</span>
            <span class="stat-value valid">{{ validRowsCount }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Class Teachers:</span>
            <span class="stat-value info">{{ classTeachersCount }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Need Attention:</span>
            <span class="stat-value warning" 
                  style="cursor: pointer;" 
                  @click="showErrorTeachersList = !showErrorTeachersList"
                  :title="invalidRowsCount > 0 ? 'Click to view teachers with errors' : ''">
              {{ invalidRowsCount }}
              <span v-if="invalidRowsCount > 0" class="error-indicator">⚠️</span>
            </span>
          </div>
        </div>

        <!-- Error Teachers Card - Scrollable like Enrollment Errors -->
        <div v-if="showErrorTeachersList && errorRows.length > 0" class="error-students-card">
          <h4 class="section-title">Teachers with Errors ({{ invalidRowsCount }})</h4>
          <div class="error-details" style="max-height: 200px; overflow-y: auto;">
            <div class="results-list">
              <div v-for="(row, rowIndex) in errorRows" :key="rowIndex" class="error-message">
                <div class="error-student">
                  <strong>{{ getTeacherFullName(row) }}</strong>
                  <span class="student-details">
                    (Email: {{ getTeacherEmail(row) }}, Mobile: {{ getTeacherMobile(row) }})
                  </span>
                </div>
              <div class="error-text">
                <span class="status-badge warning">Warning</span>
                <span v-if="getRowError(row).includes(';')" class="multiple-errors">
                  {{ getRowError(row) }}
                </span>
                <span v-else>
                  {{ getRowError(row) }}
                </span>
              </div>
              </div>
            </div>
          </div>
        </div>

        <div class="instructions">
          <p>💡 <strong>Note:</strong> Class and Division are optional fields. Only assign them for teachers who are class teachers.</p>
        </div>

        <!-- Space between error list and table -->
        <div class="table-spacing" v-if="showErrorTeachersList && errorRows.length > 0"></div>

        <div class="table-container-wrapper">
          <div class="table-scroll-container">
            <div class="table-container">
              <table class="preview-table">
                <thead>
                  <tr>
                    <th class="actions">Actions</th>
                    <th class="status-cell">Status</th>
                    <th>Class/Program <span class="optional">(Optional)</span></th>
                    <th>Division/Student Group <span class="optional">(Optional)</span></th>
                    <th v-for="(header, index) in filteredHeaders" :key="'letter-'+index">
                      {{ getExcelColumnLetter(index) }}
                    </th>
                  </tr>
                  <tr>
                    <th class="actions"></th>
                    <th class="status-cell"></th>
                    <th>Class/Program</th>
                    <th>Division/Student Group</th>
                    <th v-for="(header, index) in filteredHeaders" :key="'header-'+index">
                      <select
                        v-model="filteredMappings[index].type"
                        class="table-select"
                        @change="updateMapping(filteredMappings[index].originalIndex, 'type', $event.target.value)"
                      >
                        <option :value="null">Select Field</option>
                        <option v-for="(option, i) in options" :key="i" :value="option">
                          {{ option }}
                        </option>
                      </select>
                      <span class="header-label">{{ header }}</span>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, rowIndex) in previewData" :key="rowIndex" 
                      :class="getRowStatusClass(row)">
                    <td class="actions">
                      <button @click="deleteRow(rowIndex)" class="trash-icon">
                        Delete
                      </button>
                    </td>
                    <td class="status-cell">
                      <span v-if="row._status === 'success'" class="status-badge success">Success</span>
                      <span v-else-if="row._status === 'error'" class="status-badge error">Error</span>
                      <span v-else-if="!isRowValid(row)" class="status-badge warning">Warning</span>
                      <span v-else class="status-badge pending">Pending</span>
                      <div v-if="row._error" class="error-tooltip">{{ row._error }}</div>
                    </td>
                    <td>
                      <select 
                        v-model="row.className" 
                        class="table-select"
                        @change="onClassChange(rowIndex)"
                        :disabled="classesResource.loading"
                      >
                        <option :value="null">Not a Class Teacher</option>
                        <option v-for="cls in classes" :key="cls.name" :value="cls.name">
                          {{ cls.name }}
                        </option>
                      </select>
                    </td>
                    <td>
                      <select 
                        v-model="row.divisionName" 
                        class="table-select"
                        :disabled="!row.className || divisionsResource.loading"
                      >
                        <option :value="null">Select Division</option>
                        <option v-for="div in row.divisions" :key="div.name" :value="div.name">
                          {{ div.name }}
                        </option>
                      </select>
                      <div v-if="row.className && !row.divisionName" class="field-hint">
                        Select division if this teacher is a class teacher
                      </div>
                    </td>
                    <td v-for="(header, colIndex) in filteredHeaders" :key="colIndex">
                      <input
                        v-model="row[header]"
                        class="table-input"
                        @input="handleCellEdit(rowIndex, header, $event.target.value)"
                        @blur="markRowAsTouched(rowIndex)"
                        :placeholder="row[header] || '-'"
                      />
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading Modal -->
      <div v-if="processing" class="loading-overlay">
        <div class="loading-modal">
          <div class="loading-spinner"></div>
          <h3 class="loading-title">Enrolling Teachers</h3>
          <p class="loading-description">Please wait while we process the teacher data...</p>
        </div>
      </div>

      <!-- Success/Error Result Modal -->
      <div v-if="showResultModal" class="modal-overlay">
        <div class="result-modal">
          <div v-if="resultModalType === 'success'" class="success-icon">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <div v-else class="error-icon">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h3 class="result-title">{{ resultModalTitle }}</h3>
          <p class="result-description">{{ resultModalDescription }}</p>
          <div class="modal-actions">
            <button 
              v-if="resultModalType === 'success'" 
              class="success-button" 
              @click="closeResultModal"
            >
              Continue
            </button>
            <button 
              v-else 
              class="primary-button" 
              @click="closeResultModal"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { createResource } from 'frappe-ui';
import { reactive, ref, onMounted, computed } from 'vue';
import * as XLSX from "xlsx";
import '@/styles/form.css';
import { 
  parseDate, 
  formatDateForAPI, 
  validateDateField, 
  validDate, 
  getTodayDate 
} from '@/utils/dateUtils';

export default {
  setup() {
    // Reactive state
    const showErrorTeachersList = ref(false);
    const mappings = ref([]);
    const fileSelected = ref(null);
    const options = ref([
      "First Name", 
      "Middle Name", 
      "Last Name", 
      "Full Name", 
      "Gender", 
      "Mobile", 
      "Email", 
      "Date of Birth", 
      "Date of Joining", 
      "PAN Number", 
      "Bank Name", 
      "Bank A/C No.", 
      "IFSC Code", 
      "Current Address", 
      "Permanent Address", 
      "Blood Group", 
      "Attendance Device ID (Biometric/RF tag ID)", 
      "Qualification (Education)", 
      "School/University (Education)"
    ]);
    const message = ref(null);
    const previewData = ref([]);
    const previewHeaders = ref([]);
    const classes = ref([]);
    const editHistory = ref([]);
    const pendingEdits = ref([]);
    
    // Enhanced state for better error handling
    const enrolledTeachers = ref([]);
    const failedEnrollments = ref([]);
    const enrollmentSummary = ref({
      total_processed: 0,
      successful: 0,
      failed: 0
    });
    const processing = ref(false);
    const showResultModal = ref(false);
    const resultModalType = ref('success');
    const resultModalTitle = ref('');
    const resultModalDescription = ref('');

    // Computed properties
    const validRowsCount = computed(() => {
      return previewData.value.filter(row => isRowValid(row)).length;
    });

    const classTeachersCount = computed(() => {
      return previewData.value.filter(row => row.className && row.divisionName).length;
    });

    const invalidRowsCount = computed(() => {
      return previewData.value.filter(row => !isRowValid(row)).length;
    });

    const errorRows = computed(() => {
      return previewData.value.filter(row => !isRowValid(row));
    });

    // Filter out empty/undefined columns
    const filteredHeaders = computed(() => {
      return previewHeaders.value.filter((header, index) => {
        // Keep column if it has data in any row or has a mapping
        const hasData = previewData.value.some(row => {
          const value = row[header];
          return value !== undefined && value !== null && value !== '' && value.toString().trim() !== '';
        });
        const hasMapping = mappings.value[index]?.type;
        return hasData || hasMapping;
      });
    });

    const filteredMappings = computed(() => {
      return mappings.value.map((mapping, index) => ({
        ...mapping,
        originalIndex: index
      })).filter((mapping, index) => {
        const header = previewHeaders.value[index];
        const hasData = previewData.value.some(row => {
          const value = row[header];
          return value !== undefined && value !== null && value !== '' && value.toString().trim() !== '';
        });
        const hasMapping = mapping.type;
        return hasData || hasMapping;
      });
    });

    // Methods for error teachers display
    function getTeacherFullName(row) {
      const teacher = prepareTeacherData(row);
      return `${teacher['First Name'] || ''} ${teacher['Middle Name'] || ''} ${teacher['Last Name'] || ''}`.trim() || 'Unknown Teacher';
    }

    function getTeacherEmail(row) {
      const teacher = prepareTeacherData(row);
      return teacher['Email'] || 'N/A';
    }

    function getTeacherMobile(row) {
      const teacher = prepareTeacherData(row);
      return teacher['Mobile'] || 'N/A';
    }

    function getRowError(row) {
      const errors = [];
      
      // Check for missing required fields
      const requiredFields = [
        'Mobile', 
        'Email', 
        'Gender', 
        'First Name', 
        'Last Name', 
        "Attendance Device ID (Biometric/RF tag ID)",
        "Date of Birth",
        "Date of Joining"
      ];
      
      requiredFields.forEach(field => {
        const mappingIndex = mappings.value.findIndex(m => m.type === field);
        
        if (mappingIndex === -1) {
          // Field is not mapped at all
          errors.push(`${field} not mapped`);
        } else {
          const columnIndex = XLSX.utils.decode_col(mappings.value[mappingIndex].column);
          const columnName = previewHeaders.value[columnIndex];
          const value = row[columnName];
          
          if (!value || value.toString().trim() === '') {
            errors.push(`${field} missing`);
          } else {
            // Field-specific validation
            switch (field) {
              case 'Mobile':
                const mobileDigits = value.toString().replace(/\D/g, '');
                if (mobileDigits.length < 10) errors.push('Invalid mobile number');
                break;
                
              case 'Email':
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(value.toString().trim())) errors.push('Invalid email format');
                break;
                
              case 'Gender':
                const gender = value.toString().trim().toLowerCase();
                const validGenders = ['male', 'female', 'other', 'm', 'f', 'o'];
                if (!validGenders.includes(gender)) errors.push('Invalid gender');
                break;
                
              case 'Date of Birth':
                const dobValidation = validateDateField(value, 'Date of Birth');
                if (!dobValidation.isValid) errors.push(dobValidation.error);
                break;
                
              case 'Date of Joining':
                const dojValidation = validateDateField(value, 'Date of Joining');
                if (!dojValidation.isValid) errors.push(dojValidation.error);
                break;
            }
          }
        }
      });
      
      // Check for class/division validation
      if (row.className && !row.divisionName) {
        errors.push('Class selected but no division assigned');
      }
      
      if (errors.length > 0) {
        return errors.join('; ');
      }
      
      return 'Check field mappings';
    }

    // API Resources
    const classesResource = createResource({
      url: 'school.al_ummah.api4.get_classes',
      params: { values: {} },
      onSuccess: (data) => {
        classes.value = Array.isArray(data) ? data : [];
        console.log('Classes loaded:', classes.value);
        if (!classes.value.length) {
          showMessage('No classes available', 'error');
        }
      },
      onError: (err) => {
        console.error('Error fetching classes:', err);
        classes.value = [];
        showMessage(`Error fetching classes: ${err.messages?.[0] || 'Unknown error'}`, 'error');
      }
    });

    const divisionsResource = createResource({
      url: 'school.al_ummah.api4.get_divisions1',
      params: {
        values: {
          classId: '' // Will be updated dynamically
        }
      },
      onSuccess: (data) => {
        return Array.isArray(data) ? data : [];
      },
      onError: (err) => {
        console.error('Error fetching divisions:', err);
        showMessage(`Error fetching divisions: ${err.messages?.[0] || 'Unknown error'}`, 'error');
        return [];
      }
    });

    const enrollTeachersResource = createResource({
      url: 'school.al_ummah.api4.bulk_enroll_instructors',
      method: 'POST',
      onSuccess: (data) => {
        console.log('Bulk enrollment successful:', data);
        processing.value = false;
        
        if (data && data.success) {
          // Update enrollment results
          enrolledTeachers.value = data.enrolled_instructors || [];
          failedEnrollments.value = data.failed_enrollments || [];
          enrollmentSummary.value = data.summary || {
            total_processed: data.enrolled_instructors.length + data.failed_enrollments.length,
            successful: data.enrolled_instructors.length,
            failed: data.failed_enrollments.length
          };
          
          // Update row statuses based on bulk response
          updateRowStatusesFromBulkResponse(data.enrolled_instructors, data.failed_enrollments);
          
          // Show appropriate message and modal
          if (failedEnrollments.value.length === 0) {
            showMessage(`Successfully enrolled all ${enrolledTeachers.value.length} teachers!`, 'success');
            showResultModalFunc('success', 'Enrollment Complete', `Successfully enrolled all ${enrolledTeachers.value.length} teachers!`);
          } else {
            showMessage(`Completed: ${enrolledTeachers.value.length} successful, ${failedEnrollments.value.length} failed.`, 'warning');
            showResultModalFunc('warning', 'Enrollment Completed with Errors', 
              `Completed with ${enrolledTeachers.value.length} successful enrollments and ${failedEnrollments.value.length} failures.`);
          }
        } else {
          showMessage('Bulk enrollment completed with issues', 'warning');
        }
      },
      onError: (err) => {
        console.error('Error in bulk enrollment:', err);
        processing.value = false;
        showMessage(`Bulk enrollment failed: ${err.messages?.[0] || err.message || 'Unknown error'}`, 'error');
        showResultModalFunc('error', 'Bulk Enrollment Failed', err.messages?.[0] || err.message || 'Unknown error occurred during bulk enrollment.');
      }
    });

    // Fetch initial data on mount
    onMounted(() => {
      classesResource.reload();
    });

    // Methods
    async function onClassChange(rowIndex) {
      const row = previewData.value[rowIndex];
      
      if (row.className) {
        row.divisionName = null;
        try {
          divisionsResource.update({
            params: {
              values: {
                classId: row.className
              }
            }
          });
          const response = await divisionsResource.reload();
          row.divisions = Array.isArray(response) ? response : [];
        } catch (error) {
          console.error("Error fetching divisions:", error);
          showMessage(`Error fetching divisions for ${row.className}`, "error");
        }
      } else {
        row.divisionName = null;
        row.divisions = [];
      }
    }

    function getExcelColumnLetter(index) {
      let letter = '';
      while (index >= 0) {
        letter = String.fromCharCode(65 + (index % 26)) + letter;
        index = Math.floor(index / 26) - 1;
      }
      return letter;
    }

    async function handleFileSelection() {
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = '.xlsx,.xls';

      input.onchange = async (e) => {
        const file = e.target.files[0];
        if (file) {
          fileSelected.value = file;
          showMessage(null);
          enrolledTeachers.value = [];
          failedEnrollments.value = [];
          enrollmentSummary.value = { total_processed: 0, successful: 0, failed: 0 };
          try {
            const { data, headers } = await readExcelFile(file);
            previewData.value = data.slice(0, 100).map(row => ({
              ...row,
              className: null,
              divisionName: null,
              divisions: [],
              _status: null,
              _error: null,
              _touched: false
            }));
            previewHeaders.value = headers;
            mappings.value = headers.map((_, index) => ({
              type: null,
              column: XLSX.utils.encode_col(index)
            }));
            autoDetectMappings(headers, data.slice(0, 5));
          } catch (error) {
            console.error("Error loading preview:", error);
            showMessage("Error loading file preview", "error");
          }
        }
      };

      input.click();
    }

    function autoDetectMappings(headers, sampleData) {
      const fieldPatterns = {
        "First Name": ["first", "fname", "given", "firstname"],
        "Middle Name": ["middle", "mname", "midname"],
        "Last Name": ["last", "lname", "surname", "family", "lastname"],
        "Full Name": ["full name", "name", "teacher name"],
        "Email": ["email", "e-mail", "mail"],
        "Mobile": ["mobile", "phone", "cell", "contact"],
        "Date of Birth": ["dob", "birth", "birthdate", "date of birth"],
        "Gender": ["gender", "sex"],
        "Date of Joining": ["doj", "joining", "start date"],
        "PAN Number": ["pan", "pan no", "pan number"],
        "Bank Name": ["bank", "bank name"],
        "Bank A/C No.": ["account", "ac no", "bank account", "account no"],
        "IFSC Code": ["ifsc", "code"],
        "Current Address": ["current address", "address", "present address"],
        "Permanent Address": ["permanent address", "home address"],
        "Blood Group": ["blood", "blood group"],
        "Attendance Device ID (Biometric/RF tag ID)": ["attendance id", "biometric", "rfid", "device id"],
        "Qualification (Education)": ["qualification", "education", "degree"],
        "School/University (Education)": ["school", "university", "institution"]
      };

      headers.forEach((header, index) => {
        if (!header) return;
        const headerLower = header.toString().toLowerCase();
        for (const [field, patterns] of Object.entries(fieldPatterns)) {
          if (patterns.some(pattern => headerLower.includes(pattern))) {
            mappings.value[index].type = field;
            break;
          }
        }
      });
    }

    function removeFile() {
      fileSelected.value = null;
      previewData.value = [];
      previewHeaders.value = [];
      mappings.value = [];
      editHistory.value = [];
      pendingEdits.value = [];
      enrolledTeachers.value = [];
      failedEnrollments.value = [];
      enrollmentSummary.value = { total_processed: 0, successful: 0, failed: 0 };
      showMessage(null);
    }

    function isRowValid(row) {
      // Required fields
      const requiredFields = [
        'Mobile', 
        'Email', 
        'Gender', 
        'First Name', 
        'Last Name', 
        "Attendance Device ID (Biometric/RF tag ID)",
        "Date of Birth",
        "Date of Joining"
      ];
      
      // Check if all required fields are mapped
      const mappedFields = mappings.value.map(m => m.type).filter(type => type);
      const missingMappings = requiredFields.filter(field => !mappedFields.includes(field));
      
      if (missingMappings.length > 0) {
        return false;
      }
      
      const teacher = prepareTeacherData(row);
      
      // Validate required fields
      for (const field of requiredFields) {
        const value = teacher[field];
        
        // Check if field has value
        if (!value || value.toString().trim() === '') {
          return false;
        }
        
        // Field-specific validation
        switch (field) {
          case 'Mobile':
            const mobileDigits = value.toString().replace(/\D/g, '');
            if (mobileDigits.length < 10) return false;
            break;
            
          case 'Email':
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value.toString().trim())) return false;
            break;
            
          case 'Gender':
            const gender = value.toString().trim().toLowerCase();
            const validGenders = ['male', 'female', 'other', 'm', 'f', 'o'];
            if (!validGenders.includes(gender)) return false;
            break;
            
          case 'Date of Birth':
            const dobValidation = validateDateField(value, 'Date of Birth');
            if (!dobValidation.isValid) return false;
            break;
            
          case 'Date of Joining':
            const dojValidation = validateDateField(value, 'Date of Joining');
            if (!dojValidation.isValid) return false;
            break;
        }
      }
      
      // Validate class/division relationship
      if (row.className && !row.divisionName) {
        return false;
      }
      
      return true;
    }

    function markRowAsTouched(rowIndex) {
      if (previewData.value[rowIndex]) {
        previewData.value[rowIndex]._touched = true;
      }
    }

    function getRowStatusClass(row) {
      // Show enrollment success
      if (row._status === 'success') return 'row-success';
      // Show enrollment error (but don't interfere with field validation)
      if (row._enrollment_status === 'error') return 'row-enrollment-error';
      // Show field validation errors
      if (!isRowValid(row)) return 'row-invalid';
      return '';
    }

    function prepareTeacherData(row) {
      const teacher = {
        "First Name": "",
        "Middle Name": "",
        "Last Name": "",
        "Full Name": "",
        "Gender": "",
        "Mobile": "",
        "Email": "",
        "Date of Birth": "",
        "Date of Joining": "",
        "PAN Number": "",
        "Bank Name": "",
        "Bank A/C No.": "",
        "IFSC Code": "",
        "Current Address": "",
        "Permanent Address": "",
        "Blood Group": "",
        "Attendance Device ID (Biometric/RF tag ID)": "",
        "Qualification (Education)": "",
        "School/University (Education)": "",
        "Class": row.className || "",
        "Division": row.divisionName || "",
      };

      mappings.value.forEach(({ type, column }, index) => {
        if (type && teacher.hasOwnProperty(type)) {
          try {
            const columnIndex = XLSX.utils.decode_col(column);
            const columnName = previewHeaders.value[columnIndex];
            let value = row[columnName]?.toString().trim() || '';
            
            // Use utility functions for date handling
            if (type === 'Date of Birth' || type === 'Date of Joining') {
              const parsedDate = parseDate(value);
              value = parsedDate ? formatDateForAPI(parsedDate) : '';
            }
            
            teacher[type] = value;
          } catch (error) {
            console.error(`Error mapping column ${column} for type ${type}:`, error);
          }
        }
      });

      return teacher;
    }

    function updateRowStatusesFromBulkResponse(enrolledTeachers, failedEnrollments) {
      console.log('Updating row statuses from bulk response...');

      // Reset ALL statuses completely to avoid mixing enrollment and validation errors
      previewData.value.forEach(row => {
        row._status = null;
        row._error = null;
      });

      // Update successful enrollments
      enrolledTeachers.forEach(teacherName => {
        const rowIndex = findRowIndexByTeacherName(teacherName);
        if (rowIndex !== -1) {
          previewData.value[rowIndex]._status = 'success';
          previewData.value[rowIndex]._error = null;
        }
      });

      // Update failed enrollments - BUT use a different property to avoid conflict
      failedEnrollments.forEach(failure => {
        const rowIndex = findRowIndexByTeacherData(failure.instructor_data);
        if (rowIndex !== -1) {
          // Use a separate property for enrollment errors
          previewData.value[rowIndex]._enrollment_status = 'error';
          previewData.value[rowIndex]._enrollment_error = failure.error || 'Unknown error';
        }
      });
    }

    function findRowIndexByTeacherName(teacherName) {
      return previewData.value.findIndex(row => {
        const rowTeacherData = prepareTeacherData(row);
        const rowFullName = `${rowTeacherData['First Name']} ${rowTeacherData['Middle Name']} ${rowTeacherData['Last Name']}`.trim();
        return rowFullName === teacherName;
      });
    }

    function findRowIndexByTeacherData(teacherData) {
      return previewData.value.findIndex(row => {
        const rowTeacherData = prepareTeacherData(row);
        return rowTeacherData['Email'] === teacherData['Email'] && 
               rowTeacherData['First Name'] === teacherData['First Name'] &&
               rowTeacherData['Last Name'] === teacherData['Last Name'];
      });
    }

    function showResultModalFunc(type, title, description) {
      resultModalType.value = type;
      resultModalTitle.value = title;
      resultModalDescription.value = description;
      showResultModal.value = true;
    }

    function closeResultModal() {
      showResultModal.value = false;
      resultModalType.value = 'success';
      resultModalTitle.value = '';
      resultModalDescription.value = '';
    }

    async function handleEnrollTeachers() {
      console.log('Enroll button clicked');

      // Reset previous results
      enrolledTeachers.value = [];
      failedEnrollments.value = [];
      enrollmentSummary.value = { total_processed: 0, successful: 0, failed: 0 };
      processing.value = true;
      
      // Reset row statuses
      previewData.value.forEach(row => {
        row._status = null;
        row._error = null;
      });

      // Define required fields
      const requiredFields = [
        'Mobile', 
        'Email', 
        'Gender', 
        'First Name', 
        'Last Name', 
        "Attendance Device ID (Biometric/RF tag ID)",
        "Date of Birth",
        "Date of Joining"
      ];

      // Check if all required fields are mapped
      const mappedFields = mappings.value.map(m => m.type).filter(type => type);
      const missingFields = requiredFields.filter(field => !mappedFields.includes(field));

      if (missingFields.length > 0) {
        const msg = `Please map the following required fields: ${missingFields.join(', ')}`;
        console.error(msg);
        showMessage(msg, 'error');
        processing.value = false;
        return;
      }

      // Validate that we have data to process
      if (!fileSelected.value) {
        const msg = 'Please select a file first';
        console.error(msg);
        showMessage(msg, 'error');
        processing.value = false;
        return;
      }

      if (previewData.value.length === 0) {
        showMessage('No data available to enroll', 'error');
        processing.value = false;
        return;
      }

      // Additional validation: Check for invalid dates
      const invalidDateRows = previewData.value.filter(row => {
        const teacher = prepareTeacherData(row);
        
        // Date of Birth validation
        const dobValidation = teacher['Date of Birth'] && teacher['Date of Birth'].toString().trim() !== '' 
          ? validateDateField(teacher['Date of Birth'], 'Date of Birth')
          : { isValid: false, error: 'Date of Birth is required' };
          
        // Date of Joining validation
        const dojValidation = teacher['Date of Joining'] && teacher['Date of Joining'].toString().trim() !== ''
          ? validateDateField(teacher['Date of Joining'], 'Date of Joining')
          : { isValid: false, error: 'Date of Joining is required' };
          
        return !dobValidation.isValid || !dojValidation.isValid;
      });

      if (invalidDateRows.length > 0) {
        showMessage(`${invalidDateRows.length} rows have invalid dates. Please correct the dates before enrolling.`, 'warning');
        // Mark rows with invalid dates as error
        invalidDateRows.forEach(row => {
          const rowIndex = previewData.value.indexOf(row);
          if (rowIndex !== -1) {
            const teacher = prepareTeacherData(row);
            
            let errorMsg = '';
            
            // Check Date of Birth
            if (!teacher['Date of Birth'] || teacher['Date of Birth'].toString().trim() === '') {
              errorMsg += 'Date of Birth is required. ';
            } else {
              const dobValidation = validateDateField(teacher['Date of Birth'], 'Date of Birth');
              if (!dobValidation.isValid) errorMsg += dobValidation.error + ' ';
            }
            
            // Check Date of Joining
            if (!teacher['Date of Joining'] || teacher['Date of Joining'].toString().trim() === '') {
              errorMsg += 'Date of Joining is required. ';
            } else {
              const dojValidation = validateDateField(teacher['Date of Joining'], 'Date of Joining');
              if (!dojValidation.isValid) errorMsg += dojValidation.error;
            }
            
            previewData.value[rowIndex]._status = 'error';
            previewData.value[rowIndex]._error = errorMsg.trim();
          }
        });
        processing.value = false;
        return;
      }

      // Validate that rows with class selected also have division selected
      const invalidRows = previewData.value.filter(row => !isRowValid(row));
      if (invalidRows.length > 0) {
        showMessage(`${invalidRows.length} rows have class selected but no division. Please either select a division or remove the class assignment.`, 'warning');
        // Mark invalid rows as touched to show validation errors
        invalidRows.forEach(row => row._touched = true);
        processing.value = false;
        return;
      }

      try {
        showMessage('Starting bulk enrollment process...', 'info');
        
        // Process all valid rows
        const validRows = previewData.value.filter(row => isRowValid(row));
        
        if (validRows.length === 0) {
          showMessage('No valid rows to enroll. Please check your data and mappings.', 'warning');
          processing.value = false;
          return;
        }

        console.log(`Starting bulk enrollment for ${validRows.length} teachers...`);
        
        // Prepare teachers data for bulk enrollment
        const teachersData = validRows.map(row => {
          const teacher = prepareTeacherData(row);
          return teacher;
        });

        // Perform bulk enrollment
        await enrollTeachersResource.submit({
          teachers: teachersData,
          mappings: Object.fromEntries(
            mappings.value
              .filter(mapping => mapping.type)
              .map(mapping => [mapping.type, mapping.column])
          )
        });

      } catch (error) {
        console.error('Bulk enrollment process error:', error);
        showMessage(`Bulk enrollment process failed: ${error.message || 'Unknown error'}`, 'error');
        showResultModalFunc('error', 'Bulk Enrollment Process Failed', error.message || 'Unknown error occurred during enrollment.');
        processing.value = false;
      }
    }

    function readExcelFile(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();

        reader.onload = (e) => {
          try {
            const data = new Uint8Array(e.target.result);
            const workbook = XLSX.read(data, { type: 'array', sheetStubs: true });
            const sheet = workbook.Sheets[workbook.SheetNames[0]];
            const range = XLSX.utils.decode_range(sheet['!ref']);

            let headerRow = 0;
            for (let R = range.s.r; R <= range.e.r; ++R) {
              let hasData = false;
              for (let C = range.s.c; C <= range.e.c; ++C) {
                const cell = sheet[XLSX.utils.encode_cell({c: C, r: R})];
                if (cell && cell.v !== undefined && cell.v !== null && cell.v !== "") {
                  hasData = true;
                  break;
                }
              }
              if (hasData) {
                headerRow = R;
                break;
              }
            }

            const headers = [];
            for (let C = range.s.c; C <= range.e.c; ++C) {
              const cell = sheet[XLSX.utils.encode_cell({c: C, r: headerRow})];
              headers.push(cell ? String(cell.v).trim() : `Column ${C+1}`);
            }

            const jsonData = [];
            for (let R = headerRow + 1; R <= range.e.r; ++R) {
              const row = {};
              let hasData = false;

              for (let C = range.s.c; C <= range.e.c; ++C) {
                const cell = sheet[XLSX.utils.encode_cell({c: C, r: R})];
                const header = headers[C - range.s.c];
                row[header] = cell ? (cell.v === undefined ? '' : cell.v) : '';
                if (row[header] !== '') {
                  hasData = true;
                }
              }

              if (hasData) {
                jsonData.push(row);
              }
            }

            resolve({
              data: jsonData,
              headers: headers
            });
          } catch (error) {
            reject(error);
          }
        };

        reader.onerror = (error) => reject(error);
        reader.readAsArrayBuffer(file);
      });
    }

    function updateMapping(index, key, value) {
      mappings.value[index] = {
        ...mappings.value[index],
        [key]: value,
        column: XLSX.utils.encode_col(index)
      };
    }

    function deleteRow(rowIndex) {
      previewData.value.splice(rowIndex, 1);
      editHistory.value = editHistory.value.filter(edit => edit.rowIndex !== rowIndex);
      pendingEdits.value = pendingEdits.value.filter(edit => edit.rowIndex !== rowIndex);
      showMessage('Row deleted', 'success');
    }

    function showMessage(text, type = "info") {
      message.value = text ? { text, type } : null;
      if (text && type !== "error" && type !== "success") {
        setTimeout(() => showMessage(null), 5000);
      }
    }

    function handleCellEdit(rowIndex, header, newValue) {
      const row = previewData.value[rowIndex];
      const oldValue = row[header] || '';

      if (oldValue !== newValue) {
        const edit = {
          rowIndex,
          column: header,
          oldValue,
          newValue,
          timestamp: new Date().toISOString(),
        };
        editHistory.value.push(edit);
        pendingEdits.value.push(edit);
        console.log('Cell edit recorded:', edit);
        debouncedSendCellUpdate();
      }
    }

    function debounce(fn, wait) {
      let timeout;
      return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => fn.apply(this, args), wait);
      };
    }

    const debouncedSendCellUpdate = debounce(sendCellUpdate, 500);

    async function sendCellUpdate() {
      if (pendingEdits.value.length === 0) return;

      try {
        const lastEdit = pendingEdits.value[pendingEdits.value.length - 1];
        const row = previewData.value[lastEdit.rowIndex];
        const teacher = prepareTeacherData(row);
        
        // Use bulk enrollment with single teacher for updates
        await enrollTeachersResource.submit({
          teachers: [teacher],
          mappings: Object.fromEntries(
            mappings.value
              .filter(mapping => mapping.type)
              .map(mapping => [mapping.type, mapping.column])
          )
        });
        
        // Clear pending edits on success
        pendingEdits.value = [];
        
      } catch (error) {
        console.error('Error sending cell update:', error);
        showMessage(`Failed to save cell update: ${error.message || 'Unknown error'}`, 'error');
      }
    }

    return {
      mappings,
      fileSelected,
      options,
      message,
      previewData,
      previewHeaders,
      classes,
      editHistory,
      pendingEdits,
      enrolledTeachers,
      failedEnrollments,
      enrollmentSummary,
      processing,
      showResultModal,
      resultModalType,
      resultModalTitle,
      resultModalDescription,
      showErrorTeachersList,
      validRowsCount,
      classTeachersCount,
      invalidRowsCount,
      errorRows,
      filteredHeaders,
      filteredMappings,
      getTeacherFullName,
      getTeacherEmail,
      getTeacherMobile,
      getRowError,
      classesResource,
      divisionsResource,
      enrollTeachersResource,
      onClassChange,
      getExcelColumnLetter,
      handleFileSelection,
      removeFile,
      handleEnrollTeachers,
      updateMapping,
      deleteRow,
      showMessage,
      handleCellEdit,
      closeResultModal,
      isRowValid,
      markRowAsTouched,
      getRowStatusClass,
      validDate,
      getTodayDate
    };
  }
};
</script>