<template>
  <div class="min-h-screen bg-gray-50 p-4">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-800">
        Edit Student: {{ studentData.student_name }}
        <span class="text-sm text-gray-500 font-normal ml-2">(ID: {{ studentId }})</span>
      </h1>
      <p class="text-gray-600" v-if="!settingsLoading">
        <span v-if="allowInstructorsModify" class="text-green-600 font-medium">
          ✓ Full editing access enabled
        </span>
        <span v-else class="text-orange-600 font-medium">
          ⚠ Limited editing access (Guardian fields only)
        </span>
      </p>
    </div>

    <!-- Loading State -->
    <div v-if="settingsLoading" class="flex justify-center items-center py-8">
      <div class="spinner"></div>
      <span class="ml-2 text-gray-600">Loading settings...</span>
    </div>

    <!-- Settings Error State -->
    <div v-else-if="settingsError" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
      <p class="text-red-800">Failed to load settings. Using default permissions.</p>
      <button @click="fetchAdminSettings" class="mt-2 px-3 py-1 bg-red-600 text-white rounded text-sm">
        Retry
      </button>
    </div>

    <!-- Edit Form -->
    <div v-else class="bg-white rounded-lg shadow-sm p-6">
      <form @submit.prevent="updateStudent">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <!-- Student ID (always readonly) -->
          <div class="md:col-span-2 lg:col-span-3">
            <label class="block text-sm font-medium text-gray-700 mb-2">Student ID</label>
            <input 
              :value="studentId"
              type="text" 
              readonly
              class="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100 text-gray-500"
            />
            <p class="text-xs text-gray-500 mt-1">Student ID cannot be changed</p>
          </div>

          <!-- Personal Details Section - Only show if allowed -->
          <div v-if="allowInstructorsModify" class="md:col-span-2 lg:col-span-3">
            <h3 class="text-lg font-medium text-gray-800 mb-4 border-b pb-2">Personal Details</h3>
          </div>

          <div v-if="allowInstructorsModify">
            <label class="block text-sm font-medium text-gray-700 mb-2">First Name</label>
            <input 
              v-model="studentData['First Name']"
              type="text" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div v-if="allowInstructorsModify">
            <label class="block text-sm font-medium text-gray-700 mb-2">Middle Name</label>
            <input 
              v-model="studentData['Middle Name']"
              type="text" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div v-if="allowInstructorsModify">
            <label class="block text-sm font-medium text-gray-700 mb-2">Last Name</label>
            <input 
              v-model="studentData['Last Name']"
              type="text" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div v-if="allowInstructorsModify">
            <label class="block text-sm font-medium text-gray-700 mb-2">Student Date of Birth</label>
            <input 
              v-model="studentData['Student Date of Birth']"
              type="date" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div v-if="allowInstructorsModify">
            <label class="block text-sm font-medium text-gray-700 mb-2">GR Number</label>
            <input 
              v-model="studentData['GR Number']"
              type="text" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <!-- Contact Information Section - Only show if allowed -->
          <div v-if="allowInstructorsModify" class="md:col-span-2 lg:col-span-3 mt-4">
            <h3 class="text-lg font-medium text-gray-800 mb-4 border-b pb-2">Contact Information</h3>
          </div>
          
          <div v-if="allowInstructorsModify">
            <label class="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
            <input 
              v-model="studentData['Email Address']"
              type="email" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div v-if="allowInstructorsModify">
            <label class="block text-sm font-medium text-gray-700 mb-2">Phone Number</label>
            <input 
              v-model="studentData['Phone Number']"
              type="tel" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <!-- Guardian Management Section -->
        <div class="md:col-span-2 lg:col-span-3 mt-8">
          <h3 class="text-lg font-medium text-gray-800 mb-4 border-b pb-2">
            Guardian Management
            <span class="text-sm text-blue-600 font-normal ml-2">(Manage multiple guardians)</span>
          </h3>
        </div>

        <!-- Add Guardian Section -->
        <div class="md:col-span-2 lg:col-span-3">
          <div 
            :class="[
              'bg-gray-50 rounded-lg p-6 border-2 border-dashed mb-6 transition-all',
              isGuardianLimitReached ? 'border-gray-300 opacity-50' : 'border-blue-200 hover:border-blue-300'
            ]"
          >
            <h4 class="text-lg font-semibold text-gray-800 mb-4">Add New Guardian</h4>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Guardian Name</label>
                <input 
                  v-model="newGuardian.guardian_name"
                  type="text"
                  placeholder="Enter guardian name"
                  :disabled="isGuardianLimitReached"
                  :class="[
                    'w-full px-3 py-2 border rounded-md',
                    isGuardianLimitReached 
                      ? 'border-gray-200 bg-gray-100 text-gray-500' 
                      : 'border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500'
                  ]"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Phone Number</label>
                <input 
                  v-model="newGuardian.phone_number"
                  type="tel"
                  placeholder="10-digit number"
                  :disabled="isGuardianLimitReached"
                  :class="[
                    'w-full px-3 py-2 border rounded-md',
                    isGuardianLimitReached 
                      ? 'border-gray-200 bg-gray-100 text-gray-500' 
                      : 'border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500'
                  ]"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Relation</label>
                <select 
                  v-model="newGuardian.relation"
                  :disabled="isGuardianLimitReached"
                  :class="[
                    'w-full px-3 py-2 border rounded-md',
                    isGuardianLimitReached 
                      ? 'border-gray-200 bg-gray-100 text-gray-500' 
                      : 'border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500'
                  ]"
                >
                  <option value="Mother">Mother</option>
                  <option value="Father">Father</option>
                  <option value="Others">Others</option>
                </select>
              </div>
            </div>

            <div class="mt-4 flex items-center justify-between">
              <div>
                <p v-if="isGuardianLimitReached" class="text-red-600 text-sm font-medium">
                  ❌ Maximum of 3 guardians reached
                </p>
                <p v-else class="text-gray-600 text-sm">
                  Guardians added: {{ guardians.length }}/3
                </p>
              </div>
              <button
                type="button"
                @click="addGuardian"
                :disabled="isGuardianLimitReached || addingGuardian"
                :class="[
                  'px-4 py-2 rounded-md flex items-center space-x-2 transition-colors',
                  isGuardianLimitReached || addingGuardian
                    ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                ]"
              >
                <span v-if="addingGuardian">Adding...</span>
                <span v-else>Add Guardian</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Existing Guardians Section -->
        <div class="md:col-span-2 lg:col-span-3">
          <div class="bg-white rounded-lg border border-gray-200 p-6">
            <h4 class="text-lg font-semibold text-gray-800 mb-4">Existing Guardians</h4>
            
            <div v-if="guardiansLoading" class="flex justify-center py-4">
              <div class="spinner-small"></div>
              <span class="ml-2 text-gray-600">Loading guardians...</span>
            </div>

            <div v-else-if="guardians.length === 0" class="text-center py-8 text-gray-500">
              <svg class="w-12 h-12 mx-auto text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
              </svg>
              <p>No guardians added yet.</p>
            </div>

            <div v-else class="space-y-4">
              <div 
                v-for="guardian in guardians" 
                :key="guardian.guardian || guardian.guardian_name"
                class="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors"
              >
                <div class="flex items-start justify-between">
                  <div class="flex items-start space-x-3 flex-1">
                    <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                      <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                    
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center space-x-2 mb-1">
                        <h5 class="font-medium text-gray-800 text-lg">{{ guardian.guardian_name }}</h5>
                        <span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                          {{ guardian.relation }}
                        </span>
                      </div>
                      
                      <!-- Guardian Details Display -->
                      <div v-if="editingGuardianId !== guardian.guardian" class="space-y-2 text-sm text-gray-600">
                        <div class="flex items-center space-x-4">
                          <span class="flex items-center space-x-1">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                            </svg>
                            <span>{{ guardian.mobile_number }}</span>
                          </span>
                          <span class="text-gray-400">•</span>
                          <span class="flex items-center space-x-1">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                            </svg>
                            <span>{{ guardian.guardian_email || 'No email' }}</span>
                          </span>
                        </div>
                        <div v-if="guardian.occupation || guardian.designation" class="flex items-center space-x-2 text-xs">
                          <span v-if="guardian.occupation">💼 {{ guardian.occupation }}</span>
                          <span v-if="guardian.designation" class="text-gray-400">•</span>
                          <span v-if="guardian.designation">🎯 {{ guardian.designation }}</span>
                        </div>
                      </div>

                      <!-- Guardian Edit Form -->
                      <div v-if="editingGuardianId === guardian.guardian" class="space-y-4 mt-4 p-4 bg-gray-50 rounded-lg">
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                          <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Guardian Name</label>
                            <input
                              v-model="editedGuardian.guardian_name"
                              type="text"
                              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                          </div>

                          <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Phone Number</label>
                            <input
                              v-model="editedGuardian.phone_number"
                              type="tel"
                              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                          </div>

                          <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Relation</label>
                            <select
                              v-model="editedGuardian.relation"
                              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                              <option value="Mother">Mother</option>
                              <option value="Father">Father</option>
                              <option value="Others">Others</option>
                            </select>
                          </div>

                          <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Date of Birth</label>
                            <input
                              v-model="editedGuardian.guardian_date_of_birth"
                              type="date"
                              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                          </div>

                          <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
                            <input
                              v-model="editedGuardian.guardian_email"
                              type="email"
                              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                          </div>

                          <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Occupation</label>
                            <input
                              v-model="editedGuardian.occupation"
                              type="text"
                              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                          </div>

                          <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Designation</label>
                            <input
                              v-model="editedGuardian.designation"
                              type="text"
                              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                          </div>

                          <div class="md:col-span-2">
                            <label class="block text-sm font-medium text-gray-700 mb-2">Work Address</label>
                            <textarea
                              v-model="editedGuardian.work_address"
                              rows="2"
                              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            ></textarea>
                          </div>

                          <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Education</label>
                            <input
                              v-model="editedGuardian.education"
                              type="text"
                              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                          </div>
                        </div>

                        <div class="flex space-x-3 pt-4">
                          <button
                            @click="updateGuardianDetails(guardian.guardian)"
                            :disabled="updatingGuardian"
                            class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-green-300 flex items-center space-x-2"
                          >
                            <svg v-if="updatingGuardian" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                            </svg>
                            <span>{{ updatingGuardian ? 'Updating...' : 'Update Guardian' }}</span>
                          </button>
                          <button
                            @click="cancelEdit"
                            class="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>

                  <button
                    v-if="editingGuardianId !== guardian.guardian"
                    @click="startEdit(guardian)"
                    class="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="Edit guardian details"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Form Actions -->
        <div class="mt-8 pt-6 border-t flex justify-between items-center">
          <div class="text-sm text-gray-600">
            <span v-if="allowInstructorsModify" class="text-green-600">
              ✓ You have full editing permissions
            </span>
            <span v-else class="text-orange-600">
              ⚠ You can only edit guardian information
            </span>
          </div>
          <div class="flex space-x-3">
            <button 
              type="button" 
              class="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
              @click="$router.back()"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-blue-300 disabled:cursor-not-allowed"
              :disabled="updateLoading"
            >
              <span v-if="updateLoading">Updating...</span>
              <span v-else>Update Student</span>
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, reactive } from 'vue'
import { useRoute } from 'vue-router'
import { createResource } from 'frappe-ui'

