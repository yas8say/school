<template>
  <div class="student-list-container">
    <!-- Header -->
    <div class="student-list-header">
      <h3 class="student-list-title">
        {{ isFeeScheduleMode ? studentGroup.name + ' - Fee Category Selection' : studentGroup.name + ' - Student Management' }}
      </h3>
      <div class="header-actions">
        <button 
          v-if="isFeeScheduleMode" 
          @click="saveSelections" 
          class="save-button"
        >
          Save Selections
        </button>
        <!-- Only show close button in Fee Schedule mode -->
        <button 
          v-if="isFeeScheduleMode"
          @click="$emit('close')" 
          class="close-button"
        >
          Close
        </button>
      </div>
    </div>

    <!-- Summary Stats -->
    <div class="summary-stats">
      <div class="stat-item">
        <span class="stat-label">Total Students:</span>
        <span class="stat-value">{{ studentGroup.students?.length || 0 }}</span>
      </div>
      <div v-if="isFeeScheduleMode" class="stat-item">
        <span class="stat-label">Fee Categories:</span>
        <span class="stat-value">{{ feeCategories.length }}</span>
      </div>
      <div v-if="isFeeScheduleMode" class="stat-item">
        <span class="stat-label">Students with Exceptions:</span>
        <span class="stat-value">{{ getStudentsWithExceptionsCount() }}</span>
      </div>
      <div v-if="!isFeeScheduleMode" class="stat-item">
        <span class="stat-label">Selected Students:</span>
        <span class="stat-value">{{ selectedStudentsCount }}</span>
      </div>
    </div>

    <!-- Bulk Actions -->
    <div v-if="isFeeScheduleMode" class="bulk-actions">
      <h4 class="bulk-actions-title">Bulk Actions</h4>
      <div class="bulk-buttons">
        <button 
          v-for="category in feeCategories" 
          :key="category.fees_category"
          @click="selectCategoryForAll(category.fees_category)"
          class="bulk-category-button"
        >
          Select {{ category.fees_category }} for All
        </button>
        <button 
          @click="selectAllCategoriesForAll" 
          class="bulk-category-button"
        >
          Select All Categories for All
        </button>
        <button 
          @click="deselectAllCategories" 
          class="bulk-clear-button"
        >
          Clear All Selections
        </button>
        <button 
          @click="saveSelections" 
          class="bulk-save-button"
        >
          Save Selections
        </button>
      </div>
    </div>

    <!-- Student Selection Bulk Actions (for Students page) -->
    <div v-if="!isFeeScheduleMode" class="bulk-actions">
      <h4 class="bulk-actions-title">Student Selection</h4>
      <div class="bulk-buttons">
        <button 
          @click="selectAllStudents" 
          class="bulk-category-button"
        >
          Select All
        </button>
        <button 
          @click="unselectAllStudents" 
          class="bulk-category-button"
        >
          Unselect All
        </button>
        <button 
          @click="deleteSelectedStudents" 
          class="bulk-delete-button"
          :disabled="selectedStudentsCount === 0"
        >
          Delete Selected ({{ selectedStudentsCount }})
        </button>
      </div>
    </div>

    <!-- Students List -->
    <div class="students-grid">
      <div 
        v-for="student in studentGroup.students" 
        :key="student.student"
        class="student-card"
        :class="{ 
          'selected-student': isStudentSelected(student.student),
          'compact-card': !isFeeScheduleMode 
        }"
        @click="!isFeeScheduleMode ? handleCardClick(student) : null"
      >
        <!-- Student Selection Checkbox (for Students page) -->
        <div v-if="!isFeeScheduleMode" class="student-selection-checkbox">
          <label class="selection-checkbox-label">
            <input 
              type="checkbox"
              :checked="isStudentSelected(student.student)"
              @change="toggleStudentSelection(student.student, $event.target.checked)"
              class="student-checkbox"
            />
            <span class="selection-checkbox-custom"></span>
          </label>
        </div>

        <!-- Edit Button (for Students page) -->
        <div v-if="!isFeeScheduleMode" class="student-edit-button">
          <button 
            @click.stop="handleStudentClick(student)" 
            class="edit-button"
            title="Edit Student"
          >
            ✏️
          </button>
        </div>

        <!-- Student Basic Info -->
        <div class="student-basic-info">
          <StudentAvatar
            :image-url="getStudentImageUrl(student)"
            :student-name="student.student_name"
            alt-text="Student"
            @error="handleImageError"
          />
          
          <div class="student-details">
            <h4 class="student-name">{{ student.student_name }}</h4>
            <p class="student-roll">Roll No: {{ student.group_roll_number }}</p>
            <p class="student-id">{{ student.student }}</p>
          </div>
        </div>

        <!-- Fee Categories Checkboxes (only for Fee Schedule mode) -->
        <div v-if="isFeeScheduleMode && feeCategories.length > 0" class="fee-categories-section">
          <h5 class="fee-categories-title">Select Fee Categories</h5>
          <div class="fee-categories-checkboxes">
            <div 
              v-for="category in feeCategories" 
              :key="category.fees_category"
              class="fee-category-checkbox"
            >
              <label class="checkbox-label">
                <input 
                  type="checkbox"
                  :checked="isCategorySelected(student.student, category.fees_category)"
                  @change="toggleCategory(student.student, category.fees_category, $event.target.checked)"
                  class="category-checkbox"
                />
                <span class="checkbox-custom"></span>
                <span class="category-info">
                  <span class="category-name">{{ category.fees_category }}</span>
                  <span class="category-amount">₹{{ category.total?.toLocaleString() }}</span>
                </span>
              </label>
            </div>
          </div>
          
          <!-- Student Summary -->
          <div class="student-selection-summary">
            <span class="summary-text">
              Selected: {{ getSelectedCategoriesCount(student.student) }}/{{ feeCategories.length }} categories
            </span>
            <span 
              v-if="getSelectedCategoriesCount(student.student) === 0" 
              class="no-selection-warning"
            >
              (No fee categories selected)
            </span>
            <span 
              v-else-if="getSelectedCategoriesCount(student.student) < feeCategories.length" 
              class="partial-selection-warning"
            >
              ({{ feeCategories.length - getSelectedCategoriesCount(student.student) }} excluded)
            </span>
          </div>
        </div>

        <!-- No Fee Categories Message -->
        <div v-else-if="isFeeScheduleMode" class="no-categories-message">
          <p>No fee categories available</p>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!studentGroup.students || studentGroup.students.length === 0" class="empty-state">
      <p class="empty-message">No students found in this group</p>
    </div>

    <!-- Actions Footer (only for Fee Schedule mode) -->
    <div v-if="isFeeScheduleMode" class="actions-footer">
      <button 
        @click="saveSelections" 
        class="save-button"
      >
        Save Fee Category Selections
      </button>
      <button 
        @click="clearAllSelections" 
        class="clear-button"
      >
        Clear All
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import StudentAvatar from './StudentAvatar.vue'

