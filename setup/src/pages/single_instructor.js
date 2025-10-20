<template>
  <div class="enrollment-container">
    <div class="scroll-view-content">
      <div class="header">
        <h1 class="title">Teacher Enrollment</h1>
      </div>

      <!-- File Upload Section with Enroll Button -->
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
                {{ processing ? 'Processing...' : 'Enroll Teachers ✅' }}
              </span>
            </button>
          </div>

          <!-- Main Message Display -->
          <div v-if="message" :class="['message', message.type]">
            {{ message.text }}
          </div>

          <!-- Detailed Errors Display -->
          <div v-if="detailedErrors.length > 0" class="error-details">
            <h4 class="section-title">Enrollment Errors ({{ detailedErrors.length }}):</h4>
            <div v-for="(error, index) in detailedErrors" :key="index" class="error-message">
              ❌ {{ error }}
            </div>
          </div>

          <!-- Success Results Display -->
          <div v-if="successResults.length > 0" class="success-details">
            <h4 class="section-title">Successfully Enrolled ({{ successResults.length }}):</h4>
            <div v-for="(result, index) in successResults" :key="index" class="success-message">
              ✅ {{ result }}
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
            <span class="stat-value warning">{{ invalidRowsCount }}</span>
          </div>
        </div>

        <div class="instructions">
          <p>💡 <strong>Note:</strong> Class and Division are optional fields. Only assign them for teachers who are class teachers.</p>
        </div>

        <div class="table-container-wrapper">
          <div class="table-scroll-container">
            <div class="table-container">
              <table class="preview-table">
                <thead>
                  <tr>
                    <th class="actions">Actions</th>
                    <th class="status-cell">Status</th> <!-- Add class here -->
                    <th>Class/Program <span class="optional">(Optional)</span></th>
                    <th>Division/Student Group <span class="optional">(Optional)</span></th>
                    <th v-for="(_, index) in previewHeaders" :key="'letter-'+index">
                      {{ getExcelColumnLetter(index) }}
                    </th>
                  </tr>
                  <tr>
                    <th class="actions"></th>
                    <th class="status-cell"></th> <!-- Add class here too -->
                    <th>Class/Program</th>
                    <th>Division/Student Group</th>
                    <th v-for="(header, index) in previewHeaders" :key="'header-'+index">
                      <select
                        v-model="mappings[index].type"
                        class="table-select"
                        @change="updateMapping(index, 'type', $event.target.value)"
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
                        <span class="icon">❎</span>
                      </button>
                    </td>
                    <td class="status-cell">
                      <span v-if="row._status === 'success'" class="status-badge success">✅</span>
                      <span v-else-if="row._status === 'error'" class="status-badge error">❌</span>
                      <span v-else-if="!isRowValid(row)" class="status-badge warning">⚠️</span>
                      <span v-else class="status-badge pending">🔄</span>
                      <div v-if="row._error" class="error-tooltip">
                        {{ row._error }}
                      </div>
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
                    <td v-for="(header, colIndex) in previewHeaders" :key="colIndex">
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
import '@/styles/form.css'; // Import external CSS
import { 
  parseDate, 
  formatDateForAPI, 
  validateDateField, 
  validDate, 
  getTodayDate 
} from '@/utils/dateUtils'; // Import date utilities

