<template>
  <div class="min-h-screen bg-gray-50 p-4">
    <!-- Loading State -->
    <div v-if="leaveResource.loading" class="flex justify-center items-center py-12">
      <div class="spinner"></div>
      <span class="ml-3 text-gray-600 text-lg">Loading leave applications...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="errorMessage" class="bg-red-50 border border-red-200 rounded-xl p-6 mb-6 max-w-4xl mx-auto">
      <div class="flex items-start space-x-4">
        <div class="flex-shrink-0">
          <svg class="w-6 h-6 text-red-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div class="flex-1">
          <p class="text-red-800 font-semibold text-lg">Unable to Load Applications</p>
          <p class="text-red-700 mt-2">{{ errorMessage }}</p>
          <button 
            @click="fetchLeaveApplications" 
            class="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!appeals || appeals.length === 0" class="text-center py-16">
      <div class="max-w-md mx-auto">
        <div class="w-20 h-20 mx-auto mb-4 bg-blue-100 rounded-2xl flex items-center justify-center">
          <svg class="w-10 h-10 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 class="text-xl font-semibold text-gray-700 mb-2">No Leave Applications</h3>
        <p class="text-gray-500">There are no leave applications for this group.</p>
      </div>
    </div>

    <!-- Leave Applications List -->
    <div v-else class="max-w-6xl mx-auto">
      <!-- Header -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 mb-6">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Leave Applications</h1>
            <p class="text-gray-600 mt-1">Review and manage student leave requests</p>
          </div>
          <div class="flex items-center space-x-4 mt-4 sm:mt-0">
            <div class="flex items-center space-x-2">
              <div class="w-3 h-3 bg-yellow-500 rounded-full"></div>
              <span class="text-sm text-gray-600">{{ pendingCount }} pending</span>
            </div>
            <div class="flex items-center space-x-2">
              <div class="w-3 h-3 bg-green-500 rounded-full"></div>
              <span class="text-sm text-gray-600">{{ approvedCount }} approved</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Leave Application Cards -->
      <div class="grid gap-6">
        <div 
          v-for="(appeal, index) in appeals"
          :key="appeal.name || `appeal-${index}`"
          class="bg-white rounded-2xl shadow-sm border border-gray-200 hover:shadow-md transition-all duration-300"
        >
          <!-- Compact View -->
          <div class="p-6">
            <div class="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
              <!-- Left Section - Student Info -->
              <div class="flex items-start space-x-4 flex-1 min-w-0">
                <!-- Avatar -->
                <div class="w-14 h-14 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center flex-shrink-0 shadow-sm">
                  <span class="text-white font-semibold text-lg">
                    {{ getInitials(appeal.student_name || appeal.student || 'Unknown') }}
                  </span>
                </div>

                <!-- Student Details -->
                <div class="flex-1 min-w-0">
                  <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                    <div>
                      <h3 class="font-bold text-gray-900 text-xl">{{ appeal.student_name || appeal.student || 'Unknown Student' }}</h3>
                      <p class="text-gray-600 text-sm mt-1">{{ appeal.student || 'No Student ID' }}</p>
                    </div>
                    <div class="flex items-center space-x-3">
                      <span 
                        :class="[
                          'px-3 py-1.5 rounded-full text-sm font-semibold',
                          getStatusBadgeClass(appeal.docstatus)
                        ]"
                      >
                        {{ getStatusText(appeal.docstatus) }}
                      </span>
                      <button
                        @click="toggleExpand(appeal.name)"
                        class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                      >
                        <svg 
                          class="w-5 h-5 transition-transform duration-200"
                          :class="{ 'rotate-180': expandedAppeal === appeal.name }"
                          fill="none" 
                          stroke="currentColor" 
                          viewBox="0 0 24 24"
                        >
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                        </svg>
                      </button>
                    </div>
                  </div>

                  <!-- Leave Period -->
                  <div class="flex flex-wrap items-center gap-4 mt-4">
                    <div class="flex items-center space-x-2 text-gray-700">
                      <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      <span class="text-sm font-medium">From {{ formatDate(appeal.from_date) }}</span>
                    </div>
                    <div class="flex items-center space-x-2 text-gray-700">
                      <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      <span class="text-sm font-medium">To {{ formatDate(appeal.to_date) }}</span>
                    </div>
                    <div class="flex items-center space-x-2 text-blue-700">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span class="text-sm font-semibold">{{ appeal.total_leave_days || calculateDays(appeal.from_date, appeal.to_date) }} days</span>
                    </div>
                  </div>

                  <!-- Reason Preview -->
                  <p class="text-gray-600 mt-3 line-clamp-2">
                    {{ appeal.reason || 'No reason provided' }}
                  </p>

                  <!-- Medical Certificate Badge -->
                  <div v-if="appeal.img_url" class="mt-3">
                    <span class="inline-flex items-center px-3 py-1.5 bg-green-50 text-green-700 rounded-lg text-sm font-medium">
                      <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      Medical Certificate Available
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Expanded View -->
          <div v-if="expandedAppeal === appeal.name" class="border-t border-gray-100 p-6 bg-gray-50 rounded-b-2xl">
            <div class="grid grid-cols-1 xl:grid-cols-2 gap-8">
              <!-- Leave Details -->
              <div class="space-y-6">
                <div class="bg-white rounded-xl border border-gray-200 p-6">
                  <h4 class="font-bold text-gray-900 text-lg mb-4">Leave Details</h4>
                  <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label class="text-sm font-medium text-gray-500">Student Name</label>
                      <p class="text-gray-900 font-semibold mt-1">{{ appeal.student_name || 'N/A' }}</p>
                    </div>
                    <div>
                      <label class="text-sm font-medium text-gray-500">Student ID</label>
                      <p class="text-gray-900 font-semibold mt-1">{{ appeal.student || 'N/A' }}</p>
                    </div>
                    <div>
                      <label class="text-sm font-medium text-gray-500">Leave ID</label>
                      <p class="text-gray-900 font-semibold mt-1">{{ appeal.name || 'N/A' }}</p>
                    </div>
                    <div>
                      <label class="text-sm font-medium text-gray-500">Duration</label>
                      <p class="text-gray-900 font-semibold mt-1">{{ appeal.total_leave_days || calculateDays(appeal.from_date, appeal.to_date) }} days</p>
                    </div>
                    <div>
                      <label class="text-sm font-medium text-gray-500">Status</label>
                      <p :class="getStatusBadgeClass(appeal.docstatus)" class="px-3 py-1.5 rounded-full text-sm font-semibold inline-block mt-1">
                        {{ getStatusText(appeal.docstatus) }}
                      </p>
                    </div>
                    <div>
                      <label class="text-sm font-medium text-gray-500">Mark as Present</label>
                      <p class="text-gray-900 font-semibold mt-1">
                        {{ appeal.mark_as_present ? 'Yes' : 'No' }}
                      </p>
                    </div>
                  </div>
                </div>

                <!-- Reason -->
                <div class="bg-white rounded-xl border border-gray-200 p-6">
                  <h5 class="font-bold text-gray-900 text-lg mb-3">Reason for Leave</h5>
                  <p class="text-gray-700 bg-gray-50 p-4 rounded-lg border border-gray-200">
                    {{ appeal.reason || 'No reason provided' }}
                  </p>
                </div>

                <!-- Approval Action - Only show for docstatus 0 -->
                <div v-if="appeal.docstatus === 0" class="bg-white rounded-xl border border-gray-200 p-6">
                  <h5 class="font-bold text-gray-900 text-lg mb-4">Approve Leave</h5>
                  <button
                    @click.stop="approveLeave(appeal.name)"
                    :disabled="updateResource.loading"
                    class="w-full px-6 py-3 bg-green-600 text-white rounded-xl font-semibold hover:bg-green-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-3 shadow-sm hover:shadow-md"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span>Approve Leave Application</span>
                  </button>
                  <p class="text-gray-500 text-sm mt-3 text-center">
                    This will approve the leave request and notify the student
                  </p>
                </div>

                <!-- Status Message for Approved Leaves -->
                <div v-else class="bg-green-50 rounded-xl border border-green-200 p-6 text-center">
                  <div class="flex items-center justify-center space-x-2 text-green-700 mb-2">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span class="font-semibold">Leave Approved</span>
                  </div>
                  <p class="text-green-600 text-sm">
                    This leave application has been approved and processed.
                  </p>
                </div>
              </div>

              <!-- Medical Certificate -->
              <div v-if="appeal.img_url" class="space-y-6">
                <div class="bg-white rounded-xl border border-gray-200 p-6">
                  <h4 class="font-bold text-gray-900 text-lg mb-4">Medical Certificate</h4>
                  <div class="space-y-4">
                    <!-- Image Preview -->
                    <div class="border-2 border-dashed border-gray-200 rounded-xl overflow-hidden bg-gray-50">
                      <img 
                        :src="appeal.img_url" 
                        alt="Medical Certificate"
                        @error="handleImageError"
                        class="w-full h-64 object-contain cursor-pointer transition-transform duration-200 hover:scale-105"
                        @click.stop="viewMedicalCertificate(appeal.img_url, appeal.student_name)"
                      >
                    </div>
                    
                    <!-- Action Buttons -->
                    <div class="grid grid-cols-2 gap-3">
                      <button
                        @click.stop="viewMedicalCertificate(appeal.img_url, appeal.student_name)"
                        class="px-4 py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                        <span>View Full Size</span>
                      </button>
                      
                      <button
                        @click.stop="downloadMedicalCertificate(appeal.img_url, appeal.student_name)"
                        class="px-4 py-2.5 bg-gray-600 text-white rounded-lg font-medium hover:bg-gray-700 transition-colors flex items-center justify-center space-x-2"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                        </svg>
                        <span>Download</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- No Document Message -->
              <div v-else-if="appeal.docstatus === 0" class="flex items-center justify-center p-8 bg-white rounded-xl border border-gray-200">
                <div class="text-center">
                  <svg class="w-12 h-12 mx-auto text-gray-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p class="text-gray-500 font-medium">No medical certificate provided</p>
                </div>
              </div>

              <!-- Approved without document -->
              <div v-else class="flex items-center justify-center p-8 bg-green-50 rounded-xl border border-green-200">
                <div class="text-center">
                  <svg class="w-12 h-12 mx-auto text-green-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p class="text-green-700 font-medium">Approved without medical certificate</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading Overlay for Updates -->
    <div v-if="updateResource.loading" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl p-8 flex items-center space-x-4 shadow-xl">
        <div class="spinner-small"></div>
        <div>
          <p class="font-semibold text-gray-900">Approving Leave</p>
          <p class="text-gray-600 text-sm mt-1">Please wait while we process your request...</p>
        </div>
      </div>
    </div>

    <!-- Error Toast Notification -->
    <div v-if="showErrorToast" class="fixed top-4 right-4 z-50 max-w-sm w-full">
      <div class="bg-red-50 border border-red-200 rounded-xl p-4 shadow-lg">
        <div class="flex items-start space-x-3">
          <svg class="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div class="flex-1">
            <p class="text-red-800 font-medium text-sm">Error</p>
            <p class="text-red-700 text-sm mt-1">{{ toastMessage }}</p>
          </div>
          <button @click="showErrorToast = false" class="text-red-400 hover:text-red-600 transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Success Toast Notification -->
    <div v-if="showSuccessToast" class="fixed top-4 right-4 z-50 max-w-sm w-full">
      <div class="bg-green-50 border border-green-200 rounded-xl p-4 shadow-lg">
        <div class="flex items-start space-x-3">
          <svg class="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <div class="flex-1">
            <p class="text-green-800 font-medium text-sm">Success</p>
            <p class="text-green-700 text-sm mt-1">{{ toastMessage }}</p>
          </div>
          <button @click="showSuccessToast = false" class="text-green-400 hover:text-green-600 transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Medical Certificate Modal -->
    <div v-if="showMedicalCertificateModal" class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl max-w-6xl w-full max-h-[90vh] flex flex-col shadow-2xl">
        <div class="flex justify-between items-center p-6 border-b border-gray-200">
          <div>
            <h3 class="text-xl font-bold text-gray-900">Medical Certificate</h3>
            <p class="text-gray-600 text-sm mt-1">{{ currentStudentName }}</p>
          </div>
          <button 
            @click="showMedicalCertificateModal = false"
            class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="flex-1 p-6 overflow-auto">
          <img 
            :src="currentMedicalCertificateUrl" 
            alt="Medical Certificate Full Size"
            class="w-full h-auto max-h-full object-contain mx-auto rounded-lg"
            @error="handleModalImageError"
          >
        </div>
        <div class="p-6 border-t border-gray-200 bg-gray-50 rounded-b-2xl">
          <div class="flex justify-center">
            <button
              @click="downloadMedicalCertificateFromModal"
              class="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center space-x-3"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              <span>Download Certificate</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { createResource } from 'frappe-ui'

