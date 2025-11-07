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

    <!-- College Division Picker (Visible only for College) -->
    <div v-if="institutionType === 'college'" class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2">College Division</label>
      <select 
        v-model="selectedCollegeDivision"
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      >
        <option value="">Select a division...</option>
        <option 
          v-for="division in collegeDivisionsList" 
          :key="division"
          :value="division"
        >
          {{ division }}
        </option>
      </select>
      
      <!-- Quick Select College Divisions -->
      <div class="quick-select mt-3" v-if="selectedCollegeDivision">
        <h3 class="text-sm font-medium text-gray-700 mb-2">Quick Select {{ selectedCollegeDivision }} Subjects</h3>
        <div class="subject-grid grid grid-cols-3 gap-2">
          <div 
            v-for="subject in getCollegeSubjects(selectedCollegeDivision)" 
            :key="subject"
            class="subject-card px-3 py-2 border rounded-md text-center cursor-pointer text-sm"
            :class="{ 
              'bg-purple-100 border-purple-300': isCommonSubjectSelected(subject),
              'bg-gray-50 hover:bg-gray-100': !isCommonSubjectSelected(subject)
            }"
            @click="toggleCommonSubject(subject)"
          >
            {{ subject }}
          </div>
        </div>
      </div>
    </div>

    <!-- Global Subject Input -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        {{ institutionType === 'college' ? 'Common Courses for All Programs' : 'Common Subjects for All Classes' }}
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
          :placeholder="institutionType === 'college' ? 'Add courses...' : 'Add subjects...'"
          class="flex-1 min-w-[100px] px-2 py-1 border-0 focus:ring-0 focus:outline-none"
        />
      </div>

      <!-- Quick Select Subjects Widget -->
      <div class="quick-select mt-3" v-if="institutionType === 'school'">
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

    <!-- Global Division Input -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        {{ institutionType === 'college' ? 'Common Programs for All Classes' : 'Common Divisions for All Classes' }}
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
          :placeholder="institutionType === 'college' ? 'Add programs...' : 'Add divisions...'"
          class="flex-1 min-w-[100px] px-2 py-1 border-0 focus:ring-0 focus:outline-none"
        />
      </div>

      <!-- Quick Select Divisions Widget -->
      <div class="quick-select mt-3">
        <h3 class="text-sm font-medium text-gray-700 mb-2">
          {{ institutionType === 'college' ? 'Quick Select Programs' : 'Quick Select Divisions' }}
        </h3>
        <div class="division-grid grid grid-cols-6 gap-2">
          <div 
            v-for="division in getDivisionOptions()" 
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

    <!-- Classes Overview -->
    <h3 class="text-lg font-semibold text-gray-800 border-b pb-2">
      {{ institutionType === 'college' ? 'Programs Overview' : 'Classes Overview' }}
    </h3>

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
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(cls, index) in classesWithText"
            :key="index"
            class="border-t hover:bg-gray-50"
          >
            <td class="px-4 py-2">{{ index + 1 }}</td>
            <td class="px-4 py-2">
              <input
                type="text"
                v-model="cls.className"
                @input="updateClassName(index, $event.target.value)"
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
                :placeholder="institutionType === 'college' ? 'Program name...' : 'Class name...'"
              />
            </td>
            <td class="px-4 py-2 w-[300px]">
              <div class="flex flex-wrap gap-1 mb-1 min-h-[40px]">
                <!-- Common subjects (lighter color) -->
                <span 
                  v-for="(subject, subIdx) in commonSubjectsList" 
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
                <!-- Class-specific subjects (darker color) -->
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
                  :placeholder="institutionType === 'college' ? 'Add program-specific course...' : 'Add class-specific subject...'"
                  class="flex-1 px-2 py-1 border border-gray-300 rounded text-xs"
                />
                <button
                  @click="addSpecificSubject(index)"
                  class="px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 text-xs"
                >
                  Add
                </button>
              </div>
            </td>
            <td class="px-4 py-2">
              <div class="flex flex-wrap gap-1 mb-1 min-h-[40px]">
                <!-- Common divisions (lighter color) -->
                <span 
                  v-for="(division, divIdx) in commonDivisionsList" 
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
                <!-- Class-specific divisions (darker color) -->
                <span 
                  v-for="(division, divIdx) in cls.specificDivisions" 
                  :key="'specific-'+divIdx"
                  class="inline-flex items-center px-2 py-1 rounded-full bg-green-100 text-green-800 text-xs"
                >
                  {{ division.divisionName.split('-').slice(1).join('-') }}
                  <button 
                    @click="removeSpecificDivision(index, divIdx)"
                    class="ml-1 text-green-500 hover:text-green-700 text-xs"
                  >
                    ×
                  </button>
                </span>
              </div>
              <div class="flex gap-2">
                <input
                  type="text"
                  v-model="cls.divisionsText"
                  @keydown.enter="addSpecificDivision(index)"
                  :placeholder="institutionType === 'college' ? 'Add program-specific group...' : 'Add class-specific division...'"
                  class="flex-1 px-2 py-1 border border-gray-300 rounded text-xs"
                />
                <button
                  @click="addSpecificDivision(index)"
                  class="px-2 py-1 bg-green-500 text-white rounded hover:bg-green-600 text-xs"
                >
                  Add
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    values: Object
  },
  data() {
    return {
      institutionType: 'school', // Default to school
      selectedCollegeDivision: '',
      newCommonSubject: '',
      newCommonDivision: '',
      commonSubjectsList: [],
      commonDivisionsList: [],
      classesWithText: [],
      
      // School subjects
      commonSubjects: [
        'Math', 'Social Studies', 'Science', 'English',
        'History', 'Geography', 'Physics',
        'Chemistry', 'Biology', 'Computer',
        'Civics', 'Hindi', 'Marathi',
        'Arabic', 'Play'
      ],
      
      // School divisions
      commonDivisions: ['A', 'B', 'C', 'D', 'E', 'F'],
      
      // College data structure
      collegeDivisions: {
        "Computer Science": [
          "Data Structures", "Algorithms", "Operating Systems", "Computer Networks", 
          "Database Management Systems", "Object-Oriented Programming", "Software Engineering", 
          "Web Development", "Theory of Computation", "Artificial Intelligence", 
          "Machine Learning", "Cyber Security", "Cloud Computing"
        ],
        "Computer Applications": [
          "C Programming", "Data Structures", "Database Management", "Web Programming", 
          "Computer Architecture", "Operating Systems", "Java Programming", 
          "Python Programming", "Software Engineering", "Computer Networks", 
          "Mobile App Development"
        ],
        "Information Technology": [
          "Web Technology", "Network Security", "Database Systems", "Cloud Services", 
          "IT Project Management", "Data Analytics", "Software Testing", 
          "System Administration", "E-Commerce Systems"
        ],
        "Electronics": [
          "Basic Electronics", "Digital Electronics", "Microprocessors", "Embedded Systems", 
          "Circuit Theory", "VLSI Design", "Communication Systems", "Sensors and Instrumentation"
        ],
        "Mechanical Engineering": [
          "Engineering Mechanics", "Thermodynamics", "Fluid Mechanics", "Strength of Materials", 
          "Manufacturing Processes", "Machine Design", "Heat Transfer", "CAD/CAM"
        ],
        "Civil Engineering": [
          "Engineering Drawing", "Surveying", "Structural Engineering", "Concrete Technology", 
          "Soil Mechanics", "Transportation Engineering", "Construction Management", 
          "Environmental Engineering"
        ],
        "Electrical Engineering": [
          "Electrical Circuits", "Power Systems", "Control Systems", "Electrical Machines", 
          "Power Electronics", "Renewable Energy", "High Voltage Engineering"
        ],
        "Business Administration": [
          "Principles of Management", "Marketing Management", "Financial Management", 
          "Business Law", "Organizational Behaviour", "Human Resource Management", 
          "Accounting", "Entrepreneurship", "Business Communication"
        ],
        "Commerce": [
          "Accountancy", "Business Economics", "Cost Accounting", "Auditing", 
          "Taxation", "Business Law", "Statistics", "Financial Accounting"
        ],
        "Accounting and Finance": [
          "Financial Accounting", "Cost Accounting", "Taxation", "Statistics for Finance", 
          "Corporate Finance", "Banking and Insurance Fundamentals"
        ],
        "Banking and Insurance": [
          "Banking Operations", "Financial Markets", "Insurance Fundamentals", 
          "Risk Management", "Commercial Banking", "Customer Relationship Management"
        ],
        "Physics": [
          "Mechanics", "Electricity and Magnetism", "Optics", "Quantum Physics", 
          "Thermodynamics", "Nuclear Physics", "Basic Electronics"
        ],
        "Chemistry": [
          "Organic Chemistry", "Inorganic Chemistry", "Physical Chemistry", 
          "Analytical Techniques", "Environmental Chemistry"
        ],
        "Mathematics": [
          "Calculus", "Algebra", "Differential Equations", "Probability and Statistics", 
          "Real Analysis", "Linear Algebra", "Discrete Mathematics"
        ],
        "Biotechnology": [
          "Cell Biology", "Genetics", "Microbiology", "Biochemistry", 
          "Molecular Biology", "Immunology", "Genetic Engineering"
        ],
        "Microbiology": [
          "General Microbiology", "Environmental Microbiology", "Food Microbiology", 
          "Medical Microbiology", "Industrial Microbiology"
        ],
        "Psychology": [
          "Introduction to Psychology", "Cognitive Psychology", "Developmental Psychology", 
          "Abnormal Psychology", "Social Psychology", "Research Methods"
        ],
        "Economics": [
          "Microeconomics", "Macroeconomics", "Indian Economy", "Econometrics", 
          "Public Finance", "International Economics"
        ],
        "English Literature": [
          "Poetry", "Drama", "Novels", "Literary Theory", 
          "Indian Writing in English", "Linguistics", "Modern Literature"
        ]
      },
      
      collegeDivisionsList: [
        "Computer Science", "Computer Applications", "Information Technology", 
        "Electronics", "Mechanical Engineering", "Civil Engineering", 
        "Electrical Engineering", "Business Administration", "Commerce", 
        "Accounting & Finance", "Banking & Insurance", "Physics", 
        "Chemistry", "Mathematics", "Biotechnology", "Microbiology", 
        "Psychology", "Economics", "English Literature"
      ]
    }
  },
  computed: {
    collegeCommonSubjects() {
      if (this.selectedCollegeDivision && this.collegeDivisions[this.selectedCollegeDivision]) {
        return this.collegeDivisions[this.selectedCollegeDivision];
      }
      return [];
    }
  },
  created() {
    // Initialize with prop values if they exist
    if (this.values.commonSubjects) {
      this.commonSubjectsList = [...this.values.commonSubjects];
    }
    if (this.values.commonDivisions) {
      this.commonDivisionsList = [...this.values.commonDivisions];
    }
    if (this.values.institutionType) {
      this.institutionType = this.values.institutionType;
    }
  },
  watch: {
    'values.classes': {
      immediate: true,
      deep: true,
      handler(classes) {
        this.classesWithText = classes.map(cls => ({
          ...cls,
          subjectsText: '',
          divisionsText: '',
          // Initialize specific subjects by filtering out common ones
          specificSubjects: cls.subjects 
            ? cls.subjects.filter(sub => !this.commonSubjectsList.includes(sub))
            : [],
          // Initialize specific divisions by filtering out common ones
          specificDivisions: cls.divisions
            ? cls.divisions.filter(div => {
                const divName = div.divisionName.split('-').slice(1).join('-');
                return !this.commonDivisionsList.includes(divName);
              })
            : [],
          // Initialize excluded lists
          excludedCommonSubjects: cls.excludedCommonSubjects || [],
          excludedCommonDivisions: cls.excludedCommonDivisions || []
        }));
      }
    },
    commonSubjectsList: {
      handler(newVal) {
        this.$emit('update-field', {
          field: 'commonSubjects',
          value: newVal
        });
        // Update all classes to include the new common subjects
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
        // Update all classes to include the new common divisions
        this.updateAllClassesWithCommonData();
      },
      deep: true
    },
    institutionType: {
      handler(newVal) {
        this.$emit('update-field', {
          field: 'institutionType',
          value: newVal
        });
        // Clear college-specific selection when switching to school
        if (newVal === 'school') {
          this.selectedCollegeDivision = '';
        }
      }
    }
  },
  methods: {
    // Institution Type Methods
    setInstitutionType(type) {
      this.institutionType = type;
    },

    // College Methods
    getCollegeSubjects(division) {
      return this.collegeDivisions[division] || [];
    },

    getDivisionOptions() {
      return this.institutionType === 'college' ? this.collegeDivisionsList : this.commonDivisions;
    },

    // Common Subjects Methods
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

    // Class-specific Methods
    addSpecificSubject(index) {
      if (this.classesWithText[index].subjectsText.trim()) {
        const updatedClasses = [...this.classesWithText];
        updatedClasses[index].specificSubjects = [
          ...updatedClasses[index].specificSubjects,
          updatedClasses[index].subjectsText.trim()
        ];
        updatedClasses[index].subjectsText = '';
        this.emitUpdatedClasses(updatedClasses);
      }
    },
    removeSpecificSubject(index, subIndex) {
      const updatedClasses = [...this.classesWithText];
      updatedClasses[index].specificSubjects.splice(subIndex, 1);
      this.emitUpdatedClasses(updatedClasses);
    },
    addSpecificDivision(index) {
      if (this.classesWithText[index].divisionsText.trim()) {
        const updatedClasses = [...this.classesWithText];
        const className = updatedClasses[index].className || 'Class';
        updatedClasses[index].specificDivisions = [
          ...updatedClasses[index].specificDivisions,
          { divisionName: `${className}-${updatedClasses[index].divisionsText.trim()}` }
        ];
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
      
      // Update specific division names if className changes
      if (updatedClasses[index].specificDivisions) {
        updatedClasses[index].specificDivisions = updatedClasses[index].specificDivisions.map(div => {
          const divisionSuffix = div.divisionName.replace(`${oldClassName}-`, '');
          return {
            divisionName: `${value}-${divisionSuffix}`
          };
        });
      }

      this.emitUpdatedClasses(updatedClasses);
    },
    
    // New method to update all classes when common data changes
    updateAllClassesWithCommonData() {
      const updatedClasses = this.classesWithText.map(cls => ({
        ...cls,
        // Keep existing specific data
        specificSubjects: cls.specificSubjects || [],
        specificDivisions: cls.specificDivisions || [],
        // Keep excluded lists
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
        // Subject is currently excluded - include it
        updatedClasses[classIndex].excludedCommonSubjects.splice(excludedIndex, 1);
      } else {
        // Subject is currently included - exclude it
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
        // Division is currently excluded - include it
        updatedClasses[classIndex].excludedCommonDivisions.splice(excludedIndex, 1);
      } else {
        // Division is currently included - exclude it
        updatedClasses[classIndex].excludedCommonDivisions.push(division);
      }
      
      this.emitUpdatedClasses(updatedClasses);
    },
    
    emitUpdatedClasses(classes) {
      this.$emit('update-field-array', {
        field: 'classes',
        value: classes.map(cls => ({
          className: cls.className,
          // Combine common subjects (filtering out excluded ones) with class-specific subjects
          subjects: [
            ...this.commonSubjectsList.filter(sub => 
              !cls.excludedCommonSubjects?.includes(sub)
            ),
            ...(cls.specificSubjects || [])
          ],
          // Combine common divisions (filtering out excluded ones) with class-specific divisions
          divisions: [
            ...this.commonDivisionsList
              .filter(div => !cls.excludedCommonDivisions?.includes(div))
              .map(div => ({ divisionName: `${cls.className}-${div}` })),
            ...(cls.specificDivisions || [])
          ],
          // Include the excluded lists in the saved data
          excludedCommonSubjects: cls.excludedCommonSubjects || [],
          excludedCommonDivisions: cls.excludedCommonDivisions || [],
          // Keep specific data
          specificSubjects: cls.specificSubjects || [],
          specificDivisions: cls.specificDivisions || []
        }))
      });
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