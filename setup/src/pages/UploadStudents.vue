<template>
  <div class="scroll-view-content">
    <h1 class="title">Students Enrollment Screen</h1>

    <!-- White Card for Select Year, Class and Division -->
    <div class="white-card">
      <h2 class="card-title">Select a Year</h2>
      <select v-model="selectedYear" class="picker2" @change="onYearChange">
        <option :value="null">Select a Year</option>
        <option v-for="year in displayYears" :key="year" :value="year.original">
          {{ year.display }}
        </option>
      </select>

      <h2 class="card-title">Class / Program</h2>
      <select v-model="selectedClass" class="picker2" @change="onClassChange">
        <option :value="null">Select a Class / Program</option>
        <option v-for="cls in classes" :key="cls" :value="cls">
          {{ cls }}
        </option>
      </select>

      <h2 v-if="divisions.length > 0" class="card-title">Division / Student Group</h2>
      <select v-if="divisions.length > 0" v-model="selectedDivision" class="picker2">
        <option :value="null">Select a Division / Student Group</option>
        <option v-for="div in divisions" :key="div" :value="div">
          {{ div }}
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
        :disabled="isLoading || !selectedYear || !selectedClass || !selectedDivision || !fileSelected"
      >
        <span v-if="isLoading" class="button-text">
          <span class="spinner"></span> Processing...
        </span>
        <span v-else class="button-text">Enroll Students ✅</span>
      </button>

      <div v-if="message" :class="['message', message.type]">
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
import { enrollStudents, getAcademicYears, getClasses, getDivisions2 } from "../utils/apiUtils";
import * as XLSX from "xlsx";

