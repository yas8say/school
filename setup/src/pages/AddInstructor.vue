<template>
  <div class="enrollment-container">
    <!-- Loading Screen -->
    <div v-if="isLoading || enrollTeacherResource.loading" class="loading-overlay">
      <div class="loading-modal">
        <div class="loading-spinner"></div>
        <h3 class="loading-title">Enrolling Teacher...</h3>
        <p class="loading-description">Please wait while we process the teacher information.</p>
      </div>
    </div>

    <!-- Success/Failure Message -->
    <div v-if="showResultMessage" class="modal-overlay">
      <div class="result-modal">
        <div v-if="submitSuccess" class="success-icon">
          <svg class="icon" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <div v-else class="error-icon">
          <svg class="icon" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </div>
        <h3 class="result-title">
          {{ submitSuccess ? 'Teacher Enrolled Successfully!' : 'Enrollment Failed' }}
        </h3>
        <p class="result-description">
          {{ submitSuccess ? successMessage : errorMessage }}
        </p>
        <div class="modal-actions">
          <button
            v-if="submitSuccess"
            @click="resetAndClose"
            class="success-button"
          >
            Add Another Teacher
          </button>
          <button
            v-else
            @click="showResultMessage = false"
            class="primary-button"
          >
            Try Again
          </button>
          <button
            v-if="submitSuccess"
            @click="showResultMessage = false"
            class="secondary-button"
          >
            Close
          </button>
        </div>
      </div>
    </div>

    <div class="header">
      <h1 class="title">Teacher Enrollment</h1>
      <p class="subtitle">Add new teacher to the system</p>
    </div>

    <div class="form-card">
      <h2 class="form-title">Teacher Information</h2>
      
      <div class="form-section">
        <h3 class="section-title">Personal Details</h3>
        <div class="form-grid">
          <div class="form-group required">
            <label>First Name</label>
            <input 
              v-model="teacherData.firstName" 
              class="input" 
              placeholder="Enter first name"
              required
            >
            <span class="error-message" v-if="errors.firstName">{{ errors.firstName }}</span>
          </div>
          
          <div class="form-group">
            <label>Middle Name</label>
            <input v-model="teacherData.middleName" class="input" placeholder="Enter middle name">
          </div>
          
          <div class="form-group required">
            <label>Last Name</label>
            <input 
              v-model="teacherData.lastName" 
              class="input" 
              placeholder="Enter last name"
              required
            >
            <span class="error-message" v-if="errors.lastName">{{ errors.lastName }}</span>
          </div>
          
          <div class="form-group required">
            <label>Gender</label>
            <select 
              v-model="teacherData.gender" 
              class="picker"
              required
            >
              <option value="">Select Gender</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
            <span class="error-message" v-if="errors.gender">{{ errors.gender }}</span>
          </div>
          
          <div class="form-group required">
            <label>Date of Birth</label>
            <input 
              v-model="teacherData.dob" 
              type="date" 
              class="input"
              required
            >
            <span class="error-message" v-if="errors.dob">{{ errors.dob }}</span>
          </div>
        </div>
      </div>

      <div class="form-section">
        <h3 class="section-title">Contact Information</h3>
        <div class="form-grid">
          <div class="form-group required">
            <label>Email</label>
            <input 
              v-model="teacherData.email" 
              type="email" 
              class="input" 
              placeholder="Enter email"
              required
            >
            <span class="error-message" v-if="errors.email">{{ errors.email }}</span>
          </div>
          
          <div class="form-group required">
            <label>Mobile</label>
            <input 
              v-model="teacherData.mobile" 
              class="input" 
              placeholder="Enter mobile number"
              required
            >
            <span class="error-message" v-if="errors.mobile">{{ errors.mobile }}</span>
          </div>
          
          <div class="form-group">
            <label>Address</label>
            <textarea v-model="teacherData.address" class="input textarea" placeholder="Enter address"></textarea>
          </div>
        </div>
      </div>

      <div class="form-section">
        <h3 class="section-title">School Information</h3>
        <div class="form-grid">
          <div class="form-group">
            <label>Class / Program</label>
            <select 
              v-model="teacherData.className" 
              class="picker"
              @change="onClassChange"
              :disabled="classesResource.loading"
            >
              <option :value="null">Select Class / Program</option>
              <option v-for="cls in classes" :key="cls.name" :value="cls.name">
                {{ cls.name }}
              </option>
            </select>
            <span class="error-message" v-if="errors.className">{{ errors.className }}</span>
          </div>
          
          <div class="form-group">
            <label>Division / Student Group</label>
            <select 
              v-model="teacherData.divisionName" 
              class="picker"
              :disabled="!teacherData.className || divisionsResource.loading"
            >
              <option :value="null">Select Division / Student Group</option>
              <option v-for="div in divisions" :key="div.name" :value="div.name">
                {{ div.name }}
              </option>
            </select>
            <span class="error-message" v-if="errors.divisionName">{{ errors.divisionName }}</span>
          </div>
          
          <div class="form-group">
            <label>Designation</label>
            <input v-model="teacherData.designation" class="input" placeholder="Enter designation">
          </div>
          
          <div class="form-group">
            <label>Date of Joining</label>
            <input v-model="teacherData.doj" type="date" class="input">
          </div>
          
          <div class="form-group">
            <label>Attendance Device ID (Biometric/RF tag ID)</label>
            <input v-model="teacherData.attendanceDeviceId" class="input" placeholder="Enter attendance device ID">
          </div>
        </div>
      </div>

      <div class="form-section">
        <h3 class="section-title">Bank Details (Optional)</h3>
        <div class="form-grid">
          <div class="form-group">
            <label>Bank Name</label>
            <input v-model="teacherData.bankName" class="input" placeholder="Enter bank name">
          </div>
          
          <div class="form-group">
            <label>Account Number</label>
            <input v-model="teacherData.accountNumber" class="input" placeholder="Enter account number">
          </div>
          
          <div class="form-group">
            <label>IFSC Code</label>
            <input v-model="teacherData.ifscCode" class="input" placeholder="Enter IFSC code">
          </div>
          
          <div class="form-group">
            <label>PAN Number</label>
            <input v-model="teacherData.panNumber" class="input" placeholder="Enter PAN number">
          </div>
        </div>
      </div>

      <div class="form-actions">
        <button 
          class="enroll-button" 
          @click="validateAndSubmit"
          :disabled="isLoading || enrollTeacherResource.loading || showResultMessage"
        >
          <span v-if="isLoading || enrollTeacherResource.loading" class="button-content">
            <span class="spinner"></span> Processing...
          </span>
          <span v-else class="button-content">
            <svg class="icon" viewBox="0 0 24 24">
              <path fill="currentColor" d="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z" />
            </svg>
            Enroll Teacher
          </span>
        </button>
        
        <button 
          class="reset-button" 
          @click="resetForm"
          :disabled="isLoading || enrollTeacherResource.loading || showResultMessage"
        >
          Reset Form
        </button>
      </div>

      <!-- Inline message (for non-modal notifications) -->
      <div v-if="message && !showResultMessage" :class="['message', message.type]">
        {{ message.text }}
      </div>
    </div>
  </div>
