<template>
  <div class="academic-year-form">
    <div class="form-header">
      <h3 class="form-title">Academic Year Setup</h3>
      <p class="form-subtitle">
        Provide details about the academic year, its duration, and terms.
      </p>
    </div>

    <div class="form-grid">
      <!-- Academic Year Row -->
      <div class="form-row">
        <div class="form-group full-width">
          <label class="form-label">Academic Year</label>
          <input 
            type="text" 
            v-model="academicYear" 
            class="form-input"
            placeholder="e.g., 2023-2024"
            @input="updateField('academicYear', $event.target.value)"
          />
        </div>
      </div>

      <!-- Date Range Row -->
      <div class="form-row date-range-row">
        <div class="form-group">
          <label class="form-label">Start Date</label>
          <input 
            type="date" 
            v-model="academicYearStart"
            class="form-input"
            @input="updateField('academicYearStart', $event.target.value)"
          />
        </div>
        
        <div class="form-group">
          <label class="form-label">End Date</label>
          <input 
            type="date" 
            v-model="academicYearEnd"
            class="form-input"
            @input="updateField('academicYearEnd', $event.target.value)"
          />
        </div>
      </div>

      <!-- Number of Terms Row -->
      <div class="form-row">
        <div class="form-group full-width">
          <label class="form-label">Number of Terms</label>
          <div class="number-input-group">
            <input 
              type="number" 
              v-model.number="numberOfTerms" 
              class="form-input number-input"
              placeholder="e.g., 3"
              min="1"
              @input="handleNumberOfTermsChange"
            />
            <div class="number-input-buttons">
              <button 
                class="number-input-btn minus-btn"
                @click="decrementTerms"
                :disabled="numberOfTerms <= 1"
              >
                −
              </button>
              <button 
                class="number-input-btn plus-btn"
                @click="incrementTerms"
              >
                +
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Current Term Selection -->
      <div class="form-row">
        <div class="form-group full-width">
          <label class="form-label">Current Academic Term</label>
          <select 
            v-model="selectedTerm" 
            class="form-select"
            @change="updateField('selectedTerm', $event.target.value)"
          >
            <option value="">-- Select a Term --</option>
            <option 
              v-for="(term, index) in values.terms" 
              :key="index"
              :value="term.name"
            >
              {{ term.name }} ({{ formatDate(term.startDate) }} - {{ formatDate(term.endDate) }})
            </option>
          </select>
        </div>
      </div>
    </div>

    <!-- Terms List -->
    <div class="terms-list">
      <div v-for="(term, index) in values.terms" :key="index" class="term-card">
        <div class="term-header">
          <h4 class="term-title">Term {{ index + 1 }}</h4>
          <button 
            class="btn-icon"
            @click="removeTerm(index)"
            title="Remove term"
          >
            ✕
          </button>
        </div>
        
        <div class="term-body">
          <div class="form-group">
            <label class="form-label">Term Name</label>
            <input 
              type="text" 
              v-model="term.name" 
              class="form-input"
              :placeholder="`e.g., Spring ${index + 1}`"
              @input="updateTermField(index, 'name', $event.target.value)"
            />
          </div>

          <div class="form-row term-dates-row">
            <div class="form-group">
              <label class="form-label">Start Date</label>
              <input 
                type="date" 
                v-model="term.startDate"
                class="form-input"
                @input="updateTermField(index, 'startDate', $event.target.value)"
              />
            </div>
            
            <div class="form-group">
              <label class="form-label">End Date</label>
              <input 
                type="date" 
                v-model="term.endDate"
                class="form-input"
                @input="updateTermField(index, 'endDate', $event.target.value)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="form-actions">
      <button 
        class="btn btn-primary"
        @click="addTerm"
      >
        <span class="icon">+</span> Add Term
      </button>
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
      selectedTerm: '',
      lastValidTermCount: 0
    };
  },
  computed: {
    academicYear: {
      get() {
        return this.values.academicYear;
      },
      set(value) {
        this.$emit('update-field', { field: 'academicYear', value });
      }
    },
    academicYearStart: {
      get() {
        return this.values.academicYearStart;
      },
      set(value) {
        this.$emit('update-field', { field: 'academicYearStart', value });
      }
    },
    academicYearEnd: {
      get() {
        return this.values.academicYearEnd;
      },
      set(value) {
        this.$emit('update-field', { field: 'academicYearEnd', value });
      }
    },
    numberOfTerms: {
      get() {
        return this.values.numberOfTerms;
      },
      set(value) {
        this.$emit('update-field', { field: 'numberOfTerms', value });
      }
    }
  },
  methods: {
    handleNumberOfTermsChange(event) {
      const value = parseInt(event.target.value);
      if (!isNaN(value) && value > 0) {
        this.numberOfTerms = value;
        this.lastValidTermCount = value;
        this.adjustTermsToMatchCount();
      } else {
        this.numberOfTerms = this.lastValidTermCount;
      }
    },

    incrementTerms() {
      this.numberOfTerms = parseInt(this.numberOfTerms) + 1;
      this.adjustTermsToMatchCount();
    },

    decrementTerms() {
      if (this.numberOfTerms > 1) {
        this.numberOfTerms = parseInt(this.numberOfTerms) - 1;
        this.adjustTermsToMatchCount();
      }
    },

    adjustTermsToMatchCount() {
      const currentCount = this.values.terms.length;
      const targetCount = this.numberOfTerms;
      
      if (targetCount > currentCount) {
        // Add missing terms with calculated dates
        const termsToAdd = targetCount - currentCount;
        const newTerms = [...this.values.terms];
        
        for (let i = 0; i < termsToAdd; i++) {
          const termNumber = currentCount + i + 1;
          const { startDate, endDate } = this.calculateTermDates(termNumber, targetCount);
          newTerms.push({ 
            name: `Term ${termNumber}`,
            startDate,
            endDate
          });
        }
        
        this.$emit('update-field-array', {
          field: 'terms',
          value: newTerms
        });
      } else if (targetCount < currentCount) {
        // Remove excess terms (from the end)
        const termsToRemove = currentCount - targetCount;
        const newTerms = [...this.values.terms];
        newTerms.splice(-termsToRemove, termsToRemove);
        this.$emit('update-field-array', {
          field: 'terms',
          value: newTerms
        });
      }
    },

    calculateTermDates(termNumber, totalTerms) {
      if (!this.academicYearStart || !this.academicYearEnd) {
        return { startDate: '', endDate: '' };
      }

      const start = new Date(this.academicYearStart);
      const end = new Date(this.academicYearEnd);
      const academicYearDuration = end - start;
      const termDuration = academicYearDuration / totalTerms;
      
      const termStart = new Date(start.getTime() + (termDuration * (termNumber - 1)));
      const termEnd = new Date(start.getTime() + (termDuration * termNumber) - 1); // subtract 1ms to avoid overlap
      
      // Format as YYYY-MM-DD
      const formatDate = (date) => {
        return date.toISOString().split('T')[0];
      };

      return {
        startDate: formatDate(termStart),
        endDate: formatDate(termEnd)
      };
    },
    formatDate(dateString) {
      if (!dateString) return '';
      const options = { year: 'numeric', month: 'short', day: 'numeric' };
      return new Date(dateString).toLocaleDateString(undefined, options);
    },
    updateField(field, value) {
      this.$emit('update-field', { field, value });
    },
    updateTermField(index, subField, value) {
      this.$emit('update-field-array', { 
        field: 'terms', 
        index, 
        subField, 
        value 
      });
    },
    addTerm() {
      const newTerm = { name: '', startDate: '', endDate: '' };
      this.$emit('update-field-array', {
        field: 'terms',
        value: [...this.values.terms, newTerm]
      });
      // Update number of terms to match actual count
      this.numberOfTerms = this.values.terms.length;
    },
    removeTerm(index) {
      const updatedTerms = [...this.values.terms];
      updatedTerms.splice(index, 1);
      this.$emit('update-field-array', {
        field: 'terms',
        value: updatedTerms
      });
      // Update number of terms to match actual count
      this.numberOfTerms = updatedTerms.length;
    },
    handleTermsInput(event) {
      const value = parseInt(event.target.value);
      if (!isNaN(value) && value > 0) {
        this.numberOfTerms = value;
        this.lastValidTermCount = value;
        this.$emit('auto-create-terms');
      } else {
        // Reset to last valid value if input is invalid
        this.numberOfTerms = this.lastValidTermCount;
      }
    },
    incrementTerms() {
      this.numberOfTerms = parseInt(this.numberOfTerms) + 1;
      this.$emit('auto-create-terms');
    },
    decrementTerms() {
      if (this.numberOfTerms > 1) {
        this.numberOfTerms = parseInt(this.numberOfTerms) - 1;
        this.$emit('auto-create-terms');
      }
    }
  },
  mounted() {
    this.lastValidTermCount = this.numberOfTerms || 1;
  }
};
</script>

