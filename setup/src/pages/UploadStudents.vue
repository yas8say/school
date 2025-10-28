<template>
  <div class="enrollment-container">
    <div class="scroll-view-content">
      <div class="header">
        <h1 class="title">Students Enrollment Screen</h1>
      </div>

      <!-- Loading Screen -->
      <div v-if="processing" class="loading-overlay">
        <div class="loading-modal">
          <div class="loading-spinner"></div>
          <h3 class="loading-title">Enrolling Students</h3>
          <p class="loading-description">Please wait while we process the student data...</p>
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

      <!-- White Card for Select Year, Class and Division -->
      <div class="form-card">
        <h2 class="form-title">Academic Information</h2>
        
        <div class="form-grid">
          <div class="form-group required">
            <label>Academic Year</label>
            <select 
              v-model="selectedYear" 
              class="picker" 
              @change="onYearChange"
              :disabled="academicYearsResource.loading"
            >
              <option :value="null">Select a Year</option>
              <option v-for="year in displayYears" :key="year" :value="year.original">
                {{ year.display }}
              </option>
            </select>
          </div>

          <div class="form-group required">
            <label>Class / Program</label>
            <select 
              v-model="selectedClass" 
              class="picker" 
              @change="onClassChange"
              :disabled="!selectedYear || classesResource.loading"
            >
              <option :value="null">Select a Class / Program</option>
              <option v-for="cls in classes" :key="cls.name" :value="cls.name">
                {{ cls.name }}
              </option>
            </select>
          </div>

          <div v-if="divisions.length > 0" class="form-group required">
            <label>Division / Student Group</label>
            <select 
              v-if="divisions.length > 0" 
              v-model="selectedDivision" 
              class="picker"
              :disabled="!selectedClass || divisionsResource.loading"
            >
              <option :value="null">Select a Division / Student Group</option>
              <option v-for="div in divisions" :key="div.name" :value="div.name">
                {{ div.name }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <!-- File Upload Section -->
      <div class="form-card">
        <h2 class="form-title">Student Data Upload</h2>
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

          <!-- Enroll Students Button -->
          <div class="enroll-button-section">
            <button 
              class="enroll-button" 
              @click="handleEnrollStudents"
              :disabled="processing || !selectedYear || !selectedClass || !selectedDivision || !fileSelected"
            >
              <span class="button-content">
                <span v-if="processing" class="spinner"></span>
                {{ processing ? 'Processing...' : 'Enroll Students' }}
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
        <div v-if="enrolledStudents.length > 0" class="success-details">
          <h4 class="section-title">Successfully Enrolled ({{ enrolledStudents.length }})</h4>
          <div class="results-list">
            <div v-for="(student, index) in enrolledStudents" :key="index" class="success-message">
              <span class="status-badge success">Success</span> {{ student }}
            </div>
          </div>
        </div>

        <!-- Enrollment Errors inside Summary Card -->
        <div v-if="failedEnrollments.length > 0" class="error-details">
          <h4 class="section-title">Enrollment Errors ({{ failedEnrollments.length }})</h4>
          <div class="results-list">
            <div v-for="(failure, index) in failedEnrollments" :key="index" class="error-message">
              <div class="error-student">
                <strong>{{ failure.student_data['First Name'] }} {{ failure.student_data['Middle Name'] }} {{ failure.student_data['Last Name'] }}</strong>
                <span class="student-details">(GR: {{ failure.student_data['GR Number'] }}, Roll: {{ failure.student_data['Roll No'] }})</span>
              </div>
              <div class="error-text">
                <span class="status-badge error">Error</span> {{ failure.error }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- File Preview Section -->
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
            <span class="stat-label">With Errors:</span>
            <span class="stat-value warning" 
                  style="cursor: pointer;" 
                  @click="showErrorStudentsList = !showErrorStudentsList"
                  :title="invalidRowsCount > 0 ? 'Click to view students with errors' : ''">
              {{ invalidRowsCount }}
              <span v-if="invalidRowsCount > 0" class="error-indicator">⚠️</span>
            </span>
          </div>
        </div>

        <!-- Error Students Card - Scrollable like Enrollment Errors -->
        <div v-if="showErrorStudentsList && errorRows.length > 0" class="error-students-card">
          <h4 class="section-title">Students with Errors ({{ invalidRowsCount }})</h4>
          <div class="error-details" style="max-height: 200px; overflow-y: auto;">
            <div class="results-list">
              <div v-for="(row, rowIndex) in errorRows" :key="rowIndex" class="error-message">
                <div class="error-student">
                  <strong>{{ getStudentFullName(row) }}</strong>
                  <span class="student-details">
                    (GR: {{ getStudentGR(row) }}, Roll: {{ getStudentRoll(row) }})
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

        <!-- Space between error list and table -->
        <div class="table-spacing" v-if="showErrorStudentsList && errorRows.length > 0"></div>

        <div class="table-container-wrapper">
          <div class="table-scroll-container">
            <div class="table-container">
              <table class="preview-table">
                <thead>
                  <tr>
                    <th class="actions">Actions</th>
                    <th class="status-cell">Status</th>
                    <th v-for="(header, index) in filteredHeaders" :key="'letter-'+index">
                      {{ getExcelColumnLetter(index) }}
                    </th>
                  </tr>
                  <tr>
                    <th class="actions"></th>
                    <th class="status-cell"></th>
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
                      <div v-if="row._error" class="error-tooltip">
                        {{ row._error }}
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
    </div>
  </div>
</template>

<script>
import { createResource } from 'frappe-ui';
import { reactive, ref, computed, onMounted } from 'vue';
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
    const showErrorStudentsList = ref(false);
    const academicYears = ref([]);
    const displayYears = computed(() =>
      academicYears.value.map((year, index) => ({
        original: year,
        display: index === 0 ? `${year} - Current Year` : year
      }))
    );
    const selectedYear = ref(null);
    const classes = ref([]);
    const divisions = ref([]);
    const selectedClass = ref(null);
    const selectedDivision = ref(null);
    const mappings = ref([]);
    const fileSelected = ref(null);
    const options = ref([
      "First Name", 
      "Middle Name", 
      "Last Name", 
      "Student Date of Birth",
      "Email Address", 
      "Phone Number", 
      "GR Number", 
      "Roll No",
      "Guardian Name",
      "Guardian Number", 
      "Guardian Email",  
      "Relation",
      "Guardian Date of Birth"
    ]);
    const message = ref(null);
    const previewData = ref([]);
    const previewHeaders = ref([]);
    const editHistory = ref([]);
    const pendingEdits = ref([]);
    
    // Enhanced state for better error handling
    const enrolledStudents = ref([]);
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

    // Methods for error students display
    function getStudentFullName(row) {
      const student = prepareStudentData(row);
      return `${student['First Name'] || ''} ${student['Middle Name'] || ''} ${student['Last Name'] || ''}`.trim() || 'Unknown Student';
    }

    function getStudentGR(row) {
      const student = prepareStudentData(row);
      return student['GR Number'] || 'N/A';
    }

    function getStudentRoll(row) {
      const student = prepareStudentData(row);
      return student['Roll No'] || 'N/A';
    }
    
    function getRowError(row) {
      const errors = [];
      
      // Check for missing required fields
      const requiredFields = ['First Name', 'Last Name', 'GR Number', 'Roll No'];
      
      requiredFields.forEach(field => {
        const mappingIndex = mappings.value.findIndex(m => m.type === field);
        
        if (mappingIndex === -1) {
          errors.push(`${field} not mapped`);
        } else {
          const columnIndex = XLSX.utils.decode_col(mappings.value[mappingIndex].column);
          const columnName = previewHeaders.value[columnIndex];
          const value = row[columnName];
          
          if (!value || value.toString().trim() === '') {
            errors.push(`${field} missing`);
          }
        }
      });
      
      // ✅ FIX: Only validate Student Date of Birth if it's provided and not empty
      const student = prepareStudentData(row);
      const studentDob = student['Student Date of Birth'];
      
      if (studentDob && studentDob.toString().trim() !== '') {
        const dobValidation = validateDateField(studentDob, 'Student Date of Birth');
        if (!dobValidation.isValid) {
          errors.push(dobValidation.error);
        }
      }
      
      if (errors.length > 0) {
        return errors.join('; ');
      }
      
      return 'Check field mappings';
    }

    // API Resources
    const academicYearsResource = createResource({
      url: 'school.al_ummah.api4.get_academic_years',
      params: { values: {} },
      onSuccess: (data) => {
        academicYears.value = Array.isArray(data) ? data : [];
        if (academicYears.value.length > 0) {
          selectedYear.value = academicYears.value[0];
        }
        if (!academicYears.value.length) {
          showMessage('No academic years available', 'error');
        }
      },
      onError: (err) => {
        console.error('Error fetching academic years:', err);
        academicYears.value = [];
        showMessage(`Error fetching academic years: ${err.messages?.[0] || 'Unknown error'}`, 'error');
      }
    });

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
      url: 'school.al_ummah.api4.get_divisions2',
      params: {
        values: {
          classId: selectedClass.value,
          academicYear: selectedYear.value
        }
      },
      onSuccess: (data) => {
        divisions.value = Array.isArray(data) ? data : [];
        console.log('Divisions loaded:', divisions.value);
      },
      onError: (err) => {
        console.error('Error fetching divisions:', err);
        divisions.value = [];
        showMessage(`Error fetching divisions: ${err.messages?.[0] || 'Unknown error'}`, 'error');
      }
    });

    const enrollStudentsResource = createResource({
      url: 'school.al_ummah.api4.bulk_enroll_students',
      method: 'POST',
      onSuccess: (data) => {
        console.log('Bulk enrollment successful:', data);
        processing.value = false;
        
        if (data && data.success) {
          // Update enrollment results
          enrolledStudents.value = data.enrolled_students || [];
          failedEnrollments.value = data.failed_enrollments || [];
          enrollmentSummary.value = data.summary || {
            total_processed: data.enrolled_students.length + data.failed_enrollments.length,
            successful: data.enrolled_students.length,
            failed: data.failed_enrollments.length
          };
          
          // Update row statuses based on bulk response
          updateRowStatusesFromBulkResponse(data.enrolled_students, data.failed_enrollments);
          
          // Show appropriate message and modal
          if (failedEnrollments.value.length === 0) {
            showMessage(`Successfully enrolled all ${enrolledStudents.value.length} students!`, 'success');
            showResultModalFunc('success', 'Enrollment Complete', `Successfully enrolled all ${enrolledStudents.value.length} students!`);
          } else {
            showMessage(`Completed: ${enrolledStudents.value.length} successful, ${failedEnrollments.value.length} failed.`, 'warning');
            showResultModalFunc('warning', 'Enrollment Completed with Errors', 
              `Completed with ${enrolledStudents.value.length} successful enrollments and ${failedEnrollments.value.length} failures.`);
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
      academicYearsResource.reload();
      classesResource.reload();
    });

    // Methods
    function onYearChange() {
      selectedClass.value = null;
      selectedDivision.value = null;
      divisions.value = [];
      onClassChange();
    }

    function onClassChange() {
      selectedDivision.value = null;
      divisions.value = [];

      if (selectedClass.value && selectedYear.value) {
        divisionsResource.update({
          params: {
            values: {
              classId: selectedClass.value,
              academicYear: selectedYear.value
            }
          }
        });
        divisionsResource.reload();
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
      input.accept = '.xlsx,.xls,.csv';

      input.onchange = async (e) => {
        const file = e.target.files[0];
        if (file) {
          fileSelected.value = file;
          showMessage(null);
          enrolledStudents.value = [];
          failedEnrollments.value = [];
          enrollmentSummary.value = { total_processed: 0, successful: 0, failed: 0 };
          try {
            const { data, headers } = await readExcelFile(file);
            previewData.value = data.slice(0, 100).map(row => ({
              ...row,
              _status: null,
              _error: null,
              _touched: false
            }));
            previewHeaders.value = headers;
            // Initialize mappings for each column
            mappings.value = headers.map((_, index) => ({
              type: null,
              column: XLSX.utils.encode_col(index)
            }));
            autoDetectMappings(headers);
          } catch (error) {
            console.error("Error loading preview:", error);
            showMessage("Error loading file preview", "error");
          }
        }
      };
      input.click();
    }

    function removeFile() {
      fileSelected.value = null;
      previewData.value = [];
      previewHeaders.value = [];
      mappings.value = [];
      editHistory.value = [];
      pendingEdits.value = [];
      enrolledStudents.value = [];
      failedEnrollments.value = [];
      enrollmentSummary.value = { total_processed: 0, successful: 0, failed: 0 };
      showMessage(null);
    }

    function isRowValid(row) {
      // A row is valid if it has basic required student info
      const hasFirstName = mappings.value.some(m => m.type === 'First Name' && row[previewHeaders.value[XLSX.utils.decode_col(m.column)]]);
      const hasLastName = mappings.value.some(m => m.type === 'Last Name' && row[previewHeaders.value[XLSX.utils.decode_col(m.column)]]);
      const hasGRNumber = mappings.value.some(m => m.type === 'GR Number' && row[previewHeaders.value[XLSX.utils.decode_col(m.column)]]);
      const hasRollNo = mappings.value.some(m => m.type === 'Roll No' && row[previewHeaders.value[XLSX.utils.decode_col(m.column)]]);
      
      // Student Date of Birth is now optional - validate only if provided
      const studentDob = prepareStudentData(row)['Student Date of Birth'];
      let hasValidDob = true; // Default to true (optional field)
      
      if (studentDob && studentDob.toString().trim() !== '') {
        // Only validate if DOB is provided and not empty
        hasValidDob = validDate(studentDob);
      }
      
      return hasFirstName && hasLastName && hasGRNumber && hasRollNo && hasValidDob;
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

    function prepareStudentData(row) {
      const student = {
        "First Name": "",
        "Middle Name": "",
        "Last Name": "",
        "Student Date of Birth": "",
        "Email Address": "",
        "Phone Number": "",
        "GR Number": "",
        "Roll No": "",
        "Guardian Name": "",
        "Guardian Number": "",
        "Relation": "",
        "Guardian Email": "",
        "Guardian Date of Birth": "",
        "className": selectedClass.value,
        "divisionName": selectedDivision.value,
        "academicYear": selectedYear.value
      };

      // Map each column based on the mapping configuration
      mappings.value.forEach(({ type, column }, index) => {
        if (type && student.hasOwnProperty(type)) {
          try {
            const columnIndex = XLSX.utils.decode_col(column);
            const columnName = previewHeaders.value[columnIndex];
            let value = row[columnName]?.toString().trim() || '';
            
            // Use utility functions for date handling
            if (type === 'Student Date of Birth' || type === 'Guardian Date of Birth') {
              const parsedDate = parseDate(value);
              value = parsedDate ? formatDateForAPI(parsedDate) : ''; // Only format if valid
            }
            
            student[type] = value;
          } catch (error) {
            console.error(`Error mapping column ${column} for type ${type}:`, error);
          }
        }
      });

      return student;
    }

    function updateRowStatusesFromBulkResponse(enrolledStudents, failedEnrollments) {
      console.log('Updating row statuses from bulk response...');

      // Reset ALL statuses completely to avoid mixing enrollment and validation errors
      previewData.value.forEach(row => {
        row._status = null;
        row._error = null;
      });

      // Update successful enrollments
      enrolledStudents.forEach(studentName => {
        const rowIndex = findRowIndexByStudentName(studentName);
        if (rowIndex !== -1) {
          previewData.value[rowIndex]._status = 'success';
          previewData.value[rowIndex]._error = null;
        }
      });

      // Update failed enrollments - BUT use a different property to avoid conflict
      failedEnrollments.forEach(failure => {
        const rowIndex = findRowIndexByStudentData(failure.student_data);
        if (rowIndex !== -1) {
          // Use a separate property for enrollment errors
          previewData.value[rowIndex]._enrollment_status = 'error';
          previewData.value[rowIndex]._enrollment_error = failure.error || 'Unknown error';
        }
      });
    }

    function findRowIndexByStudentName(studentName) {
      return previewData.value.findIndex(row => {
        const rowStudentData = prepareStudentData(row);
        const rowFullName = `${rowStudentData['First Name']} ${rowStudentData['Middle Name']} ${rowStudentData['Last Name']}`.trim();
        return rowFullName === studentName;
      });
    }

    function findRowIndexByStudentData(studentData) {
      return previewData.value.findIndex(row => {
        const rowStudentData = prepareStudentData(row);
        return rowStudentData['GR Number'] === studentData['GR Number'] && 
               rowStudentData['First Name'] === studentData['First Name'] &&
               rowStudentData['Last Name'] === studentData['Last Name'];
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

    async function handleEnrollStudents() {
      console.log('Enroll button clicked');

      // Reset previous results
      enrolledStudents.value = [];
      failedEnrollments.value = [];
      enrollmentSummary.value = { total_processed: 0, successful: 0, failed: 0 };
      processing.value = true;
      
      // Reset row statuses
      previewData.value.forEach(row => {
        row._status = null;
        row._error = null;
      });

      // Define required fields (removed "Student Date of Birth")
      const requiredFields = ['First Name', 'GR Number', 'Last Name', 'Roll No'];

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
      if (!selectedYear.value || !selectedClass.value || !selectedDivision.value) {
        const msg = 'Please select an academic year, class, and division';
        console.error(msg);
        showMessage(msg, 'error');
        processing.value = false;
        return;
      }

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

      // Additional validation: Check for invalid dates (only validate if dates are provided)
      const invalidDateRows = previewData.value.filter(row => {
        const student = prepareStudentData(row);
        
        // Check Student Date of Birth only if provided
        const dobValidation = student['Student Date of Birth'] && student['Student Date of Birth'].toString().trim() !== '' 
          ? validateDateField(student['Student Date of Birth'], 'Student Date of Birth')
          : { isValid: true };
          
        // Guardian Date of Birth validation remains optional
        const guardianDobValidation = student['Guardian Date of Birth'] && student['Guardian Date of Birth'].toString().trim() !== ''
          ? validateDateField(student['Guardian Date of Birth'], 'Guardian Date of Birth')
          : { isValid: true };
          
        return !dobValidation.isValid || !guardianDobValidation.isValid;
      });

      if (invalidDateRows.length > 0) {
        showMessage(`${invalidDateRows.length} rows have invalid dates. Please correct the dates before enrolling.`, 'warning');
        // Mark rows with invalid dates as error
        invalidDateRows.forEach(row => {
          const rowIndex = previewData.value.indexOf(row);
          if (rowIndex !== -1) {
            const student = prepareStudentData(row);
            const dobValidation = validateDateField(student['Student Date of Birth'], 'Student Date of Birth');
            const guardianDobValidation = validateDateField(student['Guardian Date of Birth'], 'Guardian Date of Birth');
            
            let errorMsg = '';
            if (!dobValidation.isValid) errorMsg += dobValidation.error + ' ';
            if (!guardianDobValidation.isValid) errorMsg += guardianDobValidation.error;
            
            previewData.value[rowIndex]._status = 'error';
            previewData.value[rowIndex]._error = errorMsg.trim();
          }
        });
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

        console.log(`Starting bulk enrollment for ${validRows.length} students...`);
        
        // Prepare students data for bulk enrollment
        const studentsData = validRows.map(row => {
          const student = prepareStudentData(row);
          return student;
        });

        // Perform bulk enrollment
        await enrollStudentsResource.submit({
          academicYear: selectedYear.value,
          className: selectedClass.value,
          divisionName: selectedDivision.value,
          students: studentsData,
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

    function autoDetectMappings(headers) {
      const fieldPatterns = {
        "First Name": ["first", "fname", "given"],
        "Last Name": ["last", "lname", "surname"],
        "Middle Name": ["middle", "mname"],
        "Email Address": ["email", "mail"],
        "Phone Number": ["phone", "mobile", "contact"],
        "GR Number": ["gr", "grno", "gr_num", "gr no"],
        "Roll No": ["r. no", "roll", "rollno", "roll_num"],
        "Student Date of Birth": ["dob", "birth", "birthdate", "date of birth"],
        "Guardian Date of Birth": ["guardian dob", "parent dob", "father dob", "mother dob"],
        "Guardian Name": ["guardian name", "parent", "father", "mother"],
        "Guardian Number": ["guardian no", "guardian number", "guardian phone", "parent phone"],
        "Relation": ["relation", "relationship"],
        "Guardian Email": ["guardian email", "parent email", "father email", "mother email"]
      };
      
      headers.forEach((header, index) => {
        if (!header) return;
        const headerLower = header.toLowerCase().trim();
        
        // SPECIAL HANDLING FOR EMAIL FIELDS FIRST
        if (headerLower.includes('email')) {
          if (headerLower.includes('guardian') || headerLower.includes('parent')) {
            mappings.value[index].type = 'Guardian Email';
            console.log(`✓ Guardian Email: "${header}"`);
            return;
          } else {
            mappings.value[index].type = 'Email Address';
            console.log(`✓ Student Email: "${header}"`);
            return;
          }
        }
        
        // NORMAL MATCHING FOR OTHER FIELDS
        for (const [field, patterns] of Object.entries(fieldPatterns)) {
          if (patterns.some(pattern => headerLower.includes(pattern))) {
            // Skip if this is an email field (we already handled them)
            if (field === "Email Address" || field === "Guardian Email") continue;
            
            mappings.value[index].type = field;
            console.log(`✓ ${field}: "${header}"`);
            break;
          }
        }
      });

      console.log('Final auto-detected mappings:', mappings.value);
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
        const student = prepareStudentData(row);
        
        // Use bulk enrollment with single student for updates
        await enrollStudentsResource.submit({
          academicYear: selectedYear.value,
          className: selectedClass.value,
          divisionName: selectedDivision.value,
          students: [student],
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
      academicYears,
      displayYears,
      selectedYear,
      classes,
      divisions,
      selectedClass,
      selectedDivision,
      mappings,
      fileSelected,
      options,
      message,
      previewData,
      previewHeaders,
      editHistory,
      pendingEdits,
      enrolledStudents,
      failedEnrollments,
      enrollmentSummary,
      processing,
      showResultModal,
      resultModalType,
      resultModalTitle,
      resultModalDescription,
      showErrorStudentsList,
      validRowsCount,
      invalidRowsCount,
      errorRows,
      filteredHeaders,
      filteredMappings,
      getStudentFullName,
      getStudentGR,
      getStudentRoll,
      getRowError,
      academicYearsResource,
      classesResource,
      divisionsResource,
      enrollStudentsResource,
      
      onYearChange,
      onClassChange,
      getExcelColumnLetter,
      handleFileSelection,
      removeFile,
      handleEnrollStudents,
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