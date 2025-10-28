<!-- src/components/StudentProfileImage.vue -->
<template>
  <div class="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h3 class="text-lg font-semibold text-gray-800">Profile Image</h3>
        <p class="text-sm text-gray-600 mt-1">Update student's profile picture</p>
      </div>
      <div class="w-16 h-16 rounded-full border-2 border-gray-100 shadow-sm overflow-hidden bg-gray-50 cursor-pointer" 
           @click="openImagePreview(profileImageUrl)">
        <img :src="profileImageUrl" :alt="studentName" class="w-full h-full object-cover"
             @error="handleImageError" loading="lazy" />
      </div>
    </div>

    <!-- Current Image Preview Card -->
    <div class="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
      <div class="flex items-center space-x-4">
        <div class="relative cursor-pointer" @click="openImagePreview(profileImageUrl)">
          <div class="w-20 h-20 rounded-full border-2 border-white shadow-md overflow-hidden bg-gray-100">
            <img :src="profileImageUrl" :alt="studentName" class="w-full h-full object-cover"
                 @error="handleImageError" loading="lazy" />
            <div v-if="uploading" class="absolute inset-0 bg-black bg-opacity-50 rounded-full flex items-center justify-center">
              <div class="spinner-small !w-6 !h-6 !border-2"></div>
            </div>
          </div>
          <div class="absolute bottom-0 right-0 bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs">
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
          </div>
        </div>
        <div class="flex-1">
          <h4 class="font-medium text-gray-800">{{ studentName }}</h4>
          <p class="text-sm text-gray-600">Student ID: {{ studentId }}</p>
          <p v-if="uploading" class="text-sm text-blue-600 mt-1">Uploading image...</p>
        </div>
      </div>
    </div>

    <!-- Upload Controls Card -->
    <div class="bg-blue-50 rounded-lg border border-blue-200 p-5">
      <h4 class="font-medium text-gray-800 mb-4">Upload New Image</h4>
      
      <div class="space-y-4">
        <!-- Action Buttons -->
        <div class="flex flex-col sm:flex-row gap-3">
          <input type="file" ref="fileInput" accept="image/*" @change="onFileSelect" class="hidden" />
          <button type="button" @click="triggerFileInput" :disabled="uploading"
                  class="flex-1 px-4 py-3 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:bg-gray-100 disabled:text-gray-400 flex items-center justify-center space-x-2 transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
            </svg>
            <span>Choose File</span>
          </button>
          
          <!-- Camera Dropdown -->
          <div class="relative flex-1">
            <button type="button" @click="toggleCameraDropdown" :disabled="uploading"
                    class="w-full px-4 py-3 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:bg-gray-100 disabled:text-gray-400 flex items-center justify-center space-x-2 transition-colors">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
            <div v-if="showCameraDropdown" class="absolute top-full left-0 mt-1 w-full bg-white rounded-lg shadow-lg border border-gray-200 z-10">
              <button type="button" @click="openCamera('user')" 
                      class="w-full px-4 py-3 text-left text-gray-700 hover:bg-gray-50 flex items-center space-x-3 border-b border-gray-100">
                <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"/>
                  </svg>
                </div>
                <div class="text-left">
                  <p class="font-medium">Front Camera</p>
                  <p class="text-xs text-gray-500">Take a selfie</p>
                </div>
              </button>
              <button type="button" @click="openCamera('environment')" 
                      class="w-full px-4 py-3 text-left text-gray-700 hover:bg-gray-50 flex items-center space-x-3">
                <div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                  <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
                  </svg>
                </div>
                <div class="text-left">
                  <p class="font-medium">Rear Camera</p>
                  <p class="text-xs text-gray-500">Take a photo</p>
                </div>
              </button>
            </div>
          </div>
        </div>

        <!-- File/Camera Info -->
        <div v-if="selectedFile || capturedImage" class="p-4 bg-white rounded-lg border border-gray-200">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center cursor-pointer" 
                   @click="openImagePreview(imagePreview)">
                <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                </svg>
              </div>
              <div>
                <p class="font-medium text-gray-800">
                  {{ cropSource === 'camera' ? 'Camera Photo' : selectedFile?.name }}
                </p>
                <p class="text-sm text-gray-600">
                  {{ cropSource === 'camera' ? 
                    `Captured from ${currentCamera === 'user' ? 'Front' : 'Rear'} Camera • ${formatFileSize(currentFileSize)}` : 
                    `Size: ${selectedFile ? formatFileSize(selectedFile.size) : '0 KB'}` 
                  }}
                </p>
                <p class="text-xs text-gray-500 mt-1">
                  Dimensions: {{ imageDimensions.width }} × {{ imageDimensions.height }}px
                </p>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <button type="button" @click="showCompressor = true"
                      class="px-3 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
                Compress
              </button>
              <button type="button" @click="cropSource === 'camera' ? openCamera(currentCamera) : triggerFileInput()"
                      class="px-3 py-2 text-sm text-gray-600 hover:text-gray-800 transition-colors">
                Change
              </button>
            </div>
          </div>
        </div>

        <!-- Image Compressor -->
        <ImageCompressor
          v-if="showCompressor && (selectedFile || capturedImageBlob)"
          :image-blob="selectedFile || capturedImageBlob"
          :image-url="imagePreview"
          :auto-compress="true"
          @compressed="handleCompressedImage"
          @cancel="showCompressor = false"
          @error="handleCompressionError"
        />

        <!-- Update / Cancel Buttons -->
        <div v-if="selectedFile || capturedImage" class="flex space-x-3">
          <button type="button" @click="upload" :disabled="uploading"
                  class="flex-1 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-300 disabled:cursor-not-allowed flex items-center justify-center space-x-2 transition-colors font-medium">
            <svg v-if="uploading" class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
            <span>{{ uploading ? 'Uploading...' : 'Update Profile Image' }}</span>
          </button>
          <button type="button" @click="cancelUpload"
                  class="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium">
            Cancel
          </button>
        </div>
      </div>
    </div>

    <!-- Image Preview Modal -->
    <div v-if="showImagePreview" class="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg max-w-4xl max-h-[90vh] w-full h-full flex flex-col">
        <div class="flex justify-between items-center p-4 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-800">Image Preview</h3>
          <button @click="closeImagePreview" class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <div class="flex-1 flex items-center justify-center p-8 overflow-auto">
          <img :src="previewImageUrl" alt="Preview" class="max-w-full max-h-full object-contain" />
        </div>
        <div class="p-4 border-t border-gray-200 text-center">
          <p class="text-sm text-gray-600">
            Click anywhere outside to close
          </p>
        </div>
      </div>
    </div>

    <!-- Hidden video (camera) -->
    <video v-if="showCamera" ref="videoEl" autoplay playsinline muted class="hidden"></video>

    <!-- Camera modal -->
    <div v-if="showCamera && !showCropper"
         class="fixed inset-0 bg-black bg-opacity-90 flex flex-col items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl p-6 max-w-lg w-full">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-xl font-semibold text-gray-800">Take Photo</h3>
          <div class="flex items-center space-x-2">
            <!-- Camera Switch Button -->
            <button v-if="hasMultipleCameras" type="button" @click="switchCamera"
                    class="p-3 bg-gray-100 rounded-full hover:bg-gray-200 transition-colors"
                    title="Switch Camera">
              <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"/>
              </svg>
            </button>
            <!-- Close Button -->
            <button type="button" @click="closeCamera"
                    class="p-3 bg-gray-100 rounded-full hover:bg-gray-200 transition-colors"
                    title="Close Camera">
              <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
        </div>
        
        <div class="relative bg-gray-900 rounded-xl overflow-hidden mb-4">
          <video ref="videoEl" autoplay playsinline muted class="w-full h-80 object-cover"></video>
          <div class="absolute bottom-6 left-1/2 transform -translate-x-1/2">
            <button type="button" @click="capturePhoto"
                    class="w-20 h-20 bg-white rounded-full shadow-2xl flex items-center justify-center hover:bg-gray-100 transition-colors">
              <div class="w-16 h-16 bg-white border-4 border-gray-800 rounded-full flex items-center justify-center">
                <div class="w-12 h-12 bg-gray-800 rounded-full"></div>
              </div>
            </button>
          </div>
        </div>
        
        <!-- Camera Info -->
        <div class="text-center">
          <p class="text-sm text-gray-600">
            Using: <span class="font-medium">{{ currentCamera === 'user' ? 'Front Camera' : 'Rear Camera' }}</span>
          </p>
          <p class="text-xs text-gray-500 mt-1">Position the student's face in the frame and click the button to capture</p>
        </div>
      </div>
    </div>

    <!-- Cropper modal -->
    <div v-if="showCropper"
         class="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl p-6 w-full max-w-4xl max-h-[95vh] overflow-hidden flex flex-col">
        <h3 class="text-xl font-semibold text-gray-800 mb-6 flex-shrink-0">
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
        <div class="flex-shrink-0 mt-6">
          <div class="flex justify-center items-center space-x-4 mb-6">
            <button type="button" @click="rotate(-90)" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center space-x-2 transition-colors" title="Rotate Left">
              <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
              </svg>
              <span class="font-medium">Rotate Left</span>
            </button>
            
            <button type="button" @click="rotate(90)" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center space-x-2 transition-colors" title="Rotate Right">
              <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
              </svg>
              <span class="font-medium">Rotate Right</span>
            </button>
            
            <button type="button" @click="resetCrop" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center space-x-2 transition-colors" title="Reset Crop">
              <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
              </svg>
              <span class="font-medium">Reset</span>
            </button>
          </div>

          <!-- Action Buttons -->
          <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
            <button 
              type="button" 
              @click="cancelCropping"
              class="px-8 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-colors"
            >
              {{ cropSource === 'camera' ? 'Retake Photo' : 'Choose Different File' }}
            </button>
            <button 
              type="button" 
              @click="applyCrop"
              class="px-8 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium transition-colors"
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
import ImageCompressor from '@/components/ImageCompressor.vue'

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
const capturedImageBlob = ref(null)
const imagePreview = ref('')
const showCamera = ref(false)
const showCropper = ref(false)
const showCameraDropdown = ref(false)
const showImagePreview = ref(false)
const showCompressor = ref(false)
const imageToCrop = ref('')
const previewImageUrl = ref('')
const cropSource = ref('')
const mediaStream = ref(null)
const currentCamera = ref('user')
const availableCameras = ref([])
const hasMultipleCameras = ref(false)
const localProfileImage = ref('')
const currentFileSize = ref(0)
const imageDimensions = ref({ width: 0, height: 0 })