</template>

<script>
import { createResource } from 'frappe-ui';
import { reactive, ref, onMounted } from 'vue';
import '@/styles/form.css';

export default {
  setup() {
    // Reactive teacher data
    const teacherData = reactive({
      firstName: "",
      middleName: "",
      lastName: "",
      gender: "",
      mobile: "",
      email: "",
      dob: "",
      doj: "",
      panNumber: "",
      bankName: "",
      accountNumber: "",
      ifscCode: "",
      designation: "",
      address: "",
      className: null,
      divisionName: null,
      attendanceDeviceId: "",
    });

    // State variables
    const classes = ref([]);
    const divisions = ref([]);
    const isLoading = ref(false);
    const message = ref(null);
    const errors = reactive({});

    // New state for modal management
    const showResultMessage = ref(false);
    const submitSuccess = ref(false);
    const errorMessage = ref('');
    const successMessage = ref('');

    // API Resources
    const classesResource = createResource({
      url: 'school.al_ummah.api3.get_classes',
      params: { values: {} },
      onSuccess: (data) => {
        classes.value = Array.isArray(data) ? data : [];
        console.log('Classes loaded:', classes.value);
      },
      onError: (err) => {
        console.error('Error fetching classes:', err);
        classes.value = [];
      }
    });

    const divisionsResource = createResource({
      url: 'school.al_ummah.api3.get_divisions1',
      params: {
        values: { classId: teacherData.className }
      },
      onSuccess: (data) => {
        divisions.value = Array.isArray(data) ? data : [];
        console.log('Divisions loaded:', divisions.value);
      },
      onError: (err) => {
        console.error('Error fetching divisions:', err);
        divisions.value = [];
      }
    });

    const enrollTeacherResource = createResource({
      url: 'school.al_ummah.api3.enroll_single_instructor',
      params: {
        teacher: {
          "First Name": teacherData.firstName,
          "Middle Name": teacherData.middleName,
          "Last Name": teacherData.lastName,
          "Gender": teacherData.gender,
          "Mobile": teacherData.mobile,
          "Email": teacherData.email,
          "Date of Birth": teacherData.dob,
          "Date of Joining": teacherData.doj,
          "PAN Number": teacherData.panNumber,
          "Bank Name": teacherData.bankName,
          "Bank A/C No.": teacherData.accountNumber,
          "IFSC Code": teacherData.ifscCode,
          "Designation": teacherData.designation,
          "Current Address": teacherData.address,
          "Class": teacherData.className || "",
          "Division": teacherData.divisionName || "",
          "Attendance Device ID (Biometric/RF tag ID)": teacherData.attendanceDeviceId,
        }
      },
      onSuccess: (response) => {
        isLoading.value = false;
        submitSuccess.value = true;
        
        // Create personalized success message
        if (response && response.message) {
          successMessage.value = response.message;
        } else {
          successMessage.value = `Teacher ${teacherData.firstName} ${teacherData.lastName} has been successfully enrolled${teacherData.designation ? ` as ${teacherData.designation}` : ''}.`;
        }
        
        showResultMessage.value = true;
      },
      onError: (err) => {
        isLoading.value = false;
        submitSuccess.value = false;
        
        // Create detailed error message
        if (err.messages && err.messages.length > 0) {
          errorMessage.value = err.messages[0];
        } else if (err.message) {
          errorMessage.value = err.message;
        } else {
          errorMessage.value = 'An unexpected error occurred while enrolling the teacher. Please try again.';
        }
        
        showResultMessage.value = true;
      }
    });

    // Fetch initial data on mount
    onMounted(() => {
      classesResource.reload();
    });

    // Methods
    function onClassChange() {
      teacherData.divisionName = null;
      errors.divisionName = '';
      if (teacherData.className) {
        divisionsResource.update({
          params: { values: { classId: teacherData.className } }
        });
        divisionsResource.reload();
      } else {
        divisions.value = [];
      }
    }

    function validateForm() {
      Object.assign(errors, {});
      let isValid = true;

      if (!teacherData.firstName.trim()) {
        errors.firstName = "First name is required";
        isValid = false;
      }
      
      if (!teacherData.lastName.trim()) {
        errors.lastName = "Last name is required";
        isValid = false;
      }
      
      if (!teacherData.gender) {
        errors.gender = "Gender is required";
        isValid = false;
      }
      
      if (!teacherData.dob) {
        errors.dob = "Date of birth is required";
        isValid = false;
      }
      
      if (!teacherData.email.trim()) {
        errors.email = "Email is required";
        isValid = false;
      } else if (!validEmail(teacherData.email)) {
        errors.email = "Please enter a valid email";
        isValid = false;
      }
      
      if (!teacherData.mobile.trim()) {
        errors.mobile = "Mobile number is required";
        isValid = false;
      } else if (!validMobile(teacherData.mobile)) {
        errors.mobile = "Please enter a valid mobile number";
        isValid = false;
      }

      return isValid;
    }

    function validEmail(email) {
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return re.test(email);
    }

    function validMobile(mobile) {
      const re = /^[0-9]{10,15}$/;
      return re.test(mobile);
    }

    function validateAndSubmit() {
      if (validateForm()) {
        submitForm();
      }
    }

    function submitForm() {
      isLoading.value = true;
      enrollTeacherResource.update({
        params: {
          teacher: {
            "First Name": teacherData.firstName,
            "Middle Name": teacherData.middleName,
            "Last Name": teacherData.lastName,
            "Gender": teacherData.gender,
            "Mobile": teacherData.mobile,
            "Email": teacherData.email,
            "Date of Birth": teacherData.dob,
            "Date of Joining": teacherData.doj,
            "PAN Number": teacherData.panNumber,
            "Bank Name": teacherData.bankName,
            "Bank A/C No.": teacherData.accountNumber,
            "IFSC Code": teacherData.ifscCode,
            "Designation": teacherData.designation,
            "Current Address": teacherData.address,
            "Class": teacherData.className || "",
            "Division": teacherData.divisionName || "",
            "Attendance Device ID (Biometric/RF tag ID)": teacherData.attendanceDeviceId,
          }
        }
      });
      enrollTeacherResource.submit();
    }

    function resetForm() {
      Object.assign(teacherData, {
        firstName: "",
        middleName: "",
        lastName: "",
        gender: "",
        mobile: "",
        email: "",
        dob: "",
        doj: "",
        panNumber: "",
        bankName: "",
        accountNumber: "",
        ifscCode: "",
        designation: "",
        address: "",
        className: null,
        divisionName: null,
        attendanceDeviceId: "",
      });
      divisions.value = [];
      Object.assign(errors, {});
      showMessage(null);
    }

    function resetAndClose() {
      resetForm();
      showResultMessage.value = false;
      submitSuccess.value = false;
    }

    function showMessage(text, type = "info") {
      message.value = text ? { text, type } : null;
      if (text && type !== "error") {
        setTimeout(() => showMessage(null), 5000);
      }
    }

    return {
      teacherData,
      classes,
      divisions,
      isLoading,
      message,
      errors,
      classesResource,
      divisionsResource,
      enrollTeacherResource,
      showResultMessage,
      submitSuccess,
      errorMessage,
      successMessage,
      onClassChange,
      validateAndSubmit,
      resetForm,
      resetAndClose
    };
  }
};
</script>