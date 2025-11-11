<template>
  <div class="enrollment-container">
    <!-- Floating Navigation Buttons -->
    <div class="floating-navigation">
      <button
        v-if="currentStep > 0"
        @click="prevStep"
        class="nav-button back-button"
      >
        <svg class="button-icon" viewBox="0 0 24 24">
          <path fill="currentColor" d="M15.41,16.58L10.83,12L15.41,7.41L14,6L8,12L14,18L15.41,16.58Z" />
        </svg>
        Back
      </button>
      <div v-else class="back-button-placeholder"></div>
      <button
        @click="nextStep"
        class="nav-button next-button"
        :disabled="isSubmitting || quickSetupResource.loading"
      >
        {{ currentStep === steps.length - 1 ? (isSubmitting ? 'Submitting...' : 'Submit') : 'Next' }}
        <svg class="button-icon" viewBox="0 0 24 24">
          <path fill="currentColor" d="M8.59,16.58L13.17,12L8.59,7.41L10,6L16,12L10,18L8.59,16.58Z" />
        </svg>
      </button>
    </div>

    <div v-if="currentStep < steps.length" class="scroll-view-content">
      <div class="header">
        <h2 class="title">{{ steps[currentStep].title }}</h2>
      </div>

      <!-- Missing Fields Alert -->
      <div v-if="missingFields.length > 0 && showMissingFields" class="missing-fields-alert form-card">
        <div class="alert-header">
          <div class="alert-icon">
            <svg class="icon" viewBox="0 0 24 24">
              <path fill="currentColor" d="M13,13H11V7H13M13,17H11V15H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z" />
            </svg>
          </div>
          <h3 class="alert-title">Required Information Missing</h3>
          <button @click="showMissingFields = false" class="close-button">
            <svg class="close-icon" viewBox="0 0 24 24">
              <path fill="currentColor" d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z" />
            </svg>
          </button>
        </div>
        <div class="alert-content">
          <p class="alert-description">Please fill in the following required fields before proceeding:</p>
          <ul class="missing-fields-list">
            <li v-for="(field, index) in missingFields" :key="index" class="missing-field-item">
              <span class="field-bullet">•</span>
              {{ field }}
            </li>
          </ul>
        </div>
      </div>

      <div class="form-card">
        <component
          :is="steps[currentStep].component"
          :values="formValues"
          :previousDataList="previousDataList"
          @update-field="updateField"
          @update-field-array="updateFieldArray"
          @submit-email="submitEmailAccount"
          @auto-create-terms="autoCreateTerms"
          @auto-create-classes="autoCreateClasses" 
          @use-previous-data="usePreviousData"
          @grading-completed="handleGradingCompleted"
        />
      </div>
    </div>

    <!-- Loading Screen -->
    <div v-if="isSubmitting" class="loading-overlay">
      <div class="loading-modal">
        <div class="loading-spinner"></div>
        <h3 class="loading-title">Submitting your data...</h3>
        <p class="loading-description">Please wait while we process your information.</p>
      </div>
    </div>

    <!-- Success/Failure Message -->
    <div v-if="showResultMessage" class="modal-overlay">
      <div class="result-modal">
        <div v-if="submitSuccess" class="success-icon">
          <svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <div v-else class="error-icon">
          <svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </div>
        <h3 class="result-title">
          {{ submitSuccess ? 'Form Submitted Successfully!' : 'Submission Failed' }}
        </h3>
        <p class="result-description">
          {{ submitSuccess ? 'Your data has been successfully processed.' : errorMessage || 'An error occurred while submitting the form.' }}
        </p>
        <div class="modal-actions">
          <button
            @click="showResultMessage = false"
            class="success-button"
          >
            OK
          </button>
        </div>
      </div>
    </div>

    <!-- Success Message -->
    <div v-if="currentStep >= steps.length && !isSubmitting && !showResultMessage" class="form-card">
      <div class="header">
        <h2 class="title">Form Submitted Successfully!</h2>
        <p class="subtitle">Your data has been successfully processed.</p>
      </div>
    </div>
  </div>
</template>

<script>
import { createResource } from 'frappe-ui';
import { reactive, ref, onMounted, watch } from 'vue';
import EmailAccountSetup from './EmailAccountSetup.vue';
import AcademicYearTerms from './AcademicYearTerms.vue';
import UsePreviousData from './UsePreviousData.vue';
import SubjectsDivisions from './SubjectsDivisions.vue';
import GradingSystem from './GradingSystem.vue';
import FeeStructureCreator from './FeeStructureCreator.vue';
import '@/styles/form.css';
 
