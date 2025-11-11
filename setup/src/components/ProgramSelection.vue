<template>
  <div class="program-selector-container">
    <div class="institution-selector">
      <label class="form-label">Select Institution Type</label>
      <select 
        v-model="selectedInstitution" 
        class="form-select"
        @change="handleInstitutionChange"
      >
        <option value="">Select Institution</option>
        <option value="school">School</option>
        <option value="college">College</option>
      </select>
    </div>

    <div v-if="editablePrograms.length > 0" class="programs-list">
      <h3 class="section-title">Classes List</h3>
      
      <div 
        v-for="(program, index) in editablePrograms" 
        :key="program.uniqueId || program.id"
        class="program-item"
      >
        <input
          type="text"
          v-model="program.className"
          class="program-input"
          @input="handleEditProgram(index, $event.target.value)"
        />
        <button 
          class="delete-btn"
          @click="handleDeleteProgram(index)"
          title="Remove class"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
    </div>

    <button class="add-btn" @click="handleAddProgram">
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="12" y1="5" x2="12" y2="19"></line>
        <line x1="5" y1="12" x2="19" y2="12"></line>
      </svg>
      Add Class
    </button>
  </div>
</template>

<script>
const PROGRAM_OPTIONS = {
  school: [
    "Nursery", "Jr KG", "Sr KG", "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th"
  ],
  college: [
    "FY Bachelors", "SY Bachelors", "TY Bachelors",
    "FY Diploma", "SY Diploma",
    "FY BTech", "SY BTech", "TY BTech", "Final Year BTech",
    "FY Masters", "SY Masters",
    "PhD Year 1", "PhD Year 2", "PhD Year 3", "PhD Year 4", "PhD Year 5"
  ]
};

export default {
  props: {
    values: Object
  },
  computed: {
    selectedInstitution: {
      get() {
        return this.values.selectedInstitution || '';
      },
      set(value) {
        this.updateField('selectedInstitution', value);
      }
    }
  },
  data() {
    return {
      editablePrograms: []
    };
  },
  watch: {
    'values.classes': {
      immediate: true,
      handler(newClasses) {
        if (newClasses && newClasses.length > 0) {
          this.editablePrograms = newClasses.map(program => ({
            ...program,
            uniqueId: program.uniqueId || program.id || this.generateUniqueId()
          }));
        } else {
          this.editablePrograms = [];
        }
      }
    }
  },
  methods: {
    generateUniqueId() {
      return Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
    },
    updateField(field, value) {
      this.$emit('update-field', { field, value });
    },
    handleEditProgram(index, newName) {
      const updatedPrograms = [...this.editablePrograms];
      updatedPrograms[index].className = newName;
      this.updatePrograms(updatedPrograms);
    },
    handleDeleteProgram(index) {
      const updatedPrograms = this.editablePrograms.filter((_, i) => i !== index);
      this.updatePrograms(updatedPrograms);
    },
    handleAddProgram() {
      const newProgram = {
        uniqueId: this.generateUniqueId(),
        className: "",
        subjects: [],
        divisions: []
      };
      const updatedPrograms = [...this.editablePrograms, newProgram];
      this.updatePrograms(updatedPrograms);
    },
    handleInstitutionChange() {
      const formattedPrograms = (PROGRAM_OPTIONS[this.selectedInstitution] || []).map(name => ({
        uniqueId: this.generateUniqueId(),
        className: name,
        subjects: [],
        divisions: []
      }));
      this.updatePrograms(formattedPrograms);
    },
    updatePrograms(programs) {
      this.editablePrograms = programs;
      this.$emit('update-field-array', {
        field: 'classes',
        value: programs
      });
    }
  }
};
</script>

<style scoped>
/* Your existing styles remain the same */
.program-selector-container {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.institution-selector {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #34495e;
}

.form-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 16px;
  height: 41px;
}

.section-title {
  font-size: 1.1rem;
  color: #2c3e50;
  margin-bottom: 15px;
}

.programs-list {
  margin-bottom: 20px;
}

.program-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.program-input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
}

.delete-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: none;
  border: none;
  cursor: pointer;
  color: #e74c3c;
  transition: all 0.2s;
}

.delete-btn:hover {
  background-color: rgba(231, 76, 60, 0.1);
}

.add-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background-color: #2ecc71;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.add-btn:hover {
  background-color: #27ae60;
}

@media (max-width: 768px) {
  .program-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>