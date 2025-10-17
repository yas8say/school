<template>
  <div class="enrollment-form">
    <div class="header">
      <h1 class="title">Student Enrollment</h1>
      <p class="subtitle">Add new student to the system</p>
    </div>
    
    <div class="form-card">
      <h2 class="form-title">Student Information</h2>
      
      <!-- Academic Year, Class, and Division Selection -->
      <div class="form-grid">
        <div class="form-group required">
          <label>Academic Year</label>
          <select 
            v-model="formData.academicYear" 
            class="picker"
            @change="onYearChange"
            :disabled="academicYearsResource.loading"
          >
            <option :value="null">Select Academic Year</option>
            <option v-for="year in displayYears" :key="year" :value="year.original">
              {{ year.display }}
            </option>
          </select>
          <span class="error-message" v-if="errors.academicYear">{{ errors.academicYear }}</span>
        </div>

        <div class="form-group required">
          <label>Class / Program</label>
          <select 
            v-model="formData.className" 
            class="picker"
            @change="onClassChange"
            :disabled="!formData.academicYear || classesResource.loading"
          >
            <option :value="null">Select Class / Program</option>
            <option v-for="cls in classes" :key="cls.name" :value="cls.name">
              {{ cls.name }}
            </option>
          </select>
          <span class="error-message" v-if="errors.className">{{ errors.className }}</span>
        </div>

        <div class="form-group required" v-if="divisions.length > 0">
          <label>Division / Student Group</label>
          <select 
            v-model="formData.divisionName" 
            class="picker"
            :disabled="!formData.className || divisionsResource.loading"
          >
            <option :value="null">Select Division / Student Group</option>
            <option v-for="div in divisions" :key="div.name" :value="div.name">
              {{ div.name }}
            </option>
          </select>
          <span class="error-message" v-if="errors.divisionName">{{ errors.divisionName }}</span>
        </div>
      </div>

      <!-- Student Information -->
      <div class="form-section">
        <h3 class="section-title">Personal Details</h3>
        <div class="form-grid">
          <div class="form-group required">
            <label>First Name</label>
            <input
              v-model="formData.student_data['First Name']"
              type="text"
              class="input"
              placeholder="Enter first name"
              required
            >
            <span class="error-message" v-if="errors.firstName">{{ errors.firstName }}</span>
          </div>

          <div class="form-group">
            <label>Middle Name</label>
            <input
              v-model="formData.student_data['Middle Name']"
              type="text"
              class="input"
              placeholder="Enter middle name"
            >
          </div>

          <div class="form-group required">
            <label>Last Name</label>
            <input
              v-model="formData.student_data['Last Name']"
              type="text"
              class="input"
              placeholder="Enter last name"
              required
            >
            <span class="error-message" v-if="errors.lastName">{{ errors.lastName }}</span>
          </div>

          <div class="form-group">
            <label>Student Date of Birth</label>
            <input
              v-model="formData.student_data['Student Date of Birth']"
              type="date"
              class="input"
              required
            >
            <span class="error-message" v-if="errors.studentDob">{{ errors.studentDob }}</span>
          </div>

          <div class="form-group required">
            <label>GR Number</label>
            <input
              v-model="formData.student_data['GR Number']"
              type="text"
              class="input"
              placeholder="Enter GR number"
              required
            >
            <span class="error-message" v-if="errors.grNumber">{{ errors.grNumber }}</span>
          </div>

          <div class="form-group required">
            <label>Email Address</label>
            <input
              v-model="formData.student_data['Email Address']"
              type="email"
              class="input"
              placeholder="Enter email address"
            >
            <span class="error-message" v-if="errors.email">{{ errors.email }}</span>
          </div>

          <div class="form-group">
            <label>Phone Number</label>
            <input
              v-model="formData.student_data['Phone Number']"
              type="tel"
              class="input"
              placeholder="Enter phone number"
            >
            <span class="error-message" v-if="errors.phone">{{ errors.phone }}</span>
          </div>
        </div>
      </div>

      <!-- Guardian Information -->
      <div class="form-section">
        <h3 class="section-title">Guardian Information</h3>
        <div class="form-grid">
          <div class="form-group">
            <label>Guardian Name</label>
            <input
              v-model="formData.student_data['Guardian Name']"
              type="text"
              class="input"
              placeholder="Enter guardian name"
            >
          </div>

          <div class="form-group">
            <label>Guardian Number</label>
            <input
              v-model="formData.student_data['Guardian Number']"
              type="tel"
              class="input"
              placeholder="Enter guardian phone number"
            >
            <span class="error-message" v-if="errors.guardianNumber">{{ errors.guardianNumber }}</span>
          </div>

          <div class="form-group">
            <label>Relation</label>
            <select 
              v-model="formData.student_data['Relation']" 
              class="picker"
            >
              <option value="">Select Relation</option>
              <option value="Father">Father</option>
              <option value="Mother">Mother</option>
              <option value="Brother">Brother</option>
              <option value="Sister">Sister</option>
              <option value="Grandfather">Grandfather</option>
              <option value="Grandmother">Grandmother</option>
              <option value="Uncle">Uncle</option>
              <option value="Aunt">Aunt</option>
              <option value="Guardian">Guardian</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div class="form-group">
            <label>Guardian Date of Birth</label>
            <input
              v-model="formData.student_data['Guardian Date of Birth']"
              type="date"
              class="input"
            >
          </div>

          <div class="form-group required">
            <label>Guardian Email</label>
            <input
              v-model="formData.student_data['Guardian Email']"
              type="email"
              class="input"
              placeholder="Enter guardian email"
            >
            <span class="error-message" v-if="errors.guardianEmail">{{ errors.guardianEmail }}</span>
          </div>

          <div class="form-group">
            <label>Guardian Occupation</label>
            <input
              v-model="formData.student_data['Guardian Occupation']"
              type="text"
              class="input"
              placeholder="Enter guardian occupation"
            >
          </div>

          <div class="form-group">
            <label>Guardian Designation</label>
            <input
              v-model="formData.student_data['Guardian Designation']"
              type="text"
              class="input"
              placeholder="Enter guardian designation"
            >
          </div>
            <div class="form-group">
            <label>Guardian Education</label>
            <input
              v-model="formData.student_data['Guardian Education']"
              type="text"
              class="input"
              placeholder="Enter guardian education"
            >
          </div>
          <div class="form-group">
            <label>Guardian Work Address</label>
            <textarea
              v-model="formData.student_data['Guardian Work Address']"
              class="input textarea"
              placeholder="Enter guardian work address"
              rows="3"
            ></textarea>
          </div>


        </div>
      </div>

      <!-- Submit Button and Status Message -->
      <div class="form-actions">
        <button 
          class="enroll-button"
          @click="validateAndSubmit"
          :disabled="isSubmitting || enrollStudentResource.loading"
        >
          <span v-if="isSubmitting || enrollStudentResource.loading" class="button-content">
            <span class="spinner"></span> Processing...
          </span>
          <span v-else class="button-content">
            <svg class="icon" viewBox="0 0 24 24">
              <path fill="currentColor" d="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z" />
            </svg>
            Enroll Student
          </span>
        </button>
        
        <button 
          class="reset-button" 
          @click="resetForm"
          :disabled="isSubmitting || enrollStudentResource.loading"
        >
          Reset Form
        </button>
      </div>

      <div v-if="message" :class="['message', message.type]">
        {{ message.text }}
      </div>
    </div>
  </div>