const props = defineProps({
  studentGroup: {
    type: Object,
    required: true,
    default: () => ({})
  },
  feeStructures: {
    type: Array,
    default: () => []
  },
  initialSelections: {
    type: Object,
    default: () => ({})
  },
  mode: {
    type: String,
    default: 'fee-schedule' // 'fee-schedule' or 'students'
  }
})

const emit = defineEmits(['save', 'close', 'student-clicked', 'student-deleted', 'refresh', 'students-selected-for-delete'])

// Reactive state
const studentSelections = ref({}) // For fee category selections
const selectedStudents = ref(new Set()) // For student selection in Students mode

// Computed properties
const isFeeScheduleMode = computed(() => props.mode === 'fee-schedule')

const feeCategories = computed(() => {
  if (!isFeeScheduleMode.value) return []
  
  const allCategories = []
  props.feeStructures.forEach(structure => {
    if (structure.components) {
      structure.components.forEach(component => {
        if (component.fees_category && !allCategories.find(cat => cat.fees_category === component.fees_category)) {
          allCategories.push({
            fees_category: component.fees_category,
            amount: component.amount,
            discount: component.discount,
            total: component.total
          })
        }
      })
    }
  })
  return allCategories
})

const selectedStudentsCount = computed(() => selectedStudents.value.size)

