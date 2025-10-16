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
            :disabled="!formData.academicYear"
          >
            <option :value="null">Select Class / Program</option>
            <option v-for="cls in classes" :key="cls" :value="cls">
              {{ cls }}
            </option>
          </select>
          <span class="error-message" v-if="errors.className">{{ errors.className }}</span>
        </div>

        <div class="form-group required" v-if="divisions.length > 0">
          <label>Division / Student Group</label>
          <select 
            v-model="formData.divisionName" 
            class="picker"
            :disabled="!formData.className"
          >
            <option :value="null">Select Division / Student Group</option>
            <option v-for="div in divisions" :key="div" :value="div">
              {{ div }}
            </option>
          </select>
          <span class="error-message" v-if="errors.divisionName">{{ errors.divisionName }}</span>
        </div>
      </div>

      <!-- Student Information -->
      <div class="form-grid">
        <div class="form-group required">
          <label>First Name</label>
          <input
            v-model="formData.student_data.FirstName"
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
            v-model="formData.student_data.MiddleName"
            type="text"
            class="input"
            placeholder="Enter middle name"
          >
        </div>

        <div class="form-group required">
          <label>Last Name</label>
          <input
            v-model="formData.student_data.LastName"
            type="text"
            class="input"
            placeholder="Enter last name"
            required
          >
          <span class="error-message" v-if="errors.lastName">{{ errors.lastName }}</span>
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

        <div class="form-group">
          <label>Email Address</label>
          <input
            v-model="formData.student_data['Email Address']"
            type="email"
            class="input"
            placeholder="Enter email address"
            required
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
            required
          >
          <span class="error-message" v-if="errors.phone">{{ errors.phone }}</span>
        </div>
      </div>

      <!-- Submit Button and Status Message -->
      <div class="form-actions">
        <button 
          class="enroll-button"
          @click="validateAndSubmit"
          :disabled="isSubmitting"
        >
          <span v-if="isSubmitting" class="button-content">
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
          :disabled="isSubmitting"
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
import { enrollStudent, getAcademicYears, getClasses, getDivisions2 } from "../utils/apiUtils";
import '@/styles/form.css'

