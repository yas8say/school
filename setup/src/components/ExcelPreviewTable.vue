<!-- src/components/ExcelPreviewTable.vue -->
<template>
  <div class="preview-card">
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
              style="cursor:pointer"
              @click="$emit('toggle-error-list')"
              :title="invalidRowsCount ? 'Click to view errors' : ''">
          {{ invalidRowsCount }}
        </span>
      </div>
    </div>

    <!-- Error List -->
    <div v-if="showErrorStudentsList && errorRows.length" class="error-students-card">
      <h4 class="section-title">Records with Errors ({{ invalidRowsCount }})</h4>
      <div class="error-details">
        <div v-for="(row, i) in errorRows" :key="i" class="error-message">
          <div class="error-student">
            <strong>{{ getFullName(row) }}</strong>
            <span class="student-details">({{ getIdentifierLabel(row) }}: {{ getIdentifierValue(row) }})</span>
          </div>
          <div class="error-text">Warning {{ getRowError(row) }}</div>
        </div>
      </div>
    </div>

    <div class="table-spacing" v-if="showErrorStudentsList && errorRows.length"></div>

    <!-- Table -->
    <div class="table-container-wrapper">
      <div class="table-scroll-container" ref="scrollContainer">
        <div class="table-container">
          <table class="preview-table">
            <thead>
              <tr>
                <th class="actions">Actions</th>
                <th class="status-cell">Status</th>
                <th v-for="(_, i) in previewHeaders"
                    :key="'letter-' + i">
                  {{ getExcelColumnLetter(i) }}
                </th>
              </tr>
              <tr>
                <th class="actions"></th>
                <th class="status-cell"></th>
                <th v-for="(h, i) in previewHeaders"
                    :key="'header-' + i">
                  <select v-model="mappings[i].type"
                          class="table-select"
                          @change="$emit('update-mapping', i, 'type', $event.target.value)">
                    <option :value="null">Select Field</option>
                    <option v-for="opt in options" :key="opt" :value="opt">{{ opt }}</option>
                  </select>
                  <span class="header-label">{{ h }}</span>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, rIdx) in previewData"
                  :key="rIdx"
                  :class="getRowStatusClass(row)">
                <td class="actions">
                  <button @click="$emit('delete-row', rIdx)" class="trash-icon">Delete</button>
                </td>
                <td class="status-cell">
                  <span v-if="row._status === 'success'" class="status-badge success">Success</span>
                  <span v-else-if="row._status === 'error'" class="status-badge error">Error</span>
                  <span v-else-if="!isRowValid(row)" class="status-badge warning">Warning</span>
                  <span v-else class="status-badge pending">Pending</span>
                  <div v-if="row._error" class="error-tooltip">{{ row._error }}</div>
                </td>
                <td v-for="(h, cIdx) in previewHeaders"
                    :key="cIdx">
                  <input v-model="row[h]"
                         class="table-input"
                         @input="$emit('cell-edit', rIdx, h, $event.target.value)"
                         @blur="$emit('mark-row-touched', rIdx)"
                         :placeholder="row[h] || '-'"/>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue';
import * as XLSX from 'xlsx';
import '@/styles/EnrollmentStyles.css';

const props = defineProps({
  previewData: Array,
  previewHeaders: Array,
  mappings: Array,
  options: Array,
  showErrorStudentsList: Boolean
});

const emit = defineEmits(['toggle-error-list', 'update-mapping', 'delete-row', 'cell-edit', 'mark-row-touched']);

/* DEBUG: Log when props change */
watch(() => props.previewHeaders, (newVal) => {
  console.log('[DEBUG] previewHeaders changed:', newVal?.length || 0, newVal);
}, { deep: true });

watch(() => props.options, (newVal) => {
  console.log('[DEBUG] options changed:', newVal?.length || 0, newVal);
}, { deep: true });

/* Validation & Helpers */
const validRowsCount = computed(() => props.previewData.filter(isRowValid).length);
const invalidRowsCount = computed(() => props.previewData.filter(r => !isRowValid(r)).length);
const errorRows = computed(() => props.previewData.filter(r => !isRowValid(r)));

const isRowValid = (row) => {
  const required = props.options.filter(o => [
    'First Name', 'Last Name', 'Email', 'Mobile', 'GR Number', 'Roll No',
    "Attendance Device ID (Biometric/RF tag ID)", "Date of Birth", "Date of Joining"
  ].includes(o));
  for (const f of required) {
    const m = props.mappings.find(m => m.type === f);
    if (!m) return false;
    const col = XLSX.utils.decode_col(m.column);
    const val = row[props.previewHeaders[col]];
    if (!val || !val.toString().trim()) return false;
  }
  return true;
};

const getRowStatusClass = (r) => {
  if (r._status === 'success') return 'row-success';
  if (r._enrollment_status === 'error') return 'row-enrollment-error';
  if (!isRowValid(r)) return 'row-invalid';
  return '';
};

const getFullName = (r) => {
  const d = prepareData(r);
  return `${d['First Name']||''} ${d['Middle Name']||''} ${d['Last Name']||''}`.trim() || 'Unknown';
};

