<template>
  <div class="bg-white shadow rounded-lg p-6 space-y-6">
    <!-- Institution Type Picker -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2">Institution Type</label>
      <div class="flex space-x-4">
        <button
          @click="setInstitutionType('school')"
          class="px-4 py-2 rounded-md transition-colors"
          :class="institutionType === 'school' 
            ? 'bg-blue-500 text-white shadow-md' 
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
        >
          🏫 School
        </button>
        <button
          @click="setInstitutionType('college')"
          class="px-4 py-2 rounded-md transition-colors"
          :class="institutionType === 'college' 
            ? 'bg-blue-500 text-white shadow-md' 
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
        >
          🎓 College
        </button>
      </div>
    </div>

    <!-- Common Subjects Section (School Only) -->
    <div v-if="institutionType === 'school'">
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Common Subjects for All Classes
      </label>
      <div class="flex flex-wrap items-center gap-2 p-2 border border-gray-300 rounded-md min-h-[42px]">
        <span 
          v-for="(subject, idx) in commonSubjectsList" 
          :key="idx"
          class="inline-flex items-center px-3 py-1 rounded-full bg-blue-100 text-blue-800 text-sm"
        >
          {{ subject }}
          <button 
            @click="removeCommonSubject(idx)"
            class="ml-1.5 text-blue-500 hover:text-blue-700"
          >
            ×
          </button>
        </span>
        <input
          type="text"
          v-model="newCommonSubject"
          @keydown.enter="addCommonSubject"
          @blur="addCommonSubject"
          placeholder="Add subjects..."
          class="flex-1 min-w-[100px] px-2 py-1 border-0 focus:ring-0 focus:outline-none"
        />
      </div>

      <!-- Quick Select Subjects Widget -->
      <div class="quick-select mt-3">
        <h3 class="text-sm font-medium text-gray-700 mb-2">Quick Select Subjects</h3>
        <div class="subject-grid grid grid-cols-3 gap-2">
          <div 
            v-for="subject in commonSubjects" 
            :key="subject"
            class="subject-card px-3 py-2 border rounded-md text-center cursor-pointer text-sm"
            :class="{ 
              'bg-blue-100 border-blue-300': isCommonSubjectSelected(subject),
              'bg-gray-50 hover:bg-gray-100': !isCommonSubjectSelected(subject)
            }"
            @click="toggleCommonSubject(subject)"
          >
            {{ subject }}
          </div>
        </div>
      </div>
    </div>

    <!-- Common Divisions Section (Both School and College) -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        {{ institutionType === 'college' ? 'Common Student Groups for All Programs' : 'Common Divisions for All Classes' }}
      </label>
      <div class="flex flex-wrap items-center gap-2 p-2 border border-gray-300 rounded-md min-h-[42px]">
        <span 
          v-for="(division, idx) in commonDivisionsList" 
          :key="idx"
          class="inline-flex items-center px-3 py-1 rounded-full bg-green-100 text-green-800 text-sm"
        >
          {{ division }}
          <button 
            @click="removeCommonDivision(idx)"
            class="ml-1.5 text-green-500 hover:text-green-700"
          >
            ×
          </button>
        </span>
        <input
          type="text"
          v-model="newCommonDivision"
          @keydown.enter="addCommonDivision"
          @blur="addCommonDivision"
          :placeholder="institutionType === 'college' ? 'Add common groups...' : 'Add common divisions...'"
          class="flex-1 min-w-[100px] px-2 py-1 border-0 focus:ring-0 focus:outline-none"
        />
      </div>

      <!-- Quick Select Divisions Widget -->
      <div class="quick-select mt-3">
        <h3 class="text-sm font-medium text-gray-700 mb-2">
          {{ institutionType === 'college' ? 'Quick Select Common Groups' : 'Quick Select Common Divisions' }}
        </h3>
        <div class="division-grid grid grid-cols-6 gap-2">
          <div 
            v-for="division in quickSelectDivisions" 
            :key="division"
            class="division-card px-3 py-2 border rounded-md text-center cursor-pointer text-sm"
            :class="{ 
              'bg-green-100 border-green-300': isCommonDivisionSelected(division),
              'bg-gray-50 hover:bg-gray-100': !isCommonDivisionSelected(division)
            }"
            @click="toggleCommonDivision(division)"
          >
            {{ division }}
          </div>
        </div>
      </div>
    </div>

    <!-- Program Management -->
    <div class="flex justify-between items-center mb-4">
      <h3 class="text-lg font-semibold text-gray-800">
        {{ institutionType === 'college' ? 'Programs Overview' : 'Classes Overview' }}
      </h3>
      <button
        @click="addNewProgram"
        class="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors flex items-center gap-2"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
        </svg>
        Add {{ institutionType === 'college' ? 'Program' : 'Class' }}
      </button>
    </div>

    <!-- Select All Checkbox for Single Group -->
    <div v-if="institutionType === 'college'" class="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
      <label class="flex items-center gap-3 text-sm font-medium text-gray-700 cursor-pointer">
        <div class="relative">
          <input
            type="checkbox"
            :checked="allSingleGroup"
            @change="toggleAllSingleGroup"
            class="sr-only"
          />
          <div class="w-5 h-5 border-2 border-blue-500 rounded transition-all duration-200 flex items-center justify-center"
            :class="allSingleGroup ? 'bg-blue-500 border-blue-500' : 'bg-white border-gray-300'">
            <svg v-if="allSingleGroup" class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
            </svg>
          </div>
        </div>
        <span class="text-blue-800">Select All - Single Student Group (Uses Program Name)</span>
      </label>
    </div>

    <!-- Responsive Table -->
    <div class="overflow-x-auto">
      <table class="min-w-full text-sm text-left text-gray-700">
        <thead class="bg-gray-100">
          <tr>
            <th class="px-4 py-2 font-medium">#</th>
            <th class="px-4 py-2 font-medium">
              {{ institutionType === 'college' ? 'Program Name' : 'Class Name' }}
            </th>
            <th class="px-4 py-2 font-medium">
              {{ institutionType === 'college' ? 'Courses' : 'Subjects' }}
            </th>
            <th class="px-4 py-2 font-medium">
              {{ institutionType === 'college' ? 'Student Groups' : 'Divisions' }}
            </th>
            <th class="px-4 py-2 font-medium">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(cls, index) in classesWithText"
            :key="cls.uniqueId"
            :ref="el => { programRefs[cls.uniqueId] = el }"
            class="border-t hover:bg-gray-50"
          >
            <td class="px-4 py-2">{{ index + 1 }}</td>
            
            <!-- Program/Class Name -->
            <td class="px-4 py-2">
              <input
                type="text"
                v-model="cls.className"
                @input="updateClassName(index, $event.target.value)"
                :ref="el => { inputRefs[cls.uniqueId] = el }"
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
                :placeholder="institutionType === 'college' ? 'Program name...' : 'Class name...'"
              />
            </td>
            
            <!-- Subjects/Courses -->
            <td class="px-4 py-2 w-[300px]">
              <div class="flex flex-wrap gap-1 mb-1 min-h-[40px]">
                <!-- Common subjects (School only) -->
                <span 
                  v-for="(subject, subIdx) in commonSubjectsList" 
                  v-if="institutionType === 'school'"
                  :key="'common-'+subIdx"
                  class="inline-flex items-center px-2 py-1 rounded-full text-xs"
                  :class="isCommonSubjectExcluded(index, subject)
                    ? 'bg-red-100 text-red-600'
                    : 'bg-blue-50 text-blue-600'"
                >
                  {{ subject }}
                  <button 
                    @click.stop="toggleExcludeCommonSubject(index, subject)"
                    class="ml-1 text-blue-500 hover:text-blue-700 text-xs"
                  >
                    {{ isCommonSubjectExcluded(index, subject) ? '+' : '×' }}
                  </button>
                </span>
                <!-- Class-specific subjects -->
                <span 
                  v-for="(subject, subIdx) in cls.specificSubjects" 
                  :key="'specific-'+subIdx"
                  class="inline-flex items-center px-2 py-1 rounded-full bg-blue-100 text-blue-800 text-xs"
                >
                  {{ subject }}
                  <button 
                    @click="removeSpecificSubject(index, subIdx)"
                    class="ml-1 text-blue-500 hover:text-blue-700 text-xs"
                  >
                    ×
                  </button>
                </span>
              </div>
              <div class="flex gap-2">
                <input
                  type="text"
                  v-model="cls.subjectsText"
                  @keydown.enter="addSpecificSubject(index)"
                  :placeholder="institutionType === 'college' ? 'Add course...' : 'Add subject...'"
                  class="flex-1 px-2 py-1 border border-gray-300 rounded text-xs"
                />
                <button
                  @click="addSpecificSubject(index)"
                  class="px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 text-xs"
                >
                  Add
                </button>
              </div>
              
              <!-- Quick Select Subjects for Mapped College Programs -->
              <div v-if="institutionType === 'college' && hasMappedSubjects(cls.className)" class="mt-2">
                <div class="flex flex-wrap gap-1">
                  <button
                    v-for="subject in getMappedSubjects(cls.className)"
                    :key="subject"
                    @click="addProgramSubject(index, subject)"
                    :disabled="cls.specificSubjects.includes(subject)"
                    class="px-2 py-1 text-xs rounded border transition-colors"
                    :class="cls.specificSubjects.includes(subject)
                      ? 'bg-blue-500 text-white border-blue-500 cursor-not-allowed'
                      : 'bg-gray-100 hover:bg-gray-200 border-gray-300'"
                  >
                    {{ cls.specificSubjects.includes(subject) ? '✓ ' : '+ ' }}{{ subject }}
                  </button>
                </div>
                <!-- Add All Button -->
                <button
                  v-if="hasMappedSubjects(cls.className) && getMappedSubjects(cls.className).some(sub => !cls.specificSubjects.includes(sub))"
                  @click="addAllMappedSubjects(index, cls.className)"
                  class="mt-1 px-2 py-1 text-xs bg-green-500 text-white rounded hover:bg-green-600 transition-colors"
                >
                  Add All Subjects for {{ cls.className }}
                </button>
              </div>
            </td>
            
            <!-- Divisions/Student Groups -->
            <td class="px-4 py-2">
              <!-- Single Group Checkbox (College only) -->
              <div v-if="institutionType === 'college'" class="mb-2">
                <label class="flex items-center gap-2 text-xs text-gray-700 cursor-pointer">
                  <div class="relative">
                    <input
                      type="checkbox"
                      v-model="cls.isSingleGroup"
                      @change="handleSingleGroupChange(index)"
                      class="sr-only"
                    />
                    <div class="w-4 h-4 border-2 border-blue-500 rounded transition-all duration-200 flex items-center justify-center"
                      :class="cls.isSingleGroup ? 'bg-blue-500 border-blue-500' : 'bg-white border-gray-300'">
                      <svg v-if="cls.isSingleGroup" class="w-2.5 h-2.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                  </div>
                  Single Student Group
                </label>
              </div>

              <div class="flex flex-wrap gap-1 mb-1 min-h-[40px]">
                <!-- Single Group Display (when enabled) -->
                <span 
                  v-if="cls.isSingleGroup && institutionType === 'college'"
                  class="inline-flex items-center px-2 py-1 rounded-full bg-gray-200 text-gray-700 text-xs border border-gray-300 cursor-not-allowed"
                >
                  {{ cls.className }}
                  <span class="ml-1 text-gray-500 text-xs">(Auto)</span>
                </span>
                
                <!-- Common divisions (when not single group) -->
                <span 
                  v-for="(division, divIdx) in commonDivisionsList" 
                  v-if="!cls.isSingleGroup"
                  :key="'common-'+divIdx"
                  class="inline-flex items-center px-2 py-1 rounded-full text-xs"
                  :class="isCommonDivisionExcluded(index, division) 
                    ? 'bg-red-100 text-red-600 border border-red-300' 
                    : 'bg-green-50 text-green-600'"
                >
                  {{ division }}
                  <button 
                    @click.stop="toggleExcludeCommonDivision(index, division)"
                    class="ml-1 text-green-500 hover:text-green-700 text-xs"
                  >
                    {{ isCommonDivisionExcluded(index, division) ? '+' : '×' }}
                  </button>
                </span>
                
                <!-- Class-specific divisions (when not single group) -->
                <span 
                  v-for="(division, divIdx) in cls.specificDivisions" 
                  v-if="!cls.isSingleGroup"
                  :key="'specific-'+divIdx"
                  class="inline-flex items-center px-2 py-1 rounded-full bg-green-100 text-green-800 text-xs"
                >
                  {{ getDivisionDisplayName(division, index) }}
                  <button 
                    @click="removeSpecificDivision(index, divIdx)"
                    class="ml-1 text-green-500 hover:text-green-700 text-xs"
                  >
                    ×
                  </button>
                </span>
              </div>
              
              <!-- Division Input (when not single group) -->
              <div v-if="!cls.isSingleGroup" class="flex gap-2">
                <input
                  type="text"
                  v-model="cls.divisionsText"
                  @keydown.enter="addSpecificDivision(index)"
                  :placeholder="institutionType === 'college' ? 'Add custom group...' : 'Add custom division...'"
                  class="flex-1 px-2 py-1 border border-gray-300 rounded text-xs"
                />
                <button
                  @click="addSpecificDivision(index)"
                  class="px-2 py-1 bg-green-500 text-white rounded hover:bg-green-600 text-xs"
                >
                  Add
                </button>
              </div>

              <!-- Warning message when single group is enabled -->
              <div v-if="cls.isSingleGroup && institutionType === 'college'" class="mt-1">
                <p class="text-xs text-gray-500 italic">
                  Student group is automatically set to program name and cannot be modified.
                </p>
              </div>
            </td>

            <!-- Remove Program Button -->
            <td class="px-4 py-2">
              <button
                @click="removeProgram(index)"
                class="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-md transition-colors"
                title="Remove Program"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div v-if="classesWithText.length === 0" class="text-center py-8 text-gray-500">
      <p>No {{ institutionType === 'college' ? 'programs' : 'classes' }} added yet.</p>
      <button
        @click="addNewProgram"
        class="mt-2 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
      >
        Add Your First {{ institutionType === 'college' ? 'Program' : 'Class' }}
      </button>
    </div>
  </div>
