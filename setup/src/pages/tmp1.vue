<template>
  <div class="scroll-view-content">
    <h1 class="title">Setup Screen 2</h1>

    <!-- White Card for Select Class and Division -->
    <div class="white-card">
      <h2 class="card-title">Select a Class</h2>
      <select v-model="selectedClass" class="picker2" @change="onClassChange">
        <option :value="null">Select a Class</option>
        <option v-for="cls in classes" :key="cls.name" :value="cls.name">
          {{ cls.name }}
        </option>
      </select>

      <h2 v-if="divisions.length > 0" class="card-title">Select a Division</h2>
      <select v-if="divisions.length > 0" v-model="selectedDivision" class="picker2">
      <option :value="null">Select a Division</option>
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

    <!-- Column Mappings (only shown when file is selected) -->
    <div v-if="fileSelected" class="white-card">
      <h2 class="card-title">Column Mappings</h2>
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
          @input="(e) => updateMapping(index, 'column', e.target.value.toUpperCase())"
          placeholder="Enter column (e.g., A, B, C)"
          pattern="[A-Za-z]+"
        />
      </div>

      <button class="button" @click="addMapping">
        <span class="button-text">+ Add Mapping</span>
      </button>
    </div>

    <!-- Enroll Students Button with Loading State -->
    <div class="white-card">
      <button 
        class="button" 
        @click="handleEnrollStudents"
        :disabled="isLoading || !selectedClass || !selectedDivision || !fileSelected"
      >
        <span v-if="isLoading" class="button-text">
          <span class="spinner"></span> Processing...
        </span>
        <span v-else class="button-text">Enroll Students ✅</span>
      </button>

      <!-- Success/Error Message -->
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
        <!-- First row for Excel column letters -->
        <tr>
          <th v-for="(_, index) in previewHeaders" :key="'letter-'+index">
            {{ getExcelColumnLetter(index) }}
          </th>
        </tr>
        <!-- Second row for actual headers -->
        <tr>
          <th v-for="(header, index) in previewHeaders" :key="'header-'+index">
            {{ header }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, rowIndex) in previewData" :key="rowIndex">
          <td v-for="(header, colIndex) in previewHeaders" :key="colIndex">
            {{ row[header] || '-' }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
  </div>
</template>

<script>
import { enrollStudents, getClasses, getDivisions } from "../utils/apiUtils";
import * as XLSX from "xlsx";

export default {
  data() {
    return {
      classes: [],
      divisions: [],
      selectedClass: null,
      selectedDivision: null,
      mappings: [],
      fileSelected: null,
      studentsList: [],
      options: ["First Name", "Middle Name", "Last Name", "Name", "Email Address", "Phone Number", "GR Number", "Roll No"],
      isLoading: false,
      message: null,
      previewData: [],
      previewHeaders: []
    };
  },
  async created() {
    await this.fetchClasses();
  },
  methods: {
    getExcelColumnLetter(index) {
    // Convert 0-based index to Excel column letter (A, B, ..., Z, AA, AB, etc.)
    let letter = '';
    while (index >= 0) {
      letter = String.fromCharCode(65 + (index % 26)) + letter;
      index = Math.floor(index / 26) - 1;
    }
    return letter;
  },
  async fetchClasses() {
  try {
    const response = await getClasses({ values: {} });
    // Properly extract class names from the API response
    this.classes = response.message || [];
  } catch (error) {
    console.error("Error fetching classes:", error);
    this.showMessage("Error fetching classes", "error");
  }
},
async onClassChange() {
  this.selectedDivision = null;
  this.divisions = [];
  
  if (this.selectedClass) {
    try {
      const response = await getDivisions({ 
        values: { classId: this.selectedClass } 
      });
      // Properly extract division names from the API response
      this.divisions = response.message || [];
    } catch (error) {
      console.error("Error fetching divisions:", error);
      this.showMessage("Error fetching divisions", "error");
    }
  }
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
        
        // Auto-populate mappings if headers match known patterns
        this.autoCreateMappings(headers, data.slice(0, 5));
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
      this.showMessage(null);
    },
    async handleEnrollStudents() {

  console.log('Enroll button clicked');
  const invalidMappings = this.mappings.filter(m => 
    !m.type || !m.column || !/^[A-Z]+$/.test(m.column)
  );
  
  if (invalidMappings.length > 0) {
    this.showMessage("Please check your column mappings - some are invalid", "error");
    return;
  }

  if (!this.selectedClass || !this.selectedDivision) {
    const msg = "Please select both a class and a division";
    console.error(msg);
    this.showMessage(msg, "error");
    return;
  }

  if (!this.fileSelected) {
    const msg = "Please select a file first";
    console.error(msg);
    this.showMessage(msg, "error");
    return;
  }

  this.isLoading = true;
  this.showMessage(null);

  try {
    console.log('Starting enrollment process');
    const fileExtension = this.fileSelected.name.split('.').pop();

    if (!(fileExtension === "xlsx" || fileExtension === "xls")) {
      throw new Error("Unsupported file type. Please upload an Excel file.");
    }

    console.log('Reading Excel file');
    const { data } = await this.readExcelFile(this.fileSelected);

    if (data.length === 0) {
      throw new Error("No data found in the file");
    }

    console.log('Parsing student data with space-separated property names');
    const studentsData = data.map((row) => {
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
        try {
          const columnIndex = XLSX.utils.decode_col(column);
          const columnName = Object.keys(row)[columnIndex];
          const value = row[columnName]?.toString().trim() || '';
          student[type] = value;
        } catch (error) {
          console.error(`Error mapping column ${column} for type ${type}:`, error);
        }
      });
      return student;
    });

    console.log('Students data to be sent:');
    console.table(studentsData);

    const params = {
      className: this.selectedClass,
      divisionName: this.selectedDivision,
      students: studentsData,
      ...this.options.reduce((acc, option) => {
        const mapping = this.mappings.find((mapping) => mapping.type === option);
        acc[option] = mapping ? mapping.column : "None";
        return acc;
      }, {}),
    };

    console.log('Full API params:', JSON.stringify(params, null, 2));
    console.log('Calling enrollStudents with params:', params);

    const response = await enrollStudents(params);
    console.log('API Response:', response);

    if (response.success) {
      this.showMessage(response.message || "✅ Student enrolled successfully!", "success");
      this.resetForm();
    } else {
      let userMessage = response.error;
      this.showMessage(userMessage, "error");
    }
  } catch (error) {
    console.error("Error in enrollment process:", error);
    this.showMessage(error.message || "Unexpected error during enrollment", "error");
  } finally {
    this.isLoading = false;
  }
},
autoCreateMappings(headers) {
  const fieldPatterns = {
    "First Name": ["first", "fname", "given"],
    "Last Name": ["last", "lname", "surname"],
    "Email Address": ["email", "mail"],
    "Phone Number": ["phone", "mobile", "contact"],
    "GR Number": ["gr", "grno", "gr_num"],
    "Roll No": ["roll", "rollno", "roll_num"]
  };

  this.mappings = [];
  
  headers.forEach((header, index) => {
    const headerLower = header.toLowerCase();
    for (const [field, patterns] of Object.entries(fieldPatterns)) {
      if (patterns.some(pattern => headerLower.includes(pattern))) {
        this.mappings.push({
          type: field,
          column: XLSX.utils.encode_col(index),
          autoDetected: true
        });
        break;
      }
    }
  });
  
  // Ensure we have at least one mapping
  if (this.mappings.length === 0) {
    this.mappings.push({ type: "Name", column: "A" });
  }
},
async readExcelFile(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: 'array' });
        const sheet = workbook.Sheets[workbook.SheetNames[0]];
        
        // Get the range and find the first non-empty row for headers
        const range = XLSX.utils.decode_range(sheet['!ref']);
        let headerRow = 0;
        
        // Skip empty rows at the top
        while (headerRow <= range.e.r) {
          const cell = sheet[XLSX.utils.encode_cell({c: 0, r: headerRow})];
          if (cell && cell.v) break;
          headerRow++;
        }
        
        // Get headers from the first non-empty row
        const headers = [];
        for (let C = range.s.c; C <= range.e.c; ++C) {
          const cell = sheet[XLSX.utils.encode_cell({c: C, r: headerRow})];
          headers.push(cell ? cell.v : `Column ${C+1}`);
        }
        
        // Convert to JSON starting from the row after headers
        const jsonData = XLSX.utils.sheet_to_json(sheet, { 
          header: headers,
          range: headerRow + 1 // Skip the header row in data
        });
        
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
  this.mappings.push({ 
    type: this.options[0], // Default to first option
    column: "" 
  });
},
    updateMapping(index, key, value) {
  // For column updates, ensure it's a valid letter
  if (key === 'column') {
    // Only allow letters and convert to uppercase
    value = value.replace(/[^A-Za-z]/g, '').toUpperCase();
  }
  
  this.$set(this.mappings, index, {
    ...this.mappings[index],
    [key]: value
  });
},
    deleteMapping(index) {
      this.mappings.splice(index, 1);
    },
    showMessage(text, type = "info") {
      this.message = text ? { text, type } : null;
      // Only auto-hide non-success messages
      if (text && type !== "error" && type !== "success") {
        setTimeout(() => this.showMessage(null), 5000);
      }
    }
  },
};
</script>

