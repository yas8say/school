<template>
  <div class="space-y-6 p-6 bg-gray-50 rounded-lg shadow max-w-4xl mx-auto">
    <!-- Auto-Create Classes Section -->
    <div class="flex flex-col md:flex-row items-start md:items-center gap-4">
      <input
        class="w-full md:flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder="Enter class names (comma separated)"
        v-model="classInput"
      />
      <button
        @click="autoCreateClasses"
        class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
      >
        🔁 Auto-Create Classes
      </button>
    </div>

    <!-- Class Cards -->
    <div
      v-for="(cls, classIndex) in values.classes"
      :key="classIndex"
      class="bg-white border border-gray-200 rounded-lg p-4 shadow space-y-4"
    >
      <!-- Class Header -->
      <div class="flex justify-between items-center">
        <div class="flex items-center gap-2">
          <span class="text-sm font-medium text-gray-700">Class Index:</span>
          <input
            class="px-2 py-1 border border-gray-300 rounded-md w-24 text-sm"
            v-model="cls.classIndex"
            @input="handleChange(`classes[${classIndex}].classIndex`, $event.target.value)"
          />
        </div>
        <button
          @click="removeClass(classIndex)"
          class="text-red-600 hover:text-red-800 text-lg"
        >
          ❎
        </button>
      </div>

      <input
        class="w-full px-4 py-2 border border-gray-300 rounded-md"
        placeholder="Enter class/program name"
        v-model="cls.className"
        @input="handleChange(`classes[${classIndex}].className`, $event.target.value)"
      />

      <!-- Actions -->
      <div class="flex gap-2">
        <button
          @click="openDivisionPopup(classIndex)"
          class="px-3 py-1 bg-purple-600 text-white rounded hover:bg-purple-700"
        >
          🔁
        </button>
        <button
          @click="toggleExpandClass(classIndex)"
          class="px-3 py-1 bg-gray-200 text-black rounded hover:bg-gray-300"
        >
          {{ expandedClasses[classIndex] ? '🔼' : '🔽' }}
        </button>
      </div>

      <!-- Expanded Content -->
      <div v-if="expandedClasses[classIndex]" class="space-y-4">
        <!-- Subjects -->
        <div class="space-y-3">
          <div
            v-for="(subject, subjectIndex) in cls.subjects"
            :key="subjectIndex"
            class="flex flex-col md:flex-row gap-2 items-center"
          >
          <input
            class="flex-1 px-3 py-2 border border-gray-300 rounded-md"
            placeholder="Enter or select subject"
            :value="cls.subjects[subjectIndex]"
            @input="updateSubject(classIndex, subjectIndex, $event.target.value)"
          />
          <select
            :value="cls.subjects[subjectIndex]"
            @change="updateSubject(classIndex, subjectIndex, $event.target.value)"
            class="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="">Select Subject</option>
            <option
              v-for="(subj, index) in availableSubjects"
              :key="index"
              :value="subj"
            >
              {{ subj }}
            </option>
          </select>

            <button
              @click="removeSubject(classIndex, subjectIndex)"
              class="text-red-600 hover:text-red-800"
            >
              ❎
            </button>
          </div>
          <button
            @click="addSubject(classIndex)"
            class="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"
          >
            + Add Subject
          </button>
        </div>

        <!-- Divisions -->
        <div class="space-y-3">
          <div
            v-for="(division, divisionIndex) in cls.divisions"
            :key="divisionIndex"
            class="flex flex-col md:flex-row gap-2 items-center"
          >
            <input
              class="flex-1 px-3 py-2 border border-gray-300 rounded-md"
              placeholder="Enter division name"
              v-model="division.divisionName"
              @input="handleChange(`classes[${classIndex}].divisions[${divisionIndex}].divisionName`, $event.target.value)"
            />
            <select
              v-model="division.divisionName"
              @change="updateDivision(classIndex, divisionIndex, $event.target.value)"
              class="px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="">Select Division</option>
              <option
                v-for="(divisionName, index) in availableDivisions"
                :key="index"
                :value="divisionName"
              >
                {{ divisionName }}
              </option>
            </select>
            <button
              @click="removeDivision(classIndex, divisionIndex)"
              class="text-red-600 hover:text-red-800"
            >
              ❎
            </button>
          </div>
          <button
            @click="addDivision(classIndex)"
            class="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"
          >
            + Add Division
          </button>
        </div>
      </div>
    </div>

    <!-- Add Class Button -->
    <button
      @click="addClass"
      class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
    >
      + Add Class
    </button>

    <!-- Auto-Create Divisions Popup -->
    <div
      v-if="showDivisionPopup"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white p-6 rounded-lg shadow space-y-4 w-full max-w-md">
        <input
          class="w-full px-4 py-2 border border-gray-300 rounded-md"
          placeholder="Enter division names (comma separated)"
          v-model="divisionInput"
        />
        <div class="flex justify-end gap-2">
          <button
            @click="autoCreateDivisions"
            class="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
          >
            🔁 Auto-Create Divisions
          </button>
          <button
            @click="closeDivisionPopup"
            class="px-4 py-2 bg-gray-300 text-black rounded hover:bg-gray-400"
          >
            ❌ Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