</template>

<script>
const PROGRAM_NAMES = {
  school: [
    "Nursery", "Jr KG", "Sr KG", "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th"
  ],
  college: [
    "FY BSc-CS", "SY BSc-CS", "TY BSc-CS", "Final Year BSc-CS",
    "FY BCA", "SY BCA", "TY BCA", "Final Year BCA",
    "FY BSc-IT", "SY BSc-IT", "TY BSc-IT", "Final Year BSc-IT",
    "FY BBA", "SY BBA", "TY BBA", "Final Year BBA",
    "FY BCom", "SY BCom", "TY BCom", "Final Year BCom",
    "FY MSc-CS", "SY MSc-CS",
    "FY MBA", "SY MBA",
    "FY MCom", "SY MCom"
  ]
};

const COLLEGE_PROGRAMS_SUBJECTS = {
  "FY BSc-CS": [
    "Programming in C",
    "Discrete Mathematics",
    "Computer Architecture",
    "Operating Systems Basics",
    "Digital Electronics"
  ],
  "SY BSc-CS": [
    "Data Structures",
    "DBMS",
    "Computer Networks",
    "Web Technologies",
    "Java Programming"
  ],
  "TY BSc-CS": [
    "Software Engineering",
    "Computer Graphics",
    "Information Security",
    "Distributed Systems",
    "Elective – AI / ML / IoT"
  ],
  "Final Year BSc-CS": [
    "Cloud Computing",
    "Advanced Algorithms",
    "Data Warehousing & Mining",
    "Project Work",
    "Seminar"
  ],

  "FY BCA": [
    "Fundamentals of IT",
    "Mathematics",
    "C Programming",
    "Business Communication",
    "PC Software"
  ],
  "SY BCA": [
    "Data Structures",
    "DBMS",
    "Operating Systems",
    "OOP with C++",
    "Networking"
  ],
  "TY BCA": [
    "Web Development",
    "Software Engineering",
    "Java Programming",
    "Computer Security",
    "Mini Project"
  ],
  "Final Year BCA": [
    "Cloud Computing",
    "Mobile App Development",
    "Advanced Web Tech",
    "Major Project",
    "Internship"
  ],

  "FY BSc-IT": [
    "Basic Electronics",
    "C Programming",
    "Mathematics",
    "IT Fundamentals",
    "Web Design"
  ],
  "SY BSc-IT": [
    "OOP Java",
    "DBMS",
    "Networks",
    "OS Concepts",
    "Statistics"
  ],
  "TY BSc-IT": [
    "Software Engineering",
    "Internet of Things",
    "Cloud Computing",
    "Cyber Security",
    "Mini Project"
  ],
  "Final Year BSc-IT": [
    "Big Data",
    "Advanced Security",
    "Mobile Computing",
    "Project Work",
    "Seminar"
  ],

  "FY BBA": [
    "Business Management",
    "Microeconomics",
    "Business Mathematics",
    "Marketing Principles",
    "Communication Skills"
  ],
  "SY BBA": [
    "Human Resource Management",
    "Finance Management",
    "Organizational Behavior",
    "Business Law",
    "Operations Management"
  ],
  "TY BBA": [
    "International Business",
    "Entrepreneurship",
    "Research Methodology",
    "Strategic Management",
    "Taxation"
  ],
  "Final Year BBA": [
    "Project Work",
    "Advanced HRM / Marketing / Finance",
    "Business Ethics",
    "Corporate Governance",
    "Internship"
  ],

  "FY BCom": [
    "Financial Accounting",
    "Business Economics",
    "Mathematics & Statistics",
    "Commerce",
    "Business Communication"
  ],
  "SY BCom": [
    "Corporate Accounting",
    "Cost Accounting",
    "Business Law",
    "Banking & Finance",
    "Marketing"
  ],
  "TY BCom": [
    "Auditing",
    "Taxation",
    "Financial Management",
    "E-Commerce",
    "Business Environment"
  ],
  "Final Year BCom": [
    "Advanced Accounting",
    "Corporate Finance",
    "Research Project",
    "GST & Auditing",
    "Entrepreneurship"
  ],

  "FY MSc-CS": [
    "Advanced Algorithms",
    "Advanced DBMS",
    "Machine Learning Basics",
    "Data Science with Python",
    "Research Methodology"
  ],
  "SY MSc-CS": [
    "Deep Learning",
    "Distributed Computing",
    "Big Data Analytics",
    "Cyber Security",
    "Thesis"
  ],

  "FY MBA": [
    "Principles of Management",
    "Managerial Economics",
    "Accounting for Managers",
    "Marketing Management",
    "Organizational Behavior"
  ],
  "SY MBA": [
    "Financial Management",
    "Business Analytics",
    "Operations Research",
    "Strategic Management",
    "Major Project / Internship"
  ],

  "FY MCom": [
    "Managerial Accounting",
    "Advanced Economics",
    "Corporate Finance",
    "Taxation Laws",
    "Research Methods"
  ],
  "SY MCom": [
    "Advanced Auditing",
    "International Finance",
    "Business Analytics",
    "Corporate Governance",
    "Thesis / Project"
  ]
};