// Reactive state
const appeals = ref([])
const errorMessage = ref('')
const expandedAppeal = ref(null)
const showMedicalCertificateModal = ref(false)
const currentMedicalCertificateUrl = ref('')
const currentStudentName = ref('')
const showErrorToast = ref(false)
const showSuccessToast = ref(false)
const toastMessage = ref('')

// Computed properties for counts
const pendingCount = computed(() => {
  return appeals.value.filter(appeal => appeal.docstatus === 0).length
})

const approvedCount = computed(() => {
  return appeals.value.filter(appeal => appeal.docstatus === 1).length
})

// Toast notification functions
const showToast = (message, type = 'error') => {
  toastMessage.value = message
  if (type === 'success') {
    showSuccessToast.value = true
    setTimeout(() => {
      showSuccessToast.value = false
    }, 5000)
  } else {
    showErrorToast.value = true
    setTimeout(() => {
      showErrorToast.value = false
    }, 5000)
  }
}

// API Resources
const leaveResource = createResource({
  url: 'school.al_ummah.api2.get_leave_application_list',
  auto: false,
  onSuccess(data) {
    console.log('Raw API response:', data)
    
    // Handle different response structures
    if (Array.isArray(data)) {
      appeals.value = data
    } else if (data && typeof data === 'object') {
      if (data.message && Array.isArray(data.message)) {
        appeals.value = data.message
      } else if (data.appeals && Array.isArray(data.appeals)) {
        appeals.value = data.appeals
      } else if (data.leave_applications && Array.isArray(data.leave_applications)) {
        appeals.value = data.leave_applications
      } else if (Array.isArray(data.data)) {
        appeals.value = data.data
      } else {
        appeals.value = Object.keys(data).length > 0 ? [data] : []
      }
    } else {
      appeals.value = []
    }
    
    console.log('Processed appeals:', appeals.value)
    errorMessage.value = ''
  },
  onError(error) {
    console.error('Error fetching leave applications:', error)
    const message = parseErrorMessage(error, 'Failed to load leave applications.')
    errorMessage.value = message
    appeals.value = []
  }
})