export default {
  name: 'MultiStepForm',
  components: {
    EmailAccountSetup,
    AcademicYearTerms,
    UsePreviousData,
    SubjectsDivisions,
    GradingSystem,
    FeeStructureCreator
  },
  setup() {
    // Reactive state
    const currentStep = ref(0);
    const previousDataList = ref([]);
    const isSubmitting = ref(false);
    const showResultMessage = ref(false);
    const submitSuccess = ref(false);
    const errorMessage = ref('');
    const missingFields = ref([]);
    const showMissingFields = ref(false);

    const formValues = reactive({
      email: '',
      googleAppPassword: '',
      academicYear: '',
      academicYearStart: '',
      academicYearEnd: '',
      numberOfTerms: '',
      terms: [],
      selectedTerm: '',
      selectedInstitution: '',
      classes: [],
      subjects: [],
      divisions: [],
      commonSubjects: [],
      commonDivisions: [],
      dontCreateClasses: false,
      feeStructures: [],
      setAsCurrent: false,
      gradingSystem: {
        selectedOption: '',
        scaleName: '',
        previousScaleName: '',
        gradeData: null
      },
      gradingCompleted: false
    });

    // Reordered steps: Subjects & Divisions after Use Previous Data, Grading after Subjects
    const steps = ref([
      { title: 'Email Account Setup (Optional)', component: 'EmailAccountSetup' },
      { title: 'Academic Year & Terms', component: 'AcademicYearTerms' },
      { title: 'Use Previous Data', component: 'UsePreviousData' },
      { title: 'Subjects and Divisions', component: 'SubjectsDivisions' },
      { title: 'Grading System', component: 'GradingSystem' },
      { title: 'Create Fee Structures', component: 'FeeStructureCreator' }
    ]);

    // API Resources
    const previousDataResource = createResource({
      url: 'school.al_ummah.api3.get_previous_data',
      params: { values: {} },
      onSuccess: (data) => {
        previousDataList.value = Array.isArray(data) ? data.map(item => ({
          ...item,
          academicYear: item.json_data ? JSON.parse(item.json_data).academicYear : '',
        })) : [];
      },
      onError: (err) => {
        console.error('Error fetching previous data:', err);
        previousDataList.value = [];
      }
    });

    const setEmailAccResource = createResource({
      url: 'school.al_ummah.api3.create_email_account',
      params: {
        email_id: '',
        password: ''
      },
      onSuccess: () => {
        alert('Email account setup successfully!');
      },
      onError: (err) => {
        console.error('Error setting up email account:', err);
        alert('Error setting up email account.');
      }
    });

    const quickSetupResource = createResource({
      url: 'school.al_ummah.api3.quick_setup',
      params: {
        values: {}
      },
      onSuccess: () => {
        submitSuccess.value = true;
        currentStep.value++;
        isSubmitting.value = false;
        showResultMessage.value = true;
      },
      onError: (err) => {
        submitSuccess.value = false;
        errorMessage.value = err.messages?.[0] || 'An error occurred while submitting the form.';
        console.error('Submission error:', err);
        isSubmitting.value = false;
        showResultMessage.value = true;
      }
    });

    // Methods
    function handleGradingCompleted() {
      formValues.gradingCompleted = true;
      nextStep();
    }
    
    function autoCreateClasses({ classNames }) {
      const currentClasses = [...formValues.classes];
      const maxIndex = currentClasses.reduce(
        (max, cls) => Math.max(max, cls.classIndex || 0),
        0
      );

      const newClasses = classNames.map((name, index) => ({
        className: name,
        subjects: [],
        divisions: [{ divisionName: '' }],
        classIndex: maxIndex + index + 1
      }));

      formValues.classes = [...currentClasses, ...newClasses];
    }

    function fetchPreviousData() {
      previousDataResource.reload();
    }

    function updateField({ field, value, parent = null }) {
      if (parent && formValues[parent]) {
        formValues[parent][field] = value;
      } else {
        formValues[field] = value;
      }
    }

    function updateFieldArray({ field, index, subField, value }) {
      if (index !== undefined && subField) {
        formValues[field][index][subField] = value;
      } else if (index !== undefined) {
        formValues[field][index] = value;
      } else {
        formValues[field] = value;
      }
    }

    async function submitEmailAccount() {
      const { email, googleAppPassword } = formValues;
      if (!email || !googleAppPassword) {
        alert('Please provide both email and Google app password.');
        return;
      }

      setEmailAccResource.update({
        params: {
          email_id: email,
          password: googleAppPassword
        }
      });
      setEmailAccResource.submit();
    }

    function autoCreateTerms() {
      const numberOfTerms = parseInt(formValues.numberOfTerms, 10);
      const startDate = new Date(formValues.academicYearStart);
      const endDate = new Date(formValues.academicYearEnd);

      if (!numberOfTerms || numberOfTerms <= 0) {
        alert("Please enter a valid number of terms.");
        return;
      }
      if (isNaN(startDate.getTime())) {
        alert("Please enter valid 'From' date.");
        return;
      }
      if (isNaN(endDate.getTime())) {
        alert("Please enter valid 'To' date.");
        return;
      }
      if (startDate >= endDate) {
        alert("'From' date must be before 'To' date.");
        return;
      }

      const totalDays = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));
      const daysPerTerm = Math.floor(totalDays / numberOfTerms);
      const terms = [];

      let termStart = new Date(startDate);
      for (let i = 0; i < numberOfTerms; i++) {
        const termEnd = new Date(termStart);
        termEnd.setDate(termStart.getDate() + daysPerTerm - 1);

        if (i === numberOfTerms - 1) {
          termEnd.setTime(endDate.getTime());
        }

        terms.push({
          name: `Term ${i + 1}`,
          startDate: termStart.toISOString().split('T')[0],
          endDate: termEnd.toISOString().split('T')[0],
        });

        termStart = new Date(termEnd);
        termStart.setDate(termStart.getDate() + 1);
      }

      formValues.terms = terms;
    }

