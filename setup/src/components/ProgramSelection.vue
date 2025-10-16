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
        v-for="program in editablePrograms" 
        :key="program.id"
        class="program-item"
      >
        <input
          type="text"
          v-model="program.className"
          class="program-input"
          @input="handleEditProgram(program.id, $event.target.value)"
        />
        <button 
          class="delete-btn"
          @click="handleDeleteProgram(program.id)"
          title="Remove class"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
    </div>

    <div class="quick-select" v-if="selectedInstitution === ''">
      <h3 class="section-title">Quick Select Programs</h3>
      <div class="program-grid">
        <div 
          v-for="program in availablePrograms" 
          :key="program.id"
          class="program-card"
          :class="{ 'selected': isSelected(program) }"
          @click="toggleProgram(program)"
        >
          {{ program.name }}
        </div>
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
const ALL_PROGRAMS = [
  { id: 1, name: 'Pre-K' },
  { id: 2, name: 'Kindergarten' },
  { id: 3, name: '1st Grade' },
  { id: 4, name: '2nd Grade' },
  { id: 5, name: '3rd Grade' },
  { id: 6, name: '4th Grade' },
  { id: 7, name: '5th Grade' },
  { id: 8, name: '6th Grade' },
  { id: 9, name: '7th Grade' },
  { id: 10, name: '8th Grade' },
  { id: 11, name: '9th Grade' },
  { id: 12, name: '10th Grade' },
  { id: 13, name: '11th Grade' },
  { id: 14, name: '12th Grade' },
  { id: 15, name: 'Other' }
];

const PROGRAM_OPTIONS = {
  school: [
    "Nursery", "Jr KG", "Sr KG", "1st", "2nd", "3rd", "4th", "5th",
    "6th", "7th", "8th", "9th", "10th", "11th", "12th"
  ],
  college: [
    "FY BSc", "SY BSc", "TY BSc", "FY BCA", "SY BCA", "TY BCA",
    "FY BTech", "SY BTech", "TY BTech", "Final Year BTech",
    "FY BCom", "SY BCom", "TY BCom", "MBA"
  ]
};

export default {
  props: {
    values: Object
  },
  data() {
    return {
      selectedInstitution: '',
      editablePrograms: [],
      availablePrograms: ALL_PROGRAMS
    };
  },
  watch: {
    'values.classes': {
      immediate: true,
      handler(newClasses) {
        if (newClasses && newClasses.length > 0) {
          this.editablePrograms = [...newClasses];
        }
      }
    }
  },
  computed: {
    selectedPrograms() {
      return this.values.classes || [];
    }
  },
  methods: {
    isSelected(program) {
      return this.selectedPrograms.some(p => p.id === program.id);
    },
    toggleProgram(program) {
      let updatedPrograms;
      
      if (this.isSelected(program)) {
        updatedPrograms = this.selectedPrograms.filter(p => p.id !== program.id);
      } else {
        updatedPrograms = [...this.selectedPrograms, { 
          id: program.id, 
          className: program.name,
          subjects: [],
          divisions: []
        }];
      }
      
      this.updatePrograms(updatedPrograms);
    },
    handleEditProgram(id, newName) {
      const updatedPrograms = this.editablePrograms.map(program =>
        program.id === id ? { ...program, className: newName } : program
      );
      this.updatePrograms(updatedPrograms);
    },
    handleDeleteProgram(id) {
      const updatedPrograms = this.editablePrograms.filter(program => program.id !== id);
      this.updatePrograms(updatedPrograms);
    },
    handleAddProgram() {
      const newProgram = {
        id: Math.random().toString(),
        className: "",
        subjects: [],
        divisions: []
      };
      const updatedPrograms = [...this.editablePrograms, newProgram];
      this.updatePrograms(updatedPrograms);
    },
    handleInstitutionChange() {
      const formattedPrograms = (PROGRAM_OPTIONS[this.selectedInstitution] || []).map(name => ({
        id: Math.random().toString(),
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

.quick-select {
  margin-bottom: 20px;
}

.program-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 10px;
  margin-bottom: 15px;
}

.program-card {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background-color: #f9f9f9;
}

.program-card:hover {
  background-color: #f0f0f0;
}

.program-card.selected {
  background-color: #3498db;
  color: white;
  border-color: #2980b9;
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