<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <div class="max-w-4xl mx-auto">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-800">Admin Settings</h1>
        <p class="text-gray-600 mt-2">Manage system configuration and permissions</p>
      </div>

      <!-- Settings Form -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <div v-if="loading" class="flex justify-center py-8">
          <div class="spinner"></div>
          <span class="ml-3 text-gray-700">Loading settings...</span>
        </div>

        <div v-else-if="loadError" class="text-center py-8">
          <div class="text-red-600 mb-4">
            <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.35 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h3 class="text-lg font-medium text-gray-800 mb-2">Failed to load settings</h3>
          <p class="text-gray-600 mb-4">{{ loadError }}</p>
          <button
            @click="retryLoadSettings"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
        </div>

        <form v-else @submit.prevent="handleSaveSettings">
          <!-- Allow Instructors to Modify Student Data -->
          <div class="mb-8">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-lg font-medium text-gray-800 mb-2">
                  Allow Instructors to modify Student data
                </h3>
                <p class="text-gray-600 text-sm">
                  When enabled, instructors will have permission to edit and update student information
                </p>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  v-model="settings.allow_instructors_modify_student"
                  class="sr-only peer"
                >
                <div class="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </div>

          <!-- Allow Students Promotion for Instructors -->
          <div class="mb-8">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-lg font-medium text-gray-800 mb-2">
                  Allow Students Promotion for Instructors
                </h3>
                <p class="text-gray-600 text-sm">
                  When enabled, instructors will have permission to promote students to the next academic year
                </p>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  v-model="settings.allow_students_promotion_for_instructors"
                  class="sr-only peer"
                >
                <div class="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </div>

          <!-- Next Academic Year Picker -->
          <div class="mb-8" v-if="settings.allow_students_promotion_for_instructors">
            <label for="next_academic_year" class="block text-lg font-medium text-gray-800 mb-2">
              Next Academic Year
            </label>
            <p class="text-gray-600 text-sm mb-4">
              Select the academic year that will be used for student promotions
            </p>
            <select
              id="next_academic_year"
              v-model="settings.next_academic_year"
              class="w-full max-w-md px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              :disabled="academicYearsLoading"
            >
              <option value="" disabled>Select Academic Year</option>
              <option 
                v-for="year in academicYears" 
                :key="year.name" 
                :value="year.name"
              >
                {{ year.academic_year_name || year.name }}
              </option>
            </select>
            <div v-if="academicYearsLoading" class="mt-2 text-sm text-gray-600">
              Loading academic years...
            </div>
            <div v-else-if="academicYears.length === 0" class="mt-2 text-sm text-yellow-600">
              No academic years available. Please contact administrator.
            </div>
            
            <!-- Show current next academic year value -->
            <div v-if="originalSettings.next_academic_year" class="mt-3 p-3 bg-blue-50 rounded-lg">
              <p class="text-sm text-blue-700">
                <span class="font-medium">Current setting:</span> 
                {{ getAcademicYearName(originalSettings.next_academic_year) }}
              </p>
            </div>
          </div>

          <!-- Session Expiry -->
          <div class="mb-8">
            <label for="session_expiry" class="block text-lg font-medium text-gray-800 mb-2">
              Session Expiry (HH:MM)
            </label>
            <p class="text-gray-600 text-sm mb-4">
              Set the duration after which user sessions will automatically expire in hours and minutes
            </p>
            <div class="flex items-center space-x-4">
              <div class="flex items-center space-x-2">
                <input
                  id="hours"
                  type="number"
                  v-model.number="hours"
                  min="0"
                  class="w-24 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Hours"
                >
                <span class="text-gray-600">:</span>
                <input
                  id="minutes"
                  type="number"
                  v-model.number="minutes"
                  min="0"
                  max="59"
                  class="w-20 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Minutes"
                >
              </div>
              <div class="text-sm text-gray-600">
                <div v-if="totalHours > 0">
                  Equivalent to:
                  <span class="font-medium text-gray-800">
                    {{ formatDuration(totalHours) }}
                  </span>
                </div>
                <div v-else class="text-gray-500">
                  Enter hours and minutes
                </div>
              </div>
            </div>
            <p class="text-gray-500 text-xs mt-2">
              No maximum limit - set any duration as needed
            </p>
            
            <!-- Quick Presets -->
            <div class="mt-4 flex flex-wrap gap-2">
              <button
                type="button"
                @click="setPreset(1, 0)"
                class="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
              >
                1 hour
              </button>
              <button
                type="button"
                @click="setPreset(8, 0)"
                class="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
              >
                8 hours
              </button>
              <button
                type="button"
                @click="setPreset(24, 0)"
                class="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
              >
                24 hours
              </button>
              <button
                type="button"
                @click="setPreset(168, 0)"
                class="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
              >
                1 week
              </button>
              <button
                type="button"
                @click="setPreset(720, 0)"
                class="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
              >
                1 month
              </button>
            </div>

            <!-- Current Setting Display -->
            <div v-if="originalSessionExpiryFormat" class="mt-3 p-3 bg-blue-50 rounded-lg">
              <p class="text-sm text-blue-700">
                <span class="font-medium">Current setting:</span> 
                {{ originalSessionExpiryFormat }} ({{ formatDuration(totalHours) }})
              </p>
            </div>
          </div>

          <!-- Save Button -->
          <div class="flex justify-end space-x-4 pt-6 border-t">
            <button
              type="button"
              @click="resetForm"
              :disabled="saving"
              class="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Reset
            </button>
            <button
              type="submit"
              :disabled="saving || !hasChanges"
              :class="[
                'px-8 py-3 rounded-lg font-medium transition-colors',
                saving || !hasChanges
                  ? 'bg-gray-400 cursor-not-allowed text-white'
                  : 'bg-blue-600 hover:bg-blue-700 text-white'
              ]"
            >
              {{ saving ? 'Saving...' : 'Save Settings' }}
            </button>
          </div>
        </form>
      </div>

      <!-- Success Message -->
      <div
        v-if="successMessage"
        class="mt-4 p-4 bg-green-100 text-green-700 rounded-lg border border-green-200"
      >
        {{ successMessage }}
      </div>

      <!-- Error Message -->
      <div
        v-if="errorMessage"
        class="mt-4 p-4 bg-red-100 text-red-700 rounded-lg border border-red-200"
      >
        {{ errorMessage }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { createResource } from 'frappe-ui'

// Default settings
const defaultSettings = {
  allow_instructors_modify_student: false,
  allow_students_promotion_for_instructors: false,
  next_academic_year: '',
  session_expiry: '24:00' // HH:MM format
}

// Reactive state
const settings = reactive({ ...defaultSettings })
const originalSettings = ref({ ...defaultSettings })
const originalSessionExpiryFormat = ref('')
const academicYears = ref([])
const academicYearsLoading = ref(false)
const hours = ref(24)
const minutes = ref(0)
const loading = ref(true)
const loadError = ref('')
const saving = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

// API Resources
const academicYearsResource = createResource({
  url: 'school.al_ummah.api3.get_next_academic_years',
  params: { values: {} },
  onSuccess: (data) => {
    academicYears.value = Array.isArray(data) ? data : [];
    academicYearsLoading.value = false;
  },
  onError: (err) => {
    console.error('Error fetching academic years:', err);
    academicYears.value = [];
    academicYearsLoading.value = false;
    showMessage(`Error fetching academic years: ${err.messages?.[0] || 'Unknown error'}`, 'error');
  }
});

// Convert HH:MM to hours and minutes
const parseTimeFormat = (timeString) => {
  if (!timeString) return { hours: 24, minutes: 0 }
  const [h, m] = timeString.split(':').map(Number)
  return { hours: h || 0, minutes: m || 0 }
}

// Update settings.session_expiry when hours or minutes change
watch([hours, minutes], () => {
  settings.session_expiry = `${hours.value}:${minutes.value.toString().padStart(2, '0')}`
})

// Total hours for display
const totalHours = computed(() => {
  return hours.value + (minutes.value / 60)
})

// Computed property to check if there are changes
const hasChanges = computed(() => {
  return (
    settings.allow_instructors_modify_student !== originalSettings.value.allow_instructors_modify_student ||
    settings.allow_students_promotion_for_instructors !== originalSettings.value.allow_students_promotion_for_instructors ||
    settings.next_academic_year !== originalSettings.value.next_academic_year ||
    settings.session_expiry !== originalSettings.value.session_expiry
  )
})

// Get academic year display name
const getAcademicYearName = (yearName) => {
  const year = academicYears.value.find(ay => ay.name === yearName)
  return year ? (year.academic_year_name || year.name) : yearName
}

// Format duration for display
const formatDuration = (hours) => {
  const totalHours = Math.floor(hours)
  
  if (totalHours < 24) {
    return `${totalHours} hour${totalHours !== 1 ? 's' : ''}`
  } else if (totalHours < 168) {
    const days = Math.floor(totalHours / 24)
    const remainingHours = totalHours % 24
    if (remainingHours === 0) {
      return `${days} day${days !== 1 ? 's' : ''}`
    }
    return `${days} day${days !== 1 ? 's' : ''} and ${remainingHours} hour${remainingHours !== 1 ? 's' : ''}`
  } else if (totalHours < 8760) {
    const weeks = Math.floor(totalHours / 168)
    const remainingDays = Math.floor((totalHours % 168) / 24)
    if (remainingDays === 0) {
      return `${weeks} week${weeks !== 1 ? 's' : ''}`
    }
    return `${weeks} week${weeks !== 1 ? 's' : ''} and ${remainingDays} day${remainingDays !== 1 ? 's' : ''}`
  } else {
    const years = Math.floor(totalHours / 8760)
    const remainingWeeks = Math.floor((totalHours % 8760) / 168)
    if (remainingWeeks === 0) {
      return `${years} year${years !== 1 ? 's' : ''}`
    }
    return `${years} year${years !== 1 ? 's' : ''} and ${remainingWeeks} week${remainingWeeks !== 1 ? 's' : ''}`
  }
}

// Set preset values
const setPreset = (h, m) => {
  hours.value = h
  minutes.value = m
}

// Show message helper function
const showMessage = (message, type = 'info') => {
  if (type === 'error') {
    errorMessage.value = message
    setTimeout(() => {
      errorMessage.value = ''
    }, 5000)
  } else {
    successMessage.value = message
    setTimeout(() => {
      successMessage.value = ''
    }, 5000)
  }
}

// Create resource for fetching settings
const fetchSettingsResource = createResource({
  url: 'school.al_ummah.api3.fetch_admin_settings',
  onSuccess(data) {
    console.log('Settings fetched successfully:', data)
    
    // Update settings with fetched values (convert from int to boolean)
    settings.allow_instructors_modify_student = data.allow_instructors_modify_student === 1
    settings.allow_students_promotion_for_instructors = data.allow_students_promotion_for_instructors === 1
    settings.next_academic_year = data.next_academic_year || ''
    
    // Handle session expiry format (e.g., "170:00")
    if (data.session_expiry) {
      settings.session_expiry = data.session_expiry
      originalSessionExpiryFormat.value = data.session_expiry
      const time = parseTimeFormat(data.session_expiry)
      hours.value = time.hours
      minutes.value = time.minutes
    } else {
      settings.session_expiry = '24:00'
      originalSessionExpiryFormat.value = '24:00'
      hours.value = 24
      minutes.value = 0
    }
    
    // Update original settings
    originalSettings.value = { ...settings }
    
    loading.value = false
    loadError.value = ''
  },
  onError(error) {
    console.error('Error fetching settings:', error)
    loading.value = false
    loadError.value = error?.message || 'Failed to load settings from server.'
  }
})

// Create resource for saving settings
const saveSettingsResource = createResource({
  url: 'school.al_ummah.api3.save_admin_settings',
  onSuccess(data) {
    console.log('Settings saved successfully:', data)
    saving.value = false
    
    // Update original settings to current values
    originalSettings.value = { ...settings }
    originalSessionExpiryFormat.value = settings.session_expiry
    
    successMessage.value = 'Settings saved successfully!'
    errorMessage.value = ''
    
    // Clear success message after 5 seconds
    setTimeout(() => {
      successMessage.value = ''
    }, 5000)
  },
  onError(error) {
    console.error('Error saving settings:', error)
    saving.value = false
    errorMessage.value = error?.message || 'Failed to save settings. Please try again.'
    successMessage.value = ''
  }
})

// Handle save settings
const handleSaveSettings = async () => {
  if (!hasChanges.value) {
    errorMessage.value = 'No changes to save.'
    return
  }

  // Validate session expiry - only basic validation
  if (hours.value < 0 || minutes.value < 0 || minutes.value > 59) {
    errorMessage.value = 'Hours cannot be negative and minutes must be between 0-59.'
    return
  }

  if (hours.value === 0 && minutes.value === 0) {
    errorMessage.value = 'Session expiry cannot be zero.'
    return
  }

  // Validate next academic year if promotion is enabled
  if (settings.allow_students_promotion_for_instructors && !settings.next_academic_year) {
    errorMessage.value = 'Please select a next academic year when allowing student promotion.'
    return
  }

  saving.value = true
  successMessage.value = ''
  errorMessage.value = ''

  try {
    await saveSettingsResource.submit({
      allow_instructors_modify_student: settings.allow_instructors_modify_student,
      allow_students_promotion_for_instructors: settings.allow_students_promotion_for_instructors,
      next_academic_year: settings.next_academic_year,
      session_expiry: settings.session_expiry // Send in HH:MM format
    })
  } catch (error) {
    console.error('Error in save settings:', error)
    saving.value = false
    errorMessage.value = 'An unexpected error occurred. Please try again.'
  }
}

// Reset form to original values
const resetForm = () => {
  Object.assign(settings, originalSettings.value)
  const time = parseTimeFormat(originalSettings.value.session_expiry)
  hours.value = time.hours
  minutes.value = time.minutes
  successMessage.value = ''
  errorMessage.value = ''
}

// Retry loading settings
const retryLoadSettings = () => {
  loading.value = true
  loadError.value = ''
  fetchSettingsResource.submit()
}

// Load existing settings when component mounts
onMounted(() => {
  console.log('Admin Settings component mounted, fetching settings...')
  academicYearsLoading.value = true
  academicYearsResource.submit()
  fetchSettingsResource.submit()
})
</script>

<style scoped>
.spinner {
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
</style>