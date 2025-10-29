<template>
  <div class="min-h-screen bg-gray-50 p-4">
    <!-- Alert Notifications -->
    <div class="fixed top-4 right-4 z-50 space-y-2 w-full max-w-sm px-4 sm:px-0 sm:w-96">
      <!-- Success Alert -->
      <div 
        v-if="successMessage" 
        class="bg-green-50 border border-green-200 rounded-lg p-4 shadow-lg transform transition-all duration-300 ease-in-out"
        :class="alertAnimation"
      >
        <div class="flex items-start space-x-3">
          <div class="flex-shrink-0">
            <svg class="w-5 h-5 text-green-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="flex-1">
            <p class="text-green-800 font-medium">Success</p>
            <p class="text-green-700 text-sm mt-1">{{ successMessage }}</p>
          </div>
        </div>
        <!-- OK Button -->
        <div class="mt-4 flex justify-end">
          <button 
            type="button"
            @click="hideAlert" 
            class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors text-sm font-medium"
          >
            OK
          </button>
        </div>
      </div>

      <!-- Error Alert -->
      <div 
        v-if="errorMessage" 
        class="bg-red-50 border border-red-200 rounded-lg p-4 shadow-lg transform transition-all duration-300 ease-in-out"
        :class="alertAnimation"
      >
        <div class="flex items-start space-x-3">
          <div class="flex-shrink-0">
            <svg class="w-5 h-5 text-red-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="flex-1">
            <p class="text-red-800 font-medium">Error</p>
            <p class="text-red-700 text-sm mt-1">{{ errorMessage }}</p>
          </div>
        </div>
        <!-- OK Button -->
        <div class="mt-4 flex justify-end">
          <button 
            type="button"
            @click="hideAlert" 
            class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors text-sm font-medium"
          >
            OK
          </button>
        </div>
      </div>
    </div>
    
    <div class="mb-6">
      <h1 class="text-xl sm:text-2xl font-bold text-gray-800">
        Edit Student: {{ studentInfo.student_name || studentId }}
        <span class="text-xs sm:text-sm text-gray-500 font-normal ml-2">(ID: {{ studentId }})</span>
      </h1>
      <p class="text-gray-600 text-sm sm:text-base" v-if="!settingsLoading">
        <span v-if="allowInstructorsModify" class="text-green-600 font-medium">
          ✓ Full editing access enabled
        </span>
        <span v-else class="text-orange-600 font-medium">
          ⚠ Limited editing access (Guardian fields only)
        </span>
      </p>
    </div>

    <!-- Loading State -->
    <div v-if="studentDetailsResource.loading || settingsLoading" class="flex justify-center items-center py-8">
      <div class="spinner"></div>
      <span class="ml-2 text-gray-600">Loading student details...</span>
    </div>

    <!-- Settings Error State -->
    <div v-else-if="settingsError" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
      <p class="text-red-800">Failed to load settings. Using default permissions.</p>
      <button 
        type="button"
        @click="fetchAdminSettings" 
        class="mt-2 px-3 py-1 bg-red-600 text-white rounded text-sm"
      >
        Retry
      </button>
    </div>

    <!-- Student Details Error -->
    <div v-else-if="studentDetailsError" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
      <p class="text-red-800">Failed to load student details.</p>
      <button 
        type="button"
        @click="fetchStudentDetails" 
        class="mt-2 px-3 py-1 bg-red-600 text-white rounded text-sm"
      >
        Retry
      </button>
    </div>

    <!-- Edit Form -->
    <div v-else class="bg-white rounded-lg shadow-sm p-4 sm:p-6">
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

          <!-- Student Group (readonly) -->
          <div class="md:col-span-2 lg:col-span-3">
            <label class="block text-sm font-medium text-gray-700 mb-2">Student Group</label>
            <input 
              :value="studentGroup"
              type="text" 
              readonly
              class="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100 text-gray-500"
            />
            <p class="text-xs text-gray-500 mt-1">Student group cannot be changed</p>
          </div>
          
          <!-- Personal Details Section - Only show if allowed -->
          <div v-if="allowInstructorsModify" class="md:col-span-2 lg:col-span-3">
            <h3 class="text-lg font-medium text-gray-800 mb-4 border-b pb-2">Personal Details</h3>
          </div>

          <!-- Profile Image Component -->
          <div class="md:col-span-2 lg:col-span-3">
            <!-- Make sure the StudentProfileImage is receiving the routeImageUrl -->
            <StudentProfileImage
              :student-id="studentId"
              :current-image="routeImageUrl"
              :student-name="studentInfo.student_name"
              @image-updated="handleImageUpdated"
              @success="msg => showSuccess(msg)"
              @error="msg => showError(msg)"
            />
          </div>
          <div v-if="allowInstructorsModify">
            <label class="block text-sm font-medium text-gray-700 mb-2">First Name</label>
            <input 
              v-model="studentInfo.first_name"
              type="text" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div v-if="allowInstructorsModify">
            <label class="block text-sm font-medium text-gray-700 mb-2">Middle Name</label>
            <input 
              v-model="studentInfo.middle_name"
              type="text" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div v-if="allowInstructorsModify">
            <label class="block text-sm font-medium text-gray-700 mb-2">Last Name</label>
            <input 
              v-model="studentInfo.last_name"
              type="text" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div v-if="allowInstructorsModify">
            <label class="block text-sm font-medium text-gray-700 mb-2">Student Date of Birth</label>
            <input 
              v-model="studentInfo.student_date_of_birth"
              type="date" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div v-if="allowInstructorsModify">
            <label class="block text-sm font-medium text-gray-700 mb-2">GR Number</label>
            <input 
              v-model="studentInfo.gr_number"
              type="text" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <!-- Roll Number Field - Only show if allowed -->
          <div v-if="allowInstructorsModify">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Roll Number
            </label>
            <input 
              v-model="studentInfo.roll_number"
              type="number"
              min="1"
              max="999"
              step="1"
              placeholder="Enter roll number"
              @keypress="preventDecimal"
              @input="validateRollNumber"
              :class="[
                'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                rollNumberError ? 'border-red-300 bg-red-50' : 'border-gray-300'
              ]"
            />
            <p v-if="rollNumberError" class="text-red-600 text-xs mt-1">{{ rollNumberError }}</p>
            <p v-else class="text-gray-500 text-xs mt-1">Must be a whole number between 1-999 (optional)</p>
          </div>
          
          <!-- Contact Information Section - Only show if allowed -->
          <div v-if="allowInstructorsModify" class="md:col-span-2 lg:col-span-3 mt-4">
            <h3 class="text-lg font-medium text-gray-800 mb-4 border-b pb-2">Contact Information</h3>
          </div>
          
          <div v-if="allowInstructorsModify">
            <label class="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
            <input 
              v-model="studentInfo.email_address"
              type="email" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div v-if="allowInstructorsModify">
            <label class="block text-sm font-medium text-gray-700 mb-2">Phone Number</label>
            <input 
              v-model="studentInfo.phone_number"
              type="tel" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <!-- Form Actions -->
        <div class="mt-8 pt-6 border-t flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
          <div class="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3 w-full sm:w-auto">
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
              'bg-gray-50 rounded-lg p-4 sm:p-6 border-2 border-dashed mb-6 transition-all',
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

            <div class="mt-4 flex flex-col sm:flex-row items-start sm:items-center justify-between space-y-3 sm:space-y-0">
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
                  'px-4 py-2 rounded-md flex items-center space-x-2 transition-colors w-full sm:w-auto justify-center',
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
          <div class="bg-white rounded-lg border border-gray-200 p-4 sm:p-6">
            <h4 class="text-lg font-semibold text-gray-800 mb-4">Existing Guardians</h4>
            
            <div v-if="studentDetailsResource.loading" class="flex justify-center py-4">
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
                :key="guardian.guardian"
                class="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors"
              >
                <div class="flex items-start justify-between">
                  <div class="flex items-start space-x-3 flex-1">
                    <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                      <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                    
                    <div class="flex-1 min-w-0">
                      <div class="flex flex-col sm:flex-row sm:items-center space-y-1 sm:space-y-0 sm:space-x-2 mb-1">
                        <h5 class="font-medium text-gray-800 text-lg truncate">{{ guardian.guardian_name }}</h5>
                        <span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full self-start sm:self-auto">
                          {{ guardian.relation }}
                        </span>
                      </div>
                      
                      <!-- Guardian Details Display -->
                      <div v-if="editingGuardianId !== guardian.guardian" class="space-y-2 text-sm text-gray-600">
                        <div class="flex flex-col sm:flex-row sm:items-center space-y-1 sm:space-y-0 sm:space-x-4">
                          <span class="flex items-center space-x-1">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                            </svg>
                            <span class="truncate">{{ guardian.mobile_number || 'No phone' }}</span>
                          </span>
                          <span class="hidden sm:inline text-gray-400">•</span>
                          <span class="flex items-center space-x-1">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                            </svg>
                            <span class="truncate">{{ guardian.email || 'No email' }}</span>
                          </span>
                        </div>
                        <div v-if="guardian.occupation || guardian.designation" class="flex flex-col sm:flex-row sm:items-center space-y-1 sm:space-y-0 sm:space-x-2 text-xs">
                          <span v-if="guardian.occupation" class="flex items-center space-x-1">
                            <span>💼</span>
                            <span class="truncate">{{ guardian.occupation }}</span>
                          </span>
                          <span v-if="guardian.occupation && guardian.designation" class="hidden sm:inline text-gray-400">•</span>
                          <span v-if="guardian.designation" class="flex items-center space-x-1">
                            <span>🎯</span>
                            <span class="truncate">{{ guardian.designation }}</span>
                          </span>
                        </div>
                        <div v-if="guardian.education" class="text-xs text-gray-500 flex items-center space-x-1">
                          <span>🎓</span>
                          <span class="truncate">{{ guardian.education }}</span>
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
                              v-model="editedGuardian.mobile_number"
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
                              v-model="editedGuardian.date_of_birth"
                              type="date"
                              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                          </div>

                          <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
                            <input
                              v-model="editedGuardian.email"
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

                        <div class="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3 pt-4">
                          <button
                            type="button"
                            @click="updateGuardianDetails(guardian.guardian)"
                            :disabled="updatingGuardian"
                            class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-green-300 flex items-center space-x-2 justify-center"
                          >
                            <svg v-if="updatingGuardian" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                            </svg>
                            <span>{{ updatingGuardian ? 'Updating...' : 'Update Guardian' }}</span>
                          </button>
                          <button
                            type="button"
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
                    type="button"
                    v-if="editingGuardianId !== guardian.guardian"
                    @click="startEdit(guardian)"
                    class="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors flex-shrink-0"
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
        
        <div class="text-sm text-gray-600 mt-4">
          <span v-if="allowInstructorsModify" class="text-green-600">
            ✓ You have full editing permissions
          </span>
          <span v-else class="text-orange-600">
            ⚠ You can only edit guardian information
          </span>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, reactive } from 'vue'
