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
              
              <!-- Camera Dropdown -->
              <div class="relative">
                <button type="button" @click="toggleCameraDropdown" :disabled="uploading"
                        class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-green-300 flex items-center space-x-2">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/>
                  </svg>
                  <span>Take Photo</span>
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                  </svg>
                </button>
                
                <!-- Camera Options Dropdown -->
                <div v-if="showCameraDropdown" class="absolute top-full left-0 mt-1 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-10">
                  <button type="button" @click="openCamera('user')" 
                          class="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2">
                    <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"/>
                    </svg>
                    <span>Front Camera</span>
                  </button>
                  <button type="button" @click="openCamera('environment')" 
                          class="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2 border-t border-gray-100">
                    <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
                    </svg>
                    <span>Rear Camera</span>
                  </button>
                </div>
              </div>
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
    <video v-if="showCamera" ref="videoEl" autoplay playsinline muted class="hidden"></video>

    <!-- Camera modal -->
    <div v-if="showCamera && !showCropper"
         class="fixed inset-0 bg-black bg-opacity-90 flex flex-col items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg p-6 max-w-lg w-full">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-800">Take Photo</h3>
          <div class="flex items-center space-x-2">
            <!-- Camera Switch Button -->
            <button v-if="hasMultipleCameras" type="button" @click="switchCamera"
                    class="p-2 bg-gray-200 rounded-full hover:bg-gray-300 transition-colors"
                    title="Switch Camera">
              <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"/>
              </svg>
            </button>
            <!-- Close Button -->
            <button type="button" @click="closeCamera"
                    class="p-2 bg-gray-200 rounded-full hover:bg-gray-300 transition-colors"
                    title="Close Camera">
              <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
        </div>
        
        <div class="relative bg-gray-100 rounded-lg overflow-hidden">
          <video ref="videoEl" autoplay playsinline muted class="w-full h-64 object-cover"></video>
          <div class="absolute bottom-4 left-1/2 transform -translate-x-1/2">
            <button type="button" @click="capturePhoto"
                    class="w-16 h-16 bg-white rounded-full shadow-lg flex items-center justify-center hover:bg-gray-100 transition-colors">
              <div class="w-14 h-14 bg-white border-2 border-gray-300 rounded-full flex items-center justify-center">
                <div class="w-12 h-12 bg-gray-800 rounded-full"></div>
              </div>
            </button>
          </div>
        </div>
        
        <!-- Camera Info -->
        <div class="mt-3 text-center">
          <p class="text-sm text-gray-600">
            Using: {{ currentCamera === 'user' ? 'Front Camera' : 'Rear Camera' }}
          </p>
        </div>
      </div>
    </div>

    <!-- Cropper modal -->
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

        <!-- Controls Section -->
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

          <!-- Action Buttons -->
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
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
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
const showCameraDropdown = ref(false)
const imageToCrop = ref('')
const cropSource = ref('') // 'camera' | 'file'
const mediaStream = ref(null)
const currentCamera = ref('user') // 'user' (front) or 'environment' (rear)
const availableCameras = ref([])
const hasMultipleCameras = ref(false)

// Store the final uploaded image locally
const localProfileImage = ref('')

const fileInput = ref(null)
const videoEl = ref(null)
const cropper = ref(null)

/* ---------- CAMERA MANAGEMENT ---------- */
// Get available cameras
const getAvailableCameras = async () => {
  try {
    const devices = await navigator.mediaDevices.enumerateDevices()
    const videoDevices = devices.filter(device => device.kind === 'videoinput')
    availableCameras.value = videoDevices
    hasMultipleCameras.value = videoDevices.length > 1
    
    console.log('Available cameras:', videoDevices.map(d => ({
      label: d.label,
      deviceId: d.deviceId,
      kind: d.kind
    })))
  } catch (error) {
    console.error('Error enumerating cameras:', error)
  }
}

// Open camera with specific facing mode
const openCamera = async (facingMode = 'user') => {
  showCameraDropdown.value = false
  showCropper.value = false
  showCamera.value = true
  currentCamera.value = facingMode
  
  try {
    // Stop existing stream
    if (mediaStream.value) {
      mediaStream.value.getTracks().forEach(track => track.stop())
    }

    const constraints = {
      video: { 
        facingMode: facingMode,
        width: { ideal: 1920 },
        height: { ideal: 1080 }
      }
    }

    mediaStream.value = await navigator.mediaDevices.getUserMedia(constraints)
    if (videoEl.value) {
      videoEl.value.srcObject = mediaStream.value
    }
  } catch (error) {
    console.error('Error accessing camera:', error)
    emit('error', 'Camera access denied or not available')
    showCamera.value = false
  }
}

// Switch between front and rear cameras
const switchCamera = async () => {
  const newCamera = currentCamera.value === 'user' ? 'environment' : 'user'
  await openCamera(newCamera)
}

// Toggle camera dropdown
const toggleCameraDropdown = () => {
  showCameraDropdown.value = !showCameraDropdown.value
}

// Close camera dropdown when clicking outside
const handleClickOutside = (event) => {
  if (!event.target.closest('.relative')) {
    showCameraDropdown.value = false
  }
}