export default {
  setup() {
    // Reactive state
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
    const detailedErrors = ref([]);
    const successResults = ref([]);
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

    // API Resources
    const classesResource = createResource({
      url: 'school.al_ummah.api3.get_classes',
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
      url: 'school.al_ummah.api3.get_divisions1',
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
      url: 'school.al_ummah.api3.bulk_enroll_instructors',
      params: {
        teachers: [],
        mappings: {}
      },
      onSuccess: (data) => {
        showMessage('✅ Teachers enrollment process completed!', 'success');
        pendingEdits.value = [];
      },
      onError: (err) => {
        console.error('Error enrolling teachers:', err);
      }
    });

    // Single enrollment resource
    const singleEnrollResource = createResource({
      url: 'school.al_ummah.api3.enroll_single_instructor',
      method: 'POST'
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
          detailedErrors.value = [];
          successResults.value = [];
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
      detailedErrors.value = [];
      successResults.value = [];
      showMessage(null);
    }

    function isRowValid(row) {
      // Required fields (NOW INCLUDING Date of Birth and Date of Joining)
      const requiredFields = [
        'Mobile', 
        'Email', 
        'Gender', 
        'First Name', 
        'Last Name', 
        "Attendance Device ID (Biometric/RF tag ID)",
        "Date of Birth",  // Added as required
        "Date of Joining" // Added as required
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
            // Date of Birth is now required - always validate
            const dobValidation = validateDateField(value, 'Date of Birth');
            if (!dobValidation.isValid) return false;
            break;
            
          case 'Date of Joining':
            // Date of Joining is now required - always validate
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
      if (row._status === 'success') return 'row-success';
      if (row._status === 'error') return 'row-error';
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
              // Only format if date is valid, otherwise keep empty
            }
            
            teacher[type] = value;
          } catch (error) {
            console.error(`Error mapping column ${column} for type ${type}:`, error);
          }
        }
      });

      return teacher;
    }

    async function enrollSingleTeacher(teacher, rowIndex, teacherName) {
      try {
        // Use utility functions for validation
        // Date of Birth is now REQUIRED - always validate
        if (!teacher['Date of Birth'] || teacher['Date of Birth'].toString().trim() === '') {
          throw new Error('Date of Birth is required');
        }
        const dobValidation = validateDateField(teacher['Date of Birth'], 'Date of Birth');
        if (!dobValidation.isValid) throw new Error(dobValidation.error);

        // Date of Joining is now REQUIRED - always validate
        if (!teacher['Date of Joining'] || teacher['Date of Joining'].toString().trim() === '') {
          throw new Error('Date of Joining is required');
        }
        const dojValidation = validateDateField(teacher['Date of Joining'], 'Date of Joining');
        if (!dojValidation.isValid) throw new Error(dojValidation.error);

        const result = await singleEnrollResource.submit({
          teacher: teacher
        });

        if (rowIndex !== undefined && previewData.value[rowIndex]) {
          previewData.value[rowIndex]._status = 'success';
          previewData.value[rowIndex]._error = null;
        }
        successResults.value.push(`Enrolled: ${teacherName}`);
        return { success: true, teacherName };
      } catch (error) {
        console.error(`Error enrolling ${teacherName}:`, error);
        
        if (rowIndex !== undefined && previewData.value[rowIndex]) {
          previewData.value[rowIndex]._status = 'error';
          previewData.value[rowIndex]._error = error.messages?.[0] || error.message || 'Unknown error';
        }
        
        const errorMessage = `${teacherName}: ${error.messages?.[0] || error.message || 'Unknown error'}`;
        detailedErrors.value.push(errorMessage);
        return { success: false, teacherName, error: errorMessage };
      }
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
      detailedErrors.value = [];
      successResults.value = [];
      processing.value = true;
      
      // Reset row statuses
      previewData.value.forEach(row => {
        row._status = null;
        row._error = null;
      });

      // Define required fields (NOW INCLUDING Date of Birth and Date of Joining)
      const requiredFields = [
        'Mobile', 
        'Email', 
        'Gender', 
        'First Name', 
        'Last Name', 
        "Attendance Device ID (Biometric/RF tag ID)",
        "Date of Birth",  // Added as required
        "Date of Joining" // Added as required
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
        
        // Date of Birth is now required
        const dobValidation = teacher['Date of Birth'] && teacher['Date of Birth'].toString().trim() !== '' 
          ? validateDateField(teacher['Date of Birth'], 'Date of Birth')
          : { isValid: false, error: 'Date of Birth is required' };
          
        // Date of Joining is now required
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
        showMessage('Starting enrollment process...', 'info');
        
        // Process all valid rows
        const validRows = previewData.value.filter(row => isRowValid(row));
        
        if (validRows.length === 0) {
          showMessage('No valid rows to enroll. Please check your data.', 'warning');
          processing.value = false;
          return;
        }

        console.log(`Starting enrollment for ${validRows.length} teachers...`);
        
        for (let i = 0; i < validRows.length; i++) {
          const row = validRows[i];
          const rowIndex = previewData.value.indexOf(row);
          const teacher = prepareTeacherData(row);
          const teacherName = `${teacher['First Name']} ${teacher['Last Name']}`.trim() || `Teacher ${i + 1}`;
          
          console.log(`Enrolling teacher ${i + 1}/${validRows.length}:`, teacherName);
          
          // Enroll single teacher
          await enrollSingleTeacher(teacher, rowIndex, teacherName);
          
          // Small delay to avoid overwhelming the server
          await new Promise(resolve => setTimeout(resolve, 200));
        }
        
        // Show final summary
        if (detailedErrors.value.length === 0) {
          showMessage(`✅ Successfully enrolled all ${successResults.value.length} teachers!`, 'success');
          showResultModalFunc('success', 'Enrollment Complete', `Successfully enrolled all ${successResults.value.length} teachers!`);
        } else if (successResults.value.length === 0) {
          showMessage(`❌ All enrollments failed. Please check the errors below.`, 'error');
          showResultModalFunc('error', 'Enrollment Failed', 'All enrollments failed. Please check the error details below.');
        } else {
          showMessage(`Completed: ${successResults.value.length} successful, ${detailedErrors.value.length} failed.`, 'warning');
          showResultModalFunc('warning', 'Enrollment Completed with Errors', 
            `Completed with ${successResults.value.length} successful enrollments and ${detailedErrors.value.length} failures.`);
        }
        
      } catch (error) {
        console.error('Enrollment process error:', error);
        showMessage(`Enrollment process failed: ${error.message || 'Unknown error'}`, 'error');
        showResultModalFunc('error', 'Enrollment Process Failed', error.message || 'Unknown error occurred during enrollment.');
      } finally {
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
        
        // Use the single enrollment function for individual updates
        await enrollSingleTeacher(teacher, lastEdit.rowIndex, `${teacher['First Name']} ${teacher['Last Name']}`);
        
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
      detailedErrors,
      successResults,
      processing,
      showResultModal,
      resultModalType,
      resultModalTitle,
      resultModalDescription,
      validRowsCount,
      classTeachersCount,
      invalidRowsCount,
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