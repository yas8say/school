<template>
  <div class="scroll-view-content">
    <h1 class="title">Students Enrollment Screen</h1>

    <!-- Loading Screen -->
    <div v-if="enrollStudentsResource.loading" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white p-8 rounded-lg shadow-lg max-w-md w-full text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
        <h3 class="text-lg font-medium text-gray-900">Submitting your data...</h3>
        <p class="mt-2 text-sm text-gray-500">Please wait while we process your information.</p>
      </div>
    </div>

    <!-- Success/Failure Message -->
    <div v-if="showResultMessage" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white p-8 rounded-lg shadow-lg max-w-md w-full text-center">
        <div v-if="submitSuccess" class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
          <svg class="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <div v-else class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
          <svg class="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </div>
        <h3 class="mt-3 text-lg font-medium text-gray-900">
          {{ submitSuccess ? 'Students Enrolled Successfully!' : 'Enrollment Failed' }}
        </h3>
        <p class="mt-2 text-sm text-gray-500">
          {{ submitSuccess ? 'Students have been successfully enrolled.' : errorMessage || 'An error occurred while enrolling students.' }}
        </p>
        <div class="mt-5">
          <button
            @click="showResultMessage = false"
            class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            OK
          </button>
        </div>
      </div>
    </div>

    <!-- White Card for Select Year, Class and Division -->
    <div class="white-card">
      <h2 class="card-title">Select a Year</h2>
      <select 
        v-model="selectedYear" 
        class="picker2" 
        @change="onYearChange"
        :disabled="academicYearsResource.loading"
      >
        <option :value="null">Select a Year</option>
        <option v-for="year in displayYears" :key="year" :value="year.original">
          {{ year.display }}
        </option>
      </select>

      <h2 class="card-title">Class / Program</h2>
      <select 
        v-model="selectedClass" 
        class="picker2" 
        @change="onClassChange"
        :disabled="!selectedYear || classesResource.loading"
      >
        <option :value="null">Select a Class / Program</option>
        <option v-for="cls in classes" :key="cls.name" :value="cls.name">
          {{ cls.name }}
        </option>
      </select>

      <h2 v-if="divisions.length > 0" class="card-title">Division / Student Group</h2>
      <select 
        v-if="divisions.length > 0" 
        v-model="selectedDivision" 
        class="picker2"
        :disabled="!selectedClass || divisionsResource.loading"
      >
        <option :value="null">Select a Division / Student Group</option>
        <option v-for="div in divisions" :key="div.name" :value="div.name">
          {{ div.name }}
        </option>
      </select>
    </div>

    <!-- File Upload Section -->
    <div class="white-card">
      <h2 class="card-title">Upload Student Data</h2>
      <div v-if="fileSelected" class="file-selected">
        <span>Selected file: {{ fileSelected.name }}</span>
        <button @click="removeFile" class="remove-file-btn">×</button>
      </div>
      <button class="button" @click="handleFileSelection">
        <span class="button-text">{{ fileSelected ? 'Change File' : 'Upload File 📤' }}</span>
      </button>
    </div>

    <!-- Enroll Students and Undo Buttons -->
    <div class="white-card">
      <button 
        class="button" 
        @click="handleEnrollStudents"
        :disabled="enrollStudentsResource.loading || !selectedYear || !selectedClass || !selectedDivision || !fileSelected"
      >
        <span v-if="enrollStudentsResource.loading" class="button-text">
          <span class="spinner"></span> Processing...
        </span>
        <span v-else class="button-text">Enroll Students ✅</span>
      </button>

      <div v-if="message && !showResultMessage" :class="['message', message.type]">
        {{ message.text }}
      </div>
    </div>

    <!-- File Preview Section -->
    <div v-if="fileSelected && previewData.length > 0" class="white-card preview-card">
      <h2 class="card-title">File Preview (First 100 rows)</h2>
      <div class="table-container">
        <table class="preview-table">
          <thead>
            <tr>
              <th class="actions">Actions</th>
              <th v-for="(_, index) in previewHeaders" :key="'letter-'+index">
                {{ getExcelColumnLetter(index) }}
              </th>
            </tr>
            <tr>
              <th class="actions"></th>
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
            <tr v-for="(row, rowIndex) in previewData" :key="rowIndex">
              <td class="actions">
                <button @click="deleteRow(rowIndex)" class="trash-icon2">
                  <span class="icon">❎</span>
                </button>
              </td>
              <td v-for="(header, colIndex) in previewHeaders" :key="colIndex">
                <input
                  v-model="row[header]"
                  class="table-input"
                  @input="handleCellEdit(rowIndex, header, $event.target.value)"
                  :placeholder="row[header] || '-'"
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { createResource } from 'frappe-ui';
import { reactive, ref, computed, onMounted } from 'vue';
import * as XLSX from "xlsx";

