<template>
  <div class="bg-white shadow rounded-lg p-6 space-y-6">
    <h3 class="text-lg font-semibold text-gray-800 border-b pb-3">Create Fee Structures</h3>
    
    <!-- Institution Type Selection -->
    <div class="institution-type-section">
      <label class="block text-sm font-medium text-gray-700 mb-3">Select Institution Type</label>
      <div class="grid grid-cols-2 gap-4">
        <div 
          class="institution-card p-4 border-2 rounded-lg cursor-pointer transition-all duration-200"
          :class="selectedInstitutionType === 'school' 
            ? 'border-blue-500 bg-blue-50 shadow-sm' 
            : 'border-gray-200 hover:border-blue-300 bg-white'"
          @click="selectInstitutionType('school')"
        >
          <div class="text-center">
            <div class="w-10 h-10 mx-auto mb-2 bg-blue-100 rounded-full flex items-center justify-center">
              <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l9-5-9-5-9 5 9 5z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l9-5-9-5-9 5 9 5zm0 0l9 5m-9-5v8" />
              </svg>
            </div>
            <h4 class="font-medium text-gray-900 text-sm">School</h4>
            <p class="text-xs text-gray-500 mt-1">Primary & Secondary</p>
          </div>
        </div>
        
        <div 
          class="institution-card p-4 border-2 rounded-lg cursor-pointer transition-all duration-200"
          :class="selectedInstitutionType === 'college' 
            ? 'border-green-500 bg-green-50 shadow-sm' 
            : 'border-gray-200 hover:border-green-300 bg-white'"
          @click="selectInstitutionType('college')"
        >
          <div class="text-center">
            <div class="w-10 h-10 mx-auto mb-2 bg-green-100 rounded-full flex items-center justify-center">
              <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <h4 class="font-medium text-gray-900 text-sm">College</h4>
            <p class="text-xs text-gray-500 mt-1">Higher Education</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Global Fee Categories -->
    <div v-if="selectedInstitutionType" class="global-categories-section">
      <div class="flex items-center justify-between mb-3">
        <label class="block text-sm font-medium text-gray-700">Common Fee Categories</label>
        <span class="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
          {{ selectedGlobalCategories.length }} selected
        </span>
      </div>
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
        <div 
          v-for="category in feeCategories[selectedInstitutionType]" 
          :key="category.name"
          class="category-card p-2 border rounded-lg transition-all duration-200 h-20 flex flex-col"
          :class="getCategoryCardClass(category.name)"
        >
          <!-- Category Header -->
          <div class="flex items-center justify-between mb-1">
            <div class="flex items-center space-x-2 flex-1 min-w-0">
              <div 
                class="w-4 h-4 rounded border flex items-center justify-center cursor-pointer transition-colors"
                :class="selectedGlobalCategories.includes(category.name) 
                  ? 'bg-blue-500 border-blue-500' 
                  : 'bg-white border-gray-300'"
                @click="toggleGlobalCategory(category.name)"
              >
                <svg v-if="selectedGlobalCategories.includes(category.name)" class="w-2 h-2 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h4 class="font-medium text-gray-900 text-xs leading-tight truncate flex-1">{{ category.name }}</h4>
            </div>
          </div>
          
          <!-- Editable Amount -->
          <div class="flex items-center space-x-1">
            <span class="text-gray-500 text-xs flex-shrink-0">₹</span>
            <input
              type="number"
              v-model="category.editableAmount"
              @input="updateGlobalCategoryAmount(category.name, $event.target.value)"
              @blur="validateAmount(category)"
              :disabled="!selectedGlobalCategories.includes(category.name)"
              class="w-full px-1 py-0.5 text-xs border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:text-gray-500"
              :class="selectedGlobalCategories.includes(category.name) 
                ? 'bg-white text-gray-900' 
                : 'bg-gray-50 text-gray-400'"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Class-wise Fee Structures -->
    <div v-if="selectedInstitutionType && classes.length > 0" class="class-structures-section">
      <h4 class="text-md font-semibold text-gray-800 mb-4">Class-wise Fee Structures</h4>
      
      <div class="space-y-4">
        <div 
          v-for="(cls, index) in classes" 
          :key="index"
          class="class-fee-card p-4 border border-gray-200 rounded-lg bg-white shadow-sm"
        >
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center space-x-3">
              <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <span class="text-blue-600 font-medium text-sm">{{ index + 1 }}</span>
              </div>
              <div>
                <h5 class="font-semibold text-gray-900">{{ cls.className }}</h5>
                <p class="text-xs text-gray-500">Total: ₹{{ calculateClassTotal(index).toLocaleString() }}</p>
              </div>
            </div>
            <span class="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
              {{ feeStructures[index].components.length }} categories
            </span>
          </div>
          
          <!-- Fee Components for this Class -->
          <div v-if="feeStructures[index].components.length > 0" class="space-y-2 mb-3">
            <div 
              v-for="(component, compIndex) in feeStructures[index].components" 
              :key="compIndex"
              class="component-item flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-100"
            >
              <div class="flex items-center space-x-3 flex-1">
                <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
                <div class="flex-1 min-w-0">
                  <span class="text-sm font-medium text-gray-800 block truncate">{{ component.fees_category }}</span>
                  <div class="flex items-center space-x-1 mt-1">
                    <span class="text-gray-500 text-xs">₹</span>
                    <input
                      type="number"
                      v-model="component.amount"
                      @input="updateComponentAmount(index, compIndex, $event.target.value)"
                      @blur="validateComponentAmount(component)"
                      class="w-20 px-2 py-1 text-xs border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>
              </div>
              <button 
                @click="removeComponent(index, compIndex)"
                class="text-red-400 hover:text-red-600 transition-colors p-1"
                title="Remove category"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Add Custom Category -->
          <div class="flex space-x-2">
            <input
              v-model="newCategoryInputs[index]"
              @keydown.enter="addCustomCategory(index)"
              placeholder="Custom category name..."
              class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <div class="relative">
              <span class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 text-sm">₹</span>
              <input
                v-model="newAmountInputs[index]"
                type="number"
                placeholder="Amount"
                class="w-24 pl-8 pr-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <button
              @click="addCustomCategory(index)"
              :disabled="!newCategoryInputs[index] || !newAmountInputs[index]"
              class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-sm font-medium transition-colors"
            >
              Add
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Summary -->
    <div v-if="selectedInstitutionType && classes.length > 0" class="summary-section">
      <h4 class="text-md font-semibold text-gray-800 mb-3">Summary</h4>
      <div class="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-lg border border-blue-100">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div class="text-center">
            <div class="text-2xl font-bold text-blue-600">{{ selectedInstitutionType === 'school' ? '🏫' : '🎓' }}</div>
            <div class="text-gray-600 mt-1">Institution</div>
            <div class="font-semibold text-gray-800 capitalize">{{ selectedInstitutionType }}</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-green-600">{{ classes.length }}</div>
            <div class="text-gray-600 mt-1">Total Classes</div>
            <div class="font-semibold text-gray-800">{{ classes.length }}</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-purple-600">{{ selectedGlobalCategories.length }}</div>
            <div class="text-gray-600 mt-1">Global Categories</div>
            <div class="font-semibold text-gray-800">{{ selectedGlobalCategories.length }}</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-orange-600">{{ getTotalCategories() }}</div>
            <div class="text-gray-600 mt-1">Total Categories</div>
            <div class="font-semibold text-gray-800">{{ getTotalCategories() }}</div>
          </div>
        </div>
        <div class="mt-4 pt-4 border-t border-blue-200">
          <div class="text-center">
            <div class="text-lg font-bold text-gray-800">₹{{ getGrandTotal().toLocaleString() }}</div>
            <div class="text-gray-600 text-sm">Grand Total Across All Classes</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="selectedInstitutionType && classes.length === 0" class="text-center py-8">
      <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
        <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </div>
      <h4 class="text-lg font-medium text-gray-900 mb-2">No Classes Found</h4>
      <p class="text-gray-500 text-sm">Please go back and set up classes first to create fee structures.</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FeeStructureCreator',
  props: {
    values: Object
  },
  data() {
    return {
      selectedInstitutionType: '',
      selectedGlobalCategories: [],
      newCategoryInputs: [],
      newAmountInputs: [],
      feeStructures: [],
      
      // Indian School & College Fee Categories with editable amounts
      feeCategories: {
        school: [
          { name: 'Tuition Fee', suggestedAmount: 5000, editableAmount: 5000 },
          { name: 'Admission Fee', suggestedAmount: 1000, editableAmount: 1000 },
          { name: 'Annual Charges', suggestedAmount: 2000, editableAmount: 2000 },
          { name: 'Sports Fee', suggestedAmount: 500, editableAmount: 500 },
          { name: 'Library Fee', suggestedAmount: 300, editableAmount: 300 },
          { name: 'Lab Fee', suggestedAmount: 800, editableAmount: 800 },
          { name: 'Computer Fee', suggestedAmount: 600, editableAmount: 600 },
          { name: 'Transport Fee', suggestedAmount: 3000, editableAmount: 3000 },
          { name: 'Exam Fee', suggestedAmount: 400, editableAmount: 400 },
          { name: 'Development Fee', suggestedAmount: 1500, editableAmount: 1500 },
          { name: 'Activity Fee', suggestedAmount: 700, editableAmount: 700 },
          { name: 'Uniform Fee', suggestedAmount: 2500, editableAmount: 2500 }
        ],
        college: [
          { name: 'Tuition Fee', suggestedAmount: 15000, editableAmount: 15000 },
          { name: 'Admission Fee', suggestedAmount: 5000, editableAmount: 5000 },
          { name: 'University Fee', suggestedAmount: 3000, editableAmount: 3000 },
          { name: 'Library Fee', suggestedAmount: 1000, editableAmount: 1000 },
          { name: 'Lab Fee', suggestedAmount: 2000, editableAmount: 2000 },
          { name: 'Computer Fee', suggestedAmount: 1500, editableAmount: 1500 },
          { name: 'Sports Fee', suggestedAmount: 800, editableAmount: 800 },
          { name: 'Exam Fee', suggestedAmount: 1000, editableAmount: 1000 },
          { name: 'Development Fee', suggestedAmount: 2500, editableAmount: 2500 },
          { name: 'Identity Card', suggestedAmount: 200, editableAmount: 200 },
          { name: 'Study Material', suggestedAmount: 3000, editableAmount: 3000 },
          { name: 'Placement Fee', suggestedAmount: 2000, editableAmount: 2000 }
        ]
      }
    }
  },
  computed: {
    classes() {
      return this.values.classes || []
    }
  },
  watch: {
    classes: {
      immediate: true,
      handler(newClasses) {
        // Initialize fee structures for each class
        this.feeStructures = newClasses.map(() => ({
          components: []
        }))
        // Initialize input arrays
        this.newCategoryInputs = new Array(newClasses.length).fill('')
        this.newAmountInputs = new Array(newClasses.length).fill(0)
      }
    },
    selectedGlobalCategories: {
      handler(newCategories) {
        this.applyGlobalCategoriesToAll()
      },
      deep: true
    },
    feeStructures: {
      handler(newStructures) {
        this.emitFeeStructures()
      },
      deep: true
    }
  },
  methods: {
    getCategoryCardClass(categoryName) {
      return this.selectedGlobalCategories.includes(categoryName) 
        ? 'border-blue-500 bg-blue-50 shadow-sm' 
        : 'border-gray-200 hover:border-blue-300 bg-white hover:shadow-sm'
    },
    
    selectInstitutionType(type) {
      this.selectedInstitutionType = type
      this.selectedGlobalCategories = []
      this.feeStructures = this.classes.map(() => ({ components: [] }))
    },
    
    toggleGlobalCategory(categoryName) {
      const index = this.selectedGlobalCategories.indexOf(categoryName)
      if (index >= 0) {
        this.selectedGlobalCategories.splice(index, 1)
      } else {
        this.selectedGlobalCategories.push(categoryName)
      }
    },
    
    updateGlobalCategoryAmount(categoryName, amount) {
      const category = this.feeCategories[this.selectedInstitutionType].find(cat => cat.name === categoryName)
      if (category) {
        category.editableAmount = parseFloat(amount) || 0
        this.applyGlobalCategoriesToAll()
      }
    },
    
    validateAmount(category) {
      if (category.editableAmount <= 0) {
        category.editableAmount = category.suggestedAmount
      }
      this.applyGlobalCategoriesToAll()
    },
    
    updateComponentAmount(classIndex, compIndex, amount) {
      const component = this.feeStructures[classIndex].components[compIndex]
      if (component) {
        component.amount = parseFloat(amount) || 0
        component.total = component.amount
      }
    },
    
    validateComponentAmount(component) {
      if (component.amount <= 0) {
        component.amount = 0
        component.total = 0
      }
    },
    
    applyGlobalCategoriesToAll() {
      this.feeStructures = this.feeStructures.map(structure => {
        // Remove any global categories that are no longer selected
        const filteredComponents = structure.components.filter(comp => 
          !this.feeCategories[this.selectedInstitutionType].some(cat => cat.name === comp.fees_category)
        )
        
        // Add currently selected global categories with updated amounts
        const globalComponents = this.selectedGlobalCategories.map(categoryName => {
          const category = this.feeCategories[this.selectedInstitutionType].find(cat => cat.name === categoryName)
          return {
            fees_category: categoryName,
            amount: category.editableAmount,
            discount: 0,
            total: category.editableAmount
          }
        })
        
        return {
          components: [...globalComponents, ...filteredComponents]
        }
      })
    },
    
    addCustomCategory(classIndex) {
      const categoryName = this.newCategoryInputs[classIndex]?.trim()
      const amount = parseFloat(this.newAmountInputs[classIndex]) || 0
      
      if (categoryName && amount > 0) {
        // Check if category already exists
        const existingIndex = this.feeStructures[classIndex].components.findIndex(
          comp => comp.fees_category.toLowerCase() === categoryName.toLowerCase()
        )
        
        if (existingIndex >= 0) {
          // Update existing category
          this.feeStructures[classIndex].components[existingIndex].amount = amount
          this.feeStructures[classIndex].components[existingIndex].total = amount
        } else {
          // Add new category
          this.feeStructures[classIndex].components.push({
            fees_category: categoryName,
            amount: amount,
            discount: 0,
            total: amount
          })
        }
        
        // Clear inputs
        this.newCategoryInputs[classIndex] = ''
        this.newAmountInputs[classIndex] = 0
      }
    },
    
    removeComponent(classIndex, compIndex) {
      const component = this.feeStructures[classIndex].components[compIndex]
      
      // If it's a global category, remove it from selected global categories
      const isGlobalCategory = this.feeCategories[this.selectedInstitutionType].some(
        cat => cat.name === component.fees_category
      )
      
      if (isGlobalCategory) {
        const globalIndex = this.selectedGlobalCategories.indexOf(component.fees_category)
        if (globalIndex >= 0) {
          this.selectedGlobalCategories.splice(globalIndex, 1)
        }
      } else {
        // Remove the component directly
        this.feeStructures[classIndex].components.splice(compIndex, 1)
      }
    },
    
    calculateClassTotal(classIndex) {
      return this.feeStructures[classIndex].components.reduce(
        (total, comp) => total + comp.amount, 0
      )
    },
    
    getTotalCategories() {
      return this.feeStructures.reduce(
        (total, structure) => total + structure.components.length, 0
      )
    },
    
    getGrandTotal() {
      return this.feeStructures.reduce(
        (total, structure) => total + structure.components.reduce(
          (classTotal, comp) => classTotal + comp.amount, 0
        ), 0
      )
    },
    
    emitFeeStructures() {
      this.$emit('update-field', {
        field: 'feeStructures',
        value: this.feeStructures
      })
    }
  }
}
</script>

<style scoped>
.institution-card:hover {
  transform: translateY(-1px);
}

.category-card {
  transition: all 0.2s ease;
}

.category-card:hover {
  transform: translateY(-1px);
}

.component-item {
  transition: all 0.2s ease;
}

.component-item:hover {
  background-color: #f8fafc;
  border-color: #e2e8f0;
}

/* Custom scrollbar for better UX */
.class-structures-section {
  max-height: 60vh;
  overflow-y: auto;
}

.class-structures-section::-webkit-scrollbar {
  width: 6px;
}

.class-structures-section::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.class-structures-section::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.class-structures-section::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Input styling for better appearance */
input[type="number"] {
  -moz-appearance: textfield;
}

input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
</style>