const fileInput = ref(null)
const videoEl = ref(null)
const cropper = ref(null)

/* ---------- COMPUTED ---------- */
const profileImageUrl = computed(() => {
  if (localProfileImage.value) {
    return localProfileImage.value
  }
  if (imagePreview.value) {
    return imagePreview.value
  }
  if (props.currentImage) {
    return getProfileImageUrl(props.currentImage)
  }
  return '/assets/alummah/images/default-student.png'
})

/* ---------- UTILITY FUNCTIONS ---------- */
const formatFileSize = (bytes) => {
  if (!bytes) return '0 KB'
  if (bytes < 1024) return bytes + ' Bytes'
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1048576).toFixed(1) + ' MB'
}

const getProfileImageUrl = (imgUrl) => {
  if (!imgUrl || imgUrl === 'null' || imgUrl === '') {
    return '/assets/alummah/images/default-student.png'
  }
  
  if (imgUrl.startsWith('http') || imgUrl.startsWith('//')) {
    return imgUrl
  }
  
  if (imgUrl.startsWith('/')) {
    return window.location.origin + imgUrl
  }
  
  const baseUrl = window.location.origin
  return `${baseUrl}/${imgUrl.replace(/^\//, '')}`
}

const getImageDimensions = (src) => {
  return new Promise((resolve) => {
    const img = new Image()
    img.onload = () => {
      resolve({ width: img.width, height: img.height })
    }
    img.onerror = () => {
      resolve({ width: 0, height: 0 })
    }
    img.src = src
  })
}

