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

    <!-- Column Mappings -->
    <div v-if="fileSelected" class="white-card">
      <h2 class="card-title">Column Mappings</h2>
      <div v-if="mappings.length === 0" class="no-mappings">
        <p>No mappings detected automatically. Please add them manually.</p>
      </div>
      <div v-for="(mapping, index) in mappings" :key="index" class="card">
        <button @click="deleteMapping(index)" class="trash-icon2">
          <span class="icon">❎</span>
        </button>
        <select
          v-model="mapping.type"
          class="picker2"
          @change="(e) => updateMapping(index, 'type', e.target.value)"
        >
          <option v-for="(option, i) in options" :key="i" :value="option">
            {{ option }}
          </option>
        </select>
        <input
          class="input"
          v-model="mapping.column"
          @input="(e) => updateMapping(index, 'column', e.target.value)"
          placeholder="Enter column (e.g., A, B, C)"
        />
        <span class="confidence-badge" v-if="mapping.autoDetected">
          Auto-detected
        </span>
      </div>

      <button class="button" @click="addMapping">
        <span class="button-text">+ Add Mapping</span>
      </button>
      <button class="button secondary" @click="autoCreateMappings(previewHeaders, previewData)">
        <span class="button-text">↻ Re-detect Mappings</span>
      </button>
    </div>

    <!-- Enroll Teachers and Undo Buttons -->
    <div class="white-card">
      <button 
        class="button" 
        @click="handleEnrollTeachers"
        :disabled="isLoading || !fileSelected"
      >
        <span v-if="isLoading" class="button-text">
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
                      v-model="headerMappings[index].type"
                      class="table-select"
                      @change="syncHeaderMapping(index, $event.target.value)"
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
                    >
                      <option :value="null">Select Class</option>
                      <option v-for="cls in classes" :key="cls" :value="cls">
                        {{ cls }}
                      </option>
                    </select>
                  </td>
                  <td>
                    <select 
                      v-model="row.divisionName" 
                      class="table-select"
                      :disabled="!row.className"
                    >
                      <option :value="null">Select Division</option>
                      <option v-for="div in row.divisions" :key="div" :value="div">
                        {{ div }}
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
import { enrollTeachers, getClasses, getDivisions1 } from "../utils/apiUtils";
import * as XLSX from "xlsx";

