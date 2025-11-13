<template>
  <div class="grading-system-container">
    <div class="mb-8">
      <p class="text-gray-600">Configure your institution's grading system. This step is optional.</p>
    </div>

 <!-- Option Selection -->
  <div class="mb-8">
    <label class="block text-sm font-medium text-gray-700 mb-3">
      Select Grading System Option
    </label>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Use Previous Grading Scale -->
      <div 
        @click="selectOption('previous')"
        :class="[
          'p-6 border-2 rounded-lg cursor-pointer transition-all duration-200',
          selectedOption === 'previous'
            ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200'
            : 'border-gray-300 bg-white hover:border-gray-400'
        ]"
      >
        <div class="flex items-start space-x-4">
          <div class="flex-shrink-0 w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div class="flex-1">
            <h4 class="font-semibold text-gray-900 mb-2">Use Existing Grading Scale</h4>
            <p class="text-sm text-gray-600 mb-3">Select from previously created grading scales</p>
            
            <select
              v-model="previousScaleName"
              @change="onScaleSelect"
              :disabled="selectedOption !== 'previous'"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 mb-3"
              :class="{ 'bg-gray-100': selectedOption !== 'previous' }"
            >
              <option value="">Select a grading scale</option>
              <option v-for="scale in gradingScales" :key="scale.name" :value="scale.name">
                {{ scale.grading_scale_name }}
              </option>
            </select>
            
            <div v-if="loadingScales" class="mt-2 text-sm text-gray-500">
              Loading grading scales...
            </div>
            <div v-else-if="gradingScales.length === 0" class="mt-2 text-sm text-gray-500">
              No previous grading scales found
            </div>
          </div>
        </div>
      </div>

      <!-- Create New Grading Scale -->
      <div 
        @click="selectOption('manual')"
        :class="[
          'p-6 border-2 rounded-lg cursor-pointer transition-all duration-200',
          selectedOption === 'manual'
            ? 'border-green-500 bg-green-50 ring-2 ring-green-200'
            : 'border-gray-300 bg-white hover:border-gray-400'
        ]"
      >
        <div class="flex items-start space-x-4">
          <div class="flex-shrink-0 w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
          </div>
          <div class="flex-1">
            <h4 class="font-semibold text-gray-900 mb-2">Create New Grading Scale</h4>
            <p class="text-sm text-gray-600">Manually define your grading system</p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Grading Scale Preview (Now outside the option cards) -->
  <div v-if="selectedOption === 'previous' && selectedScalePreview" class="mb-8">
    <div class="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <h5 class="text-lg font-semibold text-gray-800">Preview: {{ selectedScalePreview.grading_scale_name }}</h5>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Grade Code</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Threshold (%)</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="(grade, index) in selectedScalePreview.grades" 
                :key="grade.grade_code" 
                class="hover:bg-gray-50 transition-colors">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ grade.grade_code }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-600">{{ grade.threshold }}% and above</div>
              </td>
              <td class="px-6 py-4">
                <div class="text-sm text-gray-500">{{ grade.description || 'No description' }}</div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="px-6 py-3 bg-gray-50 border-t border-gray-200">
        <div class="text-xs text-gray-500">
          {{ selectedScalePreview.grade_count }} grades • 
          Updated {{ formatDate(selectedScalePreview.modified) }}
        </div>
      </div>
    </div>
  </div>

    <!-- Manual Grading Setup -->
    <div v-if="selectedOption === 'manual'" class="space-y-6">
      <!-- Grading Scale Name -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Grading Scale Name
          <span class="text-red-500">*</span>
        </label>
        <input
          v-model="scaleName"
          type="text"
          placeholder="e.g., Standard Grading Scale"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          :class="{ 'border-red-300': !scaleName && showValidation }"
        />
      </div>

      <!-- Quick Templates -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-3">
          Quick Templates (Optional)
        </label>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <button
            v-for="institute in filteredInstituteTypes"
            :key="institute.value"
            @click="applyTemplate(institute)"
            class="p-4 border border-gray-300 rounded-lg text-left bg-white hover:border-gray-400 transition-colors"
            :class="{ 'border-blue-500 bg-blue-50': isRecommendedTemplate(institute) }"
          >
            <div class="flex items-center space-x-3">
              <div class="flex-shrink-0 w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <div>
                <h4 class="font-medium text-gray-900">{{ institute.label }}</h4>
                <p class="text-xs text-gray-500 mt-1">{{ institute.grades.length }} pre-defined grades</p>
                <div v-if="isRecommendedTemplate(institute)" class="mt-1">
                  <span class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
                    <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Recommended for your institution
                  </span>
                </div>
              </div>
            </div>
          </button>
        </div>
      </div>

      <!-- Grading Table -->
      <div class="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <div class="flex items-center justify-between">
            <h4 class="text-lg font-semibold text-gray-800">Grading Scale</h4>
            <button
              @click="addGrade"
              class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center space-x-2 text-sm"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              <span>Add Grade</span>
            </button>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Grade Code</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Threshold (%)</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="(grade, index) in manualGrades" :key="index" class="hover:bg-gray-50 transition-colors">
                <td class="px-6 py-4 whitespace-nowrap">
                  <input
                    v-model="grade.grade_code"
                    type="text"
                    placeholder="e.g., A, B, C"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    @input="debouncedUpdate"
                  />
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center space-x-2">
                    <input
                      v-model="grade.threshold"
                      type="number"
                      min="0"
                      max="100"
                      step="0.1"
                      placeholder="0-100"
                      class="w-24 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      @input="debouncedUpdate"
                    />
                    <span class="text-gray-500 text-sm">%</span>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <input
                    v-model="grade.description"
                    type="text"
                    placeholder="e.g., Excellent, Good, Average"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    @input="debouncedUpdate"
                  />
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    @click="removeGrade(index)"
                    class="text-red-600 hover:text-red-900 p-2 rounded-lg hover:bg-red-50 transition-colors"
                    :disabled="manualGrades.length <= 1"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="manualGrades.length === 0" class="text-center py-12">
          <p class="text-gray-500 mb-4">No grades added yet.</p>
          <button
            @click="addGrade"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Add First Grade
          </button>
        </div>
      </div>

      <!-- Validation -->
      <div v-if="showValidation && hasManualValidationErrors" class="p-4 bg-red-50 border border-red-200 rounded-lg">
        <div class="flex items-center space-x-2 text-red-700">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span class="font-medium">Please fix the following issues:</span>
        </div>
        <ul class="mt-2 text-sm text-red-600 list-disc list-inside space-y-1">
          <li v-if="!scaleName">Grading scale name is required</li>
          <li v-if="!hasValidManualGrades">All grades must have a code and valid threshold (0-100)</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import { createResource } from 'frappe-ui';

