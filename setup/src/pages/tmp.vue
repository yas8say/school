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

    <!-- Enroll Teachers Button -->
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

    <!-- File Preview with Class/Division Selection -->
    <div v-if="fileSelected && previewData.length > 0" class="table-white-card preview-card">
      <h2 class="card-title">File Preview (First 100 rows)</h2>
      <div class="table-outer-container">
          <div class="table-scroll-container">
      <div class="table-container">
        <table class="preview-table">
          <thead>
            <tr>
              <th>Class</th>
              <th>Division</th>
              <th v-for="(_, index) in previewHeaders" :key="'letter-'+index">
                {{ getExcelColumnLetter(index) }}
              </th>
            </tr>
            <tr>
              <th>Class</th>
              <th>Division</th>
              <th v-for="(header, index) in previewHeaders" :key="'header-'+index">
                {{ header }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, rowIndex) in previewData" :key="rowIndex">
              <td>

                <select 
                v-model="row.className" 
                  class="table-select"
                  @change="onClassChange(rowIndex)"
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
                  :disabled="!row.className"
                >
                  <option :value="null">Select Division</option>
                  <option v-for="div in row.divisions" :key="div.name" :value="div.name">
                    {{ div.name }}
                  </option>
                </select>
              </td>
              <td v-for="(header, colIndex) in previewHeaders" :key="colIndex">
                {{ row[header] || '-' }}
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
import { enrollTeachers, getClasses, getDivisions } from "../utils/apiUtils";
import * as XLSX from "xlsx";

