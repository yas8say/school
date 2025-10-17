<template>
  <div class="scroll-view-content">
    <h1 class="title">Teacher Enrollment</h1>

    <!-- File Upload Section -->
    <div class="white-card">
      <h2 class="card-title">Upload Teacher Data</h2>
      <div v-if="fileSelected" class="file-selected">
        <span>Selected file: {{ fileSelected.name }}</span>
        <button @click="removeFile" class="remove-file-btn">×</button>
      </div>
      <button class="button" @click="handleFileSelection">
        <span class="button-text">{{ fileSelected ? 'Change File' : 'Upload File 📤' }}</span>
      </button>
    </div>

    <!-- Enroll Teachers and Undo Buttons -->
    <div class="white-card">
      <button 
        class="button" 
        @click="handleEnrollTeachers"
        :disabled="enrollTeachersResource.loading || !fileSelected"
      >
        <span v-if="enrollTeachersResource.loading" class="button-text">
          <span class="spinner"></span> Processing...
        </span>
        <span v-else class="button-text">Enroll Teachers ✅</span>
      </button>

      <div v-if="message" :class="['message', message.type]">
        {{ message.text }}
      </div>
    </div>

    <!-- File Preview with Class/Division Selection and Mapping Pickers -->
    <div v-if="fileSelected && previewData.length > 0" class="table-white-card preview-card">
      <h2 class="card-title">File Preview (First 100 rows)</h2>
      <div class="table-outer-container">
        <div class="table-scroll-container">
          <div class="table-container">
            <table class="preview-table">
              <thead>
                <tr>
                  <th class="actions">Actions</th>
                  <th>Class/Program</th>
                  <th>Division/Student Group</th>
                  <th v-for="(_, index) in previewHeaders" :key="'letter-'+index">
                    {{ getExcelColumnLetter(index) }}
                  </th>
                </tr>
                <tr>
                  <th class="actions"></th>
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
                <tr v-for="(row, rowIndex) in previewData" :key="rowIndex">
                  <td class="actions">
                    <button @click="deleteRow(rowIndex)" class="trash-icon2">
                      <span class="icon">❎</span>
                    </button>
                  </td>
                  <td>
                    <select 
                      v-model="row.className" 
                      class="table-select"
                      @change="onClassChange(rowIndex)"
                      :disabled="classesResource.loading"
                    >
                      <option :value="null">Select Class</option>
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
    </div>
  </div>
</template>

<script>
import { createResource } from 'frappe-ui';
import { reactive, ref, onMounted } from 'vue';
import * as XLSX from "xlsx";

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
      "Designation", 
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
        // This will be handled in onClassChange method
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
        showMessage('✅ Teachers enrolled successfully!', 'success');
        pendingEdits.value = [];
      },
      onError: (err) => {
        console.error('Error enrolling teachers:', err);
        showMessage(err.messages?.[0] || 'Unexpected error during teacher enrollment', 'error');
      }
    });

    // Fetch initial data on mount
    onMounted(() => {
      classesResource.reload();
    });

    // Methods
    async function onClassChange(rowIndex) {
      const row = previewData.value[rowIndex];
      row.divisionName = null;

      if (row.className) {
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
          console.log(`Divisions for ${row.className}:`, row.divisions);
        } catch (error) {
          console.error("Error fetching divisions:", error);
          showMessage(`Error fetching divisions for ${row.className}`, "error");
        }
      } else {
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
          try {
            const { data, headers } = await readExcelFile(file);
            previewData.value = data.slice(0, 100).map(row => ({
              ...row,
              className: null,
              divisionName: null,
              divisions: []
            }));
            previewHeaders.value = headers;
            // Initialize mappings for each column
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
        "Designation": ["designation", "position", "title", "role"],
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

      console.log('Auto-detected mappings:', mappings.value);
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

    function prepareTeachersData(data, editedRowIndex = null) {
      let teachersData = data;
      if (editedRowIndex !== null) {
        teachersData = [data[editedRowIndex]];
      }

      const fullPreviewData = [...previewData.value];
      const mappedTeachers = teachersData.map((row, rowIndex) => {
        const previewRow = editedRowIndex !== null ? row : (rowIndex < fullPreviewData.length 
          ? fullPreviewData[rowIndex] 
          : {});

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
          "Designation": "",
          "Current Address": "",
          "Permanent Address": "",
          "Blood Group": "",
          "Attendance Device ID (Biometric/RF tag ID)": "",
          "Qualification (Education)": "",
          "School/University (Education)": "",
          "Class": previewRow.className || "",
          "Division": previewRow.divisionName || "",
        };

        mappings.value.forEach(({ type, column }, index) => {
          if (type) {
            try {
              const columnIndex = XLSX.utils.decode_col(column);
              const columnName = previewHeaders.value[columnIndex];
              const value = row[columnName]?.toString().trim() || '';
              teacher[type] = value;
            } catch (error) {
              console.error(`Error mapping column ${column} for type ${type}:`, error);
            }
          }
        });

        return teacher;
      });

      const filteredTeachersData = mappedTeachers.filter(teacher =>
        Object.values(teacher).some(value => value !== "")
      );

      return {
        teachers: filteredTeachersData,
        ...options.value.reduce((acc, option) => {
          const mapping = mappings.value.find((mapping) => mapping.type === option);
          acc[option] = mapping ? mapping.column : "None";
          return acc;
        }, {}),
      };
    }

    async function handleEnrollTeachers() {
      console.log('Enroll button clicked');

      // Define required fields
      const requiredFields = ['Mobile', 'Email', 'Date of Birth', 'Gender', 'First Name', 'Last Name', "Attendance Device ID (Biometric/RF tag ID)"];

      // Check if all required fields are mapped
      const mappedFields = mappings.value.map(m => m.type).filter(type => type);
      const missingFields = requiredFields.filter(field => !mappedFields.includes(field));

      if (missingFields.length > 0) {
        const msg = `Please map the following required fields: ${missingFields.join(', ')}`;
        console.error(msg);
        showMessage(msg, 'error');
        return;
      }

      // Validate column mappings
      const invalidMappings = mappings.value.filter(m => 
        m.type && (!m.column || !/^[A-Z]+$/.test(m.column))
      );

      if (invalidMappings.length > 0) {
        showMessage('Please check your column mappings - some are invalid', 'error');
        return;
      }

      // Check if a file is selected
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

      const params = prepareTeachersData(previewData.value);
      console.log('Sending updated preview data to enrollTeachers:', params);
      
      enrollTeachersResource.update({
        params: {
          teachers: params.teachers,
          mappings: { ...params }
        }
      });
      enrollTeachersResource.submit();
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
        const params = prepareTeachersData(previewData.value, lastEdit.rowIndex);
        console.log('Sending cell update via enrollTeachers:', params);
        
        enrollTeachersResource.update({
          params: {
            teachers: params.teachers,
            mappings: { ...params }
          }
        });
        enrollTeachersResource.submit();
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
      mappings,
      fileSelected,
      options,
      message,
      previewData,
      previewHeaders,
      classes,
      editHistory,
      pendingEdits,
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
      undoLastEdit
    };
  }
};
</script>

