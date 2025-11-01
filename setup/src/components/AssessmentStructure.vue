<template>
  <div class="assessment-structure-container">
    <!-- Header Section -->
    <div class="mb-8">
      <h3 class="text-xl font-bold text-gray-800 mb-2">Assessment Structure Setup</h3>
      <p class="text-gray-600">Configure your institution's assessment hierarchy as per Maharashtra education patterns. This step is optional.</p>
    </div>

    <!-- Template Selection -->
    <div class="mb-8">
      <label class="block text-sm font-medium text-gray-700 mb-4">
        Select Assessment Template
      </label>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <!-- Maharashtra School Template -->
        <div 
          @click="selectTemplate(assessmentTemplates[0])"
          :class="[
            'p-6 border-2 rounded-xl cursor-pointer transition-all duration-200 hover:shadow-md',
            formValues.selectedTemplate === 'maharashtra-school'
              ? 'border-green-500 bg-green-50 ring-2 ring-green-200 shadow-sm'
              : 'border-gray-300 bg-white hover:border-green-400'
          ]"
        >
          <div class="flex items-start space-x-4">
            <div class="flex-shrink-0 w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <svg class="w-7 h-7 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l9-5-9-5-9 5 9 5z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l9-5-9-5-9 5 9 5z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14v6l9-5-9-5-9 5 9 5z" />
              </svg>
            </div>
            <div class="flex-1">
              <h4 class="font-bold text-gray-900 mb-2 text-lg">Maharashtra State Board School</h4>
              <p class="text-gray-600 mb-3">As per Maharashtra State Board pattern with unit tests, prelims, and final exams</p>
              <div class="flex items-center text-sm text-green-600">
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                Includes Unit Tests, Prelims, Oral, Practical
              </div>
            </div>
          </div>
        </div>

        <!-- Maharashtra College Template -->
        <div 
          @click="selectTemplate(assessmentTemplates[1])"
          :class="[
            'p-6 border-2 rounded-xl cursor-pointer transition-all duration-200 hover:shadow-md',
            formValues.selectedTemplate === 'maharashtra-college'
              ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200 shadow-sm'
              : 'border-gray-300 bg-white hover:border-blue-400'
          ]"
        >
          <div class="flex items-start space-x-4">
            <div class="flex-shrink-0 w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <svg class="w-7 h-7 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <div class="flex-1">
              <h4 class="font-bold text-gray-900 mb-2 text-lg">Maharashtra University College</h4>
              <p class="text-gray-600 mb-3">As per Mumbai/Pune University pattern with internal assessments and semester exams</p>
              <div class="flex items-center text-sm text-blue-600">
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                Includes Internal Assessment, Semester Exams
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Editable Assessment Structure -->
    <div v-if="formValues.selectedTemplate" class="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
      <div class="px-4 sm:px-6 py-4 border-b border-gray-200 bg-gray-50">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <h4 class="text-lg font-semibold text-gray-800">Assessment Hierarchy</h4>
          <div class="flex flex-wrap gap-2">
            <button
              @click="addExamGroup"
              class="px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center space-x-2 text-sm"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              <span>Add Exam Group</span>
            </button>
          </div>
        </div>
      </div>

      <div class="p-4 sm:p-6">
        <!-- Exam Groups Tree -->
        <div class="space-y-6">
          <div 
            v-for="(examGroup, examGroupIndex) in formValues.examGroups" 
            :key="examGroupIndex"
            class="border border-gray-200 rounded-lg overflow-hidden"
          >
            <!-- Exam Group -->
            <div class="bg-gradient-to-r from-blue-50 to-blue-100 px-4 py-3 border-b border-blue-200">
              <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                <div class="flex items-center space-x-3">
                  <span class="text-blue-700 font-semibold text-sm">📁 EXAM GROUP</span>
                  <input
                    v-model="examGroup.examGroupName"
                    type="text"
                    placeholder="e.g., Unit Test 1, Half Yearly Exam"
                    class="px-3 py-2 border border-blue-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent w-full sm:w-64"
                    @input="debouncedUpdate"
                  />
                </div>
                <button
                  @click="removeExamGroup(examGroupIndex)"
                  class="text-red-600 hover:text-red-900 p-2 rounded-lg hover:bg-red-50 transition-colors self-start sm:self-center"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Subject Groups -->
            <div class="p-4 space-y-4">
              <div class="text-sm font-medium text-gray-700 mb-2">📚 SUBJECT GROUPS</div>
              
              <div 
                v-for="(subjectGroup, subjectGroupIndex) in examGroup.subjectGroups" 
                :key="subjectGroupIndex"
                class="ml-4 sm:ml-6 border-l-2 border-green-300 pl-3 sm:pl-4"
              >
                <div class="flex flex-col sm:flex-row sm:items-center gap-3 mb-3">
                  <input
                    v-model="subjectGroup.subjectGroupName"
                    type="text"
                    placeholder="e.g., Mathematics, Science"
                    class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    @input="debouncedUpdate"
                  />
                  <div class="flex gap-2">
                    <button
                      @click="addComponentGroup(examGroupIndex, subjectGroupIndex)"
                      class="px-3 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 flex items-center space-x-2 text-sm"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                      </svg>
                      <span class="hidden sm:inline">Add Component Group</span>
                    </button>
                    <button
                      @click="removeSubjectGroup(examGroupIndex, subjectGroupIndex)"
                      class="p-2 text-red-600 hover:text-red-900 rounded-lg hover:bg-red-50 transition-colors"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>

                <!-- Component Groups -->
                <div v-if="subjectGroup.componentGroups.length > 0" class="ml-4 sm:ml-6 space-y-4">
                  <div 
                    v-for="(componentGroup, componentGroupIndex) in subjectGroup.componentGroups" 
                    :key="componentGroupIndex"
                    class="border-l-2 border-purple-300 pl-3 sm:pl-4"
                  >
                    <div class="flex flex-col sm:flex-row sm:items-center gap-3 mb-2">
                      <div class="flex items-center space-x-2 flex-1">
                        <span class="text-purple-600 text-sm font-medium">📂</span>
                        <input
                          v-model="componentGroup.componentGroupName"
                          type="text"
                          placeholder="e.g., Written Section, Oral Section"
                          class="px-3 py-2 border border-purple-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent flex-1 text-sm"
                          @input="debouncedUpdate"
                        />
                      </div>
                      <div class="flex gap-2">
                        <button
                          @click="addCriteria(examGroupIndex, subjectGroupIndex, componentGroupIndex)"
                          class="px-3 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center space-x-2 text-sm"
                        >
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                          </svg>
                          <span class="hidden sm:inline">Add Criteria</span>
                        </button>
                        <button
                          @click="removeComponentGroup(examGroupIndex, subjectGroupIndex, componentGroupIndex)"
                          class="p-2 text-red-600 hover:text-red-900 rounded-lg hover:bg-red-50 transition-colors"
                        >
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    </div>

                    <!-- Criteria -->
                    <div v-if="componentGroup.criteria.length > 0" class="ml-4 sm:ml-6 space-y-2">
                      <div class="text-xs font-medium text-gray-600 mb-2">🎯 CRITERIA</div>
                      
                      <div 
                        v-for="(criteria, criteriaIndex) in componentGroup.criteria" 
                        :key="criteriaIndex"
                        class="flex items-center space-x-3 bg-gray-50 p-3 rounded-lg border border-gray-200"
                      >
                        <div class="flex items-center space-x-2 flex-1">
                          <span class="text-blue-500 text-lg">•</span>
                          <input
                            v-model="criteria.criteriaName"
                            type="text"
                            placeholder="e.g., MCQ, Short Answer, Long Answer"
                            class="flex-1 px-3 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm bg-white"
                            @input="debouncedUpdate"
                          />
                        </div>
                        <button
                          @click="removeCriteria(examGroupIndex, subjectGroupIndex, componentGroupIndex, criteriaIndex)"
                          class="p-1 text-red-600 hover:text-red-900 rounded hover:bg-red-100 transition-colors"
                        >
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Add Subject Group Button -->
            <div class="px-4 pb-4">
              <button
                @click="addSubjectGroup(examGroupIndex)"
                class="ml-4 sm:ml-6 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 flex items-center space-x-2 text-sm"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                <span>Add Subject Group</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="formValues.examGroups.length === 0" class="text-center py-8">
          <svg class="w-20 h-20 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="text-gray-500 mb-4 text-lg">No exam groups added yet</p>
          <button
            @click="addExamGroup"
            class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
          >
            Add First Exam Group
          </button>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="mt-8 flex flex-col sm:flex-row justify-between items-center gap-4 pt-6 border-t border-gray-200">
      <div class="text-sm text-gray-500 text-center sm:text-left">
        This step is optional. You can skip assessment structure setup.
      </div>
      <div class="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
        <button
          @click="skipAssessment"
          class="px-6 py-2 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
        >
          Skip Assessment
        </button>
        <button
          @click="submitAssessment"
          class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-sm"
        >
          Save & Continue
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';

