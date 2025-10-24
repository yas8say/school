<!-- src/components/StudentProfileImage.vue -->
<template>
  <div>
    <!-- Current image + upload controls -->
    <div class="flex items-start space-x-8">
      <div class="flex-shrink-0">
        <label class="block text-sm font-medium text-gray-700 mb-3">Profile Image</label>
        <div class="relative">
          <div class="w-24 h-24 rounded-full border-2 border-white shadow-md overflow-hidden bg-gray-100">
            <img :src="profileImageUrl" :alt="studentName" class="w-full h-full object-cover"
                 @error="handleImageError" />
          </div>
          <div v-if="uploading" class="absolute inset-0 bg-black bg-opacity-50 rounded-full flex items-center justify-center">
            <div class="spinner-small !w-6 !h-6 !border-2"></div>
          </div>
        </div>
      </div>

      <div class="flex-1">
        <div class="space-y-4">
          <!-- Choose / Camera -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Upload New Image</label>
            <div class="flex flex-col sm:flex-row gap-3 max-w-md">
              <input type="file" ref="fileInput" accept="image/*" @change="onFileSelect" class="hidden" />
              <button type="button" @click="triggerFileInput" :disabled="uploading"
                      class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-blue-300 flex items-center space-x-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
                </svg>
                <span>Choose File</span>
              </button>
              <button type="button" @click="openCamera" :disabled="uploading"
                      class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-green-300 flex items-center space-x-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/>
                </svg>
                <span>Take Photo</span>
              </button>
            </div>

            <!-- File info -->
            <div v-if="selectedFile && !showCropper" class="mt-3 max-w-md p-3 bg-blue-50 rounded-md border border-blue-200">
              <p class="text-sm text-blue-700 flex items-center space-x-2">
                <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>
                <span class="truncate">Selected: {{ selectedFile.name }}</span>
              </p>
              <p class="text-xs text-blue-600 mt-1">Size: {{ (selectedFile.size/1024/1024).toFixed(2) }} MB</p>
            </div>
          </div>

          <!-- Update / Cancel -->
          <div v-if="(selectedFile || capturedImage) && !showCropper" class="flex space-x-3 max-w-md">
            <button type="button" @click="upload" :disabled="uploading"
                    class="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:bg-purple-300 flex items-center space-x-2 flex-1">
              <svg v-if="uploading" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
              </svg>
              <span>{{ uploading ? 'Uploading...' : 'Update Profile Image' }}</span>
            </button>
            <button type="button" @click="cancelUpload"
                    class="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 flex-1">
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Hidden video (camera) -->
    <video v-if="showCamera" ref="videoEl" autoplay playsinline class="hidden"></video>

    <!-- Camera modal -->
    <div v-if="showCamera && !showCropper"
         class="fixed inset-0 bg-black bg-opacity-90 flex flex-col items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg p-6 max-w-lg w-full">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">Take Photo</h3>
        <div class="relative bg-gray-100 rounded-lg overflow-hidden">
          <video ref="videoEl" autoplay playsinline class="w-full h-64 object-cover"></video>
          <div class="absolute bottom-4 left-1/2 transform -translate-x-1/2">
            <button type="button" @click="capturePhoto"
                    class="w-16 h-16 bg-white rounded-full shadow-lg flex items-center justify-center hover:bg-gray-100">
              <svg class="w-8 h-8 text-gray-800" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/>
              </svg>
            </button>
          </div>
        </div>
        <div class="mt-4 flex justify-end">
          <button type="button" @click="closeCamera"
                  class="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50">
            Cancel
          </button>
        </div>
      </div>
    </div>