const getIdentifierLabel = (r) => {
  const d = prepareData(r);
  return d['GR Number'] ? 'GR' : d['Email'] ? 'Email' : 'ID';
};

const getIdentifierValue = (r) => {
  const d = prepareData(r);
  return d['GR Number'] || d['Email'] || d['Mobile'] || 'N/A';
};

const getRowError = (r) => {
  const errs = [];
  const req = ['First Name','Last Name','Email','Mobile','GR Number','Roll No'];
  req.forEach(f => {
    const m = props.mappings.find(m => m.type === f);
    if (!m) errs.push(`${f} not mapped`);
    else {
      const col = XLSX.utils.decode_col(m.column);
      const v = r[props.previewHeaders[col]];
      if (!v || !v.toString().trim()) errs.push(`${f} missing`);
    }
  });
  return errs.length ? errs.join('; ') : 'Check mappings';
};

const prepareData = (row) => {
  const d = {};
  props.mappings.forEach(({type, column}) => {
    if (type && column) {
      const col = XLSX.utils.decode_col(column);
      const hdr = props.previewHeaders[col];
      d[type] = row[hdr]?.toString().trim() || '';
    }
  });
  return d;
};

const getExcelColumnLetter = (i) => {
  let l = '';
  while (i >= 0) { l = String.fromCharCode(65 + (i % 26)) + l; i = Math.floor(i/26)-1; }
  return l;
};
</script>

<style scoped>
.preview-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
}

.stat-value.valid {
  color: #10b981;
}

.stat-value.warning {
  color: #f59e0b;
}

.stat-value.info {
  color: #3b82f6;
}

.error-students-card {
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 16px;
}

.error-details {
  max-height: 200px;
  overflow-y: auto;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.error-message {
  padding: 16px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  margin-bottom: 12px;
}

.error-student {
  margin-bottom: 8px;
}

.error-student strong {
  color: #1f2937;
}

.student-details {
  color: #6b7280;
  font-size: 14px;
  margin-left: 8px;
}

.error-text {
  color: #dc2626;
  font-weight: 500;
}

.multiple-errors {
  white-space: pre-wrap;
}

.table-spacing {
  height: 20px;
}

.instructions {
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 16px;
}

.instructions p {
  margin: 0;
  color: #0369a1;
  font-size: 14px;
}

/* DYNAMIC TABLE STYLES */
.table-container-wrapper {
  width: 100%;
  overflow-x: auto;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.table-scroll-container {
  min-width: min-content;
}

.table-container {
  width: auto;
  min-width: 100%;
}

.preview-table {
  width: auto;
  border-collapse: collapse;
  background: white;
  table-layout: auto; /* Critical for dynamic column sizing */
}

.preview-table th,
.preview-table td {
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  text-align: left;
  vertical-align: top;
  white-space: nowrap;
  min-width: 120px; /* Minimum width but can expand dynamically */
}

.preview-table th {
  background: #f8fafc;
  font-weight: 600;
  color: #374151;
  position: relative;
}

/* Fixed width columns for actions and status */
.preview-table th.actions,
.preview-table td.actions {
  width: 80px;
  min-width: 80px;
  max-width: 80px;
  text-align: center;
}

.preview-table th.status-cell,
.preview-table td.status-cell {
  width: 100px;
  min-width: 100px;
  max-width: 100px;
  text-align: center;
}

.table-select {
  width: 100%;
  padding: 6px 8px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 12px;
  background: white;
  min-width: 120px; /* Ensure dropdowns don't get too small */
}

.table-input {
  width: 100%;
  padding: 6px 8px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 12px;
  background: white;
  min-width: 120px; /* Ensure inputs don't get too small */
}

.table-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.header-label {
  display: block;
  margin-top: 4px;
  font-size: 11px;
  color: #6b7280;
  font-weight: normal;
}

.optional {
  color: #9ca3af;
  font-weight: normal;
  font-size: 0.8em;
}

.trash-icon {
  background: none;
  border: none;
  color: #ef4444;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.trash-icon:hover {
  background: #fef2f2;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.success {
  background: #dcfce7;
  color: #166534;
}

.status-badge.error {
  background: #fee2e2;
  color: #991b1b;
}

.status-badge.warning {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.pending {
  background: #dbeafe;
  color: #1e40af;
}

.error-tooltip {
  position: absolute;
  background: #1f2937;
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 12px;
  z-index: 10;
  max-width: 300px;
  white-space: normal;
  display: none;
}

.status-cell:hover .error-tooltip {
  display: block;
}

.field-hint {
  font-size: 11px;
  color: #6b7280;
  margin-top: 4px;
  font-style: italic;
}

/* Row status classes */
.row-success {
  background: #f0fdf4 !important;
}

.row-enrollment-error {
  background: #fef2f2 !important;
}

.row-invalid {
  background: #fffbeb !important;
}

/* Responsive design */
@media (max-width: 768px) {
  .table-container-wrapper {
    font-size: 12px;
  }
  
  .preview-table th,
  .preview-table td {
    padding: 6px 8px;
    min-width: 100px;
  }
  
  .summary-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>