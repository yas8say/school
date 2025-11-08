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

    <!-- Fee Structure Templates -->
    <div v-if="selectedInstitutionType" class="structure-templates-section">
      <div class="flex items-center justify-between mb-3">
        <label class="block text-sm font-medium text-gray-700">Fee Structure Templates</label>
        <span class="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
          {{ Object.keys(selectedTemplates).length }} selected
        </span>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div 
          v-for="template in feeStructureTemplates[selectedInstitutionType]" 
          :key="template.name"
          class="template-card p-3 border rounded-lg transition-all duration-200 cursor-pointer"
          :class="selectedTemplates[template.name] 
            ? 'border-blue-500 bg-blue-50 shadow-sm' 
            : 'border-gray-200 hover:border-blue-300 bg-white'"
          @click="toggleTemplate(template.name)"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <div 
                class="w-4 h-4 rounded border flex items-center justify-center transition-colors"
                :class="selectedTemplates[template.name] 
                  ? 'bg-blue-500 border-blue-500' 
                  : 'bg-white border-gray-300'"
              >
                <svg v-if="selectedTemplates[template.name]" class="w-2 h-2 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div>
                <h4 class="font-medium text-gray-900 text-sm">{{ template.name }}</h4>
                <p class="text-xs text-gray-500">{{ template.frequency }} • {{ template.categories.length }} categories</p>
              </div>
            </div>
            <div class="text-right">
              <span class="text-xs font-medium px-2 py-1 rounded-full"
                :class="getFrequencyBadgeClass(template.frequency)">
                {{ template.frequency }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Class-wise Fee Structures -->
    <div v-if="selectedInstitutionType && classes.length > 0" class="class-structures-section">
      <h4 class="text-md font-semibold text-gray-800 mb-4">Class-wise Fee Structures</h4>
      
      <div class="space-y-6">
        <div 
          v-for="(cls, classIndex) in classes" 
          :key="classIndex"
          class="class-fee-card p-4 border border-gray-200 rounded-lg bg-white shadow-sm"
        >
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center space-x-3">
              <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <span class="text-blue-600 font-medium text-sm">{{ classIndex + 1 }}</span>
              </div>
              <div>
                <h5 class="font-semibold text-gray-900">{{ cls.className }}</h5>
                <p class="text-xs text-gray-500">{{ getClassStructuresCount(classIndex) }} structures</p>
              </div>
            </div>
            <button
              @click="addNewStructure(classIndex)"
              class="px-3 py-1 bg-green-500 text-white rounded-lg hover:bg-green-600 text-sm font-medium transition-colors flex items-center space-x-1"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              <span>Add Structure</span>
            </button>
          </div>
          
<!-- Fee Structures for this Class -->
<div v-if="feeStructures[classIndex] && feeStructures[classIndex].length > 0" class="space-y-3">
  <div 
    v-for="(structure, structureIndex) in feeStructures[classIndex]" 
    :key="structureIndex"
    class="structure-card p-3 border border-gray-100 rounded-lg bg-gray-50"
  >
    <div class="flex items-center justify-between mb-2">
      <div class="flex items-center space-x-2">
        <input
          :value="structure.name"
          @input="updateStructureName(classIndex, structureIndex, $event.target.value)"
          class="font-medium text-gray-800 text-sm bg-transparent border-b border-transparent hover:border-gray-300 focus:border-blue-500 focus:outline-none px-1 py-0.5"
        />
    <div class="relative">
      <select
        :value="structure.frequency"
        @change="updateStructureFrequency(classIndex, structureIndex, $event.target.value)"
        class="text-xs font-medium pr-8 pl-3 py-1 rounded-full border bg-white focus:outline-none focus:ring-1 focus:ring-blue-500 transition-colors"
        :class="getFrequencySelectClass(structure.frequency)"
      >
        <option 
          v-for="freq in feeFrequencies" 
          :key="freq.value"
          :value="freq.value"
          class="text-gray-800"
        >
          {{ freq.label }}
        </option>
      </select>
      <div class="custom-select-arrow">
        <svg class="w-3 h-3 text-current" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
      </div>
      <div class="flex items-center space-x-1">
        <span class="text-xs text-gray-500">Total: ₹{{ calculateStructureTotal(classIndex, structureIndex).toLocaleString() }}</span>
        <button 
          v-if="feeStructures[classIndex].length > 1"
          @click="removeStructure(classIndex, structureIndex)"
          class="text-red-400 hover:text-red-600 transition-colors p-1"
          title="Remove structure"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </div>
              
              <!-- Fee Components for this Structure -->
              <div class="space-y-2">
                <div 
                  v-for="(component, compIndex) in structure.components" 
                  :key="compIndex"
                  class="component-item flex items-center justify-between p-2 bg-white rounded border border-gray-200"
                >
                  <div class="flex items-center space-x-3 flex-1">
                    <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <div class="flex-1 min-w-0">
                      <span class="text-sm font-medium text-gray-800 block truncate">{{ component.fees_category }}</span>
                    </div>
                  </div>
                  <div class="flex items-center space-x-2">
                    <div class="flex items-center space-x-1">
                      <span class="text-gray-500 text-xs">₹</span>
                      <input
                        type="number"
                        :value="component.amount"
                        @input="updateComponentAmount(classIndex, structureIndex, compIndex, $event.target.value)"
                        @blur="validateComponentAmount(component)"
                        class="w-20 px-2 py-1 text-xs border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>
                    <button 
                      @click="removeComponent(classIndex, structureIndex, compIndex)"
                      class="text-red-400 hover:text-red-600 transition-colors p-1"
                      title="Remove category"
                    >
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>

              <!-- Add Custom Category to this Structure -->
              <div class="flex space-x-2 mt-2">
                <input
                  :value="getCategoryInput(classIndex, structureIndex)"
                  @input="setCategoryInput(classIndex, structureIndex, $event.target.value)"
                  @keydown.enter="addCustomCategory(classIndex, structureIndex)"
                  placeholder="Custom category name..."
                  class="flex-1 px-2 py-1 border border-gray-300 rounded text-xs focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                />
                <div class="relative">
                  <span class="absolute left-2 top-1/2 transform -translate-y-1/2 text-gray-500 text-xs">₹</span>
                  <input
                    :value="getAmountInput(classIndex, structureIndex)"
                    @input="setAmountInput(classIndex, structureIndex, $event.target.value)"
                    type="number"
                    placeholder="Amount"
                    class="w-16 pl-6 pr-2 py-1 border border-gray-300 rounded text-xs focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <button
                  @click="addCustomCategory(classIndex, structureIndex)"
                  :disabled="!getCategoryInput(classIndex, structureIndex) || !getAmountInput(classIndex, structureIndex)"
                  class="px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-xs font-medium transition-colors"
                >
                  Add
                </button>
              </div>
            </div>
          </div>

          <!-- Empty State for Class -->
          <div v-else class="text-center py-4 text-gray-500 text-sm">
            No fee structures added. Click "Add Structure" to create one.
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
            <div class="text-2xl font-bold text-purple-600">{{ getTotalStructures() }}</div>
            <div class="text-gray-600 mt-1">Total Structures</div>
            <div class="font-semibold text-gray-800">{{ getTotalStructures() }}</div>
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
      selectedTemplates: {},
      newCategoryInputs: [],
      newAmountInputs: [],
      feeStructures: [],
      
      feeFrequencies: [
        { value: 'Monthly', label: 'Monthly' },
        { value: 'Quarterly', label: 'Quarterly' },
        { value: 'Semi-Annually', label: 'Semi-Annual' },
        { value: 'Annually', label: 'Annual' },
        { value: 'Term-Wise', label: 'Term-Wise' }
      ],
      
      // Pre-defined fee structure templates for School and College
      feeStructureTemplates: {
        school: [
          {
            name: 'Annual Fees',
            frequency: 'Annually',
            categories: [
              { name: 'Admission Fee', amount: 1000 },
              { name: 'Development Fee', amount: 1500 },
              { name: 'Uniform Fee', amount: 2500 }
            ]
          },
          {
            name: 'Monthly Tuition',
            frequency: 'Monthly',
            categories: [
              { name: 'Tuition Fee', amount: 5000 },
              { name: 'Transport Fee', amount: 3000 }
            ]
          },
          {
            name: 'Quarterly Fees',
            frequency: 'Quarterly',
            categories: [
              { name: 'Sports Fee', amount: 500 },
              { name: 'Library Fee', amount: 300 },
              { name: 'Lab Fee', amount: 800 },
              { name: 'Computer Fee', amount: 600 },
              { name: 'Exam Fee', amount: 400 },
              { name: 'Activity Fee', amount: 700 }
            ]
          }
        ],
        college: [
          {
            name: 'Annual Fees',
            frequency: 'Annually',
            categories: [
              { name: 'Admission Fee', amount: 5000 },
              { name: 'University Fee', amount: 3000 },
              { name: 'Sports Fee', amount: 800 },
              { name: 'Development Fee', amount: 2500 },
              { name: 'Identity Card', amount: 200 },
              { name: 'Study Material', amount: 3000 },
              { name: 'Placement Fee', amount: 2000 }
            ]
          },
          {
            name: 'Semi-Annual Tuition',
            frequency: 'Semi-Annually',
            categories: [
              { name: 'Tuition Fee', amount: 15000 },
              { name: 'Library Fee', amount: 1000 },
              { name: 'Lab Fee', amount: 2000 },
              { name: 'Computer Fee', amount: 1500 },
              { name: 'Exam Fee', amount: 1000 }
            ]
          }
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
        this.feeStructures = newClasses.map(() => [])
        // Initialize input arrays
        this.newCategoryInputs = new Array(newClasses.length).fill({})
        this.newAmountInputs = new Array(newClasses.length).fill({})
      }
    },
    selectedTemplates: {
      handler(newTemplates) {
        this.applyTemplatesToAll()
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
  getFrequencySelectClass(frequency) {
    const classes = {
      'Monthly': 'border-blue-200 text-blue-800 bg-blue-50',
      'Quarterly': 'border-purple-200 text-purple-800 bg-purple-50',
      'Semi-Annually': 'border-orange-200 text-orange-800 bg-orange-50',
      'Annually': 'border-green-200 text-green-800 bg-green-50',
      'Term-Wise': 'border-red-200 text-red-800 bg-red-50'
    }
    return classes[frequency] || 'border-gray-200 text-gray-800 bg-gray-50'
  },
    getFrequencyBadgeClass(frequency) {
      const classes = {
        'Monthly': 'bg-blue-100 text-blue-800 border-blue-200',
        'Quarterly': 'bg-purple-100 text-purple-800 border-purple-200',
        'Semi-Annually': 'bg-orange-100 text-orange-800 border-orange-200',
        'Annually': 'bg-green-100 text-green-800 border-green-200',
        'Term-Wise': 'bg-red-100 text-red-800 border-red-200'
      }
      return classes[frequency] || 'bg-gray-100 text-gray-800 border-gray-200'
    },
    
    selectInstitutionType(type) {
      this.selectedInstitutionType = type
      this.selectedTemplates = {}
      this.feeStructures = this.classes.map(() => [])
    },
    
    toggleTemplate(templateName) {
      // Vue 3 way - directly assign to reactive object
      if (this.selectedTemplates[templateName]) {
        delete this.selectedTemplates[templateName]
        // Create a new object to trigger reactivity
        this.selectedTemplates = { ...this.selectedTemplates }
      } else {
        this.selectedTemplates = {
          ...this.selectedTemplates,
          [templateName]: true
        }
      }
    },
    
    // Update the applyTemplatesToAll method to preserve custom frequencies
    applyTemplatesToAll() {
      const selectedTemplateNames = Object.keys(this.selectedTemplates)
      
      this.feeStructures = this.classes.map((cls, classIndex) => {
        const existingStructures = this.feeStructures[classIndex] || []
        
        // Remove structures that are from unselected templates
        const filteredStructures = existingStructures.filter(structure => 
          !structure.templateName || selectedTemplateNames.includes(structure.templateName)
        )
        
        // Add structures for newly selected templates
        const newStructures = selectedTemplateNames
          .filter(templateName => !filteredStructures.some(s => s.templateName === templateName))
          .map(templateName => {
            const template = this.feeStructureTemplates[this.selectedInstitutionType]
              .find(t => t.name === templateName)
            
            return {
              name: template.name,
              frequency: template.frequency,
              templateName: template.name,
              components: template.categories.map(cat => ({
                fees_category: cat.name,
                amount: cat.amount,
                discount: 0,
                total: cat.amount
              }))
            }
          })
        
        return [...filteredStructures, ...newStructures]
      })
    },
    
    updateStructureName(classIndex, structureIndex, name) {
      this.feeStructures[classIndex][structureIndex].name = name
    },
    
    updateStructureFrequency(classIndex, structureIndex, frequency) {
      this.feeStructures[classIndex][structureIndex].frequency = frequency
    },

    // Update the addNewStructure method to include frequency selection
    addNewStructure(classIndex) {
      if (!this.feeStructures[classIndex]) {
        this.feeStructures[classIndex] = []
      }
      
      const structureCount = this.feeStructures[classIndex].length + 1
      this.feeStructures[classIndex].push({
        name: `Custom Structure ${structureCount}`,
        frequency: 'Monthly', // Default frequency
        templateName: null,
        components: []
      })
      
      // Initialize inputs for this new structure
      if (!this.newCategoryInputs[classIndex]) {
        this.newCategoryInputs[classIndex] = {}
        this.newAmountInputs[classIndex] = {}
      }
      
      // Vue 3 way - directly assign
      this.newCategoryInputs[classIndex][this.feeStructures[classIndex].length - 1] = ''
      this.newAmountInputs[classIndex][this.feeStructures[classIndex].length - 1] = 0
      
      // Trigger reactivity by creating new arrays
      this.newCategoryInputs = [...this.newCategoryInputs]
      this.newAmountInputs = [...this.newAmountInputs]
    },

    removeStructure(classIndex, structureIndex) {
      this.feeStructures[classIndex].splice(structureIndex, 1)
      
      // Clean up inputs - Vue 3 way
      if (this.newCategoryInputs[classIndex]) {
        delete this.newCategoryInputs[classIndex][structureIndex]
        this.newCategoryInputs = [...this.newCategoryInputs]
      }
      if (this.newAmountInputs[classIndex]) {
        delete this.newAmountInputs[classIndex][structureIndex]
        this.newAmountInputs = [...this.newAmountInputs]
      }
    },
    
    updateComponentAmount(classIndex, structureIndex, compIndex, amount) {
      const component = this.feeStructures[classIndex][structureIndex].components[compIndex]
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
    
    getCategoryInput(classIndex, structureIndex) {
      return this.newCategoryInputs[classIndex]?.[structureIndex] || ''
    },
    
    setCategoryInput(classIndex, structureIndex, value) {
      if (!this.newCategoryInputs[classIndex]) {
        this.newCategoryInputs[classIndex] = {}
      }
      this.newCategoryInputs[classIndex][structureIndex] = value
      // Trigger reactivity
      this.newCategoryInputs = [...this.newCategoryInputs]
    },
    
    getAmountInput(classIndex, structureIndex) {
      return this.newAmountInputs[classIndex]?.[structureIndex] || 0
    },
    
    setAmountInput(classIndex, structureIndex, value) {
      if (!this.newAmountInputs[classIndex]) {
        this.newAmountInputs[classIndex] = {}
      }
      this.newAmountInputs[classIndex][structureIndex] = parseFloat(value) || 0
      // Trigger reactivity
      this.newAmountInputs = [...this.newAmountInputs]
    },
    
    addCustomCategory(classIndex, structureIndex) {
      const categoryName = this.getCategoryInput(classIndex, structureIndex)?.trim()
      const amount = this.getAmountInput(classIndex, structureIndex)
      
      if (categoryName && amount > 0) {
        const structure = this.feeStructures[classIndex][structureIndex]
        
        // Check if category already exists in this structure
        const existingIndex = structure.components.findIndex(
          comp => comp.fees_category.toLowerCase() === categoryName.toLowerCase()
        )
        
        if (existingIndex >= 0) {
          // Update existing category
          structure.components[existingIndex].amount = amount
          structure.components[existingIndex].total = amount
        } else {
          // Add new category
          structure.components.push({
            fees_category: categoryName,
            amount: amount,
            discount: 0,
            total: amount
          })
        }
        
        // Clear inputs
        this.setCategoryInput(classIndex, structureIndex, '')
        this.setAmountInput(classIndex, structureIndex, 0)
      }
    },
    
    removeComponent(classIndex, structureIndex, compIndex) {
      // Remove only from this specific structure
      this.feeStructures[classIndex][structureIndex].components.splice(compIndex, 1)
    },
    
    calculateStructureTotal(classIndex, structureIndex) {
      const structure = this.feeStructures[classIndex][structureIndex]
      return structure.components.reduce((total, comp) => total + comp.amount, 0)
    },
    
    getClassStructuresCount(classIndex) {
      return this.feeStructures[classIndex] ? this.feeStructures[classIndex].length : 0
    },
    
    getTotalStructures() {
      return this.feeStructures.reduce((total, classStructures) => 
        total + (classStructures ? classStructures.length : 0), 0
      )
    },
    
    getTotalCategories() {
      return this.feeStructures.reduce((total, classStructures) => 
        total + (classStructures ? classStructures.reduce((classTotal, structure) => 
          classTotal + structure.components.length, 0) : 0), 0
      )
    },
    
    getGrandTotal() {
      return this.feeStructures.reduce((total, classStructures) => 
        total + (classStructures ? classStructures.reduce((classTotal, structure) => 
          classTotal + structure.components.reduce((structureTotal, comp) => 
            structureTotal + comp.amount, 0), 0) : 0), 0
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
/* Remove default dropdown arrow for all browsers */
select {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  background-image: none;
}

/* Remove default arrow in IE */
select::-ms-expand {
  display: none;
}

/* Ensure custom arrow is properly positioned */
.relative select {
  padding-right: 1.75rem; /* More space for custom arrow */
}

/* Custom arrow styling */
.custom-select-arrow {
  pointer-events: none;
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
}

.institution-card:hover {
  transform: translateY(-1px);
}

.template-card:hover {
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