export default {
  data() {
    return {
      mappings: [],
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
    };
  },
  async created() {
    await this.fetchClasses();
  },
  methods: {
      autoCreateMappings(headers, sampleData) {
// Clear existing mappings
this.mappings = [];

// Common patterns to look for in column headers
const fieldPatterns = {
  "First Name": ["first", "fname", "given", "firstname"],
  "Middle Name": ["middle", "mname", "midname"],
  "Last Name": ["last", "lname", "surname", "family", "lastname"],
  "Email": ["email", "e-mail", "mail"],
  "Mobile": ["mobile", "phone", "cell", "contact"],
  "Date of Birth": ["dob", "birth", "birthdate", "date of birth"],
  "Gender": ["gender", "sex"],
  "Date of Joining": ["doj", "joining", "start date"],
  "PAN Number": ["pan", "pan no"],
  "Bank Name": ["bank", "bank name"],
  "Bank A/C No.": ["account", "ac no", "bank account"],
  "IFSC Code": ["ifsc", "code"],
  "Designation": ["designation", "position", "title"],
  // Add more patterns for other fields as needed
};

// Try to match each of our required fields to a column
for (const option of this.options) {
  // Skip if we already have a mapping for this field
  if (this.mappings.some(m => m.type === option)) {
    continue;
  }
  
  const patterns = fieldPatterns[option] || [option.toLowerCase()];
  
  // Look for matching column in headers
  const matchingHeaderIndex = headers.findIndex(header => {
    if (!header) return false;
    const headerLower = header.toString().toLowerCase();
    return patterns.some(pattern => headerLower.includes(pattern));
  });
  
  if (matchingHeaderIndex >= 0) {
    const columnLetter = XLSX.utils.encode_col(matchingHeaderIndex);
    this.mappings.push({
      type: option,
      column: columnLetter,
      autoDetected: true
    });
  }
}

console.log('Auto-created mappings:', this.mappings);
},
async fetchClasses() {
  try {
    const response = await getClasses({ values: {} });
    // Properly extract class names from the API response
    this.classes = response.message 
      ? response.message.map(cls => cls.name) 
      : [];
    console.log("Classes loaded:", this.classes);
  } catch (error) {
    console.error("Error fetching classes:", error);
    this.showMessage("Error fetching classes", "error");
  }
},
    
async onClassChange(rowIndex) {
  const row = this.previewData[rowIndex];
  row.divisionName = null;
  
  if (row.className) {
    try {
      const response = await getDivisions({ 
        values: { classId: row.className } 
      });
      // Properly extract division names from the API response
      row.divisions = response.message 
        ? response.message.map(div => div.name)
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
            this.previewData = data.slice(0, 100);
            this.previewHeaders = headers;
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
    async handleEnrollTeachers() {
  console.log('Enroll button clicked');

  if (!this.fileSelected) {
    const msg = "Please select a file first";
    console.error(msg);
    this.showMessage(msg, "error");
    return;
  }

  this.isLoading = true;
  this.showMessage(null);

  try {
    console.log('Reading Excel file:', this.fileSelected.name);
    const { data } = await this.readExcelFile(this.fileSelected);
    
    if (data.length === 0) {
      throw new Error("No data found in the file");
    }

    console.log('Excel file parsed successfully. Row count:', data.length);
    console.log('First row sample:', data[0]);

    const fullPreviewData = [...this.previewData];
    console.log('=== Current Mappings ===');
    console.table(this.mappings);

    console.log('Parsing teacher data using mappings...');
    const teachersData = data.map((row, rowIndex) => {
      const previewRow = rowIndex < fullPreviewData.length 
        ? fullPreviewData[rowIndex] 
        : {};

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
          const columnName = Object.keys(row)[columnIndex];
          const value = row[columnName]?.toString().trim() || '';
          console.log(`Row ${rowIndex}: Mapping ${column} (${columnName}) to ${type} with value:`, value);
          teacher[type] = value;
        } catch (error) {
          console.error(`Error mapping column ${column} for type ${type}:`, error);
        }
      });

      console.log(`Processed teacher data for row ${rowIndex}:`, teacher);
      return teacher;
    });

    const filteredTeachersData = teachersData.filter(teacher =>
      Object.values(teacher).some(value => value !== "")
    );

    console.log('=== Final Teachers Data ===');
    console.table(filteredTeachersData);

    const params = {
      teachers: filteredTeachersData,
      ...this.options.reduce((acc, option) => {
        const mapping = this.mappings.find((mapping) => mapping.type === option);
        acc[option] = mapping ? mapping.column : "None";
        return acc;
      }, {}),
    };

    console.log('Calling enrollTeachers API...');
    const result = await enrollTeachers(params);
    console.log('API Response:', result);

    if (result.success) {
  this.showMessage("✅ Teachers enrolled successfully!", "success");
} else {
  let userMessage = result.error;
  this.showMessage(userMessage, "error");

  console.error("Enrollment error details:", {
  error: result.error,
  duplicates: result.duplicates,
  message: result.message
});
}
  } catch (error) {
    console.error("Error enrolling teachers:", error);
    this.showMessage(error.message || "Unexpected error during teacher enrollment", "error");
  } finally {
    this.isLoading = false;
  }
}
,
async readExcelFile(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: 'array', sheetStubs: true });
        const sheet = workbook.Sheets[workbook.SheetNames[0]];
        
        // Get the range of the sheet
        const range = XLSX.utils.decode_range(sheet['!ref']);
        
        // Find header row (first non-empty row)
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
        
        // Extract headers
        const headers = [];
        for (let C = range.s.c; C <= range.e.c; ++C) {
          const cell = sheet[XLSX.utils.encode_cell({c: C, r: headerRow})];
          headers.push(cell ? String(cell.v).trim() : `Column ${C+1}`);
        }
        
        // Read data while preserving empty cells and filtering empty rows
        const jsonData = [];
        for (let R = headerRow + 1; R <= range.e.r; ++R) {
          const row = {};
          let hasData = false;
          
          for (let C = range.s.c; C <= range.e.c; ++C) {
            const cell = sheet[XLSX.utils.encode_cell({c: C, r: R})];
            const header = headers[C - range.s.c];
            // Preserve empty cells as empty strings instead of skipping them
            row[header] = cell ? (cell.v === undefined ? '' : cell.v) : '';
            
            // Check if this cell has data
            if (row[header] !== '') {
              hasData = true;
            }
          }
          
          // Only add row if it contains some data
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
      this.mappings[index][key] = value;
      this.mappings = [...this.mappings];
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

/* Sticky headers */
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

/* Vertical scrolling */
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