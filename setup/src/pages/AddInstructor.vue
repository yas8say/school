```vue
<template>
  <div class="enrollment-container">
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
            >
              <option :value="null">Select Class / Program</option>
              <option v-for="cls in classes" :key="cls" :value="cls">
                {{ cls }}
              </option>
            </select>
            <span class="error-message" v-if="errors.className">{{ errors.className }}</span>
          </div>
          
          <div class="form-group">
            <label>Division / Student Group</label>
            <select 
              v-model="teacherData.divisionName" 
              class="picker"
              :disabled="!teacherData.className"
            >
              <option :value="null">Select Division / Student Group</option>
              <option v-for="div in divisions" :key="div" :value="div">
                {{ div }}
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
          :disabled="isLoading"
        >
          <span v-if="isLoading" class="button-content">
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
          :disabled="isLoading"
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
import { enrollTeacher, getClasses, getDivisions1 } from "../utils/apiUtils";
import '@/styles/form.css'

export default {
  data() {
    return {
      teacherData: {
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
      },
      classes: [],
      divisions: [],
      isLoading: false,
      message: null,
      errors: {}
    };
  },
  async created() {
    await this.fetchClasses();
  },
  methods: {
    async fetchClasses() {
      try {
        const response = await getClasses({ values: {} });
        this.classes = response.message 
          ? response.message.map(cls => cls.name).filter(name => name)
          : [];
        console.log('Processed classes:', this.classes);
      } catch (error) {
        console.error("Error fetching classes:", error);
        this.showMessage("Error fetching classes", "error");
      }
    },
    
    async onClassChange() {
      this.teacherData.divisionName = null;
      this.errors.divisionName = "";
      
      if (this.teacherData.className) {
        try {
          const response = await getDivisions1({ 
            values: { classId: this.teacherData.className } 
          });
          this.divisions = response.message 
            ? response.message.map(div => div.name).filter(name => name)
            : [];
          console.log(`Divisions for ${this.teacherData.className}:`, this.divisions);
        } catch (error) {
          console.error("Error fetching divisions:", error);
          this.showMessage(`Error fetching divisions for ${this.teacherData.className}`, "error");
        }
      } else {
        this.divisions = [];
      }
    },

    validateForm() {
      this.errors = {};
      let isValid = true;

      if (!this.teacherData.firstName.trim()) {
        this.errors.firstName = "First name is required";
        isValid = false;
      }
      
      if (!this.teacherData.lastName.trim()) {
        this.errors.lastName = "Last name is required";
        isValid = false;
      }
      
      if (!this.teacherData.gender) {
        this.errors.gender = "Gender is required";
        isValid = false;
      }
      
      if (!this.teacherData.dob) {
        this.errors.dob = "Date of birth is required";
        isValid = false;
      }
      
      if (!this.teacherData.email.trim()) {
        this.errors.email = "Email is required";
        isValid = false;
      } else if (!this.validEmail(this.teacherData.email)) {
        this.errors.email = "Please enter a valid email";
        isValid = false;
      }
      
      if (!this.teacherData.mobile.trim()) {
        this.errors.mobile = "Mobile number is required";
        isValid = false;
      } else if (!this.validMobile(this.teacherData.mobile)) {
        this.errors.mobile = "Please enter a valid mobile number";
        isValid = false;
      }

      return isValid;
    },

    validEmail(email) {
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return re.test(email);
    },

    validMobile(mobile) {
      const re = /^[0-9]{10,15}$/;
      return re.test(mobile);
    },

    async validateAndSubmit() {
      if (this.validateForm()) {
        await this.handleEnrollTeacher();
      }
    },

    async handleEnrollTeacher() {
      this.isLoading = true;
      this.showMessage(null);

      try {
        const teacher = {
          "First Name": this.teacherData.firstName,
          "Middle Name": this.teacherData.middleName,
          "Last Name": this.teacherData.lastName,
          "Gender": this.teacherData.gender,
          "Mobile": this.teacherData.mobile,
          "Email": this.teacherData.email,
          "Date of Birth": this.teacherData.dob,
          "Date of Joining": this.teacherData.doj,
          "PAN Number": this.teacherData.panNumber,
          "Bank Name": this.teacherData.bankName,
          "Bank A/C No.": this.teacherData.accountNumber,
          "IFSC Code": this.teacherData.ifscCode,
          "Designation": this.teacherData.designation,
          "Current Address": this.teacherData.address,
          "Class": this.teacherData.className || "",
          "Division": this.teacherData.divisionName || "",
          "Attendance Device ID (Biometric/RF tag ID)": this.teacherData.attendanceDeviceId,
        };

        const response = await enrollTeacher({ teacher });
        console.log("API Response:", response);

        if (response.success) {
          this.showMessage("✅ Teacher enrolled successfully!", "success");
          // this.resetForm();
        } else {
          let userMessage = response.error || "Failed to enroll teacher";
          this.showMessage(userMessage, "error");
          console.error("Enrollment error details:", {
            error: response.error,
            message: response.message
          });
        }
      } catch (error) {
        console.error("Unexpected error in handleEnrollTeacher:", error);
        this.showMessage(error.message || "An unexpected error occurred. Please try again.", "error");
      } finally {
        this.isLoading = false;
      }
    },

    resetForm() {
      this.teacherData = {
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
      };
      this.divisions = [];
      this.errors = {};
      this.showMessage(null);
    },

    showMessage(text, type = "info") {
      this.message = text ? { text, type } : null;
      if (text && type !== "error") {
        setTimeout(() => this.showMessage(null), 5000);
      }
    }
  },
};
</script>

<!-- <style scoped>
.enrollment-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.header {
  text-align: center;
  margin-bottom: 2rem;
}

.title {
  font-size: 2.2rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.subtitle {
  font-size: 1.1rem;
  color: #7f8c8d;
  margin: 0;
}

.form-card {
  background: white;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  padding: 2rem;
}

.form-title {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-top: 0;
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #eee;
}

.form-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.1rem;
  color: #34495e;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
}

.section-title::before {
  content: "";
  display: inline-block;
  width: 4px;
  height: 16px;
  background: #3498db;
  margin-right: 8px;
  border-radius: 2px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #34495e;
  font-size: 0.95rem;
}

.form-group.required label::after {
  content: " *";
  color: #e74c3c;
}

.input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.textarea {
  min-height: 100px;
  resize: vertical;
}

.picker {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  background-color: white;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 1rem;
}

.error-message {
  display: block;
  color: #e74c3c;
  font-size: 0.85rem;
  margin-top: 0.25rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
}

.enroll-button {
  background: #27ae60;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  transition: background 0.2s, transform 0.1s;
}

.enroll-button:hover {
  background: #2ecc71;
}

.enroll-button:active {
  transform: scale(0.98);
}

.enroll-button:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

.reset-button {
  background: #f5f5f5;
  color: #7f8c8d;
  border: 1px solid #ddd;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.reset-button:hover {
  background: #ecf0f1;
}

.reset-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.button-content {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.icon {
  width: 18px;
  height: 18px;
}

.spinner {
  display: inline-block;
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.message {
  padding: 1rem;
  border-radius: 6px;
  margin-top: 1.5rem;
  font-weight: 500;
}

.message.success {
  background: #d5f5e3;
  color: #27ae60;
}

.message.error {
  background: #fadbd8;
  color: #e74c3c;
}

.message.info {
  background: #d6eaf8;
  color: #2980b9;
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .enroll-button,
  .reset-button {
    width: 100%;
  }
}
</style> -->
```