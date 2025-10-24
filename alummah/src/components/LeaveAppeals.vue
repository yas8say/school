<template>
  <div class="min-h-screen bg-gray-50 p-4">
    <!-- Loading State -->
    <div v-if="leaveResource.loading" class="flex justify-center items-center py-8">
      <div class="spinner"></div>
      <span class="ml-2 text-gray-600">Loading leave applications...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="errorMessage" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
      <div class="flex items-start space-x-3">
        <svg class="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div>
          <p class="text-red-800 font-medium">Error</p>
          <p class="text-red-700 text-sm mt-1">{{ errorMessage }}</p>
          <button @click="fetchLeaveApplications" class="mt-2 px-3 py-1 bg-red-600 text-white rounded text-sm">
            Retry
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!appeals || appeals.length === 0" class="text-center py-12">
      <svg class="w-16 h-16 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <p class="text-gray-500 text-lg">No leave applications found</p>
      <p class="text-gray-400 text-sm mt-1">There are no pending leave applications for this group.</p>
    </div>

    <!-- Leave Applications List -->
    <div v-else class="space-y-4">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-semibold text-gray-800">Leave Applications</h2>
        <span class="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">
          {{ appeals.length }} application{{ appeals.length !== 1 ? 's' : '' }}
        </span>
      </div>

      <!-- Leave Application Cards -->
      <div 
        v-for="(appeal, index) in appeals"
        :key="appeal.name || `appeal-${index}`"
        class="bg-white rounded-lg shadow-sm border border-gray-200 hover:border-blue-300 transition-colors cursor-pointer"
        @click="toggleExpand(appeal.name)"
      >
        <!-- Compact View -->
        <div class="p-4">
          <div class="flex items-start space-x-3 mb-3">
            <!-- Medical Certificate Icon -->
            <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>

            <!-- Student Info -->
            <div class="flex-1 min-w-0">
              <h3 class="font-semibold text-gray-800 text-lg">{{ appeal.student_name || appeal.student || 'Unknown Student' }}</h3>
              <p class="text-sm text-gray-500">{{ appeal.student || 'No Student ID' }}</p>
              <p class="text-sm text-gray-600 mt-1">
                From: {{ formatDate(appeal.from_date) }} - To: {{ formatDate(appeal.to_date) }}
              </p>
            </div>

            <!-- Expand/Collapse Icon -->
            <div class="flex items-center space-x-2">
              <span 
                :class="[
                  'px-3 py-1 rounded-full text-xs font-medium',
                  getStatusBadgeClass(appeal.status)
                ]"
              >
                {{ getStatusText(appeal.status) }}
              </span>
              <svg 
                class="w-5 h-5 text-gray-400 transition-transform duration-200"
                :class="{ 'rotate-180': expandedAppeal === appeal.name }"
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>

          <!-- Basic Info -->
          <div class="flex justify-between items-center">
            <div class="flex-1">
              <p class="text-sm text-gray-700">
                Total Leave Days: <span class="font-medium">{{ appeal.total_leave_days || calculateDays(appeal.from_date, appeal.to_date) }}</span>
              </p>
              <p class="text-sm text-gray-600 mt-1 line-clamp-1">
                {{ appeal.reason || 'No reason provided' }}
              </p>
            </div>
          </div>

          <!-- Medical Certificate Badge -->
          <div v-if="appeal.document_base64" class="mt-3">
            <span class="inline-flex items-center px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Medical Certificate Available
            </span>
          </div>
        </div>

        <!-- Expanded View -->
        <div v-if="expandedAppeal === appeal.name" class="border-t border-gray-200 p-4 bg-gray-50">

          <!-- Detailed Information -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Leave Details -->
            <div>
              <h4 class="font-semibold text-gray-800 mb-3">Leave Details</h4>
              <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                  <span class="text-gray-600">Student Name:</span>
                  <span class="font-medium">{{ appeal.student_name || 'N/A' }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Student ID:</span>
                  <span class="font-medium">{{ appeal.student || 'N/A' }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Leave ID:</span>
                  <span class="font-medium">{{ appeal.name || 'N/A' }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Duration:</span>
                  <span class="font-medium">{{ appeal.total_leave_days || calculateDays(appeal.from_date, appeal.to_date) }} days</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Status:</span>
                  <span :class="getStatusBadgeClass(appeal.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                    {{ getStatusText(appeal.status) }}
                  </span>
                </div>
              </div>

              <!-- Reason -->
              <div class="mt-4">
                <h5 class="font-medium text-gray-700 mb-2">Reason for Leave</h5>
                <p class="text-sm text-gray-600 bg-white p-3 rounded border">
                  {{ appeal.reason || 'No reason provided' }}
                </p>
              </div>

              <!-- Action Buttons - Circular and Transparent -->
              <div 
                v-if="shouldShowButtons(appeal.status)" 
                class="mt-4 flex space-x-3 justify-center"
              >
                <!-- Reject Button -->
                <button
                  @click.stop="updateLeaveStatus(appeal.name, 'rejected')"
                  :disabled="updateResource.loading"
                  class="w-12 h-12 rounded-full bg-red-500 bg-opacity-80 text-white hover:bg-red-600 hover:bg-opacity-90 transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center shadow-md hover:shadow-lg transform hover:scale-105"
                  :class="{ 'opacity-60': updateResource.loading }"
                  title="Reject Leave Application"
                >
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>

                <!-- Approve Button -->
                <button
                  @click.stop="updateLeaveStatus(appeal.name, 'approved')"
                  :disabled="updateResource.loading"
                  class="w-12 h-12 rounded-full bg-green-500 bg-opacity-80 text-white hover:bg-green-600 hover:bg-opacity-90 transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center shadow-md hover:shadow-lg transform hover:scale-105"
                  :class="{ 'opacity-60': updateResource.loading }"
                  title="Approve Leave Application"
                >
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </button>
              </div>

              <!-- Show message if not pending -->
              <div v-else class="mt-4 p-3 bg-gray-100 rounded-lg text-center">
                <p class="text-sm text-gray-600">
                  This leave application has been <span class="font-medium">{{ appeal.status?.toLowerCase() || 'processed' }}</span>
                </p>
              </div>
            </div>

            <!-- Medical Certificate -->
            <div v-if="appeal.document_base64">
              <h4 class="font-semibold text-gray-800 mb-3">Medical Certificate</h4>
              <div class="bg-white p-4 rounded-lg border border-gray-200">
                <!-- Image Preview -->
                <div class="mb-3">
                  <img 
                    :src="getDocumentUrl(appeal.document_base64)" 
                    alt="Medical Certificate"
                    @error="handleImageError"
                    class="w-full h-48 object-contain border border-gray-200 rounded cursor-pointer"
                    @click.stop="viewMedicalCertificate(appeal.document_base64)"
                  >
                </div>
                
                <!-- Download/View Options -->
                <div class="flex space-x-2">
                  <button
                    @click.stop="viewMedicalCertificate(appeal.document_base64)"
                    class="flex-1 px-3 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    <span>View Full Size</span>
                  </button>
                  
                  <button
                    @click.stop="downloadMedicalCertificate(appeal.document_base64, appeal.student_name)"
                    class="flex-1 px-3 py-2 bg-gray-600 text-white rounded text-sm hover:bg-gray-700 transition-colors flex items-center justify-center space-x-2"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    <span>Download</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- No Document Message -->
            <div v-else class="flex items-center justify-center p-8 bg-gray-100 rounded-lg border border-gray-200">
              <div class="text-center">
                <svg class="w-12 h-12 mx-auto text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p class="text-gray-500 text-sm">No medical certificate provided</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading Overlay for Updates -->
    <div v-if="updateResource.loading" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 flex items-center space-x-3">
        <div class="spinner-small"></div>
        <span class="text-gray-700">Updating leave application...</span>
      </div>
    </div>

    <!-- Medical Certificate Modal -->
    <div v-if="showMedicalCertificateModal" class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg max-w-4xl max-h-full w-full">
        <div class="flex justify-between items-center p-4 border-b">
          <h3 class="text-lg font-semibold text-gray-800">Medical Certificate</h3>
          <button 
            @click="showMedicalCertificateModal = false"
            class="text-gray-500 hover:text-gray-700 transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-4 max-h-[80vh] overflow-auto">
          <img 
            :src="currentMedicalCertificateUrl" 
            alt="Medical Certificate Full Size"
            class="w-full h-auto object-contain max-h-[70vh] mx-auto"
            @error="handleModalImageError"
          >
        </div>
        <div class="p-4 border-t flex justify-center">
          <button
            @click="downloadMedicalCertificateFromModal"
            class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors flex items-center space-x-2"
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
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { createResource } from 'frappe-ui'

// Reactive state
const appeals = ref([])
const errorMessage = ref('')
const expandedAppeal = ref(null)
const showMedicalCertificateModal = ref(false)
const currentMedicalCertificateUrl = ref('')
const currentMedicalCertificateBase64 = ref('')
const currentStudentName = ref('')

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
    errorMessage.value = error.message || 'Failed to load leave applications.'
    appeals.value = []
  }
})