/* ---------- IMAGE PREVIEW ---------- */
const openImagePreview = (imageUrl) => {
  if (!imageUrl || imageUrl === '/assets/alummah/images/default-student.png') return
  previewImageUrl.value = imageUrl
  showImagePreview.value = true
}

const closeImagePreview = () => {
  showImagePreview.value = false
  previewImageUrl.value = ''
}

/* ---------- COMPRESSION HANDLERS ---------- */
const handleCompressedImage = (result) => {
  // Update the current file/blob with compressed version
  if (cropSource.value === 'file' && selectedFile.value) {
    selectedFile.value = new File([result.blob], selectedFile.value.name, {
      type: result.blob.type,
      lastModified: Date.now()
    })
  } else if (cropSource.value === 'camera') {
    capturedImageBlob.value = result.blob
    capturedImage.value = new File([result.blob], `camera-photo-${Date.now()}.${result.format}`, {
      type: result.blob.type,
      lastModified: Date.now()
    })
  }
  
  // Update file size and dimensions
  currentFileSize.value = result.compressedSize
  imageDimensions.value = result.dimensions
  
  showCompressor.value = false
  emit('success', `Image compressed to ${result.reduction}% smaller`)
}

const handleCompressionError = (error) => {
  emit('error', error)
  showCompressor.value = false
}

