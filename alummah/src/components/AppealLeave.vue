<template>
  <div class="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
    <!-- Student Info Display -->
    <div class="mb-4 p-4 bg-blue-50 rounded-lg">
      <h3 class="text-lg font-semibold text-blue-800 mb-2">Student Information</h3>
      <p class="text-sm text-blue-700" v-if="studentInfo.student_name">
        <strong>Student:</strong> {{ studentInfo.student_name }}
      </p>
      <p class="text-sm text-blue-700" v-if="studentInfo.student_group">
        <strong>Group:</strong> {{ studentInfo.student_group }}
      </p>
      <p class="text-sm text-red-600" v-if="!studentInfo.student_name">
        No student information found. Please select a student first.
      </p>
    </div>

    <!-- From Date -->
    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-2">From Date *</label>
      <input
        type="date"
        v-model="formData.from_date"
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        required
      />
    </div>

    <!-- To Date -->
    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-2">To Date *</label>
      <input
        type="date"
        v-model="formData.to_date"
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        required
      />
    </div>

    <!-- Total Days (Readonly) -->
    <div v-if="formData.total_days" class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-2">Total Days</label>
      <input
        type="text"
        :value="formData.total_days"
        readonly
        class="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100 text-gray-500"
      />
    </div>

    <!-- Reason/Message -->
    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-2">Reason *</label>
      <textarea
        v-model="formData.reason"
        rows="4"
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder="Enter reason for leave..."
        required
      ></textarea>
    </div>

    <!-- Image Upload -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2">Upload Image (Optional)</label>
      <input
        type="file"
        @change="handleImageUpload"
        accept="image/*"
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <p class="text-xs text-gray-500 mt-1" v-if="formData.image">
        Image selected: {{ formData.image.name }}
      </p>
    </div>

    <!-- Submit Button -->
    <button
      @click="handleSubmit"
      :disabled="submitResource.loading || !isFormValid"
      :class="[
        'w-full flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500',
        (submitResource.loading || !isFormValid) ? 'bg-blue-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
      ]"
    >
      <svg v-if="!submitResource.loading" class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
      </svg>
      <svg v-else class="w-4 h-4 mr-2 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
      </svg>
      {{ submitResource.loading ? 'Submitting...' : 'Appeal Leave' }}
    </button>

    <!-- Error Message -->
    <div v-if="errorMessage" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
      <div class="flex items-start">
        <svg class="w-5 h-5 text-red-600 mt-0.5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div>
          <p class="text-red-700 text-sm font-medium">Unable to submit leave application</p>
          <p class="text-red-600 text-sm mt-1">{{ errorMessage }}</p>
        </div>
      </div>
    </div>

    <!-- Success Message -->
    <div v-if="successMessage" class="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
      <div class="flex items-start">
        <svg class="w-5 h-5 text-green-600 mt-0.5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div>
          <p class="text-green-700 text-sm font-medium">Success!</p>
          <p class="text-green-600 text-sm mt-1">{{ successMessage }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, onMounted, computed, ref } from 'vue'
import { createResource } from 'frappe-ui'

// Reactive state
const formData = reactive({
  from_date: "",
  to_date: "",
  reason: "",
  total_days: "",
  image: null
})

const studentInfo = reactive({
  student: "",
  student_name: "",
  student_group: ""
})

const errorMessage = ref("")
const successMessage = ref("")

// Computed property for form validation
const isFormValid = computed(() => {
  return studentInfo.student && 
         formData.from_date && 
         formData.to_date && 
         formData.reason &&
         studentInfo.student_group
})

// Load student info from localStorage
const loadStudentInfo = () => {
  try {
    const savedStudent = localStorage.getItem('selected_student')
    const savedStudentGroup = localStorage.getItem('selected_student_group')

    if (savedStudent) {
      // Parse the student data - handle both string and object formats
      let studentData
      try {
        studentData = JSON.parse(savedStudent)
      } catch (e) {
        // If it's already a string, use it directly
        studentData = savedStudent
      }

      // Extract student ID and name based on data structure
      if (typeof studentData === 'object' && studentData !== null) {
        studentInfo.student = studentData.student || studentData.name || ''
        studentInfo.student_name = studentData.student_name || studentData.name || ''
      } else {
        studentInfo.student = studentData
        studentInfo.student_name = studentData // Fallback to ID if no name available
      }

      // Handle student group
      if (savedStudentGroup) {
        try {
          const groupData = JSON.parse(savedStudentGroup)
          studentInfo.student_group = groupData.student_group || groupData.name || groupData
        } catch (e) {
          studentInfo.student_group = savedStudentGroup
        }
      }
    } else {
      errorMessage.value = 'Student data not found in storage. Please select a student first.'
    }
  } catch (err) {
    console.error("Error loading student info:", err)
    errorMessage.value = 'Failed to load student info.'
  }
}