// Methods for Fee Schedule Mode
const isCategorySelected = (studentId, category) => {
  return studentSelections.value[studentId]?.includes(category) || false
}

const toggleCategory = (studentId, category, isSelected) => {
  if (!studentSelections.value[studentId]) {
    studentSelections.value[studentId] = []
  }
  
  const currentSelections = studentSelections.value[studentId]
  
  if (isSelected) {
    if (!currentSelections.includes(category)) {
      currentSelections.push(category)
    }
  } else {
    const index = currentSelections.indexOf(category)
    if (index > -1) {
      currentSelections.splice(index, 1)
    }
  }
}

const getSelectedCategoriesCount = (studentId) => {
  return studentSelections.value[studentId]?.length || 0
}

const getStudentsWithExceptionsCount = () => {
  return Object.values(studentSelections.value).filter(
    selections => selections.length < feeCategories.value.length
  ).length
}

const selectCategoryForAll = (category) => {
  props.studentGroup.students?.forEach(student => {
    toggleCategory(student.student, category, true)
  })
}

const selectAllCategoriesForAll = () => {
  props.studentGroup.students?.forEach(student => {
    studentSelections.value[student.student] = feeCategories.value.map(cat => cat.fees_category)
  })
}

const deselectAllCategories = () => {
  props.studentGroup.students?.forEach(student => {
    studentSelections.value[student.student] = []
  })
}

const clearAllSelections = () => {
  studentSelections.value = {}
}

const saveSelections = () => {
  const exceptions = {}
  
  props.studentGroup.students?.forEach(student => {
    const studentId = student.student
    const selectedCategories = studentSelections.value[studentId] || []
    const allCategoryNames = feeCategories.value.map(cat => cat.fees_category)
    
    // Calculate excluded categories (categories NOT selected)
    const excludedCategories = allCategoryNames.filter(cat => 
      !selectedCategories.includes(cat)
    )
    
    // Only include students who have excluded categories
    if (excludedCategories.length > 0) {
      exceptions[studentId] = excludedCategories
    }
  })
  
  emit('save', exceptions)
}

// Methods for Students Mode
const isStudentSelected = (studentId) => {
  return selectedStudents.value.has(studentId)
}

const toggleStudentSelection = (studentId, isSelected) => {
  if (isSelected) {
    selectedStudents.value.add(studentId)
  } else {
    selectedStudents.value.delete(studentId)
  }
}

const handleCardClick = (student) => {
  // Toggle selection when card is clicked
  const isCurrentlySelected = isStudentSelected(student.student)
  toggleStudentSelection(student.student, !isCurrentlySelected)
}

const selectAllStudents = () => {
  props.studentGroup.students?.forEach(student => {
    selectedStudents.value.add(student.student)
  })
}

const unselectAllStudents = () => {
  selectedStudents.value.clear()
}

const deleteSelectedStudents = () => {
  if (selectedStudents.value.size === 0) return
  
  const studentIds = Array.from(selectedStudents.value)
  emit('students-selected-for-delete', studentIds)
}

const handleStudentClick = (student) => {
  console.log('📤 Emitting student data for edit:', {
    student: student.student,
    student_name: student.student_name, 
    group_roll_number: student.group_roll_number,
    student_image: student.student_image, // ← Use student_image
    address: student.address,
    mobile: student.mobile
  })
  
  emit('student-clicked', {
    student: student.student,
    student_name: student.student_name,
    group_roll_number: student.group_roll_number,
    student_image: student.student_image, // ← This is crucial
    address: student.address,
    mobile: student.mobile
  })
}

// In StudentList.vue, update the getStudentImageUrl method:
const getStudentImageUrl = (student) => {
  const imageUrl = student.student_image || student.img_url || student.image || ''
  
  // Debug: Check what image URL we actually have
  console.log('🖼️ Student image debug:', {
    student: student.student,
    student_image: student.student_image,
    img_url: student.img_url,
    image: student.image,
    finalUrl: imageUrl
  })
  
  return imageUrl
}

const handleImageError = (event) => {
  console.log('Image failed to load', event)
}