<style scoped>
/* Add these styles to your existing styles */
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

/* Column letters row */
.preview-table thead tr:first-child th {
  background-color: #f0f0f0;
  font-size: 0.8em;
  text-align: center;
  position: sticky;
  top: 0;
  z-index: 2;
}

/* Actual headers row */
.preview-table thead tr:nth-child(2) th {
  background-color: #f5f5f5;
  font-weight: bold;
  position: sticky;
  top: 24px; /* Height of first row */
  z-index: 1;
}

.preview-table tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}

.preview-table tr:hover {
  background-color: #f0f0f0;
}

/* Ensure the table headers stay visible when scrolling */
.table-container {
  position: relative;
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

.input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
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

/* Table styles - optimized and consolidated */
.table-container {
  max-height: 400px;
  overflow-y: auto;
  margin-top: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 5px;
}

.preview-table {
  width: 100%;
  border-collapse: collapse;
}

.preview-table th, 
.preview-table td {
  padding: 10px;
  border: 1px solid #e0e0e0;
  text-align: left;
}

/* Column letters row */
.preview-table thead tr:first-child th {
  background-color: #e0e0e0;
  font-size: 0.9em;
  text-align: center;
  position: sticky;
  top: 0;
  z-index: 3; /* Highest z-index */
}

/* Actual headers row */
.preview-table thead tr:nth-child(2) th {
  background-color: #f5f5f5;
  font-weight: bold;
  position: sticky;
  top: 29px; /* Height of first row */
  z-index: 2;
}

.preview-table tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}

.preview-table tr:hover {
  background-color: #f0f0f0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>