export default {
  setup() {
    // Reactive state
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
      "Email Address", 
      "Phone Number", 
      "GR Number", 
      "Roll No",
      "Guardian Name",
      "Guardian Number", 
      "Guardian Email",  
      "Relation",
    ]);
    const message = ref(null);
    const previewData = ref([]);
    const previewHeaders = ref([]);
    const editHistory = ref([]);
    const pendingEdits = ref([]);
    
    // New state for modal management
    const showResultMessage = ref(false);
    const submitSuccess = ref(false);
    const errorMessage = ref('');

    // API Resources
    const academicYearsResource = createResource({
      url: 'school.al_ummah.api3.get_academic_years',
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
      url: 'school.al_ummah.api3.get_divisions2',
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
      url: 'school.al_ummah.api3.bulk_enroll_students',
      params: {
        academicYear: selectedYear.value,
        className: selectedClass.value,
        divisionName: selectedDivision.value,
        students: [],
        mappings: {}
      },
      onSuccess: () => {
        submitSuccess.value = true;
        errorMessage.value = '';
        showResultMessage.value = true;
        pendingEdits.value = [];
      },
      onError: (err) => {
        console.error('Error enrolling students:', err);
        submitSuccess.value = false;
        errorMessage.value = err.messages?.[0] || 'Unexpected error during enrollment';
        showResultMessage.value = true;
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
          try {
            const { data, headers } = await readExcelFile(file);
            previewData.value = data.slice(0, 100);
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
      showMessage(null);
    }

    function prepareStudentsData(data, editedRowIndex = null) {
      let studentsData = data;
      if (editedRowIndex !== null) {
        studentsData = [data[editedRowIndex]];
      }

      const mappedStudents = studentsData.map(row => {
        const student = {
          "First Name": "",
          "Middle Name": "",
          "Last Name": "",
          "Name": "",
          "Email Address": "",
          "Phone Number": "",
          "GR Number": "",
          "Roll No": "",
          "Guardian Name": "",
          "Guardian Number": "",
          "Relation": "",
          "Guardian Email": ""  // Add this line
        };

        mappings.value.forEach(({ type, column }) => {
          if (type) {
            try {
              const columnIndex = XLSX.utils.decode_col(column);
              const columnName = previewHeaders.value[columnIndex];
              const value = row[columnName]?.toString().trim() || '';
              student[type] = value;
            } catch (error) {
              console.error(`Error mapping column ${column} for type ${type}:`, error);
            }
          }
        });
        return student;
      });

      const filteredStudentsData = mappedStudents.filter(student =>
        Object.values(student).some(value => value !== "")
      );

      return {
        academicYear: selectedYear.value,
        className: selectedClass.value,
        divisionName: selectedDivision.value,
        students: filteredStudentsData,
        ...options.value.reduce((acc, option) => {
          const mapping = mappings.value.find(mapping => mapping.type === option);
          acc[option] = mapping ? mapping.column : "None";
          return acc;
        }, {}),
      };
    }

    async function handleEnrollStudents() {
      console.log('Enroll button clicked');

      const requiredFields = ['First Name', 'GR Number', 'Last Name', 'Roll No'];

      const mappedFields = mappings.value.map(m => m.type).filter(type => type);
      const missingFields = requiredFields.filter(field => !mappedFields.includes(field));

      if (missingFields.length > 0) {
        const msg = `Please map the following required fields: ${missingFields.join(', ')}`;
        console.error(msg);
        showMessage(msg, 'error');
        return;
      }

      const invalidMappings = mappings.value.filter(m => 
        m.type && (!m.column || !/^[A-Z]+$/.test(m.column))
      );

      if (invalidMappings.length > 0) {
        showMessage('Please check your column mappings - some are invalid', 'error');
        return;
      }

      if (!selectedYear.value || !selectedClass.value || !selectedDivision.value) {
        const msg = 'Please select an academic year, class, and division';
        console.error(msg);
        showMessage(msg, 'error');
        return;
      }

      if (!fileSelected.value) {
        const msg = 'Please select a file first';
        console.error(msg);
        showMessage(msg, 'error');
        return;
      }

      if (previewData.value.length === 0) {
        showMessage('No data available to enroll', 'error');
        return;
      }

      const params = prepareStudentsData(previewData.value);
      console.log('Sending updated preview data to enrollStudents:', params);
      
      enrollStudentsResource.update({
        params: {
          academicYear: selectedYear.value,
          className: selectedClass.value,
          divisionName: selectedDivision.value,
          students: params.students,
          mappings: { ...params }
        }
      });
      enrollStudentsResource.submit();
    }

    function autoDetectMappings(headers) {
    const fieldPatterns = {
      "First Name": ["first", "fname", "given"],
      "Last Name": ["last", "lname", "surname"],
      "Middle Name": ["middle", "mname"],
      "Email Address": ["email", "mail"],
      "Phone Number": ["phone", "mobile", "contact"],
      "GR Number": ["gr", "grno", "gr_num"],
      "Roll No": ["roll", "rollno", "roll_num"],
      "Guardian Name": ["guardian", "parent", "father", "mother"],
      "Guardian Number": ["guardian phone", "parent phone", "father phone", "mother phone", "guardian mobile"],
      "Relation": ["relation", "relationship"],
      "Guardian Email": ["guardian email", "parent email", "father email", "mother email"]  // Add this line
    };
      headers.forEach((header, index) => {
        if (!header) return;
        const headerLower = header.toLowerCase();
        for (const [field, patterns] of Object.entries(fieldPatterns)) {
          if (patterns.some(pattern => headerLower.includes(pattern))) {
            mappings.value[index].type = field;
            break;
          }
        }
      });

      console.log('Auto-detected mappings:', mappings.value);
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
        const params = prepareStudentsData(previewData.value, lastEdit.rowIndex);
        console.log('Sending cell update via enrollStudents:', params);
        
        enrollStudentsResource.update({
          params: {
            academicYear: selectedYear.value,
            className: selectedClass.value,
            divisionName: selectedDivision.value,
            students: params.students,
            mappings: { ...params }
          }
        });
        enrollStudentsResource.submit();
      } catch (error) {
        console.error('Error sending cell update:', error);
        showMessage(`Failed to save cell update: ${error.message || 'Unknown error'}`, 'error');
      }
    }

    function undoLastEdit() {
      const lastEdit = editHistory.value.pop();
      if (lastEdit) {
        const { rowIndex, column, oldValue } = lastEdit;
        previewData.value[rowIndex][column] = oldValue;
        pendingEdits.value = pendingEdits.value.filter(edit => edit !== lastEdit);
        showMessage('Last edit undone', 'success');
      } else {
        showMessage('No edits to undo', 'info');
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
      academicYearsResource,
      classesResource,
      divisionsResource,
      enrollStudentsResource,
      showResultMessage,
      submitSuccess,
      errorMessage,
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
      undoLastEdit
    };
  }
};
</script>

<style scoped>
/* Your existing CSS styles remain the same */
.table-select {
  width: 100%;
  padding: 5px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.8em;
  background-color: white;
}

.header-label {
  display: block;
  font-size: 0.8em;
  color: #6c757d;
  margin-top: 4px;
  text-align: center;
}

.table-input {
  width: 100%;
  padding: 5px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.8em;
  background-color: white;
  box-sizing: border-box;
}

.table-input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 3px rgba(0, 123, 255, 0.3);
}

