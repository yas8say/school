<template>
  <div class="students-page">
    <!-- Page Header -->
    <div class="page-header">
      <h1 class="page-title">Student Management</h1>
      <div class="header-actions">
        <button 
          @click="navigateToUpload" 
          class="action-button secondary-button"
        >
          Upload Students
        </button>
        <button 
          @click="navigateToAdd" 
          class="action-button primary-button"
        >
          Add New Student
        </button>
      </div>
    </div>

    <!-- Academic Year, Class, and Division Selection -->
    <div class="selection-card">
      <h2 class="selection-title">Select Student Group</h2>
      
      <div class="selection-grid">
        <div class="form-group required">
          <label>Academic Year</label>
          <select 
            v-model="selectedAcademicYear" 
            class="picker"
            @change="onYearChange"
            :disabled="academicYearsResource.loading"
          >
            <option :value="null">Select Academic Year</option>
            <option v-for="year in displayYears" :key="year" :value="year.original">
              {{ year.display }}
            </option>
          </select>
          <span class="error-message" v-if="selectionErrors.academicYear">{{ selectionErrors.academicYear }}</span>
        </div>

        <div class="form-group required">
          <label>Class / Program</label>
          <select 
            v-model="selectedClassName" 
            class="picker"
            @change="onClassChange"
            :disabled="!selectedAcademicYear || classesResource.loading"
          >
            <option :value="null">Select Class / Program</option>
            <option v-for="cls in classes" :key="cls.name" :value="cls.name">
              {{ cls.name }}
            </option>
          </select>
          <span class="error-message" v-if="selectionErrors.className">{{ selectionErrors.className }}</span>
        </div>

        <div class="form-group required" v-if="divisions.length > 0">
          <label>Division / Student Group</label>
          <select 
            v-model="selectedDivisionName" 
            class="picker"
            @change="onDivisionChange"
            :disabled="!selectedClassName || divisionsResource.loading"
          >
            <option :value="null">Select Division / Student Group</option>
            <option v-for="div in divisions" :key="div.name" :value="div.name">
              {{ div.name }}
            </option>
          </select>
          <span class="error-message" v-if="selectionErrors.divisionName">{{ selectionErrors.divisionName }}</span>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="studentsResource.loading" class="loading-state">
      <p>Loading students...</p>
    </div>

    <!-- Error State -->
    <div v-if="studentsResource.error" class="error-state">
      <p>Error loading students: {{ studentsResource.error }}</p>
      <button @click="refreshStudents" class="retry-button">
        Retry
      </button>
    </div>

    <!-- Student List Component -->
    <StudentList
      v-if="!studentsResource.loading && !studentsResource.error && studentsList.length > 0"
      mode="students"
      :student-group="currentStudentGroup"
      @student-clicked="handleStudentClick"
      @students-selected-for-delete="handleStudentDelete" 
      @refresh="refreshStudents"
    />

    <!-- Empty State -->
    <div v-if="!studentsResource.loading && !studentsResource.error && studentsList?.length === 0 && selectedDivisionName" class="empty-state">
      <p class="empty-message">No students found in this group</p>
      <div class="empty-actions">
        <button 
          @click="navigateToAdd" 
          class="action-button primary-button empty-action"
        >
          Add First Student
        </button>
        <button 
          @click="navigateToUpload" 
          class="action-button secondary-button empty-action"
        >
          Upload Students
        </button>
      </div>
    </div>

    <!-- No Selection State -->
    <div v-if="!selectedDivisionName && !studentsResource.loading" class="no-selection-state">
      <p class="no-selection-message">Please select an academic year, class, and division to view students</p>
    </div>
    <Toast ref="toastRef" />
  </div>
</template>

<script>
import { createResource } from 'frappe-ui'
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import StudentList from '../components/StudentList.vue'
import Toast from '@/components/Toast.vue';