function usePreviousData(selectedData) { // 🆕 ADD 'function' keyword
  console.log('📥 USE_PREVIOUS_DATA: Selected data received', selectedData);
  
  if (!selectedData?.json_data) {
    console.error('❌ Invalid or missing previous data');
    return;
  }

  try {
    const parsedData = JSON.parse(selectedData.json_data);
    console.log('📊 Parsed previous data:', {
      classes: parsedData.classes,
      commonSubjects: parsedData.commonSubjects,
      commonDivisions: parsedData.commonDivisions,
      divisions: parsedData.divisions
    });

    // Load classes
    formValues.classes = parsedData.classes || [];
    
    // CRITICAL FIX: Load common data from previous data
    formValues.commonSubjects = parsedData.commonSubjects || [];
    formValues.commonDivisions = parsedData.commonDivisions || [];
    
    // Also update subjects and divisions arrays if they exist
    formValues.subjects = parsedData.subjects || [];
    formValues.divisions = parsedData.divisions || [];

    console.log('✅ Updated formValues:', {
      classes: formValues.classes,
      commonSubjects: formValues.commonSubjects,
      commonDivisions: formValues.commonDivisions
    });

  } catch (error) {
    console.error('❌ Error parsing previous data:', error);
    alert('Failed to load previous data. Please try another selection.');
  }
}

    function nextStep() {
      if (currentStep.value < steps.value.length - 1) {
        currentStep.value++;
        showMissingFields.value = false;
      } else {
        submitForm();
      }
    }

    function prevStep() {
      if (currentStep.value > 0) {
        currentStep.value--;
        showMissingFields.value = false;
      }
    }

    function submitForm() {
      isSubmitting.value = true;
      showResultMessage.value = false;
      submitSuccess.value = false;
      errorMessage.value = '';
      showMissingFields.value = false;

      const exceptions = ['selectedTerm', 'commonSubjects', 'commonDivisions', 'divisions', 'institutionName', 'logo', 'dontCreateClasses', 'subjects', 'terms', 'email', 'googleAppPassword', 'classes', 'gradingSystem', 'gradingCompleted', 'setAsCurrent'];
      const missing = checkMissingFields(formValues, exceptions);

      if (missing.length > 0) {
        missingFields.value = missing;
        showMissingFields.value = true;
        isSubmitting.value = false;
        
        window.scrollTo({ top: 0, behavior: 'smooth' });
        return;
      }

      quickSetupResource.update({
        params: {
          values: { ...formValues }
        }
      });
      quickSetupResource.submit();
    }

    function checkMissingFields(values, exceptions) {
      const missingFields = [];

      Object.entries(values).forEach(([key, value]) => {
        if (exceptions.includes(key)) return;

        if (Array.isArray(value)) {
          if (value.length === 0) {
            const formattedField = formatFieldName(key);
            missingFields.push(`${formattedField} list is empty`);
          } else {
            value.forEach((item, index) => {
              if (typeof item === 'object' && item !== null) {
                Object.entries(item).forEach(([subKey, subValue]) => {
                  if (!subValue || (typeof subValue === 'string' && subValue.trim() === '')) {
                    const formattedField = formatFieldName(subKey);
                    const formattedParent = formatFieldName(key);
                    missingFields.push(`${formattedParent} ${index + 1}: ${formattedField} is required`);
                  }
                });
              }
            });
          }
        } else if (!value || (typeof value === 'string' && value.trim() === '')) {
          const formattedField = formatFieldName(key);
          missingFields.push(`${formattedField} is required`);
        }
      });

      return missingFields;
    }

    function formatFieldName(fieldName) {
      return fieldName
        .replace(/([A-Z])/g, ' $1')
        .replace(/^./, str => str.toUpperCase())
        .replace(/([A-Z])/g, ' $1')
        .trim();
    }

    // Fetch initial data on mount
    onMounted(() => {
      fetchPreviousData();
    });
        // 🆕 ADD DEBUG WATCHERS HERE - right before return statement
    // Watch for formValues changes to debug data flow
    watch(
      () => formValues.commonDivisions,
      (newVal) => {
        console.log('🏠 MAIN COMPONENT: commonDivisions updated:', newVal);
      },
      { deep: true }
    );

    watch(
      () => formValues.commonSubjects,
      (newVal) => {
        console.log('🏠 MAIN COMPONENT: commonSubjects updated:', newVal);
      },
      { deep: true }
    );

    watch(
      () => formValues.classes,
      (newVal) => {
        console.log('🏠 MAIN COMPONENT: classes updated - count:', newVal?.length);
        if (newVal && newVal.length > 0) {
          console.log('🏠 MAIN COMPONENT: First class divisions:', newVal[0]?.divisions);
        }
      },
      { deep: true }
    );

    // 🆕 Also add a watcher for the entire formValues to see everything
    watch(
      formValues,
      (newVal) => {
        console.log('🏠 MAIN COMPONENT: formValues updated:', {
          commonSubjects: newVal.commonSubjects,
          commonDivisions: newVal.commonDivisions,
          classesCount: newVal.classes?.length
        });
      },
      { deep: true, immediate: true }
    );

    return {
      currentStep,
      previousDataList,
      isSubmitting,
      showResultMessage,
      submitSuccess,
      errorMessage,
      missingFields,
      showMissingFields,
      formValues,
      steps,
      quickSetupResource,
      autoCreateClasses,
      fetchPreviousData,
      updateField,
      updateFieldArray,
      submitEmailAccount,
      autoCreateTerms,
      usePreviousData,
      handleGradingCompleted,
      nextStep,
      prevStep,
      submitForm,
      checkMissingFields,
      formatFieldName
    };
  }
};
</script>