export default {
  props: {
    values: {
      type: Object,
      default: () => ({ classes: [] })
    },
    handleChange: {
      type: Function,
      default: () => {}
    },
    setFieldValue: {
      type: Function,
      default: () => {}
    }
  },
  data() {
    return {
      initialized: false,
      classInput: '',
      divisionInput: '',
      showDivisionPopup: false,
      selectedClassIndex: null,
      expandedClasses: []
    };
  },
  computed: {
    safeClasses() {
      return this.values?.classes || [];
    },
    availableSubjects() {
      // Get all subjects from all classes and flatten them
      const allSubjects = this.safeClasses.flatMap(cls => cls.subjects || []);
      // Return only unique subjects
      return [...new Set(allSubjects)];
    },
    availableDivisions() {
      return this.safeClasses.flatMap(cls => 
        (cls.divisions || []).map(d => d.divisionName)
      );
    }
  },
  mounted() {
    this.normalizeClasses();
    this.initializeClasses();
    this.initialized = true;
  },
  methods: {
    normalizeClasses() {
    const updatedClasses = [...this.safeClasses];

    let indexCounter = 1;
    for (let i = 0; i < updatedClasses.length; i++) {
      if (!('classIndex' in updatedClasses[i])) {
        updatedClasses[i].classIndex = indexCounter++;
      }
    }

    this.setFieldValue('classes', updatedClasses);
  },
    initializeClasses() {
  if (!this.values.classes || this.values.classes.length === 0) {
    this.setFieldValue('classes', [
      {
        className: '',
        subjects: [],
        divisions: [{ divisionName: '' }],
        classIndex: 1
      }
    ]);
  }
},
autoCreateClasses() {
    const classNames = this.classInput.split(',')
      .map(name => name.trim())
      .filter(name => name);
    
    if (!classNames.length) {
      alert('Please enter valid class names');
      return;
    }

    const currentClasses = [...this.safeClasses];
    const maxIndex = currentClasses.reduce((max, cls) => 
      Math.max(max, cls.classIndex || 0), 0);

    const newClasses = classNames.map((name, idx) => ({
      className: name,
      subjects: [],
      divisions: [{ divisionName: '' }],
      classIndex: maxIndex + idx + 1
    }));

    // Emit event to parent instead of direct update
    this.$emit('update-field-array', {
      field: 'classes',
      value: [...currentClasses, ...newClasses]
    });

    // Initialize expanded states for new classes
    newClasses.forEach((_, idx) => {
      const classIndex = currentClasses.length + idx;
      this.$set(this.expandedClasses, classIndex, false);
    });

    this.classInput = '';
  },
    openDivisionPopup(classIndex) {
      this.selectedClassIndex = classIndex;
      this.showDivisionPopup = true;
    },
    closeDivisionPopup() {
      this.showDivisionPopup = false;
      this.selectedClassIndex = null;
    },
    autoCreateDivisions() {
      if (this.selectedClassIndex === null) return;
      
      const divisionNames = this.divisionInput.split(',').map(name => name.trim()).filter(name => name);
      const className = this.values.classes[this.selectedClassIndex].className;
    
      const newDivisions = divisionNames.map(name => ({
        divisionName: `${className}-${name}`,
      }));
    
      const updatedClasses = [...this.values.classes];
      updatedClasses[this.selectedClassIndex].divisions = [
        ...updatedClasses[this.selectedClassIndex].divisions,
        ...newDivisions,
      ];
    
      this.divisionInput = '';
      this.setFieldValue('classes', updatedClasses);
      this.closeDivisionPopup();
    },
    toggleExpandClass(index) {
      this.expandedClasses = [...this.expandedClasses];
      this.expandedClasses[index] = !this.expandedClasses[index];
      this.$forceUpdate(); // Vue sometimes needs this for array changes
    },
    addSubject(classIndex) {
      const updatedClasses = [...this.values.classes];
      updatedClasses[classIndex].subjects.push('');
      this.setFieldValue('classes', updatedClasses);
    },
    updateSubject(classIndex, subjectIndex, value) {
      const updatedClasses = [...this.values.classes];
      updatedClasses[classIndex].subjects[subjectIndex] = value;
      this.setFieldValue('classes', updatedClasses);
    },
    removeSubject(classIndex, subjectIndex) {
      const updatedClasses = [...this.values.classes];
      updatedClasses[classIndex].subjects.splice(subjectIndex, 1);
      this.setFieldValue('classes', updatedClasses);
    },
    addDivision(classIndex) {
      const updatedClasses = [...this.values.classes];
      updatedClasses[classIndex].divisions.push({ divisionName: '' });
      this.setFieldValue('classes', updatedClasses);
    },
    updateDivision(classIndex, divisionIndex, value) {
      const updatedClasses = [...this.values.classes];
      updatedClasses[classIndex].divisions[divisionIndex].divisionName = value;
      this.setFieldValue('classes', updatedClasses);
    },
    removeDivision(classIndex, divisionIndex) {
      const updatedClasses = [...this.values.classes];
      updatedClasses[classIndex].divisions.splice(divisionIndex, 1);
      this.setFieldValue('classes', updatedClasses);
    },
    addClass() {
    const currentClasses = [...this.safeClasses];
    const maxIndex = currentClasses.reduce((max, cls) => 
      Math.max(max, cls.classIndex || 0), 0);

    const newClass = {
      className: '',
      subjects: [],
      divisions: [{ divisionName: '' }],
      classIndex: maxIndex + 1
    };

    // Emit event to parent
    this.$emit('update-field-array', {
      field: 'classes',
      value: [...currentClasses, newClass]
    });

    // Initialize expanded state
    this.$set(this.expandedClasses, currentClasses.length, false);
  },
  removeClass(index) {
    const updatedClasses = [...this.safeClasses];
    updatedClasses.splice(index, 1);
    
    // Emit event to parent
    this.$emit('update-field-array', {
      field: 'classes',
      value: updatedClasses
    });

    // Clean up expanded state
    this.$delete(this.expandedClasses, index);
  }

  }
};
</script>

<style scoped>
.program-form {
  padding: 20px;
}

.auto-create-container {
  margin-bottom: 20px;
}

.class-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  position: relative;
}

.class-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.class-title-container {
  display: flex;
  align-items: center;
}

.static-text {
  margin-right: 10px;
}

.input, .editable-title-input, .sinput {
  width: 100%;
  padding: 8px;
  margin-bottom: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.button {
  padding: 8px 12px;
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 10px;
  margin-bottom: 10px;
}

.trash-icon, .strash-icon, .three-dots-button, .arrow-button {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  padding: 5px;
}

.subject-card, .division-card {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.picker {
  width: 50%;
  padding: 8px;
  margin-left: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.modal-background {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.auto-create-modal {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  width: 80%;
  max-width: 400px;
}
</style>