export default {
  props: {
    values: Object
  },
  data() {
    return {
      isUpdatingClasses: false,
      commonSubjectsList: [],
      commonDivisionsList: [],
      newCommonSubject: '',
      newCommonDivision: '',
      classesWithText: [],
      collegeProgramsSubjects: COLLEGE_PROGRAMS_SUBJECTS,
      programRefs: {},
      inputRefs: {},
      quickSelectDivisions: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
      
      // School subjects from old code
      commonSubjects: [
        'Math', 'Social Studies', 'Science', 'English',
        'History', 'Geography', 'Physics',
        'Chemistry', 'Biology', 'Computer',
        'Civics', 'Hindi', 'Marathi',
        'Arabic', 'Play'
      ]
    }
  },
  computed: {
    institutionType: {
      get() {
        return this.values.selectedInstitution || 'school';
      },
      set(value) {
        this.updateField('selectedInstitution', value);
      }
    },
    allSingleGroup() {
      return this.classesWithText.length > 0 && 
             this.classesWithText.every(cls => cls.isSingleGroup);
    },
    mappedProgramNames() {
      return Object.keys(this.collegeProgramsSubjects);
    }
  },
  watch: {
    'values.selectedInstitution': {
      immediate: true,
      handler(newInstitution) {
        // If institution is not set, set it to default 'school'
        if (!newInstitution) {
          this.updateField('selectedInstitution', 'school');
        }
      }
    },
    'values.commonDivisions': {
      immediate: true,
      handler(newCommonDivisions) {
        if (this.isUpdatingClasses) return;
        if (newCommonDivisions && newCommonDivisions.length > 0) {
          this.commonDivisionsList = [...newCommonDivisions];
          if (this.values.classes && this.values.classes.length > 0) {
            this.initializeClassesWithText(this.values.classes);
          }
        }
      }
    },
    
    'values.commonSubjects': {
      immediate: true,
      handler(newCommonSubjects) {
        if (this.isUpdatingClasses) return;
        if (newCommonSubjects && newCommonSubjects.length > 0) {
          this.commonSubjectsList = [...newCommonSubjects];
          if (this.values.classes && this.values.classes.length > 0) {
            this.initializeClassesWithText(this.values.classes);
          }
        }
      }
    },
    
    'values.classes': {
      immediate: true,
      deep: true,
      handler(classes) {
        if (this.isUpdatingClasses) return;
        this.initializeClassesWithText(classes);
      }
    },
    
    commonSubjectsList: {
      handler(newVal) {
        this.$emit('update-field', {
          field: 'commonSubjects',
          value: newVal
        });
        this.updateAllClassesWithCommonData();
      },
      deep: true
    },
    commonDivisionsList: {
      handler(newVal) {
        this.$emit('update-field', {
          field: 'commonDivisions',
          value: newVal
        });
        this.updateAllClassesWithCommonData();
      },
      deep: true
    }
  },
  created() {
   // FIX: Ensure institution type is set to 'school' by default
    if (!this.values.selectedInstitution) {
      this.updateField('selectedInstitution', 'school');
    }

    // Initialize with prop values if they exist - WITH FALLBACKS
    if (this.values.commonSubjects && this.values.commonSubjects.length > 0) {
      this.commonSubjectsList = [...this.values.commonSubjects];
    } else {
      this.commonSubjectsList = [];
    }

    if (this.values.commonDivisions && this.values.commonDivisions.length > 0) {
      this.commonDivisionsList = [...this.values.commonDivisions];
    } else {
      // CHANGED: Empty array instead of default divisions
      this.commonDivisionsList = [];
    }

    // Force update classes if they exist
    if (this.values.classes && this.values.classes.length > 0) {
      this.initializeClassesWithText(this.values.classes);
    }
  },
  mounted() {
    // Only auto-populate if we don't have matching data
    if (this.classesWithText.length === 0 && !this.hasPreviousData()) {
      this.autoPopulatePrograms();
    }
  },
  methods: {
    generateUniqueId() {
      return Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
    },
    
    updateField(field, value) {
      this.$emit('update-field', { field, value });
    },

    // Helper to check if current classes match the institution type
    classesMatchInstitutionType() {
      if (!this.classesWithText || this.classesWithText.length === 0) {
        return false;
      }
      
      const currentClassNames = this.classesWithText.map(cls => cls.className);
      const expectedNames = PROGRAM_NAMES[this.institutionType] || [];
      
      // Check if any of our current classes match the expected names for this institution
      const hasMatching = currentClassNames.some(name => expectedNames.includes(name));
      
      return hasMatching;
    },

    // Force refresh the display
    forceRefreshDisplay() {
      if (this.values.classes && this.values.classes.length > 0) {
        this.initializeClassesWithText(this.values.classes);
      }
    },

    // Helper method to check if we have previous data for the CURRENT institution type
    hasPreviousData() {
      if (this.classesWithText.length === 0) {
        // Initial load - check if we have matching data
        if (!this.values.classes || this.values.classes.length === 0) {
          return false;
        }
        
        // Check if we have data that matches the current institution type
        const hasMatchingData = this.values.classes.some(cls => {
          // For school: check if class name matches school pattern
          if (this.institutionType === 'school') {
            return PROGRAM_NAMES.school.includes(cls.className);
          }
          // For college: check if class name matches college pattern
          else if (this.institutionType === 'college') {
            return PROGRAM_NAMES.college.includes(cls.className);
          }
          return false;
        });
        
        return hasMatchingData;
      } else {
        // We already have classes displayed - this is a switch, so don't prevent population
        return false;
      }
    },

    setInstitutionType(type) {
      // Update the institution type first
      this.institutionType = type;
      
      // Clear current classes - we want fresh data for the new institution type
      this.classesWithText = [];
      
      // Force clear the parent's classes too
      this.$emit('update-field-array', {
        field: 'classes',
        value: []
      });
      
      // Use a small delay to ensure the institution type is updated before populating
      this.$nextTick(() => {
        this.autoPopulatePrograms();
        
        // Force refresh after a bit to ensure everything is synced
        setTimeout(() => {
          this.forceRefreshDisplay();
        }, 200);
      });
    },

    // Common Subjects Methods (School only)
    addCommonSubject() {
      if (this.newCommonSubject.trim() && !this.commonSubjectsList.includes(this.newCommonSubject.trim())) {
        this.commonSubjectsList.push(this.newCommonSubject.trim());
        this.newCommonSubject = '';
      }
    },
    removeCommonSubject(index) {
      this.commonSubjectsList.splice(index, 1);
    },
    isCommonSubjectSelected(subject) {
      return this.commonSubjectsList.includes(subject);
    },
    toggleCommonSubject(subject) {
      if (this.isCommonSubjectSelected(subject)) {
        this.removeCommonSubject(this.commonSubjectsList.indexOf(subject));
      } else {
        this.newCommonSubject = subject;
        this.addCommonSubject();
      }
    },

    // Common Divisions Methods
    addCommonDivision() {
      if (this.newCommonDivision.trim() && !this.commonDivisionsList.includes(this.newCommonDivision.trim())) {
        this.commonDivisionsList.push(this.newCommonDivision.trim());
        this.newCommonDivision = '';
      }
    },
    removeCommonDivision(index) {
      this.commonDivisionsList.splice(index, 1);
    },
    isCommonDivisionSelected(division) {
      return this.commonDivisionsList.includes(division);
    },
    toggleCommonDivision(division) {
      if (this.isCommonDivisionSelected(division)) {
        this.removeCommonDivision(this.commonDivisionsList.indexOf(division));
      } else {
        this.newCommonDivision = division;
        this.addCommonDivision();
      }
    },

    hasMappedSubjects(programName) {
      return this.mappedProgramNames.includes(programName);
    },

    getMappedSubjects(programName) {
      return this.collegeProgramsSubjects[programName] || [];
    },

    // Initialize classes with text
    initializeClassesWithText(classes) {
      if (!classes || classes.length === 0) {
        this.classesWithText = [];
        return;
      }

      this.classesWithText = classes.map((cls, index) => {
        // Handle divisions transformation
        let existingSpecificDivisions = [];
        
        if (cls.divisions && cls.divisions.length > 0) {
          existingSpecificDivisions = cls.divisions
            .filter(div => {
              let divisionName = '';
              
              // Handle object format (old previous data)
              if (typeof div === 'object' && div.divisionName) {
                divisionName = div.divisionName.split('-').slice(1).join('-');
              } 
              // Handle string format (new data)
              else if (typeof div === 'string') {
                divisionName = div.includes('-') ? div.split('-').slice(1).join('-') : div;
              }
              
              const isCommon = this.commonDivisionsList.includes(divisionName);
              const isExcluded = cls.excludedCommonDivisions?.includes(divisionName);
              
              // Only filter out if it's common AND NOT excluded
              return !(isCommon && !isExcluded);
            })
            .map(div => {
              // Convert to object format for consistency
              if (typeof div === 'object' && div.divisionName) {
                return { divisionName: div.divisionName };
              } else if (typeof div === 'string') {
                const divisionName = div.includes('-') ? div : `${cls.className}-${div}`;
                return { divisionName: divisionName };
              }
              return { divisionName: String(div) };
            });
        }

        const processedClass = {
          ...cls,
          uniqueId: cls.uniqueId || this.generateUniqueId(),
          subjectsText: '',
          divisionsText: '',
          specificSubjects: cls.subjects ? cls.subjects.filter(sub => !this.commonSubjectsList.includes(sub)) : [],
          specificDivisions: existingSpecificDivisions,
          isSingleGroup: cls.isSingleGroup || false,
          excludedCommonSubjects: cls.excludedCommonSubjects || [],
          excludedCommonDivisions: cls.excludedCommonDivisions || []
        };

        return processedClass;
      });
    },

// Get display name for division - FIXED for college mode
getDivisionDisplayName(division, classIndex) {
  console.log(`🔍 getDivisionDisplayName called with:`, division, `for class ${classIndex}`);
  
  if (this.institutionType === 'college') {
    // For college, always show just the letter (A, B, C) or custom name as-is
    if (typeof division === 'object' && division.divisionName) {
      const parts = division.divisionName.split('-');
      console.log(`   📦 College object division parts:`, parts);
      
      // If it's a common division (like "FY BSc-CS-A"), return just "A"
      if (parts.length > 1 && this.commonDivisionsList.includes(parts[parts.length - 1])) {
        const result = parts[parts.length - 1];
        console.log(`   ✅ Common division, returning: ${result}`);
        return result;
      }
      // If it's a custom division, return the full custom name
      // FIX: Don't try to split custom names that don't contain dashes
      const hasProgramNamePrefix = parts.length > 1 && 
                                 this.classesWithText[classIndex]?.className && 
                                 division.divisionName.startsWith(this.classesWithText[classIndex].className + '-');
      
      if (hasProgramNamePrefix) {
        // This is a common division with program name prefix, return just the letter
        const result = parts[parts.length - 1];
        console.log(`   ✅ Common division with prefix, returning: ${result}`);
        return result;
      } else {
        // This is a custom division, return as-is
        console.log(`   ✅ Custom division, returning: ${division.divisionName}`);
        return division.divisionName;
      }
    }
    if (typeof division === 'string') {
      const parts = division.split('-');
      console.log(`   📦 College string division parts:`, parts);
      
      if (parts.length > 1 && this.commonDivisionsList.includes(parts[parts.length - 1])) {
        const result = parts[parts.length - 1];
        console.log(`   ✅ Common string division, returning: ${result}`);
        return result;
      }
      // For custom string divisions, return as-is
      console.log(`   ✅ Custom string division, returning: ${division}`);
      return division;
    }
  } else {
    // School mode - original logic
    if (typeof division === 'object' && division.divisionName) {
      const displayName = division.divisionName.split('-').slice(1).join('-');
      console.log(`   🏫 School object division, returning: ${displayName}`);
      return displayName || division.divisionName;
    }
    if (typeof division === 'string') {
      if (division.includes('-')) {
        const displayName = division.split('-').slice(1).join('-');
        console.log(`   🏫 School string division with dash, returning: ${displayName}`);
        return displayName;
      }
      console.log(`   🏫 School string division without dash, returning: ${division}`);
      return division;
    }
  }
  const fallback = String(division);
  console.log(`   ❓ Fallback division, returning: ${fallback}`);
  return fallback;
},
    // Program Management with auto-focus and scroll
    addNewProgram() {
      const newProgram = {
        uniqueId: this.generateUniqueId(),
        className: "",
        subjects: [],
        divisions: [],
        specificSubjects: [],
        specificDivisions: [],
        isSingleGroup: false,
        excludedCommonSubjects: [],
        excludedCommonDivisions: []
      };
      
      const updatedClasses = [...this.classesWithText, newProgram];
      this.emitUpdatedClasses(updatedClasses);
      
      this.$nextTick(() => {
        const inputElement = this.inputRefs[newProgram.uniqueId];
        const rowElement = this.programRefs[newProgram.uniqueId];
        
        if (inputElement) {
          inputElement.focus();
        }
        
        if (rowElement) {
          rowElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      });
    },

    removeProgram(index) {
      const updatedClasses = this.classesWithText.filter((_, i) => i !== index);
      this.emitUpdatedClasses(updatedClasses);
    },

    autoPopulatePrograms() {
      // Get the appropriate program names based on institution type
      const programNames = PROGRAM_NAMES[this.institutionType] || [];
      
      if (programNames.length === 0) {
        return;
      }
      
      const updatedClasses = programNames.map(name => ({
        uniqueId: this.generateUniqueId(),
        className: name,
        subjects: [],
        divisions: [],
        specificSubjects: [],
        specificDivisions: [],
        isSingleGroup: false,
        excludedCommonSubjects: [],
        excludedCommonDivisions: []
      }));
      
      // Update local state immediately
      this.classesWithText = updatedClasses;
      
      // Also emit to parent
      this.emitUpdatedClasses(updatedClasses, true);
    },

    toggleAllSingleGroup() {
      const newValue = !this.allSingleGroup;
      const updatedClasses = this.classesWithText.map(cls => ({
        ...cls,
        isSingleGroup: newValue
      }));
      this.emitUpdatedClasses(updatedClasses);
    },

    handleSingleGroupChange(index) {
      const updatedClasses = [...this.classesWithText];
      
      if (updatedClasses[index].isSingleGroup) {
        updatedClasses[index].specificDivisions = [];
        updatedClasses[index].excludedCommonDivisions = [];
        updatedClasses[index].divisionsText = '';
      }
      
      this.emitUpdatedClasses(updatedClasses);
    },

    addSpecificSubject(index) {
      if (this.classesWithText[index].subjectsText.trim()) {
        const updatedClasses = [...this.classesWithText];
        const subject = this.classesWithText[index].subjectsText.trim();
        
        if (!updatedClasses[index].specificSubjects.includes(subject)) {
          updatedClasses[index].specificSubjects.push(subject);
        }
        
        updatedClasses[index].subjectsText = '';
        this.emitUpdatedClasses(updatedClasses);
      }
    },

    addProgramSubject(index, subject) {
      const updatedClasses = [...this.classesWithText];
      
      if (!updatedClasses[index].specificSubjects.includes(subject)) {
        updatedClasses[index].specificSubjects.push(subject);
        this.emitUpdatedClasses(updatedClasses);
      }
    },

    addAllMappedSubjects(index, programName) {
      const updatedClasses = [...this.classesWithText];
      const mappedSubjects = this.getMappedSubjects(programName);
      
      mappedSubjects.forEach(subject => {
        if (!updatedClasses[index].specificSubjects.includes(subject)) {
          updatedClasses[index].specificSubjects.push(subject);
        }
      });
      
      this.emitUpdatedClasses(updatedClasses);
    },

    removeSpecificSubject(index, subIndex) {
      const updatedClasses = [...this.classesWithText];
      updatedClasses[index].specificSubjects.splice(subIndex, 1);
      this.emitUpdatedClasses(updatedClasses);
    },

    // Division Management - FIXED for college mode custom groups
    addSpecificDivision(index) {
      if (this.classesWithText[index].divisionsText.trim() && !this.classesWithText[index].isSingleGroup) {
        const updatedClasses = [...this.classesWithText];
        const divisionName = this.classesWithText[index].divisionsText.trim();
        const className = updatedClasses[index].className || 'Class';
        
        // For college mode, don't append program name to custom groups
        const fullDivisionName = this.institutionType === 'college' 
          ? divisionName  // Just use the custom name as-is for college
          : `${className}-${divisionName}`;  // Append class name for school
        
        const divisionExistsInSpecific = updatedClasses[index].specificDivisions
          .some(div => this.getDivisionDisplayName(div, index) === divisionName);
        const divisionExistsInCommon = this.commonDivisionsList.includes(divisionName);
        
        if (!divisionExistsInSpecific && !divisionExistsInCommon) {
          updatedClasses[index].specificDivisions.push({ divisionName: fullDivisionName });
        }
        
        updatedClasses[index].divisionsText = '';
        this.emitUpdatedClasses(updatedClasses);
      }
    },

    removeSpecificDivision(index, divIndex) {
      const updatedClasses = [...this.classesWithText];
      updatedClasses[index].specificDivisions.splice(divIndex, 1);
      this.emitUpdatedClasses(updatedClasses);
    },

    updateClassName(index, value) {
      const updatedClasses = [...this.classesWithText];
      const oldClassName = updatedClasses[index].className;
      updatedClasses[index].className = value;
      
      if (updatedClasses[index].specificDivisions && this.institutionType === 'school') {
        // Only update division names for school mode
        updatedClasses[index].specificDivisions = updatedClasses[index].specificDivisions.map(div => {
          if (typeof div === 'object' && div.divisionName && div.divisionName.includes('-')) {
            const divisionSuffix = div.divisionName.replace(`${oldClassName}-`, '');
            return { divisionName: `${value}-${divisionSuffix}` };
          }
          return div;
        });
      }

      this.emitUpdatedClasses(updatedClasses);
    },
    
    // Common Data Management
    updateAllClassesWithCommonData() {
      const updatedClasses = this.classesWithText.map(cls => ({
        ...cls,
        specificSubjects: cls.specificSubjects || [],
        specificDivisions: cls.specificDivisions || [],
        excludedCommonSubjects: cls.excludedCommonSubjects || [],
        excludedCommonDivisions: cls.excludedCommonDivisions || []
      }));
      this.emitUpdatedClasses(updatedClasses);
    },

    // Methods for handling excluded common subjects/divisions
    isCommonSubjectExcluded(classIndex, subject) {
      const cls = this.classesWithText[classIndex];
      return cls.excludedCommonSubjects?.includes(subject) || false;
    },
    
    toggleExcludeCommonSubject(classIndex, subject) {
      const updatedClasses = [...this.classesWithText];
      if (!updatedClasses[classIndex].excludedCommonSubjects) {
        updatedClasses[classIndex].excludedCommonSubjects = [];
      }
      
      const excludedIndex = updatedClasses[classIndex].excludedCommonSubjects.indexOf(subject);
      if (excludedIndex >= 0) {
        updatedClasses[classIndex].excludedCommonSubjects.splice(excludedIndex, 1);
      } else {
        updatedClasses[classIndex].excludedCommonSubjects.push(subject);
      }
      
      this.emitUpdatedClasses(updatedClasses);
    },

    isCommonDivisionExcluded(classIndex, division) {
      const cls = this.classesWithText[classIndex];
      return cls.excludedCommonDivisions?.includes(division) || false;
    },
    
    toggleExcludeCommonDivision(classIndex, division) {
      const updatedClasses = [...this.classesWithText];
      if (!updatedClasses[classIndex].excludedCommonDivisions) {
        updatedClasses[classIndex].excludedCommonDivisions = [];
      }
      
      const excludedIndex = updatedClasses[classIndex].excludedCommonDivisions.indexOf(division);
      if (excludedIndex >= 0) {
        updatedClasses[classIndex].excludedCommonDivisions.splice(excludedIndex, 1);
      } else {
        updatedClasses[classIndex].excludedCommonDivisions.push(division);
      }
      
      this.emitUpdatedClasses(updatedClasses);
    },

  // Emit updated classes with circular update protection
  emitUpdatedClasses(classes, isInitialPopulation = false) {
    if (this.isUpdatingClasses && !isInitialPopulation) {
      return;
    }
    
    this.isUpdatingClasses = true;
    
    const emittedValue = classes.map(cls => {
      if (cls.isSingleGroup && this.institutionType === 'college') {
        return {
          uniqueId: cls.uniqueId,
          className: cls.className,
          subjects: cls.specificSubjects || [],
          divisions: [cls.className],
          isSingleGroup: cls.isSingleGroup,
          excludedCommonSubjects: [],
          excludedCommonDivisions: [],
          specificSubjects: cls.specificSubjects || [],
          specificDivisions: []
        };
      } else {
        // Handle common divisions - FIX: Only include common divisions if they exist
        const commonDivisions = this.commonDivisionsList
          .filter(div => !cls.excludedCommonDivisions?.includes(div))
          .map(div => {
            // For college, common divisions should be appended with program name
            // For custom divisions in college, they should remain as-is
            if (this.institutionType === 'college') {
              return { divisionName: `${cls.className}-${div}` };
            } else {
              return { divisionName: `${cls.className}-${div}` };
            }
          });

        // Handle specific divisions
        const specificDivisions = (cls.specificDivisions || []).map(div => {
          if (typeof div === 'string') {
            return { divisionName: div };
          }
          return div;
        });

        const allDivisions = [...commonDivisions, ...specificDivisions];

        return {
          uniqueId: cls.uniqueId,
          className: cls.className,
          subjects: [
            ...this.commonSubjectsList.filter(sub => 
              !cls.excludedCommonSubjects?.includes(sub)
            ),
            ...(cls.specificSubjects || [])
          ],
          divisions: allDivisions,
          isSingleGroup: cls.isSingleGroup,
          excludedCommonSubjects: cls.excludedCommonSubjects || [],
          excludedCommonDivisions: cls.excludedCommonDivisions || [],
          specificSubjects: cls.specificSubjects || [],
          specificDivisions: cls.specificDivisions || []
        };
      }
    });

    this.$emit('update-field-array', {
      field: 'classes',
      value: emittedValue
    });

    // Update local state to match what we emitted
    this.classesWithText = classes;

    // Reset the flag after a short delay to allow the update to complete
    setTimeout(() => {
      this.isUpdatingClasses = false;
    }, 100);
  }
  }
}
</script>

<style scoped>
.subject-card, .division-card {
  transition: all 0.2s ease;
}

.subject-card:hover, .division-card:hover {
  transform: translateY(-1px);
}

input, textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.classes-table th,
.classes-table td {
  border: 1px solid #eee;
  padding: 8px 12px;
  text-align: left;
}

/* Custom checkbox styles */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

@media (max-width: 768px) {
  .division-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 480px) {
  .division-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  .subject-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>