/* ---------- CAMERA MANAGEMENT ---------- */
const getAvailableCameras = async () => {
  try {
    const devices = await navigator.mediaDevices.enumerateDevices()
    const videoDevices = devices.filter(device => device.kind === 'videoinput')
    availableCameras.value = videoDevices
    hasMultipleCameras.value = videoDevices.length > 1
  } catch (error) {
    // Silent fail
  }
}

const openCamera = async (facingMode = 'user') => {
  showCameraDropdown.value = false
  showCropper.value = false
  showCamera.value = true
  currentCamera.value = facingMode
  
  try {
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
    emit('error', 'Camera access denied or not available')
    showCamera.value = false
  }
}

const switchCamera = async () => {
  const newCamera = currentCamera.value === 'user' ? 'environment' : 'user'
  await openCamera(newCamera)
}

const toggleCameraDropdown = () => {
  showCameraDropdown.value = !showCameraDropdown.value
}

const handleClickOutside = (event) => {
  if (!event.target.closest('.relative')) {
    showCameraDropdown.value = false
  }
}

/* ---------- API ---------- */
const uploadResource = createResource({
  url: 'school.al_ummah.api2.update_student_profile_image',
  auto: false,
  onSuccess(data) {
    uploading.value = false
    
    if (data.status === 'success') {
      localProfileImage.value = imagePreview.value
      emit('image-updated', data.image_url)
      emit('success', data.message || 'Profile image updated successfully!')
      resetAll()
    } else {
      emit('error', data.message || 'Upload failed')
    }
  },
  onError(err) {
    uploading.value = false
    emit('error', err.message || 'Upload error occurred')
  }
})

/* ---------- FILE / CAMERA ---------- */
const triggerFileInput = () => fileInput.value?.click()

const onFileSelect = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  if (!file.type.startsWith('image/')) return emit('error', 'Select an image')
  if (file.size > 10 * 1024 * 1024) return emit('error', 'Image must be less than 10MB')
  
  selectedFile.value = file
  currentFileSize.value = file.size
  
  const reader = new FileReader()
  reader.onload = async (ev) => {
    imageToCrop.value = ev.target.result
    imagePreview.value = ev.target.result
    cropSource.value = 'file'
    
    // Get image dimensions
    const dimensions = await getImageDimensions(ev.target.result)
    imageDimensions.value = dimensions
    
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
  
  canvas.toBlob(async (blob) => {
    if (!blob) return
    
    capturedImageBlob.value = blob
    currentFileSize.value = blob.size
    
    capturedImage.value = new File([blob], `camera-photo-${Date.now()}.jpg`, {
      type: 'image/jpeg',
      lastModified: Date.now()
    })
    
    const reader = new FileReader()
    reader.onload = async (e) => {
      imageToCrop.value = e.target.result
      imagePreview.value = e.target.result
      cropSource.value = 'camera'
      
      // Get image dimensions
      const dimensions = await getImageDimensions(e.target.result)
      imageDimensions.value = dimensions
      
      showCropper.value = true
    }
    reader.readAsDataURL(blob)
    
  }, 'image/jpeg', 0.8)
  
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
      throw new Error('Cannot crop image')
    }
    
    // Use 0.8 quality by default for good compression
    canvas.toBlob((blob) => {
      if (!blob) {
        emit('error', 'Failed to process cropped image')
        return
      }
      
      processCroppedBlob(blob)
    }, 'image/jpeg', 0.8)
  } catch (error) {
    emit('error', 'Failed to crop image. Please try again.')
  }
}