// Initialization for Fee Schedule Mode
const initializeSelections = () => {
  if (!isFeeScheduleMode.value) return
  
  // If we have meaningful initial selections, use them
  if (props.initialSelections && Object.keys(props.initialSelections).length > 0) {
    const hasData = Object.values(props.initialSelections).some(
      selections => Array.isArray(selections) && selections.length > 0
    )
    
    if (hasData) {
      studentSelections.value = JSON.parse(JSON.stringify(props.initialSelections))
      return
    }
  }

  // Otherwise, initialize with all categories selected
  studentSelections.value = {}
  props.studentGroup.students?.forEach(student => {
    studentSelections.value[student.student] = feeCategories.value.map(cat => cat.fees_category)
  })
}

// Lifecycle
onMounted(() => {
  if (isFeeScheduleMode.value) {
    initializeSelections()
  }
})

// Watch for prop changes (Fee Schedule mode only)
watch(() => props.initialSelections, (newSelections) => {
  if (isFeeScheduleMode.value && newSelections && Object.keys(newSelections).length > 0) {
    initializeSelections()
  }
}, { deep: true })

watch(() => props.studentGroup, () => {
  if (isFeeScheduleMode.value) {
    initializeSelections()
  }
}, { deep: true })

watch(() => props.feeStructures, () => {
  if (isFeeScheduleMode.value) {
    nextTick(() => {
      initializeSelections()
    })
  }
}, { deep: true })
</script>

<style scoped>
/* Alternative: Use a class-based approach */
.compact-card .edit-button {
  width: 1.5rem;
  height: 1.5rem;
  padding: 0.2rem;
  font-size: 0.7rem;
  background: rgba(59, 130, 246, 0.2); /* Light blue with transparency */
  border: 1px solid rgba(59, 130, 246, 0.3); /* Light blue border */
  color: #3b82f6; /* Blue text color */
  backdrop-filter: blur(5px); /* Optional: adds blur effect for better transparency */
}

.compact-card .edit-button:hover {
  background: rgba(59, 130, 246, 0.3); /* Slightly more opaque on hover */
  border-color: rgba(59, 130, 246, 0.5);
  transform: scale(1.05);
}
.compact-card {
  padding: 0.375rem;
  min-height: 60px; /* Slightly increased to accommodate bigger text */
  display: flex;
  align-items: center;
  position: relative;
}

.compact-card .student-basic-info {
  margin-bottom: 0;
  margin-left: 2.5rem;
  gap: 1.5rem;
  display: flex;
  align-items: center;
  flex: 1;
  min-height: 45px; /* Slightly increased */
}

/* .compact-card .student-avatar {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
  margin-right: 1rem;
  align-self: center;
} */

.compact-card .student-details {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 32px;
  padding-left: 0.5rem;
  align-self: center;
}

.compact-card .student-name {
  font-size: 0.9rem; /* Increased from 0.75rem */
  margin: 0 0 0.1rem 0;
  line-height: 1.2;
  font-weight: 600; /* Make it bolder */
}

.compact-card .student-roll {
  font-size: 0.8rem; /* Increased from 0.6rem */
  margin: 0 0 0.05rem 0;
  line-height: 1.2;
}

.compact-card .student-id {
  font-size: 0.7rem; /* Increased from 0.55rem */
  margin: 0;
  line-height: 1.2;
  color: #6b7280; /* Make ID less prominent */
}

/* Add new styles for student selection and edit button */
.student-selection-checkbox {
  position: absolute;
  top: 1rem;
  left: 1rem;
  z-index: 2;
}

.student-edit-button {
  position: absolute;
  top: 1rem;
  right: 1rem;
  z-index: 2;
}

.student-basic-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  margin-left: 2.5rem; /* Add left margin to push content away from checkbox */
}

.selection-checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.student-checkbox {
  display: none;
}