import { useRoute } from 'vue-router'
import { createResource } from 'frappe-ui'
import StudentProfileImage from '@/components/StudentProfileImage.vue'

const route = useRoute()

// Reactive state
const studentInfo = reactive({
  student: '',
  first_name: '',
  middle_name: '',
  last_name: '',
  student_date_of_birth: '',
  gr_number: '',
  email_address: '',
  phone_number: '',
  roll_number: '',
  // Remove image since API doesn't provide it
})
const studentId = ref('')
const studentGroup = ref('')
const settingsLoading = ref(true)
const settingsError = ref(false)
const updateLoading = ref(false)
const rollNumberError = ref('')
const errorMessage = ref('')
const successMessage = ref('')
const alertAnimation = ref('')
const studentDetailsError = ref('')
// const studentImageUrl = ref('')


// Guardian management state
const guardians = ref([])
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
  mobile_number: '',
  relation: 'Mother',
  date_of_birth: '',
  email: '',
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

// Replace the current routeImageUrl computed property with this:
// Add a reactive ref to store the image URL from route
const studentImageUrl = ref('')

// Update the routeImageUrl computed property to use the stored image URL
const routeImageUrl = computed(() => {
  if (studentImageUrl.value) {
    console.log('🖼️ Using stored image URL:', studentImageUrl.value)
    return getProfileImageUrl(studentImageUrl.value)
  }
  
  console.log('❌ No image URL available')
  return ''
})