export default {
  name: 'StudentsPage',
  
  components: {
    StudentList,
    Toast
  },
  
  setup() {
    const router = useRouter()

    // Selection state
    const selectedAcademicYear = ref(null)
    const selectedClassName = ref(null)
    const selectedDivisionName = ref(null)
    const toastRef = ref(null)

    // Data stores
    const academicYears = ref([])
    const classes = ref([])
    const divisions = ref([])
    const studentsList = ref([])

    // Errors
    const selectionErrors = reactive({})

    // Computed properties
    const displayYears = computed(() =>
      academicYears.value.map((year, index) => ({
        original: year,
        display: index === 0 ? `${year} - Current Year` : year
      }))
    )

    // Current student group for StudentList compatibility
    const currentStudentGroup = computed(() => ({
      name: selectedDivisionName.value,
      students: studentsList.value.map(student => ({
        student: student.student,
        student_name: student.student_name,
        group_roll_number: student.group_roll_number,
        student_image: student.student_image, // ← Keep original field name
        address: student.address,
        mobile: student.mobile
        // Remove img_url mapping as it's confusing
      }))
    }))

    // Consolidated API configuration
    const apiConfig = {
      academicYears: {
        url: 'school.al_ummah.api3.get_academic_years',
        params: { values: {} }
      },
      classes: {
        url: 'school.al_ummah.api3.get_classes', 
        params: { values: {} }
      },
      divisions: {
        url: 'school.al_ummah.api3.get_divisions2',
        getParams: () => ({
          values: {
            classId: selectedClassName.value,
            academicYear: selectedAcademicYear.value
          }
        })
      },
      students: {
        url: 'school.al_ummah.api2.get_basic_student_list',
        getParams: () => ({
          student_group: selectedDivisionName.value
        })
      },
      deleteStudents: {
        url: 'school.al_ummah.api2.delete_students',
        method: 'POST'
      }
    }

    // API Resources
    const createApiResource = (config) => {
      return createResource({
        url: config.url,
        params: config.getParams ? config.getParams() : config.params,
        auto: config.auto !== false,
        onSuccess: config.onSuccess,
        onError: config.onError
      })
    }

    const academicYearsResource = createApiResource({
      ...apiConfig.academicYears,
      onSuccess: (data) => {
        academicYears.value = Array.isArray(data) ? data : []
        if (academicYears.value.length > 0) {
          selectedAcademicYear.value = academicYears.value[0]
        }
      },
      onError: (err) => {
        console.error('Error fetching academic years:', err)
        academicYears.value = []
      }
    })

    const classesResource = createApiResource({
      ...apiConfig.classes,
      onSuccess: (data) => {
        classes.value = Array.isArray(data) ? data : []
      },
      onError: (err) => {
        console.error('Error fetching classes:', err)
        classes.value = []
      }
    })

    const divisionsResource = createApiResource({
      ...apiConfig.divisions,
      auto: false,
      onSuccess: (data) => {
        divisions.value = Array.isArray(data) ? data : []
        selectedDivisionName.value = null
      },
      onError: (err) => {
        console.error('Error fetching divisions:', err)
        divisions.value = []
        selectedDivisionName.value = null
      }
    })

    const studentsResource = createApiResource({
      ...apiConfig.students,
      auto: false,
      onSuccess: (data) => {
        studentsList.value = Array.isArray(data) ? data : [];
        
        // DEBUG: Check ALL fields from backend
        console.log('🔍 COMPLETE Backend response analysis:')
        if (studentsList.value.length > 0) {
          const firstStudent = studentsList.value[0]
          console.log('🔍 First student ALL fields:', firstStudent)
          console.log('🔍 Available fields:', Object.keys(firstStudent))
          
          // Check specifically for address and mobile
          console.log('🔍 Address field:', firstStudent.address)
          console.log('🔍 Mobile field:', firstStudent.mobile)
          console.log('🔍 student_image field:', firstStudent.student_image)
        }
        
        if (studentsList.value.length > 0) {
          showSuccess(`Loaded ${studentsList.value.length} students`);
        }
      },
      onError: (error) => {
        console.error('Error loading students:', error);
        studentsList.value = [];
        showError('Failed to load students. Please try again.');
      }
    });

    // Delete Students Resource
    const deleteStudentsResource = createResource({
      url: apiConfig.deleteStudents.url,
      method: apiConfig.deleteStudents.method,
      auto: false,
      onSuccess: (data) => {
        studentsResource.reload();
        if (data.success) {
          showSuccess(`Successfully deleted ${data.deleted_count} student(s)`);
        } else if (data.errors && data.errors.length > 0) {
          showError(`Deleted ${data.deleted_count} students with ${data.errors.length} errors: ${data.errors.join(', ')}`);
        }
      },
      onError: (err) => {
        console.error('Error deleting students:', err);
        showError(err.messages?.[0] || 'Failed to delete students');
      }
    });

    // Methods

    // Toast helper functions
    const showToast = (message, type = 'success', duration = 6000, actions = []) => {
      if (toastRef.value && toastRef.value.showToast) {
        toastRef.value.showToast(message, type, duration, actions);
      } else {
        // Fallback for toast errors
        console.log(`Toast: ${type} - ${message}`);
      }
    };

    const showError = (message) => {
      showToast(message, 'error', 8000);
    };

    const showSuccess = (message) => {
      showToast(message, 'success', 5000);
    };

    const showWarning = (message) => {
      showToast(message, 'warning', 6000);
    };

    const showConfirmation = (message, confirmAction, cancelAction = null) => {
      showToast(message, 'warning', 0, [
        {
          label: 'Confirm',
          type: 'primary',
          onClick: confirmAction,
          closeOnClick: true
        },
        {
          label: 'Cancel',
          type: 'secondary',
          onClick: cancelAction || (() => {}),
          closeOnClick: true
        }
      ]);
    };

    const onYearChange = () => {
      selectedClassName.value = null
      selectedDivisionName.value = null
      divisions.value = []
      clearSelectionErrors()
    }

    const onClassChange = () => {
      selectedDivisionName.value = null
      clearSelectionErrors()
      
      if (selectedClassName.value && selectedAcademicYear.value) {
        divisionsResource.update({
          params: apiConfig.divisions.getParams()
        })
        divisionsResource.reload()
      } else {
        divisions.value = []
      }
    }

    const onDivisionChange = () => {
      clearSelectionErrors()
      
      // Automatically load students when division is selected
      if (selectedDivisionName.value) {
        loadStudents()
      }
    }

    const loadStudents = () => {
      if (validateSelection()) {
        studentsResource.update({
          params: apiConfig.students.getParams()
        });
        studentsResource.reload();
        showToast('Loading students...', 'info', 2000);
      } else {
        showError('Please select academic year, class, and division');
      }
    };

    const validateSelection = () => {
      Object.assign(selectionErrors, {})
      let isValid = true

      if (!selectedAcademicYear.value) {
        selectionErrors.academicYear = 'Please select an academic year'
        isValid = false
      }
      if (!selectedClassName.value) {
        selectionErrors.className = 'Please select a class'
        isValid = false
      }
      if (!selectedDivisionName.value) {
        selectionErrors.divisionName = 'Please select a division'
        isValid = false
      }

      return isValid
    }

    const clearSelectionErrors = () => {
      Object.assign(selectionErrors, {})
    }

    const handleStudentClick = (student) => {
      console.log('🎯 COMPLETE Student data being sent:', student)
      
      // Create navigation data with ALL available fields
      const navigationData = {
        student: student.student,
        student_name: student.student_name,
        group_roll_number: student.group_roll_number,
        student_image: student.student_image,
        address: student.address, // Make sure this exists
        mobile: student.mobile,   // Make sure this exists
        student_group: currentStudentGroup.value.name
      }
      
      console.log('📤 Navigation payload with ALL fields:', navigationData)
      
      const query = {
        studentId: student.student,
        studentData: JSON.stringify(navigationData)
      }
      
      router.push({
        name: 'EditStudent',
        query: query
      }).catch((routerError) => {
        console.error('❌ Router navigation failed:', routerError)
        const editUrl = `/edit-student?studentId=${student.student}&studentData=${JSON.stringify(navigationData)}`
        window.location.href = editUrl
      })
    }

    const handleStudentDelete = async (studentIds) => {
      const ids = Array.isArray(studentIds) ? studentIds : [studentIds];
      
      const confirmMessage = `Are you sure you want to delete ${ids.length} student(s)? This action cannot be undone.`;
      
      showConfirmation(
        confirmMessage,
        async () => {
          try {
            deleteStudentsResource.submit({
              student_ids: ids
            });
          } catch (error) {
            showError('Failed to delete students. Please try again.');
          }
        },
        () => {
          // Cancel action - do nothing
          showToast('Deletion cancelled', 'info', 3000);
        }
      );
    };

    const navigateToAdd = () => {
      router.push({ name: 'AddStudent' })
    }

    const navigateToUpload = () => {
      router.push({ name: 'UploadStudents' })
    }

    const refreshStudents = () => {
      studentsResource.reload()
    }

    // Fetch initial data
    onMounted(() => {
      academicYearsResource.reload()
      classesResource.reload()
    })

    return {
      // Reactive data
      selectedAcademicYear,
      selectedClassName,
      selectedDivisionName,
      academicYears,
      classes,
      divisions,
      studentsList,
      selectionErrors,
      
      // Computed
      displayYears,
      currentStudentGroup,
      
      // Resources
      academicYearsResource,
      classesResource,
      divisionsResource,
      studentsResource,
      toastRef,

      // Methods
      onYearChange,
      onClassChange,
      onDivisionChange,
      loadStudents,
      handleStudentClick,
      handleStudentDelete,
      navigateToAdd,
      navigateToUpload,
      refreshStudents
    }
  }
}
</script>