export default {
  data() {
    return {
      mappings: [],
      headerMappings: [],
      fileSelected: null,
      options: [
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
      ],
      isLoading: false,
      message: null,
      previewData: [],
      previewHeaders: [],
      classes: [],
      editHistory: [],
      pendingEdits: [],
    };
  },
  created() {
    this.fetchClasses();
    this.debouncedSendCellUpdate = this.debounce(this.sendCellUpdate, 500);
  },
  methods: {
    async fetchClasses() {
      try {
        const response = await getClasses({ values: {} });
        console.log('getClasses API response:', response);
        if (response && response.message && Array.isArray(response.message)) {
          this.classes = response.message.map(cls => cls.name).filter(name => name);
          console.log('Processed classes:', this.classes);
        } else {
          this.classes = [];
          console.warn('No valid classes found in response');
          this.showMessage("No classes available", "error");
        }
      } catch (error) {
        console.error("Error fetching classes:", error);
        this.classes = [];
        this.showMessage("Error fetching classes: " + (error.message || "Unknown error"), "error");
      }
    },
    async onClassChange(rowIndex) {
      const row = this.previewData[rowIndex];
      row.divisionName = null;

      if (row.className) {
        try {
          const response = await getDivisions1({ 
            values: { classId: row.className } 
          });
          console.log('getDivisions1 API response:', response);
          row.divisions = response.message 
            ? response.message.map(div => div.name).filter(name => name)
            : [];
          console.log(`Divisions for ${row.className}:`, row.divisions);
        } catch (error) {
          console.error("Error fetching divisions:", error);
          this.showMessage(`Error fetching divisions for ${row.className}`, "error");
        }
      } else {
        row.divisions = [];
      }
    },
    getExcelColumnLetter(index) {
      let letter = '';
      while (index >= 0) {
        letter = String.fromCharCode(65 + (index % 26)) + letter;
        index = Math.floor(index / 26) - 1;
      }
      return letter;
    },
    async handleFileSelection() {
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = '.xlsx,.xls';

      input.onchange = async (e) => {
        const file = e.target.files[0];
        if (file) {
          this.fileSelected = file;
          this.showMessage(null);
          try {
            const { data, headers } = await this.readExcelFile(file);
            this.previewData = data.slice(0, 100).map(row => ({
              ...row,
              className: null,
              divisionName: null,
              divisions: []
            }));
            this.previewHeaders = headers;
            // Initialize header mappings
            this.headerMappings = headers.map((_, index) => ({
              type: null,
              column: XLSX.utils.encode_col(index)
            }));
            this.autoCreateMappings(headers, data.slice(0, 5));
          } catch (error) {
            console.error("Error loading preview:", error);
            this.showMessage("Error loading file preview", "error");
          }
        }
      };

      input.click();
    },
    autoCreateMappings(headers, sampleData) {
      this.mappings = [];
      this.headerMappings = this.previewHeaders.map((_, index) => ({
        type: null,
        column: XLSX.utils.encode_col(index)
      }));

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
            const column = XLSX.utils.encode_col(index);
            this.mappings.push({
              type: field,
              column: column,
              autoDetected: true
            });
            this.headerMappings[index].type = field;
            break;
          }
        }
      });

      if (this.mappings.length === 0) {
        const defaultMapping = { type: "Full Name", column: "A", autoDetected: false };
        this.mappings.push(defaultMapping);
        this.headerMappings[0].type = "Full Name";
      }
      console.log('Auto-created mappings:', this.mappings);
      console.log('Header mappings:', this.headerMappings);
    },
    removeFile() {
      this.fileSelected = null;
      this.previewData = [];
      this.previewHeaders = [];
      this.mappings = [];
      this.headerMappings = [];
      this.editHistory = [];
      this.pendingEdits = [];
      this.showMessage(null);
    },
    prepareTeachersData(data, editedRowIndex = null) {
      let teachersData = data;
      if (editedRowIndex !== null) {
        teachersData = [data[editedRowIndex]];
      }

      const fullPreviewData = [...this.previewData];
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

        this.mappings.forEach(({ type, column }) => {
          try {
            const columnIndex = XLSX.utils.decode_col(column);
            const columnName = this.previewHeaders[columnIndex];
            const value = row[columnName]?.toString().trim() || '';
            teacher[type] = value;
          } catch (error) {
            console.error(`Error mapping column ${column} for type ${type}:`, error);
          }
        });

        return teacher;
      });

      const filteredTeachersData = mappedTeachers.filter(teacher =>
        Object.values(teacher).some(value => value !== "")
      );

      return {
        teachers: filteredTeachersData,
        ...this.options.reduce((acc, option) => {
          const mapping = this.mappings.find((mapping) => mapping.type === option);
          acc[option] = mapping ? mapping.column : "None";
          return acc;
        }, {}),
      };
    },
    async handleEnrollTeachers() {
      console.log('Enroll button clicked');

      // Define required fields
      const requiredFields = ['Mobile', 'Email', 'Date of Birth', 'Gender', 'First Name', 'Last Name', "Attendance Device ID (Biometric/RF tag ID)"];

      // Check if all required fields are mapped
      const mappedFields = this.mappings.map(m => m.type).filter(type => type);
      const missingFields = requiredFields.filter(field => !mappedFields.includes(field));

      if (missingFields.length > 0) {
        const msg = `Please map the following required fields: ${missingFields.join(', ')}`;
        console.error(msg);
        this.showMessage(msg, 'error');
        return;
      }

      // Validate column mappings
      const invalidMappings = this.mappings.filter(m => 
        m.type && (!m.column || !/^[A-Z]+$/.test(m.column))
      );

      if (invalidMappings.length > 0) {
        this.showMessage('Please check your column mappings - some are invalid', 'error');
        return;
      }

      // Check if a file is selected
      if (!this.fileSelected) {
        const msg = 'Please select a file first';
        console.error(msg);
        this.showMessage(msg, 'error');
        return;
      }

      this.isLoading = true;
      this.showMessage(null);

      try {
        if (this.previewData.length === 0) {
          throw new Error('No data available to enroll');
        }

        const params = this.prepareTeachersData(this.previewData);
        console.log('Sending updated preview data to enrollTeachers:', params);
        const result = await enrollTeachers(params);

        if (result.success) {
          this.showMessage('✅ Teachers enrolled successfully!', 'success');
          this.pendingEdits = [];
        } else {
          this.showMessage(result.error || 'Failed to enroll teachers', 'error');
          console.error('Enrollment error details:', {
            error: result.error,
            duplicates: result.duplicates,
            message: result.message
          });
        }
      } catch (error) {
        console.error('Error enrolling teachers:', error);
        this.showMessage(error.message || 'Unexpected error during teacher enrollment', 'error');
      } finally {
        this.isLoading = false;
      }
    },
    async readExcelFile(file) {
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
    },
    addMapping() {
      this.mappings.push({ type: "Full Name", column: "" });
    },
    updateMapping(index, key, value) {
      if (key === 'column') {
        value = value.toUpperCase().replace(/[^A-Z]/g, '');
      }
      this.$set(this.mappings, index, {
        ...this.mappings[index],
        [key]: value
      });
      // Sync with headerMappings
      if (key === 'type' || key === 'column') {
        const mapping = this.mappings[index];
        const colIndex = XLSX.utils.decode_col(mapping.column);
        if (colIndex >= 0 && colIndex < this.headerMappings.length) {
          this.$set(this.headerMappings, colIndex, {
            type: mapping.type,
            column: mapping.column
          });
        }
      }
    },
    syncHeaderMapping(index, value) {
      this.$set(this.headerMappings, index, {
        type: value,
        column: XLSX.utils.encode_col(index)
      });
      // Sync with mappings
      const existingIndex = this.mappings.findIndex(m => m.column === this.headerMappings[index].column);
      if (existingIndex >= 0) {
        this.$set(this.mappings, existingIndex, {
          type: value,
          column: this.headerMappings[index].column,
          autoDetected: this.mappings[existingIndex].autoDetected
        });
      } else {
        this.mappings.push({
          type: value,
          column: this.headerMappings[index].column,
          autoDetected: false
        });
      }
    },
    deleteMapping(index) {
      const mapping = this.mappings[index];
      const colIndex = XLSX.utils.decode_col(mapping.column);
      if (colIndex >= 0 && colIndex < this.headerMappings.length) {
        this.$set(this.headerMappings, colIndex, {
          type: null,
          column: mapping.column
        });
      }
      this.mappings.splice(index, 1);
    },
    deleteRow(rowIndex) {
      this.previewData.splice(rowIndex, 1);
      this.editHistory = this.editHistory.filter(edit => edit.rowIndex !== rowIndex);
      this.pendingEdits = this.pendingEdits.filter(edit => edit.rowIndex !== rowIndex);
      this.showMessage('Row deleted', 'success');
    },
    showMessage(text, type = "info") {
      this.message = text ? { text, type } : null;
      if (text && type !== "error" && type !== "success") {
        setTimeout(() => this.showMessage(null), 5000);
      }
    },
    handleCellEdit(rowIndex, header, newValue) {
      const row = this.previewData[rowIndex];
      const oldValue = row[header] || '';

      if (oldValue !== newValue) {
        const edit = {
          rowIndex,
          column: header,
          oldValue,
          newValue,
          timestamp: new Date().toISOString(),
        };
        this.editHistory.push(edit);
        this.pendingEdits.push(edit);
        console.log('Cell edit recorded:', edit);
        this.debouncedSendCellUpdate();
      }
    },
    debounce(fn, wait) {
      let timeout;
      return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => fn.apply(this, args), wait);
      };
    },
    async sendCellUpdate() {
      if (this.pendingEdits.length === 0) return;

      this.isLoading = true;
      try {
        const lastEdit = this.pendingEdits[this.pendingEdits.length - 1];
        const params = this.prepareTeachersData(this.previewData, lastEdit.rowIndex);
        console.log('Sending cell update via enrollTeachers:', params);
        const result = await enrollTeachers(params);

        if (result.success) {
          this.showMessage('Cell update saved successfully', 'success');
          this.pendingEdits = [];
        } else {
          this.showMessage(result.error || 'Failed to save cell update', 'error');
        }
      } catch (error) {
        console.error('Error sending cell update:', error);
        this.showMessage(`Failed to save cell update: ${error.message || 'Unknown error'}`, 'error');
      } finally {
        this.isLoading = false;
      }
    },
    undoLastEdit() {
      const lastEdit = this.editHistory.pop();
      if (lastEdit) {
        const { rowIndex, column, oldValue } = lastEdit;
        this.previewData[rowIndex][column] = oldValue;
        this.pendingEdits = this.pendingEdits.filter(edit => edit !== lastEdit);
        this.showMessage('Last edit undone', 'success');
      } else {
        this.showMessage('No edits to undo', 'info');
      }
    },
  },
};
</script>