<!-- Update the Cropper modal section in StudentProfileImage.vue -->
<div v-if="showCropper"
     class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
  <div class="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[95vh] overflow-hidden flex flex-col">
    <h3 class="text-lg font-semibold text-gray-800 mb-4 flex-shrink-0">
      {{ cropSource === 'camera' ? 'Crop Your Photo' : 'Crop Uploaded Image' }}
    </h3>
    
    <!-- Cropper Container with Fixed Height -->
    <div class="flex-1 min-h-0 bg-gray-100 rounded-lg p-4 overflow-hidden">
      <vue-cropper 
        ref="cropper"
        :src="imageToCrop"
        :aspect-ratio="1"
        :view-mode="2"
        :guides="true"
        :background="false"
        :auto-crop-area="0.8"
        :min-container-width="200"
        :min-container-height="200"
        class="cropper-container h-full w-full max-h-[50vh]"
      />
    </div>

    <!-- Controls Section - Always Visible -->
    <div class="flex-shrink-0 mt-4">
      <div class="flex justify-center items-center space-x-4 mb-4">
        <button type="button" @click="rotate(-90)" class="p-2 border rounded hover:bg-gray-100 flex items-center space-x-2" title="Rotate Left">
          <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
          <span class="text-sm">Rotate Left</span>
        </button>
        
        <button type="button" @click="rotate(90)" class="p-2 border rounded hover:bg-gray-100 flex items-center space-x-2" title="Rotate Right">
          <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
          <span class="text-sm">Rotate Right</span>
        </button>
        
        <button type="button" @click="resetCrop" class="p-2 border rounded hover:bg-gray-100 flex items-center space-x-2" title="Reset Crop">
          <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
          <span class="text-sm">Reset</span>
        </button>
      </div>

      <!-- Action Buttons - Always at Bottom -->
      <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
        <button 
          type="button" 
          @click="cancelCropping"
          class="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 font-medium transition-colors"
        >
          {{ cropSource === 'camera' ? 'Retake Photo' : 'Choose Different File' }}
        </button>
        <button 
          type="button" 
          @click="applyCrop"
          class="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 font-medium transition-colors"
        >
          Apply Crop
        </button>
      </div>
    </div>
  </div>
</div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { createResource } from 'frappe-ui'
import VueCropper from 'vue-cropperjs'
import 'cropperjs/dist/cropper.css'

const props = defineProps({
  studentId: { type: String, required: true },
  currentImage: { type: String, default: '' },
  studentName: { type: String, default: '' }
})

const emit = defineEmits(['image-updated', 'error', 'success'])

/* ---------- STATE ---------- */
const uploading = ref(false)
const selectedFile = ref(null)
const capturedImage = ref(null)
const imagePreview = ref('')
const showCamera = ref(false)
const showCropper = ref(false)
const imageToCrop = ref('')
const cropSource = ref('') // 'camera' | 'file'
const mediaStream = ref(null)

const fileInput = ref(null)
const videoEl = ref(null)
const cropper = ref(null)

/* ---------- HELPER FUNCTIONS ---------- */
const formatBase64Image = (base64String) => {
  if (!base64String || base64String === 'null' || base64String === '') {
    return '/assets/alummah/images/default-student.png'
  }
  
  // If it's already a data URL, return as is
  if (base64String.startsWith('data:')) {
    return base64String
  }
  
  // If it's just base64 data, format it as a data URL
  // Check if it looks like base64 (alphanumeric, +, /, =)
  if (/^[A-Za-z0-9+/=]+$/.test(base64String)) {
    return `data:image/jpeg;base64,${base64String}`
  }
  
  // If it's a URL or invalid, return as is (might be a regular URL)
  return base64String
}

/* ---------- COMPUTED ---------- */
const profileImageUrl = computed(() => {
  if (imagePreview.value) return imagePreview.value
  if (props.currentImage) return formatBase64Image(props.currentImage)
  return '/assets/alummah/images/default-student.png'
})

/* ---------- API ---------- */
const uploadResource = createResource({
  url: 'school.al_ummah.api2.update_student_profile_image',
  auto: false,
  onSuccess(data) {
    uploading.value = false
    if (data.status === 'success') {
      emit('image-updated', data.image_url)
      emit('success', data.message || 'Profile image updated!')
      resetAll()
    } else {
      emit('error', data.message || 'Upload failed')
    }
  },
  onError(err) {
    uploading.value = false
    emit('error', err.message || 'Upload error')
  }
})

/* ---------- FILE / CAMERA ---------- */
const triggerFileInput = () => fileInput.value?.click()

const onFileSelect = (e) => {
  const file = e.target.files[0]
  if (!file) return
  if (!file.type.startsWith('image/')) return emit('error', 'Select an image')
  if (file.size > 5 * 1024 * 1024) return emit('error', 'Image < 5 MB')
  selectedFile.value = file
  const reader = new FileReader()
  reader.onload = ev => {
    imageToCrop.value = ev.target.result
    cropSource.value = 'file'
    showCropper.value = true
  }
  reader.readAsDataURL(file)
}

const openCamera = async () => {
  showCropper.value = false
  showCamera.value = true
  try {
    mediaStream.value = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } })
    if (videoEl.value) videoEl.value.srcObject = mediaStream.value
  } catch {
    emit('error', 'Camera access denied')
    showCamera.value = false
  }
}

const capturePhoto = () => {
  if (!videoEl.value) return
  const canvas = document.createElement('canvas')
  const v = videoEl.value
  canvas.width = v.videoWidth; canvas.height = v.videoHeight
  canvas.getContext('2d').drawImage(v, 0, 0)
  imageToCrop.value = canvas.toDataURL('image/jpeg', 0.8)
  cropSource.value = 'camera'
  showCropper.value = true
  closeCamera()
}

