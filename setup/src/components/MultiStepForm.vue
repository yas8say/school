<template>
  <div class="p-4 max-w-4xl mx-auto">
    <div v-if="currentStep < steps.length">
      <h2 class="text-2xl font-semibold mb-6">{{ steps[currentStep].title }}</h2>

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
        class="mb-6"
      />

      <div class="flex justify-between gap-4">
        <button
          v-if="currentStep > 0"
          @click="prevStep"
          class="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
        >
          Back
        </button>
        <button
          @click="nextStep"
          class="ml-auto px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          :disabled="isSubmitting || quickSetupResource.loading"
        >
          {{ currentStep === steps.length - 1 ? (isSubmitting ? 'Submitting...' : 'Submit') : 'Next' }}
        </button>
      </div>
    </div>

    <!-- Loading Screen -->
    <div v-if="isSubmitting" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white p-8 rounded-lg shadow-lg max-w-md w-full text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
        <h3 class="text-lg font-medium text-gray-900">Submitting your data...</h3>
        <p class="mt-2 text-sm text-gray-500">Please wait while we process your information.</p>
      </div>
    </div>

    <!-- Success/Failure Message -->
    <div v-if="showResultMessage" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white p-8 rounded-lg shadow-lg max-w-md w-full text-center">
        <div v-if="submitSuccess" class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
          <svg class="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <div v-else class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
          <svg class="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </div>
        <h3 class="mt-3 text-lg font-medium text-gray-900">
          {{ submitSuccess ? 'Form Submitted Successfully!' : 'Submission Failed' }}
        </h3>
        <p class="mt-2 text-sm text-gray-500">
          {{ submitSuccess ? 'Your data has been successfully processed.' : errorMessage || 'An error occurred while submitting the form.' }}
        </p>
        <div class="mt-5">
          <button
            @click="showResultMessage = false"
            class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            OK
          </button>
        </div>
      </div>
    </div>

    <!-- Original Success Message (now hidden behind modal) -->
    <div v-if="currentStep >= steps.length && !isSubmitting && !showResultMessage" class="text-center mt-10">
      <h2 class="text-2xl font-semibold text-green-600">Form Submitted Successfully!</h2>
    </div>
  </div>
</template>

<script>
import { createResource } from 'frappe-ui';
import { reactive, ref, onMounted } from 'vue';
import EmailAccountSetup from './EmailAccountSetup.vue';
import AcademicYearTerms from './AcademicYearTerms.vue';
import UsePreviousData from './UsePreviousData.vue';
import ProgramSelection from './ProgramSelection.vue';
import SubjectsDivisions from './SubjectsDivisions.vue';

export default {
  components: {
    EmailAccountSetup,
    AcademicYearTerms,
    UsePreviousData,
    ProgramSelection,
    SubjectsDivisions
  },
  setup() {
    // Reactive state
    const currentStep = ref(0);
    const previousDataList = ref([]);
    const isSubmitting = ref(false);
    const showResultMessage = ref(false);
    const submitSuccess = ref(false);
    const errorMessage = ref('');

    const formValues = reactive({
      email: '',
      googleAppPassword: '',
      academicYear: '',
      academicYearStart: '',
      academicYearEnd: '',
      numberOfTerms: '',
      terms: [],
      selectedTerm: '',
      classes: [],
      subjects: [],
      divisions: [],
      commonSubjects: [],
      commonDivisions: [],
      dontCreateClasses: false
    });

    const steps = ref([
      { title: 'Email Account Setup (Optional)', component: 'EmailAccountSetup' },
      { title: 'Academic Year & Terms', component: 'AcademicYearTerms' },
      { title: 'Use Previous Data', component: 'UsePreviousData' },
      { title: 'Select Institution Type & Classes', component: 'ProgramSelection' },
      { title: 'Subjects and Divisions', component: 'SubjectsDivisions' }
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

    function updateField({ field, value }) {
      formValues[field] = value;
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

    function usePreviousData(selectedData) {
      if (!selectedData?.json_data) {
        console.error('Invalid or missing previous data');
        return;
      }

      try {
        const parsedData = JSON.parse(selectedData.json_data);
        formValues.classes = parsedData.classes || [];
        formValues.subjects = parsedData.subjects || [];
      } catch (error) {
        console.error('Error parsing previous data:', error);
        alert('Failed to load previous data. Please try another selection.');
      }
    }

    function nextStep() {
      if (currentStep.value < steps.value.length - 1) {
        currentStep.value++;
      } else {
        submitForm();
      }
    }

    function prevStep() {
      if (currentStep.value > 0) {
        currentStep.value--;
      }
    }

    function submitForm() {
      isSubmitting.value = true;
      showResultMessage.value = false;
      submitSuccess.value = false;
      errorMessage.value = '';

      const exceptions = ['selectedTerm', 'commonSubjects', 'commonDivisions', 'divisions', 'institutionName', 'logo', 'dontCreateClasses', 'subjects', 'terms', 'email', 'googleAppPassword', 'classes'];
      const missingFields = checkMissingFields(formValues, exceptions);

      if (missingFields.length > 0) {
        alert(`Please fill in the following fields:\n - ${missingFields.join('\n- ')}`);
        isSubmitting.value = false;
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
            missingFields.push(`The list of ${key} is empty`);
          }
        } else if (!value || (typeof value === 'string' && value.trim() === '')) {
          missingFields.push(`${key} is missing or empty`);
        }
      });

      return missingFields;
    }

    // Fetch initial data on mount
    onMounted(() => {
      fetchPreviousData();
    });

    return {
      currentStep,
      previousDataList,
      isSubmitting,
      showResultMessage,
      submitSuccess,
      errorMessage,
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
      nextStep,
      prevStep,
      submitForm,
      checkMissingFields
    };
  }
};
</script>

<style scoped>
.form-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.form-title {
  margin-bottom: 20px;
  text-align: center;
}

.navigation-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

button {
  padding: 10px 20px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #45a049;
}
</style>