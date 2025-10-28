<template>
  <div class="form-card">
    <h2 class="form-title">Academic Information</h2>
    <div class="form-grid">
      <div class="form-group required">
        <label>Academic Year</label>
        <select 
          :value="selectedYear" 
          class="picker" 
          @change="onYearChange"
          :disabled="academicYearsResource?.loading"
        >
          <option :value="null">Select a Year</option>
          <option v-for="year in academicYears" :key="year" :value="year">
            {{ year }}
          </option>
        </select>
      </div>

      <div class="form-group required">
        <label>Class / Program</label>
        <select 
          :value="selectedClass" 
          class="picker" 
          @change="onClassChange"
          :disabled="!selectedYear || classesResource?.loading"
        >
          <option :value="null">Select a Class / Program</option>
          <option v-for="cls in classes" :key="cls.name" :value="cls.name">
            {{ cls.name }}
          </option>
        </select>
      </div>

      <div v-if="divisions.length > 0" class="form-group required">
        <label>Division / Student Group</label>
        <select 
          :value="selectedDivision" 
          class="picker"
          @change="onDivisionChange"
          :disabled="!selectedClass || divisionsResource?.loading"
        >
          <option :value="null">Select a Division / Student Group</option>
          <option v-for="div in divisions" :key="div.name" :value="div.name">
            {{ div.name }}
          </option>
        </select>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AcademicInfoCard',
  props: {
    selectedYear: [String, Number],
    selectedClass: [String, Number],
    selectedDivision: [String, Number],
    academicYears: {
      type: Array,
      default: () => []
    },
    classes: {
      type: Array,
      default: () => []
    },
    divisions: {
      type: Array,
      default: () => []
    },
    academicYearsResource: Object,
    classesResource: Object,
    divisionsResource: Object
  },
  emits: ['update:selectedYear', 'update:selectedClass', 'update:selectedDivision', 'year-change', 'class-change', 'division-change'],
  methods: {
    onYearChange(event) {
      const value = event.target.value;
      this.$emit('update:selectedYear', value);
      this.$emit('year-change', value);
    },
    
    onClassChange(event) {
      const value = event.target.value;
      this.$emit('update:selectedClass', value);
      this.$emit('class-change', value);
    },
    
    onDivisionChange(event) {
      const value = event.target.value;
      this.$emit('update:selectedDivision', value);
      this.$emit('division-change', value);
    }
  }
};
</script>