.preview-card {
  margin-top: 20px;
}

.table-container {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #e0e0e0;
  border-radius: 5px;
  background-color: white;
}

.preview-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9em;
}

.preview-table th, 
.preview-table td {
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  text-align: left;
  white-space: nowrap;
}

.preview-table th.actions,
.preview-table td.actions {
  width: 60px;
  text-align: center;
}

.preview-table thead tr:first-child th {
  background-color: #f0f0f0;
  font-size: 0.8em;
  text-align: center;
  position: sticky;
  top: 0;
  z-index: 2;
}

.preview-table thead tr:nth-child(2) th {
  background-color: #f5f5f5;
  font-weight: bold;
  position: sticky;
  top: 24px;
  z-index: 1;
}

.preview-table tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}

.preview-table tr:hover {
  background-color: #f0f0f0;
}

.scroll-view-content {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
}

.white-card {
  background-color: white;
  padding: 15px;
  border-radius: 10px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.card-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 10px;
}

.picker2 {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  margin-bottom: 10px;
}

.button {
  background-color: #007bff;
  padding: 10px 15px;
  border-radius: 5px;
  border: none;
  cursor: pointer;
  margin-top: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.button-text {
  color: white;
  font-weight: bold;
}

.trash-icon2 {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
}

.icon {
  font-size: 16px;
}

.file-selected {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 5px;
  margin-bottom: 10px;
}

.remove-file-btn {
  background: none;
  border: none;
  color: #dc3545;
  font-size: 1.2em;
  cursor: pointer;
  padding: 0 5px;
}

.message {
  padding: 10px;
  border-radius: 5px;
  margin-top: 10px;
}

.message.success {
  background-color: #d4edda;
  color: #155724;
}

.message.error {
  background-color: #f8d7da;
  color: #721c24;
}

.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s ease-in-out infinite;
  margin-right: 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>