</template>

<script>
import { createResource } from 'frappe-ui';
import { reactive, ref, computed, onMounted } from 'vue';
import '@/styles/form.css';

export default {
  setup() {
    // Reactive form data - using backend-expected field names
    const formData = reactive({
      academicYear: null,
      className: null,
      divisionName: null,
      student_data: {
        'First Name': '',
        'Middle Name': '',
        'Last Name': '',
        'Student Date of Birth': '',
        'GR Number': '',
        'Email Address': '',
        'Phone Number': '',
        'Guardian Name': '',
        'Guardian Number': '',
        'Relation': '',
        'Guardian Date of Birth': '',
        'Guardian Email': '',
        'Guardian Occupation': '',
        'Guardian Designation': '',
        'Guardian Work Address': '',
        'Guardian Education': ''
      }
    });

    // State variables
    const academicYears = ref([]);
    const displayYears = computed(() =>
      academicYears.value.map((year, index) => ({
        original: year,
        display: index === 0 ? `${year} - Current Year` : year
      }))
    );
    const classes = ref([]);
    const divisions = ref([]);
    const isSubmitting = ref(false);
    const message = ref(null);
    const errors = reactive({});

    // API Resources
    const academicYearsResource = createResource({
      url: 'school.al_ummah.api3.get_academic_years',
      params: { values: {} },
      onSuccess: (data) => {
        academicYears.value = Array.isArray(data) ? data : [];
        if (academicYears.value.length > 0) {
          formData.academicYear = academicYears.value[0];
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
          classId: formData.className,
          academicYear: formData.academicYear
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

    const enrollStudentResource = createResource({
      url: 'school.al_ummah.api3.enroll_single_student',
      params: {
        academicYear: formData.academicYear,
        className: formData.className,
        divisionName: formData.divisionName,
        student_data: formData.student_data
      },
      onSuccess: (response) => {
        isSubmitting.value = false;
        showMessage("✅ Student enrolled successfully!", "success");
        // resetForm();
      },
      onError: (err) => {
        isSubmitting.value = false;
        showMessage(err.messages?.[0] || 'Unexpected error occurred', 'error');
      }
    });

    // Fetch initial data on mount
    onMounted(() => {
      academicYearsResource.reload();
      classesResource.reload();
    });

    // Methods
    function onYearChange() {
      formData.className = null;
      formData.divisionName = null;
      divisions.value = [];
      errors.className = '';
      errors.divisionName = '';
      onClassChange();
    }

    function onClassChange() {
      formData.divisionName = null;
      errors.divisionName = '';
      if (formData.className && formData.academicYear) {
        divisionsResource.update({
          params: {
            values: {
              classId: formData.className,
              academicYear: formData.academicYear
            }
          }
        });
        divisionsResource.reload();
      } else {
        divisions.value = [];
      }
    }

    function validateForm() {
      Object.assign(errors, {});
      let isValid = true;

      // Required fields validation
      if (!formData.academicYear) {
        errors.academicYear = 'Please select an academic year';
        isValid = false;
      }
      if (!formData.className) {
        errors.className = 'Please select a class';
        isValid = false;
      }
      if (!formData.divisionName) {
        errors.divisionName = 'Please select a division';
        isValid = false;
      }
      if (!formData.student_data['First Name'].trim()) {
        errors.firstName = 'First name is required';
        isValid = false;
      }
      if (!formData.student_data['Last Name'].trim()) {
        errors.lastName = 'Last name is required';
        isValid = false;
      }
      // if (!formData.student_data['Student Date of Birth']) {
      //   errors.studentDob = 'Student date of birth is required';
      //   isValid = false;
      // }
      if (!formData.student_data['GR Number'].trim()) {
        errors.grNumber = 'GR number is required';
        isValid = false;
      }

      // Optional fields validation (only if provided)
      const email = formData.student_data['Email Address'].trim();
      if (email && !validEmail(email)) {
        errors.email = 'Please enter a valid email';
        isValid = false;
      }

      const phone = formData.student_data['Phone Number'].trim();
      if (phone && !validPhone(phone)) {
        errors.phone = 'Please enter a valid phone number (10-15 digits)';
        isValid = false;
      }

      const guardianNumber = formData.student_data['Guardian Number'].trim();
      if (guardianNumber && !validPhone(guardianNumber)) {
        errors.guardianNumber = 'Please enter a valid guardian phone number (10-15 digits)';
        isValid = false;
      }

      const guardianEmail = formData.student_data['Guardian Email'].trim();
      if (!guardianEmail) {
        errors.guardianEmail = 'Guardian email is required';
        isValid = false;
      } else if (!validEmail(guardianEmail)) {
        errors.guardianEmail = 'Please enter a valid guardian email';
        isValid = false;
      }
      return isValid;
    }

    function validEmail(email) {
      if (!email) return true; // Optional field
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return re.test(email);
    }

    function validPhone(phone) {
      if (!phone) return true; // Optional field
      const re = /^[0-9]{10,15}$/;
      return re.test(phone);
    }

    function validateAndSubmit() {
      if (validateForm()) {
        submitForm();
      }
    }

    function submitForm() {
      isSubmitting.value = true;
      enrollStudentResource.update({
        params: {
          academicYear: formData.academicYear,
          className: formData.className,
          divisionName: formData.divisionName,
          student_data: { ...formData.student_data }
        }
      });
      enrollStudentResource.submit();
    }

    function resetForm() {
      Object.assign(formData, {
        academicYear: academicYears.value.length > 0 ? academicYears.value[0] : null,
        className: null,
        divisionName: null,
        student_data: {
          'First Name': '',
          'Middle Name': '',
          'Last Name': '',
          'Student Date of Birth': '',
          'GR Number': '',
          'Email Address': '',
          'Phone Number': '',
          'Guardian Name': '',
          'Guardian Number': '',
          'Relation': '',
          'Guardian Date of Birth': '',
          'Guardian Email': '',
          'Guardian Occupation': '',
          'Guardian Designation': '',
          'Guardian Work Address': '',
          'Guardian Education': ''
        }
      });
      divisions.value = [];
      Object.assign(errors, {});
      message.value = null;
    }

    function showMessage(text, type = 'info') {
      message.value = { text, type };
      if (type !== 'error') {
        setTimeout(() => (message.value = null), 5000);
      }
    }

    return {
      formData,
      academicYears,
      displayYears,
      classes,
      divisions,
      isSubmitting,
      message,
      errors,
      academicYearsResource,
      classesResource,
      divisionsResource,
      enrollStudentResource,
      onYearChange,
      onClassChange,
      validateAndSubmit,
      resetForm
    };
  }
};
</script>