const closeCamera = () => {
  if (mediaStream.value) mediaStream.value.getTracks().forEach(t => t.stop())
  mediaStream.value = null
  showCamera.value = false
}

/* ---------- CROPPER ---------- */
const rotate = (deg) => cropper.value?.rotate(deg)
const resetCrop = () => cropper.value?.reset()

const applyCrop = () => {
  if (!cropper.value) return
  
  try {
    const canvas = cropper.value.getCroppedCanvas()
    if (!canvas) {
      throw new Error('Canvas is null - cannot crop image')
    }
    
    // Check if toBlob is supported
    if (typeof canvas.toBlob !== 'function') {
      // Fallback: convert to data URL and create blob manually
      const dataURL = canvas.toDataURL('image/jpeg', 0.85)
      const blob = dataURLToBlob(dataURL)
      processCroppedBlob(blob)
      return
    }
    
    canvas.toBlob(blob => {
      processCroppedBlob(blob)
    }, 'image/jpeg', 0.85)
  } catch (error) {
    console.error('Error applying crop:', error)
    emit('error', 'Failed to crop image. Please try again.')
  }
}

// Helper function to convert data URL to blob
const dataURLToBlob = (dataURL) => {
  const arr = dataURL.split(',')
  const mime = arr[0].match(/:(.*?);/)[1]
  const bstr = atob(arr[1])
  let n = bstr.length
  const u8arr = new Uint8Array(n)
  while (n--) {
    u8arr[n] = bstr.charCodeAt(n)
  }
  return new Blob([u8arr], { type: mime })
}

const processCroppedBlob = (blob) => {
  const reader = new FileReader()
  reader.onload = e => {
    imagePreview.value = e.target.result
    capturedImage.value = e.target.result
    if (cropSource.value === 'file' && selectedFile.value) {
      selectedFile.value = new File([blob], selectedFile.value.name, {
        type: 'image/jpeg',
        lastModified: Date.now()
      })
    }
  }
  reader.readAsDataURL(blob)
  showCropper.value = false
  emit('success', 'Cropped – click "Update Profile Image" to save.')
}

const cancelCropping = () => {
  showCropper.value = false
  imageToCrop.value = ''
  selectedFile.value = null
  if (fileInput.value) fileInput.value.value = ''
  if (cropSource.value === 'camera') openCamera()
}

/* ---------- UPLOAD / CANCEL ---------- */
const upload = () => {
  let base64 = ''
  if (selectedFile.value) {
    const reader = new FileReader()
    reader.onload = e => { base64 = e.target.result; doUpload(base64) }
    reader.readAsDataURL(selectedFile.value)
  } else if (capturedImage.value) {
    base64 = capturedImage.value
    doUpload(base64)
  } else {
    emit('error', 'No image selected')
    return
  }
}

const doUpload = (base64) => {
  uploading.value = true
  
  // Extract just the base64 data without the data URL prefix for API
  let base64Data = base64
  if (base64.startsWith('data:')) {
    const commaIndex = base64.indexOf(',')
    if (commaIndex !== -1) {
      base64Data = base64.substring(commaIndex + 1)
    }
  }
  
  uploadResource.fetch({ 
    student_id: props.studentId, 
    base64_image: base64Data 
  })
}

const cancelUpload = () => resetAll()

const resetAll = () => {
  selectedFile.value = null
  capturedImage.value = null
  imagePreview.value = ''
  showCropper.value = false
  imageToCrop.value = ''
  if (fileInput.value) fileInput.value.value = ''
  closeCamera()
}

/* ---------- IMAGE ERROR ---------- */
const handleImageError = (e) => {
  console.warn('Image failed to load, using default image')
  e.target.src = '/assets/alummah/images/default-student.png'
}

/* ---------- WATCH currentImage prop (when base64 data is passed from parent) ---------- */
watch(() => props.currentImage, (newImage, oldImage) => {
  if (newImage !== oldImage) {
    console.log('StudentProfileImage: currentImage prop changed', {
      hasNewImage: !!newImage,
      isBase64: newImage && !newImage.startsWith('data:') && !newImage.startsWith('/'),
      length: newImage?.length
    })
    
    // Clear any preview when new base64 image is provided from parent
    if (newImage && !imagePreview.value) {
      imagePreview.value = ''
    }
  }
})
</script>

<style scoped>
.spinner-small { @apply w-5 h-5 border-2 border-gray-200 border-t-blue-600 rounded-full animate-spin; }
.cropper-container { @apply h-full w-full; }
</style>