export default {
  data() {
    return {
      formData: {
        academicYear: null,
        className: null,
        divisionName: null,
        student_data: {
          FirstName: '',
          MiddleName: '',
          LastName: '',
          'GR Number': '',
          'Email Address': '',
          'Phone Number': ''
        }
      },
      academicYears: [],
      displayYears: [],
      classes: [],
      divisions: [],
      isSubmitting: false,
      message: null,
      errors: {}
    };
  },
  async created() {
    // Trigger both API calls independently
    await Promise.all([
      this.fetchAcademicYears(),
      this.fetchClasses()
    ]);
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
          // Automatically select the first year if available
          if (this.academicYears.length > 0) {
            this.formData.academicYear = this.academicYears[0];
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
        this.classes = response.message 
          ? response.message.map(cls => cls.name) 
          : [];
      } catch (error) {
        console.error("Error fetching classes:", error);
        this.showMessage("Error fetching classes", "error");
      }
    },
    async onYearChange() {
      this.formData.className = null;
      this.formData.divisionName = null;
      this.divisions = [];
      this.errors.className = "";
      this.errors.divisionName = "";
      await this.onClassChange();
    },
    async onClassChange() {
      this.formData.divisionName = null;
      this.errors.divisionName = "";
      
      if (this.formData.className && this.formData.academicYear) {
        try {
          const response = await getDivisions2({ 
            values: { 
              classId: this.formData.className,
              academicYear: this.formData.academicYear 
            } 
          });
          this.divisions = response.message 
            ? response.message.map(div => div.name)
            : [];
        } catch (error) {
          console.error("Error fetching divisions:", error);
          this.showMessage(`Error fetching divisions for ${this.formData.className} in ${this.formData.academicYear}`, "error");
        }
      } else {
        this.divisions = [];
      }
    },
    validateForm() {
      this.errors = {};
      let isValid = true;

      if (!this.formData.academicYear) {
        this.errors.academicYear = "Please select an academic year";
        isValid = false;
      }
      if (!this.formData.className) {
        this.errors.className = "Please select a class";
        isValid = false;
      }
      if (!this.formData.divisionName) {
        this.errors.divisionName = "Please select a division";
        isValid = false;
      }
      if (!this.formData.student_data.FirstName.trim()) {
        this.errors.firstName = "First name is required";
        isValid = false;
      }
      if (!this.formData.student_data.LastName.trim()) {
        this.errors.lastName = "Last name is required";
        isValid = false;
      }
      if (!this.formData.student_data['GR Number'].trim()) {
        this.errors.grNumber = "GR number is required";
        isValid = false;
      }
      if (!this.validEmail(this.formData.student_data['Email Address'])) {
        this.errors.email = "Please enter a valid email";
        isValid = false;
      }
      if (!this.validPhone(this.formData.student_data['Phone Number'])) {
        this.errors.phone = "Please enter a valid phone number";
        isValid = false;
      }

      return isValid;
    },
    validEmail(email) {
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return re.test(email);
    },
    validPhone(phone) {
      const re = /^[0-9]{10,15}$/;
      return re.test(phone);
    },
    async validateAndSubmit() {
      if (this.validateForm()) {
        await this.submitForm();
      }
    },
    async submitForm() {
      this.isSubmitting = true;
      this.message = null;

      try {
        const payload = {
          academicYear: this.formData.academicYear,
          student_data: {
            "First Name": this.formData.student_data.FirstName,
            "Middle Name": this.formData.student_data.MiddleName,
            "Last Name": this.formData.student_data.LastName,
            "GR Number": this.formData.student_data['GR Number'],
            "Email Address": this.formData.student_data['Email Address'],
            "Phone Number": this.formData.student_data['Phone Number']
          },
          className: this.formData.className,
          divisionName: this.formData.divisionName
        };

        console.log('Submitting student data:', JSON.stringify(payload, null, 2));

        const response = await enrollStudent(payload);

        if (response.success) {
          this.showMessage("✅ Student enrolled successfully!", "success");
          // this.resetForm();
        } else {
          let userMessage = response.error;
          this.showMessage(userMessage, "error");
        }
      } catch (error) {
        console.error('Enrollment exception:', error);
        this.showMessage(error.message || 'Unexpected error occurred', 'error');
      } finally {
        this.isSubmitting = false;
      }
    },
    resetForm() {
      this.formData = {
        academicYear: this.academicYears.length > 0 ? this.academicYears[0] : null,
        className: null,
        divisionName: null,
        student_data: {
          FirstName: '',
          MiddleName: '',
          LastName: '',
          'GR Number': '',
          'Email Address': '',
          'Phone Number': ''
        }
      };
      this.divisions = [];
      this.errors = {};
    },
    showMessage(text, type = 'info') {
      this.message = { text, type };
      if (type !== 'error') {
        setTimeout(() => this.message = null, 5000);
      }
    }
  }
};
</script>
<!-- <style scoped>
/* Base Styles */
.enrollment-form {
  max-width: 800px;
  margin: 0 auto;
  padding: 1rem;
}

.header {
  text-align: center;
  margin-bottom: 2rem;
}

.title {
  font-size: 2rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #718096;
  font-size: 1rem;
}

/* Form Card */
.form-card {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.form-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e2e8f0;
}

/* Form Grid Layout */
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

/* Form Elements */
.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #4a5568;
  margin-bottom: 0.25rem;
}

.form-group.required label::after {
  content: " *";
  color: #e53e3e;
}

.input,
.picker {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  transition: border-color 0.2s;
}

.input:focus,
.picker:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
}

.picker {
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 0.5rem center;
  background-size: 1em;
}

/* Buttons */
.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.enroll-button,
.reset-button {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.enroll-button {
  background-color: #4299e1;
  color: white;
  border: none;
}

.enroll-button:hover {
  background-color: #3182ce;
}

.enroll-button:disabled {
  background-color: #a0aec0;
  cursor: not-allowed;
}

.reset-button {
  background-color: white;
  color: #4a5568;
  border: 1px solid #e2e8f0;
}

.reset-button:hover {
  background-color: #f7fafc;
}

.reset-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.button-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.icon {
  width: 1rem;
  height: 1rem;
}

.spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
}

/* Messages */
.message {
  padding: 0.75rem 1rem;
  border-radius: 0.375rem;
  margin-top: 1rem;
  font-size: 0.875rem;
}

.message.success {
  background-color: #f0fff4;
  color: #276749;
}

.message.error {
  background-color: #fff5f5;
  color: #9b2c2c;
}

.error-message {
  display: block;
  font-size: 0.75rem;
  color: #e53e3e;
  margin-top: 0.25rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 640px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style> -->