// API Resource for updating leave status
const updateResource = createResource({
  url: 'school.al_ummah.api2.update_leave_status',
  method: 'POST',
  auto: false,
  onSuccess(data) {
    console.log('✅ Update API Response:', data)
    
    if (data.success) {
      // Find and update the specific appeal in the list
      const appealIndex = appeals.value.findIndex(app => app.name === data.name)
      if (appealIndex !== -1) {
        appeals.value[appealIndex].status = data.status
        console.log('🔄 Updated appeal status:', data.status)
      }
      
      showAlert('Success', data.message || 'Leave application updated successfully.')
      
      // Refresh the list to get updated data
      fetchLeaveApplications()
    } else {
      console.log('❌ API returned success: false')
      showAlert('Error', data.message || 'Failed to update leave application.')
    }
  },
  onError(error) {
    console.error('🚨 Error updating leave status:', error)
    
    let errorMessage = 'Failed to update leave application.'
    if (error._server_messages) {
      try {
        const serverMessages = JSON.parse(error._server_messages || '[]')
        const lastMessage = serverMessages[serverMessages.length - 1]
        const parsedMessage = JSON.parse(lastMessage)
        errorMessage = parsedMessage.message || errorMessage
      } catch (e) {
        console.log('❌ Error parsing server messages:', e)
        errorMessage = error.message || errorMessage
      }
    } else if (error.message) {
      errorMessage = error.message
    }
    
    showAlert('Error', errorMessage)
  }
})

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

