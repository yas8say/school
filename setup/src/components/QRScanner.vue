<template>
  <div class="qr-scanner-component">
    <!-- Camera Controls -->
    <div class="camera-controls">
      <button 
        @click="switchCamera" 
        class="secondary-button"
        :disabled="!cameraActive"
      >
        <span class="button-content">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          Switch Camera ({{ currentCamera }})
        </span>
      </button>
      
      <button 
        @click="startScanner" 
        class="primary-button"
        v-if="!cameraActive"
      >
        Start Scanner
      </button>
      
      <button 
        @click="stopScanner" 
        class="secondary-button"
        v-if="cameraActive"
      >
        Stop Scanner
      </button>
    </div>

    <!-- QR Scanner Container -->
    <div class="scanner-container">
      <div id="qr-scanner" ref="qrScanner" class="qr-scanner"></div>
      <div class="scanner-overlay">
        <div class="scan-frame"></div>
        <p class="scan-instruction">Position QR code within the frame</p>
      </div>
    </div>

    <!-- Scanner Status -->
    <div v-if="errorMessage" class="message error">
      {{ errorMessage }}
    </div>

    <div v-if="loading" class="loading-text">
      Initializing camera...
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue';
import { Html5Qrcode } from 'html5-qrcode';

export default {
  name: 'QRScanner',
  emits: ['qrScanned', 'error'],
  
  setup(props, { emit }) {
    // Reactive state
    const currentCamera = ref('rear');
    const cameraActive = ref(false);
    const errorMessage = ref('');
    const loading = ref(false);
    
    // QR Scanner instance
    let html5QrCode = null;
    const qrScanner = ref(null);

    // Methods
    async function startScanner() {
      try {
        loading.value = true;
        errorMessage.value = '';

        const cameras = await Html5Qrcode.getCameras();
        if (cameras.length === 0) {
          errorMessage.value = 'No cameras found on this device';
          emit('error', 'No cameras found');
          loading.value = false;
          return;
        }

        // Determine which camera to use
        let cameraId;
        if (currentCamera.value === 'rear' && cameras.length > 1) {
          // Prefer rear camera if available
          cameraId = cameras.find(cam => 
            cam.label.toLowerCase().includes('back') || 
            cam.label.toLowerCase().includes('rear')
          )?.id || cameras[1].id;
        } else {
          cameraId = cameras[0].id;
        }

        html5QrCode = new Html5Qrcode("qr-scanner");
        
        await html5QrCode.start(
          cameraId,
          {
            fps: 10,
            qrbox: { width: 250, height: 250 },
            aspectRatio: 1.0
          },
          (decodedText) => {
            onQRCodeScanned(decodedText);
          },
          (errorMessage) => {
            // Silent error handling for scanning failures
            console.debug(`QR scan attempt: ${errorMessage}`);
          }
        );
        
        cameraActive.value = true;
        loading.value = false;
        errorMessage.value = '';
      } catch (err) {
        console.error('Error starting scanner:', err);
        errorMessage.value = 'Failed to start camera: ' + err.message;
        emit('error', err.message);
        loading.value = false;
      }
    }

    async function stopScanner() {
      if (html5QrCode && cameraActive.value) {
        try {
          await html5QrCode.stop();
          cameraActive.value = false;
        } catch (err) {
          console.error('Error stopping scanner:', err);
          emit('error', err.message);
        }
      }
    }

    async function switchCamera() {
      currentCamera.value = currentCamera.value === 'rear' ? 'front' : 'rear';
      if (cameraActive.value) {
        await stopScanner();
        await startScanner();
      }
    }

    function onQRCodeScanned(decodedText) {
      console.log('QR Code scanned:', decodedText);
      emit('qrScanned', decodedText);
    }

    function getCameraStatus() {
      return {
        active: cameraActive.value,
        currentCamera: currentCamera.value
      };
    }

    // Lifecycle
    onMounted(() => {
      // Auto-start scanner when component mounts
      setTimeout(startScanner, 100);
    });

    onUnmounted(() => {
      stopScanner();
    });

    // Expose methods to parent component
    return {
      currentCamera,
      cameraActive,
      errorMessage,
      loading,
      qrScanner,
      startScanner,
      stopScanner,
      switchCamera,
      getCameraStatus
    };
  }
};
</script>

<style scoped>
.qr-scanner-component {
  width: 100%;
}

.camera-controls {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.scanner-container {
  position: relative;
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
  border-radius: 12px;
  overflow: hidden;
  background: #000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.qr-scanner {
  width: 100%;
  height: 400px;
}

.scanner-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.scan-frame {
  width: 250px;
  height: 250px;
  border: 3px solid #fff;
  border-radius: 12px;
  box-shadow: 0 0 0 4000px rgba(0, 0, 0, 0.3);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { border-color: #fff; }
  50% { border-color: #007bff; }
  100% { border-color: #fff; }
}

.scan-instruction {
  color: white;
  margin-top: 20px;
  font-size: 16px;
  text-align: center;
  font-weight: 500;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
}

.loading-text {
  text-align: center;
  color: #666;
  font-style: italic;
  margin-top: 10px;
}

/* Responsive Design */
@media (max-width: 768px) {
  .scanner-container {
    height: 300px;
  }
  
  .scan-frame {
    width: 200px;
    height: 200px;
  }
  
  .scan-instruction {
    font-size: 14px;
    margin-top: 15px;
  }
}

@media (max-width: 480px) {
  .scanner-container {
    height: 250px;
  }
  
  .scan-frame {
    width: 180px;
    height: 180px;
  }
  
  .camera-controls {
    flex-direction: column;
    align-items: center;
  }
}
</style>