<style scoped>
.no-mappings {
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 5px;
  margin-bottom: 15px;
  text-align: center;
  color: #6c757d;
}

.confidence-badge {
  background-color: #e2f0fd;
  color: #0d6efd;
  padding: 3px 8px;
  border-radius: 10px;
  font-size: 0.8em;
  margin-left: 10px;
}

.header-label {
  display: block;
  font-size: 0.8em;
  color: #6c757d;
  margin-top: 4px;
  text-align: center;
}

.button.secondary {
  background-color: #6c757d;
  margin-left: 10px;
}

.table-select {
  width: 100%;
  padding: 5px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.8em;
  background-color: white;
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
  width: 20%;
  box-sizing: border-box;
}

.table-white-card {
  background-color: white;
  padding: 15px;
  border-radius: 10px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  width: 50%;
  box-sizing: border-box;
}

.card-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 10px;
}

.input {
  width: 20%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
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

.card {
  background-color: white;
  padding: 15px;
  border-radius: 10px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
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

.table-outer-container {
  width: 100%;
  overflow: hidden;
  border-radius: 5px;
  margin-top: 15px;
}

.table-container {
  width: 100%;
  overflow-x: auto;
  border: 1px solid #e0e0e0;
  border-radius: 5px;
  background-color: white;
}

.preview-table {
  width: auto;
  min-width: 100%;
  border-collapse: collapse;
  font-size: 0.9em;
  table-layout: auto;
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

.table-scroll-container {
  max-height: 400px;
  overflow-y: auto;
  display: block;
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

.preview-card {
  margin-top: 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>