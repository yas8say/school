<!-- src/components/ImageCompressor.vue -->
<template>
  <div class="bg-white rounded-lg border border-gray-200 p-4">
    <!-- Compression Header -->
    <div class="flex items-center justify-between mb-4">
      <div>
        <h4 class="font-medium text-gray-800">Image Compression</h4>
        <p class="text-sm text-gray-600">Optimize image size for better performance</p>
      </div>
      <div class="flex items-center space-x-2">
        <span class="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded-full">
          {{ formatFileSize(originalSize) }}
        </span>
        <span class="text-gray-400">→</span>
        <span class="text-xs px-2 py-1 bg-green-100 text-green-700 rounded-full">
          {{ formatFileSize(compressedSize) }}
        </span>
      </div>
    </div>

    <!-- Compression Controls -->
    <div class="space-y-4">
      <!-- Quality Slider -->
      <div>
        <div class="flex justify-between items-center mb-2">
          <label class="text-sm font-medium text-gray-700">Compression Quality</label>
          <span class="text-sm text-blue-600 font-medium">{{ compressionQuality }}%</span>
        </div>
        <input 
          type="range" 
          v-model="compressionQuality"
          min="10"
          max="100"
          step="5"
          class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
          @input="updateCompression"
        />
        <div class="flex justify-between text-xs text-gray-500 mt-1">
          <span>Smaller File</span>
          <span>Better Quality</span>
        </div>
      </div>

      <!-- Quick Presets -->
      <div>
        <p class="text-sm font-medium text-gray-700 mb-2">Quick Presets</p>
        <div class="grid grid-cols-4 gap-2">
          <button 
            v-for="preset in compressionPresets"
            :key="preset.name"
            @click="applyPreset(preset)"
            :class="[
              'px-3 py-2 text-xs rounded-md transition-colors border',
              preset.quality === compressionQuality 
                ? 'bg-blue-100 text-blue-700 border-blue-300' 
                : 'bg-gray-100 text-gray-700 border-gray-300 hover:bg-gray-200'
            ]"
          >
            {{ preset.name }}
          </button>
        </div>
      </div>

      <!-- Size & Dimension Controls -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="text-sm font-medium text-gray-700 mb-2 block">Max Width</label>
          <select 
            v-model="maxWidth"
            @change="updateCompression"
            class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="original">Original</option>
            <option value="800">800px</option>
            <option value="1024">1024px</option>
            <option value="1200">1200px</option>
            <option value="1600">1600px</option>
          </select>
        </div>
        <div>
          <label class="text-sm font-medium text-gray-700 mb-2 block">Format</label>
          <select 
            v-model="outputFormat"
            @change="updateCompression"
            class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="jpeg">JPEG</option>
            <option value="webp">WebP</option>
            <option value="png">PNG</option>
          </select>
        </div>
      </div>

      <!-- Compression Results -->
      <div v-if="compressedBlob" class="bg-gray-50 rounded-lg p-3 border border-gray-200">
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p class="text-gray-600">Original Size</p>
            <p class="font-medium text-gray-800">{{ formatFileSize(originalSize) }}</p>
          </div>
          <div>
            <p class="text-gray-600">Compressed Size</p>
            <p class="font-medium text-green-600">{{ formatFileSize(compressedSize) }}</p>
          </div>
          <div>
            <p class="text-gray-600">Reduction</p>
            <p class="font-medium text-blue-600">{{ sizeReduction }}%</p>
          </div>
          <div>
            <p class="text-gray-600">Dimensions</p>
            <p class="font-medium text-gray-800">{{ compressedDimensions.width }}×{{ compressedDimensions.height }}px</p>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex space-x-3 pt-2">
        <button 
          @click="applyCompression"
          :disabled="!compressedBlob || compressing"
          class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-blue-300 disabled:cursor-not-allowed flex items-center justify-center space-x-2 transition-colors"
        >
          <svg v-if="compressing" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
          <span>{{ compressing ? 'Compressing...' : 'Apply Compression' }}</span>
        </button>
        <button 
          @click="$emit('cancel')"
          class="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
        >
          Cancel
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

const emit = defineEmits(['compressed', 'cancel', 'error'])

const props = defineProps({
  imageBlob: {
    type: Blob,
    required: true
  },
  imageUrl: {
    type: String,
    default: ''
  },
  autoCompress: {
    type: Boolean,
    default: true
  },
  defaultQuality: {
    type: Number,
    default: 80
  },
  defaultMaxWidth: {
    type: [String, Number],
    default: '1024'
  }
})