<style scoped>
/* Navigation Container */
.floating-navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 20px 0;
  gap: 20px;
  position: sticky;
  bottom: 0;
  background: white;
  border-top: 1px solid #e2e8f0;
  margin-top: auto;
}

.back-button-placeholder {
  min-width: 120px;
  height: 44px;
  visibility: hidden;
}

.nav-button {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 25px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
  justify-content: center;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.back-button {
  background: #f8fafc;
  color: #475569;
  border: 2px solid #e2e8f0;
  margin-right: auto; /* Push to left */
}

.next-button {
  background: #3b82f6;
  color: white;
  border: 2px solid #3b82f6;
  margin-left: auto; /* Push to right */
}

/* Responsive Navigation */
@media (max-width: 768px) {
  .navigation-container {
    padding: 15px 0;
    gap: 15px;
  }
  
  .back-button-placeholder {
    min-width: 100px;
    height: 40px;
  }

  .nav-button {
    min-width: 100px;
    padding: 10px 20px;
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .navigation-container {
    padding: 10px 0;
    gap: 10px;
  }

  .back-button-placeholder {
    min-width: 80px;
    height: 40px;
  }

  .nav-button {
    width: auto;
    min-width: 80px;
    padding: 10px 15px;
    font-size: 13px;
  }
}

@media (max-width: 320px) {
  .navigation-container {
    padding: 8px 0;
  }
  
  .back-button-placeholder {
    min-width: 70px;
  }
  
  .nav-button {
    padding: 8px 12px;
    font-size: 12px;
    min-width: 70px;
  }
}
</style>