const route = useRoute()

// Reactive state
const studentData = ref({})
const studentId = ref('')
const settingsLoading = ref(true)
const settingsError = ref(false)
const updateLoading = ref(false)

// Guardian management state
const guardians = ref([])
const guardiansLoading = ref(false)
const editingGuardianId = ref(null)
const updatingGuardian = ref(false)
const addingGuardian = ref(false)

// New guardian form
const newGuardian = reactive({
  guardian_name: '',
  phone_number: '',
  relation: 'Mother'
})

// Edited guardian form
const editedGuardian = reactive({
  guardian_name: '',
  phone_number: '',
  relation: 'Mother',
  guardian_date_of_birth: '',
  guardian_email: '',
  occupation: '',
  designation: '',
  work_address: '',
  education: ''
})

// Admin settings
const adminSettings = ref({
  allow_instructors_modify_student: 0,
  session_expiry: "24:00"
})

// Computed properties
const allowInstructorsModify = computed(() => {
  return adminSettings.value.allow_instructors_modify_student === 1
})

const isGuardianLimitReached = computed(() => {
  return guardians.value.length >= 3
})

// API Resources
const adminSettingsResource = createResource({
  url: 'school.al_ummah.api3.fetch_admin_settings',
  auto: false,
  onSuccess(data) {
    adminSettings.value = data
    settingsLoading.value = false
    settingsError.value = false
  },
  onError(error) {
    console.error('Error fetching admin settings:', error)
    settingsLoading.value = false
    settingsError.value = true
    adminSettings.value = {
      allow_instructors_modify_student: 0,
      session_expiry: "24:00"
    }
  }
})