export default {
  name: 'AssessmentStructure',
  emits: ['update-field', 'assessment-completed'],
  props: {
    values: {
      type: Object,
      required: true
    }
  },
  setup(props, { emit }) {
    // Local state
    const formValues = ref({
      selectedTemplate: props.values.assessmentStructure?.selectedTemplate || '',
      examGroups: props.values.assessmentStructure?.examGroups || []
    });

    let updateTimeout = null;

    // Maharashtra-specific Assessment Templates
    const assessmentTemplates = ref([
      {
        value: 'maharashtra-school',
        label: 'Maharashtra State Board School',
        description: 'As per Maharashtra State Board pattern',
        template: [
          {
            examGroupName: 'Unit Test 1',
            subjectGroups: [
              { 
                subjectGroupName: 'Mathematics',
                componentGroups: [
                  {
                    componentGroupName: 'Written Section',
                    criteria: [
                      { criteriaName: 'MCQ' },
                      { criteriaName: 'Short Answer' },
                      { criteriaName: 'Long Answer' }
                    ]
                  },
                  {
                    componentGroupName: 'Oral Section',
                    criteria: [
                      { criteriaName: 'Viva' }
                    ]
                  }
                ]
              }
            ]
          },
          {
            examGroupName: 'Half Yearly Exam',
            subjectGroups: [
              { 
                subjectGroupName: 'Science',
                componentGroups: [
                  {
                    componentGroupName: 'Practical Section',
                    criteria: [
                      { criteriaName: 'Experiment' },
                      { criteriaName: 'Journal' },
                      { criteriaName: 'Activity' }
                    ]
                  }
                ]
              }
            ]
          }
        ]
      },
      {
        value: 'maharashtra-college',
        label: 'Maharashtra University College',
        description: 'As per Mumbai/Pune University pattern',
        template: [
          {
            examGroupName: 'Semester I',
            subjectGroups: [
              { 
                subjectGroupName: 'Computer Science',
                componentGroups: [
                  {
                    componentGroupName: 'Theory Paper',
                    criteria: [
                      { criteriaName: 'Section A - Objective' },
                      { criteriaName: 'Section B - Descriptive' }
                    ]
                  },
                  {
                    componentGroupName: 'Practical Exam',
                    criteria: [
                      { criteriaName: 'Programming Lab' },
                      { criteriaName: 'Viva Voce' }
                    ]
                  }
                ]
              }
            ]
          }
        ]
      }
    ]);

    // Methods
    function selectTemplate(template) {
      formValues.value.selectedTemplate = template.value;
      formValues.value.examGroups = JSON.parse(JSON.stringify(template.template));
      updateFormData();
    }

    function addExamGroup() {
      formValues.value.examGroups.push({
        examGroupName: 'New Exam Group',
        subjectGroups: []
      });
      updateFormData();
    }

    function removeExamGroup(examGroupIndex) {
      formValues.value.examGroups.splice(examGroupIndex, 1);
      updateFormData();
    }

    function addSubjectGroup(examGroupIndex) {
      formValues.value.examGroups[examGroupIndex].subjectGroups.push({
        subjectGroupName: 'New Subject Group',
        componentGroups: []
      });
      updateFormData();
    }

    function removeSubjectGroup(examGroupIndex, subjectGroupIndex) {
      formValues.value.examGroups[examGroupIndex].subjectGroups.splice(subjectGroupIndex, 1);
      updateFormData();
    }

    function addComponentGroup(examGroupIndex, subjectGroupIndex) {
      formValues.value.examGroups[examGroupIndex].subjectGroups[subjectGroupIndex].componentGroups.push({
        componentGroupName: 'New Component Group',
        criteria: []
      });
      updateFormData();
    }

    function removeComponentGroup(examGroupIndex, subjectGroupIndex, componentGroupIndex) {
      formValues.value.examGroups[examGroupIndex].subjectGroups[subjectGroupIndex].componentGroups.splice(componentGroupIndex, 1);
      updateFormData();
    }

    function addCriteria(examGroupIndex, subjectGroupIndex, componentGroupIndex) {
      formValues.value.examGroups[examGroupIndex].subjectGroups[subjectGroupIndex].componentGroups[componentGroupIndex].criteria.push({
        criteriaName: 'New Criteria'
      });
      updateFormData();
    }

    function removeCriteria(examGroupIndex, subjectGroupIndex, componentGroupIndex, criteriaIndex) {
      formValues.value.examGroups[examGroupIndex].subjectGroups[subjectGroupIndex].componentGroups[componentGroupIndex].criteria.splice(criteriaIndex, 1);
      updateFormData();
    }

    function debouncedUpdate() {
      clearTimeout(updateTimeout);
      updateTimeout = setTimeout(updateFormData, 300);
    }

    function updateFormData() {
      clearTimeout(updateTimeout);
      emit('update-field', {
        field: 'assessmentStructure',
        value: { ...formValues.value }
      });
    }

    function submitAssessment() {
      updateFormData();
      emit('assessment-completed');
    }

    function skipAssessment() {
      formValues.value.selectedTemplate = '';
      formValues.value.examGroups = [];
      updateFormData();
      emit('assessment-completed');
    }

    onMounted(() => {
      updateFormData();
    });

    return {
      formValues,
      assessmentTemplates,
      selectTemplate,
      addExamGroup,
      removeExamGroup,
      addSubjectGroup,
      removeSubjectGroup,
      addComponentGroup,
      removeComponentGroup,
      addCriteria,
      removeCriteria,
      debouncedUpdate,
      submitAssessment,
      skipAssessment
    };
  }
};
</script>