/* ---------- HELPER FUNCTIONS ---------- */
const formatBase64Image = (base64String) => {
  if (!base64String || base64String === 'null' || base64String === '') {
    return '/assets/alummah/images/default-student.png'
  }
  
  if (base64String.startsWith('data:')) {
    return base64String
  }
  
  if (/^[A-Za-z0-9+/=]+$/.test(base64String)) {
    return `data:image/jpeg;base64,${base64String}`
  }
  
  return base64String
}

/* ---------- COMPUTED ---------- */
const profileImageUrl = computed(() => {
  // Priority: 1. Local uploaded image, 2. Preview image, 3. Current prop image, 4. Default
  if (localProfileImage.value) {
    return localProfileImage.value
  }
  if (imagePreview.value) {
    return imagePreview.value
  }
  if (props.currentImage) {
    return formatBase64Image(props.currentImage)
  }
  return '/assets/alummah/images/default-student.png'
})

/* ---------- API ---------- */
const uploadResource = createResource({
  url: 'school.al_ummah.api2.update_student_profile_image',
  auto: false,
  onSuccess(data) {
    uploading.value = false
    console.log('🟢 Upload response details:', {
      status: data.status,
      message: data.message,
      image_url: data.image_url,
      full_response: data
    })
    
    if (data.status === 'success') {
      console.log('✅ Upload successful, updating UI with image:', data.image_url)
      
      // Store the uploaded image locally for immediate display
      if (capturedImage.value) {
        localProfileImage.value = capturedImage.value
      } else if (selectedFile.value) {
        // For file uploads, we need to store the preview
        localProfileImage.value = imagePreview.value
      }
      
      emit('image-updated', data.image_url)
      emit('success', data.message || 'Profile image updated successfully!')
      resetAll()
    } else {
      console.error('❌ Upload failed:', data.message)
      emit('error', data.message || 'Upload failed')
    }
  },
  onError(err) {
    uploading.value = false
    console.error('🔴 Upload error:', err)
    emit('error', err.message || 'Upload error occurred')
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

const capturePhoto = () => {
  if (!videoEl.value) return
  const canvas = document.createElement('canvas')
  const v = videoEl.value
  canvas.width = v.videoWidth
  canvas.height = v.videoHeight
  canvas.getContext('2d').drawImage(v, 0, 0)
  imageToCrop.value = canvas.toDataURL('image/jpeg', 0.8)
  cropSource.value = 'camera'
  showCropper.value = true
  closeCamera()
}

const closeCamera = () => {
  if (mediaStream.value) {
    mediaStream.value.getTracks().forEach(track => track.stop())
  }
  mediaStream.value = null
  showCamera.value = false
  showCameraDropdown.value = false
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
    
    if (typeof canvas.toBlob !== 'function') {
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
    const croppedImageDataUrl = e.target.result
    
    // UPDATE: Store the cropped image in localProfileImage immediately
    localProfileImage.value = croppedImageDataUrl
    imagePreview.value = croppedImageDataUrl
    capturedImage.value = croppedImageDataUrl
    
    if (cropSource.value === 'file' && selectedFile.value) {
      selectedFile.value = new File([blob], selectedFile.value.name, {
        type: 'image/jpeg',
        lastModified: Date.now()
      })
    }
    
    console.log('✅ Cropped image applied and stored locally:', {
      hasLocalImage: !!localProfileImage.value,
      localImageLength: localProfileImage.value?.length
    })
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
  if (cropSource.value === 'camera') openCamera(currentCamera.value)
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
  
  let base64Data = base64
  if (base64.startsWith('data:')) {
    const commaIndex = base64.indexOf(',')
    if (commaIndex !== -1) {
      base64Data = base64.substring(commaIndex + 1)
    }
  }
  
  console.log('Uploading image data:', {
    studentId: props.studentId,
    dataLength: base64Data.length,
    startsWith: base64Data.substring(0, 20) + '...'
  })
  
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
  showCameraDropdown.value = false
  if (fileInput.value) fileInput.value.value = ''
  closeCamera()
  
  // Don't reset localProfileImage here - we want to keep it
  // Only reset if user explicitly cancels the entire process
}

/* ---------- IMAGE ERROR ---------- */
const handleImageError = (e) => {
  console.warn('Image failed to load, using default image')
  e.target.src = '/assets/alummah/images/default-student.png'
}

/* ---------- LIFECYCLE ---------- */
onMounted(() => {
  getAvailableCameras()
  document.addEventListener('click', handleClickOutside)
  
  // Initialize local profile image with current prop
  if (props.currentImage) {
    localProfileImage.value = formatBase64Image(props.currentImage)
  }
})

onUnmounted(() => {
  closeCamera()
  document.removeEventListener('click', handleClickOutside)
})

/* ---------- WATCH currentImage prop ---------- */
watch(() => props.currentImage, (newImage, oldImage) => {
  if (newImage !== oldImage) {
    console.log('StudentProfileImage: currentImage prop changed', {
      hasNewImage: !!newImage,
      isBase64: newImage && !newImage.startsWith('data:') && !newImage.startsWith('/'),
      length: newImage?.length
    })
    
    // Update local profile image when prop changes (e.g., from parent component)
    if (newImage) {
      localProfileImage.value = formatBase64Image(newImage)
    }
    
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