// State
const compressionQuality = ref(props.defaultQuality)
const maxWidth = ref(props.defaultMaxWidth)
const outputFormat = ref('jpeg')
const compressedBlob = ref(null)
const compressing = ref(false)
const originalSize = ref(0)
const compressedSize = ref(0)
const compressedDimensions = ref({ width: 0, height: 0 })

// Compression presets
const compressionPresets = ref([
  { name: 'High', quality: 90, maxWidth: 'original' },
  { name: 'Medium', quality: 75, maxWidth: '1024' },
  { name: 'Low', quality: 50, maxWidth: '800' },
  { name: 'Minimal', quality: 30, maxWidth: '600' }
])

// Computed
const sizeReduction = computed(() => {
  if (!originalSize.value || !compressedSize.value) return 0
  return Math.round(((originalSize.value - compressedSize.value) / originalSize.value) * 100)
})

// Utility functions
const formatFileSize = (bytes) => {
  if (!bytes) return '0 KB'
  if (bytes < 1024) return bytes + ' Bytes'
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1048576).toFixed(1) + ' MB'
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

// Compression functions
const compressImage = async (blob, quality = 0.8, maxWidth = 'original', format = 'jpeg') => {
  return new Promise((resolve) => {
    const img = new Image()
    const url = URL.createObjectURL(blob)
    
    img.onload = async () => {
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')
      
      let { width, height } = img
      
      // Resize if needed
      if (maxWidth !== 'original' && width > maxWidth) {
        height = (height * maxWidth) / width
        width = maxWidth
      }
      
      canvas.width = width
      canvas.height = height
      
      // Draw image with high quality scaling
      ctx.imageSmoothingEnabled = true
      ctx.imageSmoothingQuality = 'high'
      ctx.drawImage(img, 0, 0, width, height)
      
      // Convert to desired format
      const mimeType = format === 'webp' ? 'image/webp' : 
                       format === 'png' ? 'image/png' : 'image/jpeg'
      
      canvas.toBlob(
        (compressedBlob) => {
          URL.revokeObjectURL(url)
          resolve({
            blob: compressedBlob || blob,
            dimensions: { width, height }
          })
        },
        mimeType,
        quality / 100
      )
    }
    
    img.onerror = () => {
      URL.revokeObjectURL(url)
      resolve({
        blob: blob,
        dimensions: { width: 0, height: 0 }
      })
    }
    
    img.src = url
  })
}

const updateCompression = async () => {
  if (!props.imageBlob) return
  
  compressing.value = true
  
  try {
    const result = await compressImage(
      props.imageBlob,
      compressionQuality.value,
      maxWidth.value === 'original' ? 'original' : parseInt(maxWidth.value),
      outputFormat.value
    )
    
    compressedBlob.value = result.blob
    compressedSize.value = result.blob.size
    compressedDimensions.value = result.dimensions
    
  } catch (error) {
    emit('error', 'Failed to compress image: ' + error.message)
  } finally {
    compressing.value = false
  }
}

const applyPreset = (preset) => {
  compressionQuality.value = preset.quality
  maxWidth.value = preset.maxWidth
  updateCompression()
}

const applyCompression = () => {
  if (compressedBlob.value) {
    emit('compressed', {
      blob: compressedBlob.value,
      quality: compressionQuality.value,
      dimensions: compressedDimensions.value,
      format: outputFormat.value,
      originalSize: originalSize.value,
      compressedSize: compressedSize.value,
      reduction: sizeReduction.value
    })
  }
}

// Initialize
onMounted(async () => {
  if (props.imageBlob) {
    originalSize.value = props.imageBlob.size
    
    // Get original dimensions
    if (props.imageUrl) {
      const dimensions = await getImageDimensions(props.imageUrl)
      compressedDimensions.value = dimensions
    }
    
    if (props.autoCompress) {
      await updateCompression()
    }
  }
})

// Watch for image blob changes
watch(() => props.imageBlob, async (newBlob) => {
  if (newBlob) {
    originalSize.value = newBlob.size
    if (props.autoCompress) {
      await updateCompression()
    }
  }
})
</script>

<style scoped>
.slider::-webkit-slider-thumb {
  appearance: none;
  height: 20px;
  width: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 2px solid #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.slider::-moz-range-thumb {
  height: 20px;
  width: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 2px solid #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>