.selection-checkbox-custom {
  width: 1.25rem;
  height: 1.25rem;
  border: 2px solid #d1d5db;
  border-radius: 0.375rem;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.student-checkbox:checked + .selection-checkbox-custom {
  background: #3b82f6;
  border-color: #3b82f6;
}

.student-checkbox:checked + .selection-checkbox-custom::after {
  content: '✓';
  color: white;
  font-size: 0.75rem;
  font-weight: bold;
}

.selected-student {
  border-color: #3b82f6 !important;
  background: #f0f9ff !important;
}

.edit-button {
  padding: 0.5rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.edit-button:hover {
  background: #2563eb;
  transform: scale(1.1);
}

.bulk-delete-button {
  padding: 0.5rem 1rem;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.bulk-delete-button:hover:not(:disabled) {
  background: #dc2626;
}

.bulk-delete-button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

/* Existing styles remain the same */
.partial-selection-warning {
  font-size: 0.75rem;
  color: #d97706;
  font-weight: 500;
}

.bulk-save-button {
  padding: 0.5rem 1rem;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.bulk-save-button:hover {
  background: #059669;
}

.student-list-container {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  display: block;
  width: 100%;
}

.student-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.student-list-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.close-button {
  padding: 0.5rem 1rem;
  background: #6b7280;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.close-button:hover {
  background: #4b5563;
}

.summary-stats {
  display: flex;
  gap: 2rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 0.5rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
}

/* Bulk Actions */
.bulk-actions {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f0f9ff;
  border-radius: 0.5rem;
  border: 1px solid #bae6fd;
}

.bulk-actions-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #0369a1;
  margin: 0 0 0.75rem 0;
}

.bulk-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.bulk-category-button {
  padding: 0.5rem 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.bulk-category-button:hover {
  background: #2563eb;
}

.bulk-clear-button {
  padding: 0.5rem 1rem;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.bulk-clear-button:hover {
  background: #dc2626;
}

.students-grid {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.student-card {
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1.25rem;
  transition: all 0.3s ease;
  position: relative;
  cursor: pointer;
}

.student-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
}

.student-basic-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.student-details {
  flex: 1;
  min-width: 0;
}

.student-name {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.25rem 0;
}

.student-roll {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0 0 0.25rem 0;
}

.student-id {
  font-size: 0.75rem;
  color: #9ca3af;
  margin: 0;
}

/* Fee Categories Checkboxes */
.fee-categories-section {
  border-top: 1px solid #f1f5f9;
  padding-top: 1rem;
}

.fee-categories-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin: 0 0 0.75rem 0;
}

.fee-categories-checkboxes {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.fee-category-checkbox {
  display: flex;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 0.375rem;
  transition: background-color 0.2s;
  width: 100%;
}

.checkbox-label:hover {
  background: #f8fafc;
}

.category-checkbox {
  display: none;
}

.checkbox-custom {
  width: 1.25rem;
  height: 1.25rem;
  border: 2px solid #d1d5db;
  border-radius: 0.375rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.category-checkbox:checked + .checkbox-custom {
  background: #10b981;
  border-color: #10b981;
}

.category-checkbox:checked + .checkbox-custom::after {
  content: '✓';
  color: white;
  font-size: 0.75rem;
  font-weight: bold;
}

.category-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex: 1;
}

.category-name {
  font-size: 0.875rem;
  color: #374151;
  font-weight: 500;
}

.category-amount {
  font-size: 0.875rem;
  color: #059669;
  font-weight: 600;
}

/* Student Selection Summary */
.student-selection-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 0.375rem;
  border: 1px solid #e5e7eb;
}

.summary-text {
  font-size: 0.875rem;
  color: #374151;
  font-weight: 500;
}

.no-selection-warning {
  font-size: 0.75rem;
  color: #ef4444;
  font-weight: 500;
}

.no-categories-message {
  text-align: center;
  padding: 1rem;
  color: #6b7280;
  font-style: italic;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #6b7280;
}

.empty-message {
  margin: 0;
  font-size: 1rem;
}

.actions-footer {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.save-button,
.clear-button {
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.save-button {
  background: #10b981;
  color: white;
  border: none;
}

.save-button:hover {
  background: #059669;
}

.clear-button {
  background: #ef4444;
  color: white;
  border: none;
}

.clear-button:hover {
  background: #dc2626;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .student-list-container {
    padding: 1rem;
  }
  
  .student-list-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .bulk-buttons {
    flex-direction: column;
  }
  
  .fee-categories-checkboxes {
    grid-template-columns: 1fr;
  }
  
  .category-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .actions-footer {
    flex-direction: column;
  }
  
  .save-button,
  .clear-button {
    width: 100%;
  }
}
</style>