const updateStudentResource = createResource({
  url: 'school.al_ummah.api2.update_student_details',
  auto: false,
  onSuccess(data) {
    updateLoading.value = false
    console.log('Student updated successfully:', data)
    alert('Student information updated successfully!')
  },
  onError(error) {
    console.error('Error updating student:', error)
    updateLoading.value = false
    alert('Failed to update student information. Please try again.')
  }
})

const addGuardianResource = createResource({
  url: 'school.al_ummah.api2.add_guardian_to_student',
  auto: false,
  onSuccess() {
    addingGuardian.value = false
    fetchGuardians()
    resetNewGuardianForm()
  },
  onError(error) {
    console.error('Error adding guardian:', error)
    addingGuardian.value = false
    alert('Failed to add guardian. Please try again.')
  }
})

const getGuardiansResource = createResource({
  url: 'school.al_ummah.api2.get_student_guardian_names',
  auto: false,
  onSuccess(data) {
    guardians.value = data || []
    guardiansLoading.value = false
  },
  onError(error) {
    console.error('Error fetching guardians:', error)
    guardiansLoading.value = false
    guardians.value = []
  }
})

const updateGuardianDetailsResource = createResource({
  url: 'school.al_ummah.api2.update_guardian_details',
  auto: false,
  onSuccess() {
    updatingGuardian.value = false
    editingGuardianId.value = null
    resetEditedGuardianForm()
    fetchGuardians()
    alert('Guardian details updated successfully!')
  },
  onError(error) {
    console.error('Error updating guardian details:', error)
    updatingGuardian.value = false
    alert('Failed to update guardian details. Please try again.')
  }
})