// API Resource for approving leave
const updateResource = createResource({
  url: 'school.al_ummah.api2.approve_leave',
  method: 'POST',
  auto: false,
  onSuccess(data) {
    console.log('✅ Approve API Response:', data)
    
    if (data.success) {
      // Find and update the specific appeal in the list
      const appealIndex = appeals.value.findIndex(app => app.name === data.name)
      if (appealIndex !== -1) {
        // Update the docstatus to 1 (approved)
        appeals.value[appealIndex].docstatus = 1
        console.log('🔄 Updated appeal docstatus to approved')
      }
      
      showToast(data.message || 'Leave application approved successfully.', 'success')
      
      // Close the expanded view
      expandedAppeal.value = null
      
      // Refresh the list to get updated data
      fetchLeaveApplications()
    } else {
      console.log('❌ API returned success: false')
      showToast(data.message || 'Failed to approve leave application.')
    }
  },
  onError(error) {
    console.error('🚨 Error approving leave:', error)
    const message = parseErrorMessage(error, 'Failed to approve leave application.')
    showToast(message)
  }
})

// Improved error message parser
const parseErrorMessage = (error, defaultMessage) => {
  if (!error) return defaultMessage
  
  // Handle Frappe UI error structure
  if (error._server_messages) {
    try {
      const serverMessages = JSON.parse(error._server_messages || '[]')
      if (serverMessages.length > 0) {
        const lastMessage = serverMessages[serverMessages.length - 1]
        try {
          const parsedMessage = JSON.parse(lastMessage)
          return parsedMessage.message || parsedMessage.exc_type || defaultMessage
        } catch (e) {
          return lastMessage || defaultMessage
        }
      }
    } catch (e) {
      console.error('Error parsing server messages:', e)
    }
  }
  
  // Handle direct message
  if (error.message) {
    return error.message
  }
  
  // Handle exception objects
  if (error.exc_type || error.exc_message) {
    return error.exc_message || error.exc_type || defaultMessage
  }
  
  // Handle string errors
  if (typeof error === 'string') {
    return error
  }
  
  return defaultMessage
}

