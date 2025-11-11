<template>
  <div class="student-list-container">
    <!-- Header -->
    <div class="student-list-header">
      <h3 class="student-list-title">{{ studentGroup.name }} - Fee Category Selection</h3>
      <div class="header-actions">
        <button 
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
      <div class="stat-item">
        <span class="stat-label">Fee Categories:</span>
        <span class="stat-value">{{ feeCategories.length }}</span>
      </div>
    </div>

    <!-- Bulk Actions -->
    <div class="bulk-actions">
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
          @click="deselectAllCategories" 
          class="bulk-clear-button"
        >
          Clear All Selections
        </button>
      </div>
    </div>

    <!-- Students List -->
    <div class="students-grid">
      <div 
        v-for="student in studentGroup.students" 
        :key="student.student"
        class="student-card"
      >
        <!-- Student Basic Info -->
        <div class="student-basic-info">
          <div class="student-avatar">
            <img
              v-if="student.student_image"
              :src="getProfileImageUrl(student.student_image)"
              alt="Student"
              class="avatar-image"
              @error="handleImageError"
            />
            <div v-else class="avatar-placeholder">
              {{ getInitials(student.student_name) }}
            </div>
          </div>
          
          <div class="student-details">
            <h4 class="student-name">{{ student.student_name }}</h4>
            <p class="student-roll">Roll No: {{ student.group_roll_number }}</p>
            <p class="student-id">{{ student.student }}</p>
          </div>
        </div>

        <!-- Fee Categories Checkboxes -->
        <div v-if="feeCategories.length > 0" class="fee-categories-section">
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
          </div>
        </div>

        <!-- No Fee Categories Message -->
        <div v-else class="no-categories-message">
          <p>No fee categories available</p>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!studentGroup.students || studentGroup.students.length === 0" class="empty-state">
      <p class="empty-message">No students found in this group</p>
    </div>

    <!-- Actions Footer -->
    <div class="actions-footer">
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
import { ref, computed, onMounted, watch } from 'vue'

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
  }
})

const emit = defineEmits(['save', 'close'])

// Reactive state for student fee category selections
// Structure: { studentId: [category1, category2, ...] }
const studentSelections = ref({})

// Computed properties
const feeCategories = computed(() => {
  // Combine fee categories from all selected fee structures
  const allCategories = []
  props.feeStructures.forEach(structure => {
    if (structure.components) {
      structure.components.forEach(component => {
        // Avoid duplicates
        if (!allCategories.find(cat => cat.fees_category === component.fees_category)) {
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

// Methods
const isCategorySelected = (studentId, category) => {
  return studentSelections.value[studentId]?.includes(category) || false
}

const toggleCategory = (studentId, category, isSelected) => {
  if (!studentSelections.value[studentId]) {
    studentSelections.value[studentId] = []
  }
  
  const currentSelections = studentSelections.value[studentId]
  
  if (isSelected) {
    // Add category if not already present
    if (!currentSelections.includes(category)) {
      currentSelections.push(category)
    }
  } else {
    // Remove category
    const index = currentSelections.indexOf(category)
    if (index > -1) {
      currentSelections.splice(index, 1)
    }
  }
}

const getSelectedCategoriesCount = (studentId) => {
  return studentSelections.value[studentId]?.length || 0
}

const selectCategoryForAll = (category) => {
  props.studentGroup.students?.forEach(student => {
    toggleCategory(student.student, category, true)
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
  // Prepare exceptions data: students with missing fee categories
  const exceptions = {}
  
  props.studentGroup.students?.forEach(student => {
    const studentId = student.student
    const selectedCategories = studentSelections.value[studentId] || []
    
    if (selectedCategories.length < feeCategories.value.length) {
      // Student has some categories unselected - add to exceptions
      const missingCategories = feeCategories.value
        .filter(cat => !selectedCategories.includes(cat.fees_category))
        .map(cat => cat.fees_category)
      
      if (missingCategories.length > 0) {
        exceptions[studentId] = missingCategories
      }
    }
  })
  
  emit('save', exceptions)
}

const getProfileImageUrl = (imgUrl) => {
  if (!imgUrl) return null
  if (imgUrl.startsWith('http') || imgUrl.startsWith('//')) {
    return imgUrl
  }
  if (imgUrl.startsWith('/')) {
    return window.location.origin + imgUrl
  }
  const baseUrl = window.location.origin
  return `${baseUrl}/${imgUrl.replace(/^\//, '')}`
}

const getInitials = (name) => {
  if (!name) return '?'
  return name
    .split(' ')
    .map(part => part.charAt(0))
    .join('')
    .toUpperCase()
    .substring(0, 2)
}

const handleImageError = (event) => {
  event.target.style.display = 'none'
}

// Lifecycle
onMounted(() => {
  // Initialize with initial selections if provided
  if (props.initialSelections && Object.keys(props.initialSelections).length > 0) {
    studentSelections.value = { ...props.initialSelections }
  } else {
    // Initialize with all categories selected for all students
    props.studentGroup.students?.forEach(student => {
      studentSelections.value[student.student] = feeCategories.value.map(cat => cat.fees_category)
    })
  }
})

// Watch for changes in student group
watch(() => props.studentGroup, () => {
  // Reset selections when student group changes
  studentSelections.value = {}
  // Initialize with all categories selected for all students
  props.studentGroup.students?.forEach(student => {
    studentSelections.value[student.student] = feeCategories.value.map(cat => cat.fees_category)
  })
}, { deep: true })
</script>

<style scoped>
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

.student-avatar {
  flex-shrink: 0;
}

.avatar-image {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 0.875rem;
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