// Helper functions
const isValidPhoneNumber = (number) => {
  return /^[0-9]{10}$/.test(number)
}

const resetNewGuardianForm = () => {
  newGuardian.guardian_name = ''
  newGuardian.phone_number = ''
  newGuardian.relation = 'Mother'
}

const resetEditedGuardianForm = () => {
  Object.keys(editedGuardian).forEach(key => {
    editedGuardian[key] = ''
  })
  editedGuardian.relation = 'Mother'
}

// Guardian management functions
const fetchGuardians = () => {
  guardiansLoading.value = true
  getGuardiansResource.fetch({ student: studentId.value })
}

const addGuardian = async () => {
  if (!isValidPhoneNumber(newGuardian.phone_number)) {
    alert('Please enter a valid 10-digit phone number.')
    return
  }

  if (!newGuardian.guardian_name.trim()) {
    alert('Please enter guardian name.')
    return
  }

  addingGuardian.value = true
  const params = {
    student_id: studentId.value,
    student_name: studentData.value.student_name,
    guardian_name: newGuardian.guardian_name,
    relation: newGuardian.relation,
    phone_number: newGuardian.phone_number,
  }

  addGuardianResource.fetch(params)
}

const startEdit = (guardian) => {
  editingGuardianId.value = guardian.guardian
  // Populate the edit form with current guardian data
  editedGuardian.guardian_name = guardian.guardian_name || ''
  editedGuardian.phone_number = guardian.mobile_number || ''
  editedGuardian.relation = guardian.relation || 'Mother'
  editedGuardian.guardian_date_of_birth = guardian.guardian_date_of_birth || ''
  editedGuardian.guardian_email = guardian.guardian_email || ''
  editedGuardian.occupation = guardian.occupation || ''
  editedGuardian.designation = guardian.designation || ''
  editedGuardian.work_address = guardian.work_address || ''
  editedGuardian.education = guardian.education || ''
}

const cancelEdit = () => {
  editingGuardianId.value = null
  resetEditedGuardianForm()
}

const updateGuardianDetails = (guardianId) => {
  if (!isValidPhoneNumber(editedGuardian.phone_number)) {
    alert('Please enter a valid 10-digit phone number.')
    return
  }

  if (!editedGuardian.guardian_name.trim()) {
    alert('Please enter guardian name.')
    return
  }

  updatingGuardian.value = true

  const params = {
    guardian_id: guardianId,
    guardian_name: editedGuardian.guardian_name,
    phone_number: editedGuardian.phone_number,
    relation: editedGuardian.relation,
    guardian_date_of_birth: editedGuardian.guardian_date_of_birth,
    guardian_email: editedGuardian.guardian_email,
    occupation: editedGuardian.occupation,
    designation: editedGuardian.designation,
    work_address: editedGuardian.work_address,
    education: editedGuardian.education
  }

  updateGuardianDetailsResource.fetch(params)
}

// Fetch admin settings
const fetchAdminSettings = () => {
  settingsLoading.value = true
  settingsError.value = false
  adminSettingsResource.fetch()
}

// Update student function
const updateStudent = async () => {
  updateLoading.value = true
  
  try {
    const updateData = {
      student_id: studentId.value,
    }

    if (allowInstructorsModify.value) {
      updateData.first_name = studentData.value['First Name'] || ''
      updateData.middle_name = studentData.value['Middle Name'] || ''
      updateData.last_name = studentData.value['Last Name'] || ''
      updateData.student_date_of_birth = studentData.value['Student Date of Birth'] || ''
      updateData.gr_number = studentData.value['GR Number'] || ''
      updateData.email_address = studentData.value['Email Address'] || ''
      updateData.phone_number = studentData.value['Phone Number'] || ''
    }

    console.log('Sending update data:', updateData)
    await updateStudentResource.fetch(updateData)
    
  } catch (error) {
    console.error('Error in update student:', error)
    updateLoading.value = false
  }
}

onMounted(() => {
  studentId.value = route.query.studentId
  
  if (route.query.studentData) {
    try {
      studentData.value = JSON.parse(decodeURIComponent(route.query.studentData))
      console.log('Student ID:', studentId.value)
      console.log('Complete student data:', studentData.value)
    } catch (error) {
      console.error('Error parsing student data:', error)
    }
  }

  fetchAdminSettings()
  fetchGuardians()
})
</script>

<style scoped>
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.spinner-small {
  width: 20px;
  height: 20px;
  border: 2px solid #e5e7eb;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>