// Helper functions
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  } catch (e) {
    return dateString || 'N/A'
  }
}

const calculateDays = (fromDate, toDate) => {
  if (!fromDate || !toDate) return 0
  try {
    const from = new Date(fromDate)
    const to = new Date(toDate)
    const diffTime = Math.abs(to - from)
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1
  } catch (e) {
    return 0
  }
}

const getInitials = (name) => {
  if (!name) return '?'
  return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2)
}

// Status functions based on docstatus
const getStatusText = (docstatus) => {
  return docstatus === 0 ? 'Pending' : 'Approved'
}

const getStatusBadgeClass = (docstatus) => {
  return docstatus === 0 ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'
}

const handleImageError = (event) => {
  console.error('Image failed to load')
  event.target.style.display = 'none'
}

const handleModalImageError = (event) => {
  console.error('Modal image failed to load')
  showToast('Failed to load medical certificate image.')
  showMedicalCertificateModal.value = false
}

// Event handlers
const toggleExpand = (appealName) => {
  expandedAppeal.value = expandedAppeal.value === appealName ? null : appealName
}

const viewMedicalCertificate = (imgUrl, studentName) => {
  if (imgUrl) {
    currentMedicalCertificateUrl.value = imgUrl
    currentStudentName.value = studentName
    showMedicalCertificateModal.value = true
  } else {
    showToast('Unable to display medical certificate.')
  }
}