<style scoped>
/* Base Styles */
.academic-year-form {
  max-width: 800px;
  margin: 0 auto;
  padding: 16px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.form-header {
  margin-bottom: 20px;
  text-align: center;
}

.form-title {
  font-size: 1.4rem;
  color: #2c3e50;
  margin-bottom: 6px;
}

.form-subtitle {
  color: #7f8c8d;
  font-size: 0.9rem;
  margin: 0;
  line-height: 1.4;
}

.form-grid {
  display: grid;
  gap: 16px;
  margin-bottom: 20px;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  flex: 1;
  margin-bottom: 0;
}

.full-width {
  width: 100%;
}

.form-label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #34495e;
  font-size: 0.9rem;
}

.form-input,
.form-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: all 0.2s;
  height: 40px;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.form-select {
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 16px;
}

/* Number Input Group */
.number-input-group {
  display: flex;
  gap: 8px;
  align-items: center;
}

.number-input {
  flex: 1;
  text-align: center;
}

.number-input-buttons {
  display: flex;
  gap: 4px;
}

.number-input-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.number-input-btn:hover {
  background-color: #e0e0e0;
}

.number-input-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: #f5f5f5;
}

/* Terms List */
.terms-list {
  display: grid;
  gap: 16px;
  margin-bottom: 20px;
}

.term-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  background-color: #f9f9f9;
}

.term-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.term-title {
  margin: 0;
  font-size: 1.1rem;
  color: #2c3e50;
}

.term-body {
  display: grid;
  gap: 12px;
}

.btn-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: none;
  border: none;
  cursor: pointer;
  color: #e74c3c;
  font-size: 1.2rem;
  transition: all 0.2s;
}

.btn-icon:hover {
  background-color: rgba(231, 76, 60, 0.1);
}

.form-actions {
  display: flex;
  justify-content: center;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 12px 20px;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  font-size: 1rem;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-primary:hover {
  background-color: #2980b9;
}

.icon {
  margin-right: 6px;
}

/* Responsive Adjustments */
@media (min-width: 640px) {
  .form-row {
    flex-direction: row;
  }
  
  .date-range-row,
  .term-dates-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }
  
  .number-input-group {
    max-width: 300px;
  }
}

@media (max-width: 400px) {
  .form-input,
  .form-select {
    padding: 8px 10px;
    font-size: 0.95rem;
  }
  
  .number-input-btn {
    width: 36px;
    height: 36px;
  }
  
  .term-card {
    padding: 12px;
  }
}
</style>