// Watch for date changes and calculate total days
const calculateTotalDays = () => {
  if (formData.from_date && formData.to_date) {
    const fromDate = new Date(formData.from_date)
    const toDate = new Date(formData.to_date)
    
    // Validate dates
    const currentDate = new Date().toISOString().split("T")[0]
    
    if (formData.from_date < currentDate) {
      errorMessage.value = "From date cannot be in the past"
      formData.from_date = ""
      return
    }
    
    if (formData.to_date < currentDate) {
      errorMessage.value = "To date cannot be in the past"
      formData.to_date = ""
      return
    }
    
    if (toDate < fromDate) {
      errorMessage.value = "To date cannot be before From date"
      formData.to_date = ""
      return
    }
    
    errorMessage.value = ""
    
    // Calculate total days
    const diffTime = Math.abs(toDate - fromDate)
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1
    formData.total_days = diffDays.toString()
  } else {
    formData.total_days = ""
  }
}

// Convert image to base64
const convertImageToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      const base64 = reader.result.split(',')[1]
      resolve(base64)
    }
    reader.onerror = error => reject(error)
    reader.readAsDataURL(file)
  })
}

// Handle image upload
const handleImageUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    formData.image = file
  } else {
    formData.image = null
  }
}

// Submit leave application using createResource with proper error handling
const submitResource = createResource({
  url: 'school.al_ummah.api2.submit_leave_application',
  method: 'POST',
  auto: false,
  onSuccess(data) {
    console.log("API response:", data)
    
    if (data.status === "success") {
      const message = data.message || "Leave application submitted successfully!"
      successMessage.value = message
      errorMessage.value = ""
      
      // Reset form
      Object.assign(formData, {
        from_date: "",
        to_date: "",
        reason: "",
        total_days: "",
        image: null
      })
      
      // Clear success message after 5 seconds
      setTimeout(() => {
        successMessage.value = ""
      }, 5000)
    } else {
      errorMessage.value = data.message || 'Failed to submit leave application.'
    }
  },
  onError(error) {
    console.error("API error details:", {
      response: error.response,
      exc_type: error.exc_type,
      exc_message: error.exc_message,
      _server_messages: error._server_messages,
      message: error.message
    })
    
    // Handle the specific ValidationError for duplicate leave applications
    if (error.response && error.response.includes('already exists against the student')) {
      errorMessage.value = "Leave already submitted for this student. You cannot submit multiple applications."
    } 
    else if (error._server_messages && error._server_messages.includes('already exists against the student')) {
      errorMessage.value = "Leave already submitted for this student."
    }
    else if (error.exc_message && error.exc_message.includes('already exists against the student')) {
      errorMessage.value = "Leave already submitted for this student."
    }
    // Handle other ValidationErrors
    else if (error.exc_type === 'ValidationError') {
      if (error.exc_message) {
        errorMessage.value = error.exc_message.replace('frappe.exceptions.ValidationError: ', '')
      } else {
        errorMessage.value = "Validation error occurred. Please check your input."
      }
    }
    // Handle server messages
    else if (error._server_messages) {
      try {
        const serverMessages = JSON.parse(error._server_messages || '[]')
        if (serverMessages.length > 0) {
          const lastMessage = serverMessages[serverMessages.length - 1]
          const parsedMessage = JSON.parse(lastMessage)
          errorMessage.value = parsedMessage.message || 'An error occurred while submitting the leave application.'
        }
      } catch (e) {
        errorMessage.value = error.message || 'An error occurred while submitting the leave application.'
      }
    }
    // Fallback to general error message
    else {
      errorMessage.value = error.message || 'An error occurred while submitting the leave application.'
    }
    
    successMessage.value = ""
  }
})

// Handle form submission
const handleSubmit = async () => {
  if (!isFormValid.value) {
    errorMessage.value = "Please fill in all required fields."
    return
  }

  // Clear previous messages
  errorMessage.value = ""
  successMessage.value = ""

  try {
    let imageBase64 = null
    if (formData.image && formData.image instanceof File) {
      imageBase64 = await convertImageToBase64(formData.image)
    }

    const submitData = {
      student: studentInfo.student,
      from_date: formData.from_date,
      to_date: formData.to_date,
      student_group: studentInfo.student_group,
      reason: formData.reason,
      image: imageBase64,
    }

    console.log("Submitting leave application with data:", submitData)

    // Submit using createResource
    await submitResource.submit(submitData)

  } catch (error) {
    console.error("Submission error:", error)
    errorMessage.value = "An error occurred while processing your request."
  }
}

// Set up watchers for date fields
onMounted(() => {
  loadStudentInfo()
  
  // Watch for date changes
  const watchDates = () => {
    calculateTotalDays()
  }
})
</script>