const downloadMedicalCertificate = (imgUrl, studentName) => {
  if (imgUrl) {
    const link = document.createElement('a')
    link.href = imgUrl
    link.download = `medical-certificate-${studentName || 'student'}.jpg`
    link.target = '_blank'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}

const downloadMedicalCertificateFromModal = () => {
  if (currentMedicalCertificateUrl.value) {
    downloadMedicalCertificate(currentMedicalCertificateUrl.value, currentStudentName.value)
  }
}

// Approve leave function with better validation
const approveLeave = async (appealName) => {
  if (!appealName) {
    showToast('Cannot approve: Missing leave application ID')
    return
  }

  // Validate that the appeal exists and is pending
  const appeal = appeals.value.find(app => app.name === appealName)
  if (!appeal) {
    showToast('Leave application not found.')
    return
  }

  if (appeal.docstatus !== 0) {
    showToast('This leave application has already been processed.')
    return
  }

  console.log('Approving leave:', appealName)
  
  const approveData = {
    name: appealName
  }
  
  console.log('Sending approve data:', approveData)
  await updateResource.submit(approveData)
}

// Get student group and fetch data
const getStudentGroup = () => {
  try {
    const savedStudentGroup = localStorage.getItem('selected_student_group')
    if (savedStudentGroup) {
      try {
        const groupData = JSON.parse(savedStudentGroup)
        return groupData.student_group || groupData.name || groupData
      } catch (e) {
        return savedStudentGroup
      }
    }
    return null
  } catch (error) {
    console.error('Error getting student group:', error)
    return null
  }
}

const fetchLeaveApplications = () => {
  const studentGroup = getStudentGroup()
  
  if (!studentGroup) {
    errorMessage.value = 'No student group found. Please select a student first.'
    appeals.value = []
    return
  }

  const params = { student_group: studentGroup }
  console.log('Fetching leave applications with params:', params)
  leaveResource.fetch(params)
}

onMounted(() => {
  fetchLeaveApplications()
})
</script>

<style scoped>
.spinner {
  width: 44px;
  height: 44px;
  border: 4px solid #e5e7eb;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.spinner-small {
  width: 24px;
  height: 24px;
  border: 3px solid #e5e7eb;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.rotate-180 {
  transform: rotate(180deg);
}
</style>