export default {
  data() {
    return {
      academicYears: [],
      displayYears: [],
      selectedYear: null,
      classes: [],
      divisions: [],
      selectedClass: null,
      selectedDivision: null,
      mappings: [],
      fileSelected: null,
      studentsList: [],
      options: ["First Name", "Middle Name", "Last Name", "Email Address", "Phone Number", "GR Number", "Roll No"],
      isLoading: false,
      message: null,
      previewData: [],
      previewHeaders: [],
      editHistory: [],
      pendingEdits: [],
    };
  },
  created() {
    this.fetchAcademicYears();
    this.fetchClasses();
    this.debouncedSendCellUpdate = this.debounce(this.sendCellUpdate, 500);
  },
  methods: {
    async fetchAcademicYears() {
      try {
        const response = await getAcademicYears({ values: {} });
        console.log('getAcademicYears API response:', response);

        if (response && Array.isArray(response.message)) {
          this.academicYears = response.message;
          this.displayYears = this.academicYears.map((year, index) => ({
            original: year,
            display: index === 0 ? `${year} - Current Year` : year
          }));
          if (this.academicYears.length > 0) {
            this.selectedYear = this.academicYears[0];
          }
          console.log('Processed academic years:', this.academicYears);
        } else {
          this.academicYears = [];
          this.displayYears = [];
          console.warn('No valid academic years found in response');
          this.showMessage("No academic years available", "error");
        }
      } catch (error) {
        console.error("Error fetching academic years:", error);
        this.academicYears = [];
        this.displayYears = [];
        this.showMessage("Error fetching academic years: " + (error.message || "Unknown error"), "error");
      }
    },
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
    async onYearChange() {
      this.selectedClass = null;
      this.selectedDivision = null;
      this.divisions = [];
      await this.onClassChange();
    },
    async onClassChange() {
      this.selectedDivision = null;
      this.divisions = [];

      if (this.selectedClass && this.selectedYear) {
        try {
          const response = await getDivisions2({ 
            values: { 
              classId: this.selectedClass,
              academicYear: this.selectedYear 
            } 
          });
          console.log('getDivisions2 API response:', response);
          this.divisions = response.message 
            ? response.message.map(div => div.name).filter(name => name)
            : [];
          console.log(`Divisions for ${this.selectedClass} in ${this.selectedYear}:`, this.divisions);
        } catch (error) {
          console.error("Error fetching divisions:", error);
          this.showMessage(`Error fetching divisions for ${this.selectedClass} in ${this.selectedYear}`, "error");
        }
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
      input.accept = '.xlsx,.xls,.csv';

      input.onchange = async (e) => {
        const file = e.target.files[0];
        if (file) {
          this.fileSelected = file;
          this.showMessage(null);
          try {
            const { data, headers } = await this.readExcelFile(file);
            this.previewData = data.slice(0, 100);
            this.previewHeaders = headers;
            // Initialize mappings for each column
            this.mappings = headers.map((_, index) => ({
              type: null,
              column: XLSX.utils.encode_col(index)
            }));
            this.autoDetectMappings(headers);
          } catch (error) {
            console.error("Error loading preview:", error);
            this.showMessage("Error loading file preview", "error");
          }
        }
      };
      input.click();
    },
    removeFile() {
      this.fileSelected = null;
      this.previewData = [];
      this.previewHeaders = [];
      this.mappings = [];
      this.editHistory = [];
      this.pendingEdits = [];
      this.showMessage(null);
    },
    prepareStudentsData(data, editedRowIndex = null) {
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
          "Roll No": ""
        };

        this.mappings.forEach(({ type, column }) => {
          if (type) {
            try {
              const columnIndex = XLSX.utils.decode_col(column);
              const columnName = this.previewHeaders[columnIndex];
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
        academicYear: this.selectedYear,
        className: this.selectedClass,
        divisionName: this.selectedDivision,
        students: filteredStudentsData,
        ...this.options.reduce((acc, option) => {
          const mapping = this.mappings.find(mapping => mapping.type === option);
          acc[option] = mapping ? mapping.column : "None";
          return acc;
        }, {}),
      };
    },
    async handleEnrollStudents() {
      console.log('Enroll button clicked');

      const requiredFields = ['First Name', 'GR Number', 'Last Name', 'Roll No'];

      const mappedFields = this.mappings.map(m => m.type).filter(type => type);
      const missingFields = requiredFields.filter(field => !mappedFields.includes(field));

      if (missingFields.length > 0) {
        const msg = `Please map the following required fields: ${missingFields.join(', ')}`;
        console.error(msg);
        this.showMessage(msg, 'error');
        return;
      }

      const invalidMappings = this.mappings.filter(m => 
        m.type && (!m.column || !/^[A-Z]+$/.test(m.column))
      );

      if (invalidMappings.length > 0) {
        this.showMessage('Please check your column mappings - some are invalid', 'error');
        return;
      }

      if (!this.selectedYear || !this.selectedClass || !this.selectedDivision) {
        const msg = 'Please select an academic year, class, and division';
        console.error(msg);
        this.showMessage(msg, 'error');
        return;
      }

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

        const params = this.prepareStudentsData(this.previewData);
        console.log('Sending updated preview data to enrollStudents:', params);
        const response = await enrollStudents(params);

        if (response.success) {
          this.showMessage('✅ Students enrolled successfully!', 'success');
          this.pendingEdits = [];
        } else {
          this.showMessage(response.error || 'Failed to enroll students', 'error');
          console.error('Enrollment error details:', {
            error: response.error,
            duplicates: response.duplicates,
            message: response.message
          });
        }
      } catch (error) {
        console.error('Error enrolling students:', error);
        this.showMessage(error.message || 'Unexpected error during enrollment', 'error');
      } finally {
        this.isLoading = false;
      }
    },
    autoDetectMappings(headers) {
      const fieldPatterns = {
        "First Name": ["first", "fname", "given"],
        "Last Name": ["last", "lname", "surname"],
        "Middle Name": ["middle", "mname"],
        "Email Address": ["email", "mail"],
        "Phone Number": ["phone", "mobile", "contact"],
        "GR Number": ["gr", "grno", "gr_num"],
        "Roll No": ["roll", "rollno", "roll_num"]
      };

      headers.forEach((header, index) => {
        if (!header) return;
        const headerLower = header.toLowerCase();
        for (const [field, patterns] of Object.entries(fieldPatterns)) {
          if (patterns.some(pattern => headerLower.includes(pattern))) {
            this.mappings[index].type = field;
            break;
          }
        }
      });

      console.log('Auto-detected mappings:', this.mappings);
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
    updateMapping(index, key, value) {
      this.$set(this.mappings, index, {
        ...this.mappings[index],
        [key]: value,
        column: XLSX.utils.encode_col(index)
      });
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
        const params = this.prepareStudentsData(this.previewData, lastEdit.rowIndex);
        console.log('Sending cell update via enrollStudents:', params);
        const result = await enrollStudents(params);

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