// In onMounted, extract and store the image URL from route
onMounted(() => {
  studentId.value = route.query.studentId

  if (route.query.studentData) {
    try {
      const data = JSON.parse(decodeURIComponent(route.query.studentData))
      studentGroup.value = data.student_group || ''
      
      // Store the image URL from route data
      studentImageUrl.value = data.img_url || ''
      
      console.log('🎯 Route data analysis:', {
        studentGroup: studentGroup.value,
        hasImgUrl: !!data.img_url,
        imgUrl: data.img_url,
        allKeys: Object.keys(data) // See all available data
      })
      
    } catch (e) {
      console.error('Error parsing student data:', e)
      showError('Invalid student data')
    }
  }

  fetchAdminSettings()
  fetchStudentDetails()
})

// Add this helper function:
const getProfileImageUrl = (imgUrl) => {
  if (!imgUrl) return null
  
  // If URL is already absolute, use it directly
  if (imgUrl.startsWith('http') || imgUrl.startsWith('//')) {
    return imgUrl
  }
  
  // If URL starts with /, prepend current origin
  if (imgUrl.startsWith('/')) {
    return window.location.origin + imgUrl
  }
  
  // For relative URLs, construct full URL
  const baseUrl = window.location.origin
  return `${baseUrl}/${imgUrl.replace(/^\//, '')}`
}