<style scoped>
.header-label {
  display: block;
  font-size: 0.8em;
  color: #6c757d;
  margin-top: 4px;
  text-align: center;
}

.table-select {
  width: 100%;
  padding: 5px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.8em;
  background-color: white;
  box-sizing: border-box;
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

.scroll-view-content {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  min-height: 100vh;
}

.title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
  width: 100%;
}

.white-card {
  background-color: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  width: 100%;
  box-sizing: border-box;
}

.table-white-card {
  background-color: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  width: 100%;
  box-sizing: border-box;
  flex: 1;
}

.card-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 15px;
  width: 100%;
}

/* Buttons remain their original size */
.button {
  background-color: #007bff;
  padding: 10px 15px;
  border-radius: 5px;
  border: none;
  cursor: pointer;
  margin-top: 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: auto;
  min-width: 120px;
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
  width: auto;
}

.icon {
  font-size: 16px;
}

.table-outer-container {
  width: 100%;
  overflow: hidden;
  border-radius: 5px;
  margin-top: 15px;
  flex: 1;
}

.table-container {
  width: 100%;
  overflow-x: auto;
  border: 1px solid #e0e0e0;
  border-radius: 5px;
  background-color: white;
  min-height: 200px;
}

.preview-table {
  width: 100%;
  min-width: 100%;
  border-collapse: collapse;
  font-size: 0.9em;
  table-layout: fixed;
}

.preview-table th, 
.preview-table td {
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  text-align: left;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.preview-table th.actions,
.preview-table td.actions {
  width: 60px;
  text-align: center;
  min-width: 60px;
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

.table-scroll-container {
  max-height: 60vh;
  overflow-y: auto;
  display: block;
  flex: 1;
}

.file-selected {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 5px;
  margin-bottom: 10px;
  width: 100%;
  box-sizing: border-box;
}

.remove-file-btn {
  background: none;
  border: none;
  color: #dc3545;
  font-size: 1.2em;
  cursor: pointer;
  padding: 0 5px;
  width: auto;
}

.message {
  padding: 10px;
  border-radius: 5px;
  margin-top: 10px;
  width: 100%;
  box-sizing: border-box;
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

.preview-card {
  margin-top: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* Additional responsive styles */
@media (max-width: 768px) {
  .scroll-view-content {
    padding: 10px;
    gap: 15px;
  }
  
  .white-card,
  .table-white-card {
    padding: 15px;
  }
  
  .table-scroll-container {
    max-height: 50vh;
  }
  
  .preview-table {
    font-size: 0.8em;
  }
  
  .preview-table th, 
  .preview-table td {
    padding: 6px 8px;
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>