<style scoped>
/* Updated CSS with consistent button styling */
.students-page {
  padding: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.action-button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.primary-button {
  background: #10b981;
  color: white;
}

.primary-button:hover {
  background: #059669;
}

.secondary-button {
  background: #6b7280;
  color: white;
}

.secondary-button:hover {
  background: #4b5563;
}

.add-button {
  background: #10b981;
  color: white;
}

.add-button:hover {
  background: #059669;
}

.upload-button {
  background: #10b981;
  color: white;
}

.upload-button:hover {
  background: #059669;
}

/* Selection Card Styles */
.selection-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  margin-bottom: 1.5rem;
}

.selection-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 1rem 0;
}

.selection-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.required label::after {
  content: " *";
  color: #ef4444;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.picker {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  background: white;
  transition: all 0.2s;
}

.picker:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.picker:disabled {
  background-color: #f9fafb;
  color: #6b7280;
  cursor: not-allowed;
}

.error-message {
  font-size: 0.75rem;
  color: #ef4444;
  margin-top: 0.25rem;
}

/* Load Actions */
.load-actions {
  display: flex;
  justify-content: flex-end;
}

.load-button {
  padding: 0.75rem 2rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.load-button:hover:not(:disabled) {
  background: #2563eb;
}

.load-button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.button-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* State Styles */
.loading-state,
.error-state,
.empty-state,
.no-selection-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #6b7280;
}

.error-state {
  color: #ef4444;
}

.retry-button {
  padding: 0.75rem 1.5rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  margin-top: 1rem;
}

.retry-button:hover {
  background: #2563eb;
}

.empty-message,
.no-selection-message {
  margin: 0 0 1.5rem 0;
  font-size: 1.125rem;
}

.empty-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.empty-action {
  margin: 0;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .students-page {
    padding: 1rem;
  }
  
  .page-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
    flex-direction: column;
  }
  
  .action-button {
    width: 100%;
  }
  
  .selection-grid {
    grid-template-columns: 1fr;
  }
  
  .empty-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .empty-action {
    width: 200px;
  }
  
  .load-actions {
    justify-content: stretch;
  }
  
  .load-button {
    width: 100%;
  }
}
</style>