<style scoped>
.assessment-structure-container {
  max-width: 100%;
}

/* Custom tree lines for better visual hierarchy */
.tree-line {
  position: relative;
}

.tree-line::before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: -1rem;
  width: 2px;
  background: linear-gradient(to bottom, transparent 10%, #d1d5db 10%, #d1d5db 90%, transparent 90%);
}

.tree-line::after {
  content: '';
  position: absolute;
  top: 50%;
  left: -1rem;
  width: 0.75rem;
  height: 2px;
  background: #d1d5db;
}

/* Focus styles for better accessibility */
input:focus {
  outline: none;
  ring: 2px;
}

/* Smooth transitions */
* {
  transition: all 0.2s ease-in-out;
}

/* Responsive design improvements */
@media (max-width: 640px) {
  .assessment-structure-container {
    padding: 0 0.5rem;
  }
  
  .ml-4 {
    margin-left: 0.5rem;
  }
  
  .ml-6 {
    margin-left: 1rem;
  }
  
  .pl-3 {
    padding-left: 0.75rem;
  }
  
  .pl-4 {
    padding-left: 1rem;
  }
}

/* Better mobile touch targets */
button {
  min-height: 44px;
  min-width: 44px;
}

/* Improved input responsiveness */
input {
  min-height: 44px;
}

/* Custom scrollbar for better UX */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>