export default {
  name: 'GradingSystem',
  emits: ['update-field', 'grading-completed'],
  props: {
    values: {
      type: Object,
      required: true
    }
  },
  setup(props, { emit }) {
    // Local state
    const selectedOption = ref(props.values.gradingSystem?.selectedOption || '');
    const scaleName = ref(props.values.gradingSystem?.scaleName || '');
    const previousScaleName = ref(props.values.gradingSystem?.previousScaleName || '');
    const manualGrades = ref(props.values.gradingSystem?.gradeData || [{ grade_code: '', threshold: '', description: '' }]);
    const gradingScales = ref([]);
    const selectedScalePreview = ref(null);
    const loadingScales = ref(false);
    const showValidation = ref(false);

    let updateTimeout = null;

    // Get institution type from parent component
    const institutionType = computed(() => {
      return props.values.selectedInstitution || 'school';
    });

    // API Resource for fetching grading scales
    const gradingScalesResource = createResource({
      url: 'school.al_ummah.api3.fetch_grading_scales',
      onSuccess: (data) => {
        if (data.success) {
          gradingScales.value = data.grading_scales || [];
          
          // If we have a previously selected scale, show its preview
          if (previousScaleName.value) {
            const selectedScale = gradingScales.value.find(scale => scale.name === previousScaleName.value);
            if (selectedScale) {
              selectedScalePreview.value = selectedScale;
            }
          }
        }
        loadingScales.value = false;
      },
      onError: (err) => {
        console.error('Error fetching grading scales:', err);
        loadingScales.value = false;
      }
    });

    // Templates
    const instituteTypes = ref([
      {
        value: 'school',
        label: 'School',
        description: 'Comprehensive grading system suitable for K-12 schools',
        grades: [
          { grade_code: 'A+', threshold: 95, description: 'Outstanding' },
          { grade_code: 'A', threshold: 90, description: 'Excellent' },
          { grade_code: 'B+', threshold: 85, description: 'Very Good' },
          { grade_code: 'B', threshold: 80, description: 'Good' },
          { grade_code: 'C+', threshold: 75, description: 'Above Average' },
          { grade_code: 'C', threshold: 70, description: 'Average' },
          { grade_code: 'D', threshold: 60, description: 'Below Average' },
          { grade_code: 'F', threshold: 0, description: 'Fail' }
        ]
      },
      {
        value: 'college',
        label: 'College/University',
        description: 'Standard grading system for higher education',
        grades: [
          { grade_code: 'A', threshold: 90, description: 'Excellent' },
          { grade_code: 'B', threshold: 80, description: 'Good' },
          { grade_code: 'C', threshold: 70, description: 'Satisfactory' },
          { grade_code: 'D', threshold: 60, description: 'Pass' },
          { grade_code: 'F', threshold: 0, description: 'Fail' }
        ]
      }
    ]);

    // Computed properties
    const filteredInstituteTypes = computed(() => {
      return instituteTypes.value;
    });

    const isRecommendedTemplate = (institute) => {
      return institute.value === institutionType.value;
    };

    const hasValidManualGrades = computed(() => {
      return manualGrades.value.length > 0 && 
             manualGrades.value.every(grade => 
               grade.grade_code?.trim() && 
               isValidThreshold(grade.threshold)
             );
    });

    const hasManualValidationErrors = computed(() => {
      return !scaleName.value || !hasValidManualGrades.value;
    });

    const isFormValid = computed(() => {
      if (selectedOption.value === 'previous') {
        return !!previousScaleName.value;
      } else if (selectedOption.value === 'manual') {
        return scaleName.value?.trim() && hasValidManualGrades.value;
      }
      return true; // No option selected is valid (skip)
    });

    // Methods
    function fetchGradingScales() {
      loadingScales.value = true;
      gradingScalesResource.fetch();
    }

    function selectOption(option) {
      selectedOption.value = option;
      
      if (option === 'manual') {
        selectedScalePreview.value = null;
        // Auto-apply template when selecting manual and no grades exist
        if (manualGrades.value.length === 1 && !manualGrades.value[0].grade_code) {
          const recommendedTemplate = instituteTypes.value.find(t => t.value === institutionType.value);
          if (recommendedTemplate) {
            applyTemplate(recommendedTemplate);
          }
        }
      }
      
      updateFormData();
    }

    function onScaleSelect() {
      if (previousScaleName.value) {
        const selectedScale = gradingScales.value.find(scale => scale.name === previousScaleName.value);
        selectedScalePreview.value = selectedScale || null;
      } else {
        selectedScalePreview.value = null;
      }
      updateFormData();
    }

    function applyTemplate(institute) {
      manualGrades.value = JSON.parse(JSON.stringify(institute.grades));
      if (!scaleName.value) {
        scaleName.value = `${institute.label} Grading Scale`;
      }
      updateFormData();
    }

    function addGrade() {
      manualGrades.value.push({ grade_code: '', threshold: '', description: '' });
      updateFormData();
    }

    function removeGrade(index) {
      if (manualGrades.value.length > 1) {
        manualGrades.value.splice(index, 1);
        updateFormData();
      }
    }

    function isValidThreshold(threshold) {
      const num = parseFloat(threshold);
      return !isNaN(num) && num >= 0 && num <= 100 && threshold !== '';
    }

    function formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      });
    }

    function debouncedUpdate() {
      clearTimeout(updateTimeout);
      updateTimeout = setTimeout(updateFormData, 300);
    }

    function updateFormData() {
      clearTimeout(updateTimeout);
      
      const gradeData = selectedOption.value === 'manual' 
        ? manualGrades.value
            .map(grade => ({
              grade_code: (grade.grade_code || '').trim(),
              threshold: parseFloat(grade.threshold) || 0,
              description: (grade.description || '').trim()
            }))
            .filter(grade => grade.grade_code && !isNaN(grade.threshold))
        : null;

      emit('update-field', {
        field: 'gradingSystem',
        value: {
          selectedOption: selectedOption.value,
          scaleName: scaleName.value,
          previousScaleName: previousScaleName.value,
          gradeData,
          selectedScaleData: selectedScalePreview.value
        }
      });
    }

    function handleSubmit() {
      if (selectedOption.value !== '') {
        showValidation.value = true;
        
        if (!isFormValid.value) {
          return;
        }
      }

      updateFormData();
      emit('grading-completed');
    }

    // Watch for institution type changes and auto-apply template if manual mode is selected
    watch(institutionType, (newType) => {
      if (selectedOption.value === 'manual' && manualGrades.value.length === 1 && !manualGrades.value[0].grade_code) {
        const recommendedTemplate = instituteTypes.value.find(t => t.value === newType);
        if (recommendedTemplate) {
          applyTemplate(recommendedTemplate);
        }
      }
    });

    onMounted(() => {
      fetchGradingScales();
      
      // Auto-apply template based on institution type if no grades are set
      if (selectedOption.value === 'manual' && manualGrades.value.length === 1 && !manualGrades.value[0].grade_code) {
        const recommendedTemplate = instituteTypes.value.find(t => t.value === institutionType.value);
        if (recommendedTemplate) {
          applyTemplate(recommendedTemplate);
        }
      }
      
      // Initial update
      updateFormData();
    });

    return {
      selectedOption,
      scaleName,
      previousScaleName,
      manualGrades,
      gradingScales,
      selectedScalePreview,
      loadingScales,
      instituteTypes,
      filteredInstituteTypes,
      showValidation,
      hasValidManualGrades,
      hasManualValidationErrors,
      isFormValid,
      isRecommendedTemplate,
      selectOption,
      onScaleSelect,
      applyTemplate,
      addGrade,
      removeGrade,
      handleSubmit,
      debouncedUpdate,
      formatDate
    };
  }
};
</script>

<style scoped>
.grading-system-container {
  max-width: 100%;
}

/* Ensure proper spacing in the preview section */
.space-y-2 > * {
  margin-bottom: 0.5rem;
}

/* Improve table responsiveness */
@media (max-width: 768px) {
  .overflow-x-auto {
    -webkit-overflow-scrolling: touch;
  }
}
</style>