// Alert helpers
const showError = (message) => {
  errorMessage.value = message
  successMessage.value = ''
  alertAnimation.value = 'animate-slide-in-right'
}

const showSuccess = (message) => {
  successMessage.value = message
  errorMessage.value = ''
  alertAnimation.value = 'animate-slide-in-right'
}

const hideAlert = () => {
  alertAnimation.value = 'animate-slide-out-right'
  setTimeout(() => {
    errorMessage.value = ''
    successMessage.value = ''
    alertAnimation.value = ''
  }, 300)
}

// Add this method to handle image updates
// Update the image updated handler to store the new URL
const handleImageUpdated = (newImageUrl) => {
  console.log('📸 Image updated in StudentProfileImage:', newImageUrl)
  // Store the new image URL so it persists
  studentImageUrl.value = newImageUrl
}

// API Resources
const adminSettingsResource = createResource({
  url: 'school.al_ummah.api3.fetch_admin_settings',
  auto: false,
  onSuccess(data) {
    adminSettings.value = data
    settingsLoading.value = false
    settingsError.value = false
  },
  onError() {
    settingsLoading.value = false
    settingsError.value = true
    adminSettings.value = { allow_instructors_modify_student: 0, session_expiry: "24:00" }
  }
})

const studentDetailsResource = createResource({
  url: 'school.al_ummah.api2.get_student_details',
  auto: false,
  onSuccess(data) {
    if (data.student_info) {
      Object.assign(studentInfo, data.student_info)
    }
    if (data.guardians && Array.isArray(data.guardians)) {
      guardians.value = data.guardians
    }
    studentDetailsError.value = ''
  },
  onError() {
    studentDetailsError.value = 'Failed to load student details.'
    guardians.value = []
  }
})

const updateStudentResource = createResource({
  url: 'school.al_ummah.api2.update_student_details',
  auto: false,
  onSuccess(data) {
    updateLoading.value = false
    showSuccess(data.message || 'Student updated successfully!')
  },
  onError(error) {
    updateLoading.value = false
    const msg = error._server_messages
      ? JSON.parse(JSON.parse(error._server_messages.at(-1))?.message || '{}')?.message
      : error.message
    showError(msg || 'Update failed.')
  }
})

const addGuardianResource = createResource({
  url: 'school.al_ummah.api2.add_guardian_to_student',
  auto: false,
  onSuccess(data) {
    addingGuardian.value = false
    showSuccess(data.message || 'Guardian added!')
    fetchStudentDetails()
    resetNewGuardianForm()
  },
  onError(error) {
    addingGuardian.value = false
    const msg = error._server_messages
      ? JSON.parse(JSON.parse(error._server_messages.at(-1))?.message || '{}')?.message
      : error.message
    showError(msg || 'Failed to add guardian.')
  }
})

const updateGuardianDetailsResource = createResource({
  url: 'school.al_ummah.api2.update_guardian_details',
  auto: false,
  onSuccess(data) {
    updatingGuardian.value = false
    showSuccess(data.message || 'Guardian updated!')
    editingGuardianId.value = null
    resetEditedGuardianForm()
    fetchStudentDetails()
  },
  onError(error) {
    updatingGuardian.value = false
    const msg = error._server_messages
      ? JSON.parse(JSON.parse(error._server_messages.at(-1))?.message || '{}')?.message
      : error.message
    showError(msg || 'Failed to update guardian.')
  }
})

// Validation
const isValidPhoneNumber = (number) => /^[0-9]{10}$/.test(number)

const preventDecimal = (event) => {
  if (['.', ',', 'e', 'E', '-'].includes(event.key)) {
    event.preventDefault()
  }
}

const validateRollNumber = () => {
  const val = studentInfo.roll_number
  if (!val && val !== 0) return rollNumberError.value = ''
  const num = Number(val)
  if (!Number.isInteger(num)) return rollNumberError.value = 'Must be a whole number'
  if (num < 1) return rollNumberError.value = 'Must be at least 1'
  if (num > 999) return rollNumberError.value = 'Cannot exceed 999'
  rollNumberError.value = ''
}