// Status checking functions
const isPendingStatus = (status) => {
  if (!status) return true
  const statusStr = String(status).trim().toLowerCase()
  return statusStr === 'pending'
}

const shouldShowButtons = (status) => {
  if (!status) return true
  
  const statusStr = String(status).trim().toLowerCase()
  const finalStatuses = ['approved', 'rejected']
  
  return !finalStatuses.includes(statusStr)
}

const getStatusText = (status) => {
  if (!status) return 'Pending'
  const statusStr = String(status).trim()
  return statusStr.charAt(0).toUpperCase() + statusStr.slice(1).toLowerCase()
}

const getStatusBadgeClass = (status) => {
  if (!status) return 'bg-yellow-100 text-yellow-800'
  
  const statusLower = String(status).trim().toLowerCase()
  
  switch (statusLower) {
    case 'approved':
      return 'bg-green-100 text-green-800'
    case 'rejected':
      return 'bg-red-100 text-red-800'
    case 'pending':
      return 'bg-yellow-100 text-yellow-800'
    default:
      return 'bg-yellow-100 text-yellow-800'
  }
}

const getDocumentUrl = (base64Data) => {
  if (!base64Data) return ''
  try {
    let cleanBase64 = base64Data
    if (cleanBase64.includes('base64,')) {
      cleanBase64 = cleanBase64.split('base64,')[1]
    }
    cleanBase64 = cleanBase64.trim()
    return `data:image/jpeg;base64,${cleanBase64}`
  } catch (error) {
    console.error('Error creating document URL:', error)
    return ''
  }
}

const handleImageError = (event) => {
  console.error('Image failed to load')
  event.target.style.display = 'none'
}

const handleModalImageError = (event) => {
  console.error('Modal image failed to load')
  showAlert('Error', 'Failed to load medical certificate image.')
  showMedicalCertificateModal.value = false
}

// Event handlers
const toggleExpand = (appealName) => {
  expandedAppeal.value = expandedAppeal.value === appealName ? null : appealName
}

// FIXED: Medical certificate viewing with modal
const viewMedicalCertificate = (base64Data) => {
  const url = getDocumentUrl(base64Data)
  if (url) {
    currentMedicalCertificateUrl.value = url
    currentMedicalCertificateBase64.value = base64Data
    showMedicalCertificateModal.value = true
  } else {
    showAlert('Error', 'Unable to display medical certificate.')
  }
}

const downloadMedicalCertificate = (base64Data, studentName) => {
  const url = getDocumentUrl(base64Data)
  if (url) {
    const link = document.createElement('a')
    link.href = url
    link.download = `medical-certificate-${studentName || 'student'}.jpg`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}

const downloadMedicalCertificateFromModal = () => {
  if (currentMedicalCertificateUrl.value) {
    const link = document.createElement('a')
    link.href = currentMedicalCertificateUrl.value
    link.download = `medical-certificate-${currentStudentName.value || 'student'}.jpg`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}

// Update leave status function
const updateLeaveStatus = async (appealName, newStatus) => {
  if (!appealName) {
    showAlert('Error', 'Cannot update: Missing leave application ID')
    return
  }

  console.log('Updating leave status:', appealName, 'to:', newStatus)
  
  const updateData = {
    name: appealName,
    status: newStatus
  }
  
  console.log('Sending update data:', updateData)
  await updateResource.submit(updateData)
}

const showAlert = (title, message) => {
  alert(`${title}: ${message}`)
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

.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.rotate-180 {
  transform: rotate(180deg);
}

/* Custom styles for circular buttons */
.circular-button {
  border-radius: 50%;
  opacity: 0.8;
  transition: all 0.3s ease;
}

.circular-button:hover {
  opacity: 0.9;
  transform: scale(1.05);
}

.circular-button:disabled {
  opacity: 0.4;
  transform: scale(1);
}
</style>