const processCroppedBlob = async (blob) => {
  const reader = new FileReader()
  reader.onload = async (e) => {
    const croppedImageDataUrl = e.target.result
    
    localProfileImage.value = croppedImageDataUrl
    imagePreview.value = croppedImageDataUrl
    currentFileSize.value = blob.size
    
    // Update dimensions for cropped image
    const dimensions = await getImageDimensions(croppedImageDataUrl)
    imageDimensions.value = dimensions
    
    if (cropSource.value === 'file' && selectedFile.value) {
      selectedFile.value = new File([blob], selectedFile.value.name, {
        type: 'image/jpeg',
        lastModified: Date.now()
      })
    } else if (cropSource.value === 'camera') {
      capturedImage.value = new File([blob], `camera-photo-${Date.now()}.jpg`, {
        type: 'image/jpeg',
        lastModified: Date.now()
      })
      capturedImageBlob.value = blob
    }
  }
  reader.readAsDataURL(blob)
  showCropper.value = false
  emit('success', 'Image cropped successfully! Click "Update Profile Image" to save.')
}

const cancelCropping = () => {
  showCropper.value = false
  imageToCrop.value = ''
  if (cropSource.value === 'file') {
    selectedFile.value = null
    if (fileInput.value) fileInput.value.value = ''
  } else {
    capturedImage.value = null
    capturedImageBlob.value = null
    openCamera(currentCamera.value)
  }
}

/* ---------- UPLOAD / CANCEL ---------- */
const upload = () => {
  let base64 = ''
  
  if (selectedFile.value) {
    const reader = new FileReader()
    reader.onload = e => { 
      base64 = e.target.result
      doUpload(base64) 
    }
    reader.readAsDataURL(selectedFile.value)
  } else if (capturedImage.value && capturedImageBlob.value) {
    const reader = new FileReader()
    reader.onload = e => { 
      base64 = e.target.result
      doUpload(base64) 
    }
    reader.readAsDataURL(capturedImageBlob.value)
  } else {
    emit('error', 'No image selected or image data missing')
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
  
  uploadResource.fetch({ 
    student_id: props.studentId, 
    base64_image: base64Data 
  })
}

const cancelUpload = () => resetAll()

const resetAll = () => {
  selectedFile.value = null
  capturedImage.value = null
  capturedImageBlob.value = null
  imagePreview.value = ''
  showCropper.value = false
  imageToCrop.value = ''
  showCameraDropdown.value = false
  showCompressor.value = false
  currentFileSize.value = 0
  imageDimensions.value = { width: 0, height: 0 }
  if (fileInput.value) fileInput.value.value = ''
  closeCamera()
}

/* ---------- IMAGE ERROR ---------- */
const handleImageError = (e) => {
  e.target.src = '/assets/alummah/images/default-student.png'
}

/* ---------- LIFECYCLE ---------- */
onMounted(() => {
  getAvailableCameras()
  document.addEventListener('click', handleClickOutside)
  
  if (props.currentImage) {
    localProfileImage.value = getProfileImageUrl(props.currentImage)
  }
})

onUnmounted(() => {
  closeCamera()
  document.removeEventListener('click', handleClickOutside)
})

/* ---------- WATCH currentImage prop ---------- */
watch(() => props.currentImage, (newImage) => {
  if (newImage) {
    localProfileImage.value = getProfileImageUrl(newImage)
  }
})
</script>

<style scoped>
.spinner-small { 
  @apply w-5 h-5 border-2 border-gray-200 border-t-blue-600 rounded-full animate-spin; 
}
.cropper-container { 
  @apply h-full w-full; 
}
</style>