// Guardian form helpers
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

// Guardian actions
const addGuardian = async () => {
  if (!newGuardian.guardian_name.trim()) return showError('Guardian name required')
  if (!isValidPhoneNumber(newGuardian.phone_number)) return showError('Valid 10-digit phone required')
  addingGuardian.value = true
  addGuardianResource.fetch({
    student_id: studentId.value,
    student_name: `${studentInfo.first_name} ${studentInfo.last_name}`.trim(),
    guardian_name: newGuardian.guardian_name,
    relation: newGuardian.relation,
    phone_number: newGuardian.phone_number
  })
}

const startEdit = (guardian) => {
  editingGuardianId.value = guardian.guardian
  Object.assign(editedGuardian, {
    guardian_name: guardian.guardian_name || '',
    mobile_number: guardian.mobile_number || '',
    relation: guardian.relation || 'Mother',
    date_of_birth: guardian.date_of_birth || '',
    email: guardian.email || '',
    occupation: guardian.occupation || '',
    designation: guardian.designation || '',
    work_address: guardian.work_address || '',
    education: guardian.education || ''
  })
}

const cancelEdit = () => {
  editingGuardianId.value = null
  resetEditedGuardianForm()
}

const updateGuardianDetails = (guardianId) => {
  if (!editedGuardian.guardian_name.trim()) return showError('Guardian name required')
  if (!isValidPhoneNumber(editedGuardian.mobile_number)) return showError('Valid 10-digit phone required')
  updatingGuardian.value = true
  updateGuardianDetailsResource.fetch({
    guardian_id: guardianId,
    guardian_name: editedGuardian.guardian_name,
    phone_number: editedGuardian.mobile_number,
    relation: editedGuardian.relation,
    guardian_date_of_birth: editedGuardian.date_of_birth,
    guardian_email: editedGuardian.email,
    occupation: editedGuardian.occupation,
    designation: editedGuardian.designation,
    work_address: editedGuardian.work_address,
    education: editedGuardian.education
  })
}

const updateStudent = async (event) => {
  // Debug: log what triggered this
  console.log('🚨 updateStudent called', {
    eventType: event?.type,
    target: event?.target?.tagName,
    timestamp: new Date().toISOString(),
    studentId: studentId.value
  })
  
  // Prevent default form behavior
  if (event) {
    event.preventDefault()
    event.stopPropagation()
  }
  
  // Early return if no changes detected
  if (!hasFormChanges()) {
    console.log('No changes detected, skipping update')
    showError('No changes to update')
    return
  }

  validateRollNumber()
  if (rollNumberError.value) {
    showError(rollNumberError.value)
    return
  }

  updateLoading.value = true
  const data = {
    student_id: studentId.value,
    student_group: studentGroup.value
  }

  if (allowInstructorsModify.value) {
    Object.assign(data, {
      first_name: studentInfo.first_name || '',
      middle_name: studentInfo.middle_name || '',
      last_name: studentInfo.last_name || '',
      student_date_of_birth: studentInfo.student_date_of_birth || '',
      gr_number: studentInfo.gr_number || '',
      email_address: studentInfo.email_address || '',
      phone_number: studentInfo.phone_number || '',
      roll_number: studentInfo.roll_number || ''
    })
  }

  console.log('Sending update data:', data)
  await updateStudentResource.fetch(data)
}

// Add change detection
const hasFormChanges = () => {
  // You can implement logic to check if any fields have actually changed
  // For now, return true to allow updates
  return true
}

// Fetchers
const fetchStudentDetails = () => {
  if (!studentId.value) return
  studentDetailsResource.fetch({ student: studentId.value })
}

const fetchAdminSettings = () => {
  settingsLoading.value = true
  adminSettingsResource.fetch()
}

// Lifecycle
onMounted(() => {
  studentId.value = route.query.studentId

  if (route.query.studentData) {
    try {
      const data = JSON.parse(decodeURIComponent(route.query.studentData))
      studentGroup.value = data.student_group || ''
      
    } catch (e) {
      console.error('Error parsing student data:', e)
      showError('Invalid student data')
    }
  }

  fetchAdminSettings()
  fetchStudentDetails()
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

/* Alert Animations */
.animate-slide-in-right {
  animation: slideInRight 0.3s ease-out;
}

.animate-slide-out-right {
  animation: slideOutRight 0.3s ease-in;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes slideOutRight {
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(100%);
    opacity: 0;
  }
}

/* Responsive text truncation */
.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>