<template>
  <div class="bg-white shadow rounded-lg p-6 space-y-6">
    <!-- Saved Common Structures -->
    <div v-if="savedCommonStructures.length > 0" class="saved-structures-section">
      <label class="block text-sm font-medium text-gray-700 mb-3">
        Saved Common Structures
      </label>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="(savedStructure, index) in savedCommonStructures"
          :key="savedStructure.id"
          class="saved-structure-card p-4 border border-gray-200 rounded-lg bg-white shadow-sm cursor-pointer hover:shadow-md transition-shadow relative"
          :class="{ 'border-blue-500 bg-blue-50': currentStructureId === savedStructure.id }"
          @click="loadSavedStructure(savedStructure.id)"
        >
          <!-- Delete Button -->
          <button
            @click.stop="deleteSavedStructure(savedStructure.id, $event)"
            class="absolute top-2 right-2 text-red-500 hover:text-red-700 transition-colors"
            title="Delete this structure from all programs"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>

          <div class="flex items-center justify-between mb-2 pr-8">
            <h4 class="font-semibold text-gray-800 text-sm">{{ savedStructure.name }}</h4>
            <span class="text-xs font-medium px-2 py-1 rounded-full"
                  :class="getFrequencyBadgeClass(savedStructure.frequency)">
              {{ savedStructure.frequency }}
            </span>
          </div>
          <div class="text-xs text-gray-600 mb-2">
            {{ savedStructure.categories.length }} categories • ₹{{ calculateSavedStructureTotal(savedStructure).toLocaleString() }}
          </div>
          <div class="flex flex-wrap gap-1">
            <span
              v-for="(category, catIndex) in savedStructure.categories.slice(0, 3)"
              :key="catIndex"
              class="inline-block px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
            >
              {{ category.name }}
            </span>
            <span v-if="savedStructure.categories.length > 3" class="inline-block px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
              +{{ savedStructure.categories.length - 3 }} more
            </span>
          </div>
          <div v-if="currentStructureId === savedStructure.id" class="mt-2 text-xs text-blue-600 font-medium">
            ✓ Connected
          </div>
        </div>
      </div>
    </div>

    <!-- Common Structure Builder (Always Visible) -->
    <div class="create-structure-section">
      <div class="flex items-center justify-between mb-4">
        <label class="block text-sm font-medium text-gray-700">
          Common Structure Builder
        </label>
        <button
          @click="startNewStructure"
          class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 text-sm font-medium transition-colors flex items-center space-x-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          <span>Reset</span>
        </button>
      </div>

      <!-- Common Structure Builder -->
      <div class="common-structure-builder bg-blue-50 p-4 rounded-lg border border-gray-200 mb-4">
        <div class="flex items-center justify-between mb-4">
          <h4 class="text-lg font-semibold text-gray-800">
            {{ currentStructureId ? 'Editing Common Structure' : 'Building Common Structure' }}
          </h4>
          <button
            @click="saveCommonStructure"
            :disabled="!commonStructure.name || commonStructure.categories.length === 0"
            class="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-sm font-medium transition-colors flex items-center space-x-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <span>{{ currentStructureId ? 'Update Structure' : 'Save Common Structure' }}</span>
          </button>
        </div>

        <!-- Common Structure Configuration -->
        <div class="space-y-4">
          <!-- Structure Name and Frequency -->
          <div class="flex items-center space-x-4">
            <div class="flex-1">
              <label class="block text-sm font-medium text-gray-700 mb-1">Structure Name</label>
              <input
                v-model="commonStructure.name"
                @keydown.enter="onStructureNameEnter"
                placeholder="e.g., Annual Fees, Basic Charges, etc."
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div class="w-48">
              <label class="block text-sm font-medium text-gray-700 mb-1">Frequency</label>
              <div class="relative">
                <select
                  v-model="commonStructure.frequency"
                  class="w-full text-sm font-medium pr-8 pl-3 py-2 rounded-md border bg-white focus:outline-none focus:ring-1 focus:ring-blue-500 transition-colors"
                  :class="getFrequencySelectClass(commonStructure.frequency)"
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
                  <svg class="w-4 h-4 text-current" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>
            </div>
          </div>

          <!-- Common Categories Display -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Common Categories</label>
            <div class="flex flex-wrap items-center gap-2 p-3 bg-white rounded border border-gray-200 min-h-[60px]">
              <div
                v-for="(category, idx) in commonStructure.categories"
                :key="idx"
                class="inline-flex items-center px-3 py-2 rounded-lg bg-blue-100 text-blue-800 text-sm border border-blue-200"
              >
                <div class="flex items-center space-x-2">
                  <span class="font-medium">{{ category.name }}</span>
                  <span class="text-blue-600">₹{{ category.amount.toLocaleString() }}</span>
                  <button
                    @click="removeCommonCategory(idx)"
                    class="ml-2 text-blue-500 hover:text-blue-700 transition-colors"
                  >
                    ×
                  </button>
                </div>
              </div>
             
              <!-- Add Common Category Input -->
              <div class="flex items-center space-x-2 flex-1 min-w-[200px]">
                <input
                  type="text"
                  v-model="newCommonCategory.name"
                  @keydown.enter="addCommonCategory"
                  placeholder="Add common category..."
                  class="flex-1 px-3 py-2 border border-gray-300 rounded text-sm focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                />
                <div class="relative">
                  <span class="absolute left-2 top-1/2 transform -translate-y-1/2 text-gray-500 text-sm">₹</span>
                  <input
                    type="number"
                    v-model="newCommonCategory.amount"
                    @keydown.enter="addCommonCategory"
                    placeholder="Amount"
                    class="w-24 pl-6 pr-3 py-2 border border-gray-300 rounded text-sm focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
            </div>

            <!-- Quick Select Common Categories -->
            <div class="quick-select mt-3">
              <h3 class="text-sm font-medium text-gray-700 mb-2">Quick Select Common Categories</h3>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
                <div
                  v-for="category in quickSelectCategories"
                  :key="category.name"
                  class="category-card px-3 py-2 border rounded-md text-center cursor-pointer text-sm"
                  :class="{
                    'bg-blue-100 border-blue-300': isCommonCategorySelected(category.name),
                    'bg-gray-50 hover:bg-gray-100': !isCommonCategorySelected(category.name)
                  }"
                  @click="toggleCommonCategory(category)"
                >
                  <div class="font-medium">{{ category.name }}</div>
                  <div class="text-xs text-gray-600">₹{{ category.amount.toLocaleString() }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Structure Summary -->
          <div class="bg-white p-3 rounded border border-gray-200">
            <div class="flex items-center justify-between">
              <span class="text-sm font-medium text-gray-700">Total Amount:</span>
              <span class="text-lg font-bold text-blue-600">₹{{ calculateCommonStructureTotal().toLocaleString() }}</span>
            </div>
            <div class="text-xs text-gray-500 mt-1">
              {{ currentStructureId ? 'Editing connected structure - changes update all programs' : 'Create new structure or select a saved one above' }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Class-wise Fee Structures -->
    <div v-if="classes.length > 0" class="class-structures-section">
      <div class="flex items-center justify-between mb-4">
        <h4 class="text-md font-semibold text-gray-800">Class-wise Fee Structures</h4>
        <span class="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
          {{ getTotalStructures() }} structures across {{ classes.length }} classes
        </span>
      </div>
     
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

              <!-- Connection Status -->
              <div v-if="structure.savedStructureId" class="mb-2">
                <span class="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                  <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  Connected to Saved Structure
                </span>
              </div>
             
              <!-- Fee Components for this Structure -->
              <div class="space-y-2">
                <!-- Common Categories (from applied common structures) -->
                <div
                  v-for="(commonCategory, commonIdx) in getAppliedCommonCategories(classIndex, structureIndex)"
                  :key="'common-' + commonIdx"
                  class="component-item flex items-center justify-between p-2 bg-white rounded border text-sm border-blue-200 bg-blue-50"
                >
                  <div class="flex items-center space-x-3 flex-1">
                    <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <div class="flex-1 min-w-0">
                      <span class="font-medium text-gray-800 block truncate">
                        {{ commonCategory.name }}
                        <span class="text-blue-600 text-xs ml-1">(Common)</span>
                      </span>
                    </div>
                  </div>
                  <div class="flex items-center space-x-2">
                    <div class="flex items-center space-x-1">
                      <span class="text-gray-500 text-xs">₹</span>
                      <input
                        type="number"
                        :value="commonCategory.amount"
                        @input="updateCommonCategoryAmount(classIndex, structureIndex, commonCategory.name, $event.target.value)"
                        class="w-20 px-2 py-1 text-xs border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>
                    <button
                      @click="removeCommonCategoryFromStructure(classIndex, structureIndex, commonCategory.name)"
                      class="text-red-400 hover:text-red-600 transition-colors p-1"
                      title="Remove common category"
                    >
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>

                <!-- Class-specific Categories (EDITABLE LABELS) -->
                <div
                  v-for="(component, compIndex) in structure.components"
                  :key="'specific-' + compIndex"
                  class="component-item flex items-center justify-between p-2 bg-white rounded border border-gray-200"
                >
                  <div class="flex items-center space-x-3 flex-1">
                    <div class="w-2 h-2 bg-green-500 rounded-full"></div>
                    <div class="flex-1 min-w-0">
                      <!-- EDITABLE CATEGORY LABEL -->
                      <input
                        type="text"
                        :value="component.fees_category"
                        @input="updateComponentLabel(classIndex, structureIndex, compIndex, $event.target.value)"
                        @blur="validateComponentLabel(classIndex, structureIndex, compIndex)"
                        class="w-full bg-transparent border-b border-transparent hover:border-gray-300 focus:border-green-500 focus:outline-none px-1 py-0.5 text-sm font-medium text-gray-800"
                        placeholder="Category name..."
                      />
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
                    @keydown.enter="addCustomCategory(classIndex, structureIndex)"
                    type="number"
                    placeholder="Amount"
                    class="w-16 pl-6 pr-2 py-1 border border-gray-300 rounded text-xs focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <button
                  @click="addCustomCategory(classIndex, structureIndex)"
                  :disabled="!getCategoryInput(classIndex, structureIndex) || !getAmountInput(classIndex, structureIndex)"
                  class="px-2 py-1 bg-green-500 text-white rounded hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-xs font-medium transition-colors"
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
    <div v-if="classes.length > 0" class="summary-section">
      <h4 class="text-md font-semibold text-gray-800 mb-3">Summary</h4>
      <div class="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-lg border border-blue-100">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div class="text-center">
            <div class="text-2xl font-bold text-blue-600">{{ institutionType === 'school' ? 'School' : 'College' }}</div>
            <div class="text-gray-600 mt-1">Institution</div>
            <div class="font-semibold text-gray-800 capitalize">{{ institutionType }}</div>
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
    <div v-if="classes.length === 0" class="text-center py-8">
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
      selectedTemplates: {},
      newCategoryInputs: [],
      newAmountInputs: [],
      feeStructures: [],
     
      // Common Structure Management
      savedCommonStructures: [],
      currentStructureId: null, // Tracks which saved structure is currently loaded
      commonStructure: {
        name: '',
        frequency: 'Annually',
        categories: []
      },
      newCommonCategory: {
        name: '',
        amount: 0
      },
     
      // Quick select categories
      quickSelectCategories: [
        { name: 'Tuition Fee', amount: 5000 },
        { name: 'Admission Fee', amount: 1000 },
        { name: 'Library Fee', amount: 500 },
        { name: 'Sports Fee', amount: 800 },
        { name: 'Lab Fee', amount: 1200 },
        { name: 'Exam Fee', amount: 600 },
        { name: 'Transport Fee', amount: 3000 },
        { name: 'Development Fee', amount: 2000 }
      ],
     
      feeFrequencies: [
        { value: 'Monthly', label: 'Monthly' },
        { value: 'Quarterly', label: 'Quarterly' },
        { value: 'Semi-Annually', label: 'Semi-Annual' },
        { value: 'Annually', label: 'Annual' },
        { value: 'Term-Wise', label: 'Term-Wise' }
      ]
    }
  },
  computed: {
    classes() {
      return this.values.classes || []
    },
    institutionType() {
      return this.values.selectedInstitution || 'school'
    },
    isEditingSavedStructure() {
      return this.currentStructureId !== null;
    }
  },
  watch: {
    classes: {
      immediate: true,
      handler(newClasses) {
        this.feeStructures = newClasses.map(() => [])
        this.newCategoryInputs = new Array(newClasses.length).fill({})
        this.newAmountInputs = new Array(newClasses.length).fill({})
      }
    },
    feeStructures: {
      handler(newStructures) {
        this.emitFeeStructures()
      },
      deep: true
    }
  },
  methods: {
    // === Core Logic ===
    
    // When structure name is entered via Enter key
    onStructureNameEnter() {
      if (this.commonStructure.name.trim()) {
        this.addStructureToAllPrograms();
      }
    },
    
    // Add structure to all programs (only called when creating NEW structure)
    addStructureToAllPrograms() {
      if (!this.commonStructure.name.trim() || this.commonStructure.categories.length === 0) return;
      
      // Don't add if we're editing a saved structure
      if (this.isEditingSavedStructure) return;
      
      this.classes.forEach((cls, classIndex) => {
        if (!this.feeStructures[classIndex]) {
          this.feeStructures[classIndex] = [];
        }
        
        // Check if structure with same name and frequency already exists
        const existingIndex = this.feeStructures[classIndex].findIndex(
          structure => structure.name === this.commonStructure.name && 
                      structure.frequency === this.commonStructure.frequency
        );
        
        if (existingIndex === -1) {
          // Create new structure
          const newStructure = {
            name: this.commonStructure.name,
            frequency: this.commonStructure.frequency,
            templateName: null,
            components: [],
            commonCategories: [...this.commonStructure.categories], // Copy categories
            savedStructureId: null // No saved structure ID for new structures
          };
          this.feeStructures[classIndex].push(newStructure);
        } else {
          // Update existing structure
          const structure = this.feeStructures[classIndex][existingIndex];
          structure.commonCategories = [...this.commonStructure.categories];
          structure.savedStructureId = null; // Clear saved structure ID when manually updated
        }
      });
      
      this.feeStructures = [...this.feeStructures];
    },
    
    // Connect selected saved structure to all programs
    connectSavedStructureToAllPrograms(savedStructure) {
      if (!savedStructure) return;
      
      this.classes.forEach((cls, classIndex) => {
        if (!this.feeStructures[classIndex]) {
          this.feeStructures[classIndex] = [];
        }
        
        // Check if structure with same name and frequency already exists
        const existingIndex = this.feeStructures[classIndex].findIndex(
          structure => structure.name === savedStructure.name && 
                      structure.frequency === savedStructure.frequency
        );
        
        if (existingIndex === -1) {
          // Create new structure with saved structure ID
          const newStructure = {
            name: savedStructure.name,
            frequency: savedStructure.frequency,
            templateName: null,
            components: [],
            commonCategories: [...savedStructure.categories],
            savedStructureId: savedStructure.id // Link to saved structure
          };
          this.feeStructures[classIndex].push(newStructure);
        } else {
          // Update existing structure with saved structure ID
          const structure = this.feeStructures[classIndex][existingIndex];
          structure.commonCategories = [...savedStructure.categories];
          structure.savedStructureId = savedStructure.id; // Link to saved structure
        }
      });
      
      this.feeStructures = [...this.feeStructures];
    },
    
    // Remove saved structure from all programs by unique ID
    removeSavedStructureFromAllPrograms(structureId) {
      this.classes.forEach((_, classIndex) => {
        if (!this.feeStructures[classIndex]) return;

        // Remove structures that have matching savedStructureId
        this.feeStructures[classIndex] = this.feeStructures[classIndex].filter(structure => {
          if (structure.savedStructureId === structureId) {
            return false; // Remove structure
          }
          return true;
        });
      });

      // Remove from saved list
      this.savedCommonStructures = this.savedCommonStructures.filter(s => s.id !== structureId);
      
      // Clear current structure if it was the one being deleted
      if (this.currentStructureId === structureId) {
        this.startNewStructure();
      }

      this.$emit('update-field', { field: 'savedCommonStructures', value: this.savedCommonStructures });
      this.feeStructures = [...this.feeStructures];
    },
    
    // Update programs when editing a saved structure
    updateProgramsWithCurrentStructure() {
      if (!this.isEditingSavedStructure || !this.commonStructure.name) return;
      
      const currentSavedStructure = this.savedCommonStructures.find(s => s.id === this.currentStructureId);
      if (!currentSavedStructure) return;
      
      this.classes.forEach((cls, classIndex) => {
        if (!this.feeStructures[classIndex]) return;
        
        // Find and update structures that have matching savedStructureId
        this.feeStructures[classIndex].forEach(structure => {
          if (structure.savedStructureId === this.currentStructureId) {
            structure.commonCategories = [...this.commonStructure.categories];
            structure.name = this.commonStructure.name; // Update name if changed
            structure.frequency = this.commonStructure.frequency; // Update frequency if changed
          }
        });
      });
      
      this.feeStructures = [...this.feeStructures];
    },
    
    // === Common Structure Management ===
    
    // Reset to create new structure
    startNewStructure() {
      this.currentStructureId = null;
      this.commonStructure = {
        name: '',
        frequency: 'Annually',
        categories: []
      };
      this.newCommonCategory = {
        name: '',
        amount: 0
      };
    },
    
    // Load saved structure for editing and connect it to programs
    loadSavedStructure(structureId) {
      const savedStructure = this.savedCommonStructures.find(s => s.id === structureId);
      if (savedStructure) {
        // Disconnect current structure first
        if (this.currentStructureId) {
          this.disconnectCurrentStructure();
        }
        
        // Load the new structure
        this.commonStructure = JSON.parse(JSON.stringify(savedStructure));
        this.currentStructureId = structureId;
        
        // Connect the selected structure to all programs
        this.connectSavedStructureToAllPrograms(savedStructure);
      }
    },
    
    // Disconnect current structure from programs (remove savedStructureId)
    disconnectCurrentStructure() {
      if (!this.currentStructureId) return;
      
      this.classes.forEach((_, classIndex) => {
        if (!this.feeStructures[classIndex]) return;
        
        this.feeStructures[classIndex].forEach(structure => {
          if (structure.savedStructureId === this.currentStructureId) {
            structure.savedStructureId = null; // Disconnect but keep the structure
          }
        });
      });
      
      this.feeStructures = [...this.feeStructures];
    },
    
    // Save common structure (does NOT apply to programs)
    saveCommonStructure() {
      if (!this.commonStructure.name || this.commonStructure.categories.length === 0) return;
      
      if (this.isEditingSavedStructure) {
        // Update existing saved structure
        const index = this.savedCommonStructures.findIndex(s => s.id === this.currentStructureId);
        if (index !== -1) {
          this.savedCommonStructures[index] = {
            ...this.commonStructure,
            id: this.currentStructureId
          };
          
          // Update programs with the new structure data
          this.updateProgramsWithCurrentStructure();
        }
      } else {
        // Create new saved structure
        const newStructureId = Date.now() + Math.random().toString(36).substr(2, 9);
        const newSavedStructure = {
          ...this.commonStructure,
          id: newStructureId
        };
        
        this.savedCommonStructures.unshift(newSavedStructure);
        this.currentStructureId = newStructureId;
        
        // Connect the new saved structure to programs
        this.connectSavedStructureToAllPrograms(newSavedStructure);
      }
      
      this.$emit('update-field', {
        field: 'savedCommonStructures',
        value: this.savedCommonStructures
      });
    },
    
    // Delete saved structure card and remove from all programs
    deleteSavedStructure(structureId, event) {
      event.stopPropagation(); // Prevent triggering loadSavedStructure
      if (confirm('Are you sure you want to delete this saved structure? This will remove it from all programs.')) {
        this.removeSavedStructureFromAllPrograms(structureId);
      }
    },
    
    // === Category Management ===
    
    addCommonCategory() {
      if (this.newCommonCategory.name.trim() && this.newCommonCategory.amount > 0) {
        const existingIndex = this.commonStructure.categories.findIndex(
          cat => cat.name.toLowerCase() === this.newCommonCategory.name.trim().toLowerCase()
        );
       
        if (existingIndex >= 0) {
          this.commonStructure.categories[existingIndex].amount = this.newCommonCategory.amount;
        } else {
          this.commonStructure.categories.push({
            name: this.newCommonCategory.name.trim(),
            amount: this.newCommonCategory.amount
          });
        }
       
        this.newCommonCategory.name = '';
        this.newCommonCategory.amount = 0;
        
        // Auto-update programs based on context
        if (this.isEditingSavedStructure) {
          this.updateProgramsWithCurrentStructure();
        } else if (this.commonStructure.name) {
          this.addStructureToAllPrograms();
        }
      }
    },
    
    removeCommonCategory(index) {
      this.commonStructure.categories.splice(index, 1);
      
      // Auto-update programs based on context
      if (this.isEditingSavedStructure) {
        this.updateProgramsWithCurrentStructure();
      } else if (this.commonStructure.name) {
        this.addStructureToAllPrograms();
      }
    },
    
    isCommonCategorySelected(categoryName) {
      return this.commonStructure.categories.some(cat => cat.name === categoryName);
    },
    
    toggleCommonCategory(category) {
      if (this.isCommonCategorySelected(category.name)) {
        const index = this.commonStructure.categories.findIndex(cat => cat.name === category.name);
        this.removeCommonCategory(index);
      } else {
        this.newCommonCategory.name = category.name;
        this.newCommonCategory.amount = category.amount;
        this.addCommonCategory();
      }
    },
    
    // === UI Helper Methods ===
    
    calculateCommonStructureTotal() {
      return this.commonStructure.categories.reduce((total, cat) => total + cat.amount, 0);
    },
    
    calculateSavedStructureTotal(structure) {
      return structure.categories.reduce((total, cat) => total + cat.amount, 0);
    },
    
    getAppliedCommonCategories(classIndex, structureIndex) {
      const structure = this.feeStructures[classIndex]?.[structureIndex];
      return structure?.commonCategories || [];
    },
    
    removeCommonCategoryFromStructure(classIndex, structureIndex, categoryName) {
      const structure = this.feeStructures[classIndex][structureIndex];
      if (structure.commonCategories) {
        const index = structure.commonCategories.findIndex(cat => cat.name === categoryName);
        if (index !== -1) {
          structure.commonCategories.splice(index, 1);
          this.feeStructures = [...this.feeStructures];
        }
      }
    },
    
    updateCommonCategoryAmount(classIndex, structureIndex, categoryName, amount) {
      const structure = this.feeStructures[classIndex][structureIndex];
      if (structure.commonCategories) {
        const category = structure.commonCategories.find(cat => cat.name === categoryName);
        if (category) {
          category.amount = parseFloat(amount) || 0;
          this.feeStructures = [...this.feeStructures];
        }
      }
    },

    getFrequencySelectClass(frequency) {
      const classes = {
        'Monthly': 'border-blue-200 text-blue-800 bg-blue-50',
        'Quarterly': 'border-purple-200 text-purple-800 bg-purple-50',
        'Semi-Annually': 'border-orange-200 text-orange-800 bg-orange-50',
        'Annually': 'border-green-200 text-green-800 bg-green-50',
        'Term-Wise': 'border-red-200 text-red-800 bg-red-50'
      };
      return classes[frequency] || 'border-gray-200 text-gray-800 bg-gray-50';
    },
   
    getFrequencyBadgeClass(frequency) {
      const classes = {
        'Monthly': 'bg-blue-100 text-blue-800 border-blue-200',
        'Quarterly': 'bg-purple-100 text-purple-800 border-purple-200',
        'Semi-Annually': 'bg-orange-100 text-orange-800 border-orange-200',
        'Annually': 'bg-green-100 text-green-800 border-green-200',
        'Term-Wise': 'bg-red-100 text-red-800 border-red-200'
      };
      return classes[frequency] || 'bg-gray-100 text-gray-800 border-gray-200';
    },

    // === Class Structure Management ===
    updateComponentLabel(classIndex, structureIndex, compIndex, value) {
      const component = this.feeStructures[classIndex][structureIndex].components[compIndex];
      if (component) component.fees_category = value;
    },
    
    validateComponentLabel(classIndex, structureIndex, compIndex) {
      const component = this.feeStructures[classIndex][structureIndex].components[compIndex];
      if (component && !component.fees_category.trim()) {
        component.fees_category = 'Unnamed Category';
      }
    },
    
    updateStructureName(classIndex, structureIndex, name) {
      this.feeStructures[classIndex][structureIndex].name = name;
    },
    
    updateStructureFrequency(classIndex, structureIndex, frequency) {
      this.feeStructures[classIndex][structureIndex].frequency = frequency;
    },

    addNewStructure(classIndex) {
      if (!this.feeStructures[classIndex]) this.feeStructures[classIndex] = [];
      const structureCount = this.feeStructures[classIndex].length + 1;
      this.feeStructures[classIndex].push({
        name: `Custom Structure ${structureCount}`,
        frequency: 'Monthly',
        templateName: null,
        components: [],
        commonCategories: [],
        savedStructureId: null
      });
      if (!this.newCategoryInputs[classIndex]) {
        this.newCategoryInputs[classIndex] = {};
        this.newAmountInputs[classIndex] = {};
      }
      this.newCategoryInputs[classIndex][this.feeStructures[classIndex].length - 1] = '';
      this.newAmountInputs[classIndex][this.feeStructures[classIndex].length - 1] = 0;
      this.newCategoryInputs = [...this.newCategoryInputs];
      this.newAmountInputs = [...this.newAmountInputs];
    },

    removeStructure(classIndex, structureIndex) {
      this.feeStructures[classIndex].splice(structureIndex, 1);
      if (this.newCategoryInputs[classIndex]) {
        delete this.newCategoryInputs[classIndex][structureIndex];
        this.newCategoryInputs = [...this.newCategoryInputs];
      }
      if (this.newAmountInputs[classIndex]) {
        delete this.newAmountInputs[classIndex][structureIndex];
        this.newAmountInputs = [...this.newAmountInputs];
      }
    },
    
    updateComponentAmount(classIndex, structureIndex, compIndex, amount) {
      const component = this.feeStructures[classIndex][structureIndex].components[compIndex];
      if (component) {
        component.amount = parseFloat(amount) || 0;
        component.total = component.amount;
      }
    },
    
    validateComponentAmount(component) {
      if (component.amount <= 0) {
        component.amount = 0;
        component.total = 0;
      }
    },
    
    getCategoryInput(classIndex, structureIndex) {
      return this.newCategoryInputs[classIndex]?.[structureIndex] || '';
    },
    
    setCategoryInput(classIndex, structureIndex, value) {
      if (!this.newCategoryInputs[classIndex]) this.newCategoryInputs[classIndex] = {};
      this.newCategoryInputs[classIndex][structureIndex] = value;
      this.newCategoryInputs = [...this.newCategoryInputs];
    },
    
    getAmountInput(classIndex, structureIndex) {
      return this.newAmountInputs[classIndex]?.[structureIndex] || 0;
    },
    
    setAmountInput(classIndex, structureIndex, value) {
      if (!this.newAmountInputs[classIndex]) this.newAmountInputs[classIndex] = {};
      this.newAmountInputs[classIndex][structureIndex] = parseFloat(value) || 0;
      this.newAmountInputs = [...this.newAmountInputs];
    },
    
    addCustomCategory(classIndex, structureIndex) {
      const categoryName = this.getCategoryInput(classIndex, structureIndex)?.trim();
      const amount = this.getAmountInput(classIndex, structureIndex);
      if (categoryName && amount > 0) {
        const structure = this.feeStructures[classIndex][structureIndex];
        const existingIndex = structure.components.findIndex(
          comp => comp.fees_category.toLowerCase() === categoryName.toLowerCase()
        );
        if (existingIndex >= 0) {
          structure.components[existingIndex].amount = amount;
          structure.components[existingIndex].total = amount;
        } else {
          structure.components.push({
            fees_category: categoryName,
            amount: amount,
            discount: 0,
            total: amount
          });
        }
        this.setCategoryInput(classIndex, structureIndex, '');
        this.setAmountInput(classIndex, structureIndex, 0);
      }
    },
    
    removeComponent(classIndex, structureIndex, compIndex) {
      this.feeStructures[classIndex][structureIndex].components.splice(compIndex, 1);
    },
    
    calculateStructureTotal(classIndex, structureIndex) {
      const structure = this.feeStructures[classIndex][structureIndex];
      let total = 0;
      if (structure.commonCategories) {
        total += structure.commonCategories.reduce((sum, cat) => sum + cat.amount, 0);
      }
      total += structure.components.reduce((sum, comp) => sum + comp.amount, 0);
      return total;
    },
    
    getClassStructuresCount(classIndex) {
      return this.feeStructures[classIndex] ? this.feeStructures[classIndex].length : 0;
    },
    
    getTotalStructures() {
      return this.feeStructures.reduce((total, classStructures) => 
        total + (classStructures ? classStructures.length : 0), 0
      );
    },
    
    getTotalCategories() {
      let total = 0;
      this.feeStructures.forEach(classStructures => {
        if (classStructures) {
          classStructures.forEach(structure => {
            if (structure.commonCategories) total += structure.commonCategories.length;
            total += structure.components.length;
          });
        }
      });
      return total;
    },
    
    getGrandTotal() {
      let total = 0;
      this.feeStructures.forEach((classStructures, classIndex) => {
        if (classStructures) {
          classStructures.forEach((structure, structureIndex) => {
            total += this.calculateStructureTotal(classIndex, structureIndex);
          });
        }
      });
      return total;
    },
    
    emitFeeStructures() {
      this.$emit('update-field', {
        field: 'feeStructures',
        value: this.feeStructures
      });
    }
  }
}
</script>

<style scoped>
.saved-structure-card {
  position: relative;
}
.saved-structure-card:hover {
  transform: translateY(-2px);
  transition: all 0.2s ease;
}
.category-card:hover {
  transform: translateY(-1px);
  transition: all 0.2s ease;
}
select {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
}
select::-ms-expand { display: none; }
.relative select { padding-right: 1.75rem; }
.custom-select-arrow {
  pointer-events: none;
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
}
.component-item {
  transition: all 0.2s ease;
}
.component-item:hover {
  background-color: #f8fafc;
  border-color: #e2e8f0;
}
.class-structures-section {
  max-height: 60vh;
  overflow-y: auto;
}
.class-structures-section::-webkit-scrollbar { width: 6px; }
.class-structures-section::-webkit-scrollbar-track { background: #f1f5f9; border-radius: 3px; }
.class-structures-section::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
.class-structures-section::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
input[type="number"] { -moz-appearance: textfield; }
input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
</style>