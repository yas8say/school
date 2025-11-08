<template>
  <div class="qr-payment-container">
    <div class="header">
      <h1 class="title">Student Payment</h1>
      <p class="subtitle">Scan QR code or search student to pay invoices</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-modal">
        <div class="loading-spinner"></div>
        <h3 class="loading-title">Processing...</h3>
      </div>
    </div>

    <!-- Student Search Section -->
    <div class="form-card" v-if="!scannedStudentId">
      <h2 class="form-title">Find Student</h2>
      
      <div class="search-section">
        <!-- QR Scanner -->
        <div class="qr-section">
          <QRScanner 
            @qr-scanned="onQRCodeScanned"
            @error="onScannerError"
            ref="qrScannerRef"
          />
        </div>

        <!-- Divider -->
        <div class="divider">
          <span>OR</span>
        </div>

        <!-- Manual Search -->
        <div class="search-input-section">
          <div class="search-input-group">
            <div class="input-with-icon">
              <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                v-model="searchQuery"
                type="text"
                class="search-input"
                placeholder="Enter Student ID or GR Number"
                @keyup.enter="searchStudent"
              >
            </div>
            <button 
              @click="searchStudent" 
              class="search-button"
              :disabled="!searchQuery"
            >
              Search
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Student Info & Invoices -->
    <div v-if="scannedStudentId" class="form-card">
      <div class="student-header">
        <div class="student-info">
          <h2 class="student-name">{{ studentInfo.student_name || scannedStudentId }}</h2>
          <div class="student-meta">
            <span class="student-id">ID: {{ scannedStudentId }}</span>
            <span v-if="studentInfo.name" class="gr-number">GR: {{ studentInfo.name }}</span>
          </div>
        </div>
        <button @click="resetScanner" class="icon-button">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
          Scan Another
        </button>
      </div>

      <!-- Error Message -->
      <div v-if="errorMessage" class="message error">
        {{ errorMessage }}
      </div>

      <!-- No Invoices -->
      <div v-if="invoicesResource.data && invoicesResource.data.count === 0" class="empty-state">
        <div class="empty-icon">✅</div>
        <h3>No Unpaid Invoices</h3>
        <p>All invoices are paid for this student</p>
      </div>

      <!-- Invoices List -->
      <div v-if="invoicesResource.data && invoicesResource.data.count > 0" class="invoices-section">
        <div class="section-header">
          <h3>Unpaid Invoices ({{ invoicesResource.data.count }})</h3>
          <div class="selection-controls">
            <button @click="selectAllInvoices" class="text-button">
              Select All
            </button>
            <button @click="deselectAllInvoices" class="text-button">
              Clear
            </button>
          </div>
        </div>

        <div class="invoices-grid">
          <div 
            v-for="invoice in invoicesResource.data.invoices" 
            :key="invoice.name"
            :class="['invoice-card', { selected: selectedInvoices.includes(invoice.name) }]"
            @click="toggleInvoiceSelection(invoice.name)"
          >
            <div class="invoice-checkbox">
              <input
                type="checkbox"
                :checked="selectedInvoices.includes(invoice.name)"
                @change="toggleInvoiceSelection(invoice.name)"
                @click.stop
              >
            </div>
            
            <div class="invoice-content">
              <div class="invoice-header">
                <div class="invoice-info">
                  <h4 class="invoice-title">{{ invoice.name }}</h4>
                  <p class="invoice-customer">{{ invoice.customer_name }}</p>
                </div>
                <div class="invoice-amount">₹{{ invoice.grand_total }}</div>
              </div>
              
              <div class="invoice-details">
                <div class="detail-row">
                  <span class="detail-label">Due:</span>
                  <span class="due-date">{{ getMonthName(invoice.due_date) }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Outstanding:</span>
                  <span class="outstanding-amount">₹{{ invoice.outstanding_amount }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Payment Section -->
    <div v-if="selectedInvoices.length > 0" class="form-card payment-section">
      <h2 class="form-title">Payment</h2>
      
      <div class="payment-summary">
        <div class="summary-item">
          <span>Selected Invoices:</span>
          <strong>{{ selectedInvoices.length }}</strong>
        </div>
        <div class="summary-item total">
          <span>Total Amount:</span>
          <strong>₹{{ totalSelectedAmount }}</strong>
        </div>
      </div>

      <!-- Account Selection -->
      <div class="form-group">
        <label>Account Paid To</label>
        <select 
          v-model="paymentData.paid_to_account" 
          class="select-input"
          :disabled="accountsResource.loading"
        >
          <option value="">Select Account</option>
          <option 
            v-for="account in accountsList" 
            :key="account.name" 
            :value="account.name"
          >
            {{ account.account_name }}
          </option>
        </select>
      </div>

      <!-- Payment Method -->
      <div class="payment-methods">
        <div class="payment-method-option">
          <input
            type="radio"
            id="cash"
            v-model="selectedPaymentMethod"
            value="cash"
            class="payment-radio"
          >
          <label for="cash" class="payment-label">
            <div class="payment-icon">💵</div>
            <span>Cash</span>
          </label>
        </div>
        
        <div class="payment-method-option">
          <input
            type="radio"
            id="cheque"
            v-model="selectedPaymentMethod"
            value="cheque"
            class="payment-radio"
          >
          <label for="cheque" class="payment-label">
            <div class="payment-icon">🏦</div>
            <span>Cheque</span>
          </label>
        </div>
        
        <div class="payment-method-option" v-if="razorpaySettingsConfigured">
          <input
            type="radio"
            id="razorpay"
            v-model="selectedPaymentMethod"
            value="razorpay"
            class="payment-radio"
          >
          <label for="razorpay" class="payment-label">
            <div class="payment-icon">💳</div>
            <span>Online</span>
          </label>
        </div>
      </div>

      <!-- Cheque Fields -->
      <div v-if="selectedPaymentMethod === 'cheque'" class="cheque-fields">
        <div class="form-group">
          <label>Cheque Number</label>
          <input
            v-model="paymentData.cheque_no"
            type="text"
            class="input"
            placeholder="Enter cheque number"
          >
        </div>
        <div class="form-group">
          <label>Cheque Date</label>
          <input
            v-model="paymentData.cheque_date"
            type="date"
            class="input"
            :max="getTodayDate()"
          >
        </div>
      </div>

      <!-- Payment Action -->
      <div class="payment-action">
        <button 
          v-if="selectedPaymentMethod === 'razorpay'"
          @click="initiateRazorpayPayment" 
          class="pay-button online"
          :disabled="processingPayment || !paymentData.paid_to_account"
        >
          <span v-if="processingPayment" class="button-content">
            <span class="spinner"></span> Processing...
          </span>
          <span v-else class="button-content">
            Pay ₹{{ totalSelectedAmount }} Online
          </span>
        </button>

        <button 
          v-else
          @click="processManualPayment" 
          class="pay-button"
          :disabled="!isManualPaymentValid || processingPayment"
        >
          <span v-if="processingPayment" class="button-content">
            <span class="spinner"></span> Processing...
          </span>
          <span v-else class="button-content">
            Confirm Payment
          </span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { createResource } from 'frappe-ui';
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import QRScanner from '@/components/QRScanner.vue';

export default {
  name: 'QRPaymentPage',
  components: {
    QRScanner
  },
  
  setup() {
    // Reactive state
    const scannedStudentId = ref('');
    const searchQuery = ref('');
    const selectedInvoices = ref([]);
    const errorMessage = ref('');
    const loading = ref(false);
    const processingPayment = ref(false);
    const qrScannerRef = ref(null);
    const selectedPaymentMethod = ref('cash');
    const razorpayLoaded = ref(false);
    const razorpayInstance = ref(null);
    const razorpaySettingsConfigured = ref(false);
    const studentInfo = ref({});
    
    // Payment form data
    const paymentData = ref({
      paid_to_account: '',
      paid_amount: '',
      cheque_no: '',
      cheque_date: ''
    });

    // API Resources
    const invoicesResource = createResource({
      url: 'school.al_ummah.api4.get_sales_invoices_by_student',
      params: { student_id: scannedStudentId },
      onSuccess: (data) => {
        loading.value = false;
        studentInfo.value = data.student_info || {};
        console.log('Invoices loaded:', data);
      },
      onError: (err) => {
        loading.value = false;
        errorMessage.value = err.messages?.[0] || 'Failed to fetch invoices';
        console.error('Error fetching invoices:', err);
      }
    });

    const accountsResource = createResource({
      url: 'school.al_ummah.api4.get_all_paid_to_accounts',
      auto: true,
      onSuccess: (data) => {
        console.log('Accounts loaded:', data);
      },
      onError: (err) => {
        console.error('Error fetching accounts:', err);
      }
    });

    const processPaymentResource = createResource({
      url: 'school.al_ummah.api4.process_student_payment',
      method: 'POST',
      onSuccess: (data) => {
        processingPayment.value = false;
        console.log('Payment processed:', data);
        showSuccessMessage(data);
      },
      onError: (err) => {
        processingPayment.value = false;
        errorMessage.value = err.messages?.[0] || 'Payment processing failed';
        console.error('Error processing payment:', err);
      }
    });

    const razorpaySettingsResource = createResource({
      url: 'school.al_ummah.api4.get_razorpay_settings_status',
      auto: true,
      onSuccess: (data) => {
        if (data.success && data.configured) {
          razorpaySettingsConfigured.value = true;
          loadRazorpayScript();
        } else {
          razorpaySettingsConfigured.value = false;
        }
      },
      onError: (err) => {
        console.error('Failed to check Razorpay settings:', err);
        razorpaySettingsConfigured.value = false;
      }
    });

    const razorpayOrderResource = createResource({
      url: 'school.al_ummah.api4.create_razorpay_order',
      method: 'POST',
      onSuccess: (data) => {
        if (data.success) {
          openRazorpayCheckout(data);
        } else {
          processingPayment.value = false;
          errorMessage.value = data.message || 'Failed to create payment order';
        }
      },
      onError: (err) => {
        processingPayment.value = false;
        errorMessage.value = err.messages?.[0] || 'Failed to create payment order';
      }
    });

    const verifyPaymentResource = createResource({
      url: 'school.al_ummah.api4.verify_razorpay_payment',
      method: 'POST',
      onSuccess: (data) => {
        processingPayment.value = false;
        if (data.success) {
          showSuccessMessage(data);
        } else {
          errorMessage.value = data.message || 'Payment verification failed';
        }
      },
      onError: (err) => {
        processingPayment.value = false;
        errorMessage.value = err.messages?.[0] || 'Payment verification failed';
      }
    });

    // Computed properties
    const totalSelectedAmount = computed(() => {
      if (!invoicesResource.data?.invoices) return 0;
      
      return invoicesResource.data.invoices
        .filter(invoice => selectedInvoices.value.includes(invoice.name))
        .reduce((total, invoice) => total + parseFloat(invoice.grand_total), 0)
        .toFixed(2);
    });

    const isManualPaymentValid = computed(() => {
      const basicValidation = paymentData.value.paid_to_account;

      if (selectedPaymentMethod.value === 'cheque') {
        return basicValidation && 
               paymentData.value.cheque_no && 
               paymentData.value.cheque_date;
      }

      return basicValidation;
    });

    const accountsList = computed(() => {
      if (accountsResource.data && accountsResource.data.accounts) {
        return accountsResource.data.accounts;
      }
      return [];
    });

    // Watch for selected invoices and auto-set paid amount
    watch(selectedInvoices, (newVal) => {
      if (newVal.length > 0) {
        paymentData.value.paid_amount = totalSelectedAmount.value;
      } else {
        paymentData.value.paid_amount = '';
      }
    }, { deep: true });

    // Methods
    function loadRazorpayScript() {
      if (razorpayLoaded.value) return;

      return new Promise((resolve, reject) => {
        if (window.Razorpay) {
          razorpayLoaded.value = true;
          resolve();
          return;
        }

        const script = document.createElement('script');
        script.src = 'https://checkout.razorpay.com/v1/checkout.js';
        script.async = true;
        script.defer = true;
        
        script.onload = () => {
          razorpayLoaded.value = true;
          resolve();
        };
        
        script.onerror = () => {
          reject(new Error('Failed to load Razorpay payment gateway'));
        };
        
        document.head.appendChild(script);
      });
    }

    function initiateRazorpayPayment() {
      processingPayment.value = true;
      errorMessage.value = '';

      if (!paymentData.value.paid_to_account) {
        processingPayment.value = false;
        errorMessage.value = 'Please select Account Paid To';
        return;
      }

      razorpayOrderResource.submit({
        invoice_names: selectedInvoices.value,
        student_id: scannedStudentId.value,
        total_amount: totalSelectedAmount.value,
        paid_to_account: paymentData.value.paid_to_account
      });
    }

    function openRazorpayCheckout(orderData) {
      if (!window.Razorpay) {
        errorMessage.value = 'Razorpay payment gateway not loaded. Please refresh the page.';
        processingPayment.value = false;
        return;
      }

      const options = {
        key: orderData.key_id,
        amount: orderData.amount,
        currency: orderData.currency,
        name: 'School Al Ummah',
        description: `Payment for ${selectedInvoices.value.length} invoice(s)`,
        order_id: orderData.order_id,
        handler: function (response) {
          verifyRazorpayPayment(response);
        },
        prefill: {
          name: studentInfo.value.student_name || `Student ${scannedStudentId.value}`,
        },
        theme: {
          color: '#10b981'
        }
      };

      try {
        razorpayInstance.value = new window.Razorpay(options);
        razorpayInstance.value.open();
      } catch (error) {
        console.error('Error opening Razorpay checkout:', error);
        processingPayment.value = false;
        errorMessage.value = 'Failed to open payment gateway. Please try again.';
      }
    }

    function verifyRazorpayPayment(razorpayResponse) {
      verifyPaymentResource.submit({
        razorpay_payment_id: razorpayResponse.razorpay_payment_id,
        razorpay_order_id: razorpayResponse.razorpay_order_id,
        razorpay_signature: razorpayResponse.razorpay_signature,
        invoice_names: selectedInvoices.value,
        student_id: scannedStudentId.value,
        paid_to_account: paymentData.value.paid_to_account,
        paid_amount: paymentData.value.paid_amount
      });
    }

    function processManualPayment() {
      if (!isManualPaymentValid.value) return;
      
      processingPayment.value = true;
      errorMessage.value = '';

      processPaymentResource.submit({
        student_id: scannedStudentId.value,
        invoice_names: selectedInvoices.value,
        mode_of_payment: selectedPaymentMethod.value === 'cash' ? 'Cash' : 'Cheque',
        paid_to_account: paymentData.value.paid_to_account,
        paid_amount: parseFloat(paymentData.value.paid_amount),
        cheque_no: paymentData.value.cheque_no,
        cheque_date: paymentData.value.cheque_date
      });
    }

    function showSuccessMessage(data) {
      const message = `
Payment processed successfully!
Payment Entry: ${data.payment_entry}
Amount: ₹${data.amount || data.total_amount}
Invoices: ${data.invoices_processed ? data.invoices_processed.length : data.processed_invoices.length}

${data.pdf_download_url ? 'Click OK to download the receipt.' : ''}
      `;
      
      if (confirm(message) && data.pdf_download_url) {
        // Download the PDF receipt
        window.open(data.pdf_download_url, '_blank');
      }
      
      resetScanner();
    }

    function extractStudentId(input) {
      // Match Student ID format or GR Number
      const studentIdMatch = input.match(/^(EDU-STU-\d{4}-\d+)/);
      if (studentIdMatch) return studentIdMatch[1];
      
      // If it's a GR number, we'll search by it
      return input.trim();
    }

    function onQRCodeScanned(decodedText) {
      console.log('QR Code scanned:', decodedText);
      
      const studentId = extractStudentId(decodedText);
      if (studentId) {
        if (qrScannerRef.value) {
          qrScannerRef.value.stopScanner();
        }
        processStudentId(studentId);
      } else {
        errorMessage.value = 'Invalid QR code format';
      }
    }

    function onScannerError(error) {
      console.error('Scanner error:', error);
      errorMessage.value = `Scanner error: ${error}`;
    }

    function searchStudent() {
      if (searchQuery.value) {
        const studentId = extractStudentId(searchQuery.value);
        processStudentId(studentId);
      }
    }

    function processStudentId(studentId) {
      scannedStudentId.value = studentId;
      loading.value = true;
      errorMessage.value = '';
      selectedInvoices.value = [];
      
      invoicesResource.update({
        params: { student_id: studentId }
      });
      invoicesResource.reload();
    }

    function toggleInvoiceSelection(invoiceName) {
      const index = selectedInvoices.value.indexOf(invoiceName);
      if (index > -1) {
        selectedInvoices.value.splice(index, 1);
      } else {
        selectedInvoices.value.push(invoiceName);
      }
    }

    function selectAllInvoices() {
      if (invoicesResource.data?.invoices) {
        selectedInvoices.value = invoicesResource.data.invoices.map(inv => inv.name);
      }
    }

    function deselectAllInvoices() {
      selectedInvoices.value = [];
    }

    function resetScanner() {
      scannedStudentId.value = '';
      searchQuery.value = '';
      selectedInvoices.value = [];
      errorMessage.value = '';
      studentInfo.value = {};
      paymentData.value = {
        paid_to_account: '',
        paid_amount: '',
        cheque_no: '',
        cheque_date: ''
      };
      selectedPaymentMethod.value = 'cash';
      
      if (qrScannerRef.value) {
        setTimeout(() => {
          qrScannerRef.value.startScanner();
        }, 500);
      }
    }

    function getMonthName(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-IN', { 
        month: 'long',
        year: 'numeric'
      });
    }

    function getTodayDate() {
      return new Date().toISOString().split('T')[0];
    }

    return {
      // State
      scannedStudentId,
      searchQuery,
      selectedInvoices,
      errorMessage,
      loading,
      processingPayment,
      paymentData,
      qrScannerRef,
      selectedPaymentMethod,
      razorpaySettingsConfigured,
      studentInfo,
      
      // Resources
      invoicesResource,
      accountsResource,
      processPaymentResource,
      razorpayOrderResource,
      verifyPaymentResource,
      razorpaySettingsResource,
      
      // Computed
      totalSelectedAmount,
      isManualPaymentValid,
      accountsList,
      
      // Methods
      onQRCodeScanned,
      onScannerError,
      searchStudent,
      toggleInvoiceSelection,
      selectAllInvoices,
      deselectAllInvoices,
      resetScanner,
      processManualPayment,
      initiateRazorpayPayment,
      getMonthName,
      getTodayDate
    };
  }
};
</script>

<style scoped>
.qr-payment-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 1.5rem;
  min-height: 100vh;
}

.header {
  text-align: center;
  margin-bottom: 2rem;
}

.title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #6b7280;
  font-size: 1rem;
}

/* Form Cards */
.form-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
}

.form-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

/* Search Section */
.search-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.qr-section {
  display: flex;
  justify-content: center;
}

.divider {
  display: flex;
  align-items: center;
  text-align: center;
  color: #9ca3af;
  font-size: 0.875rem;
  font-weight: 500;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #e5e7eb;
}

.divider span {
  padding: 0 1rem;
}

.search-input-group {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.input-with-icon {
  position: relative;
  flex: 1;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  width: 1.25rem;
  height: 1.25rem;
  color: #9ca3af;
}

.search-input {
  width: 100%;
  padding: 0.75rem 0.75rem 0.75rem 2.5rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.search-button {
  padding: 0.75rem 1.5rem;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
}

.search-button:hover:not(:disabled) {
  background: #059669;
}

.search-button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

/* Student Header */
.student-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  gap: 1rem;
}

.student-info {
  flex: 1;
}

.student-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.5rem 0;
}

.student-meta {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.student-id,
.gr-number {
  font-size: 0.875rem;
  color: #6b7280;
  background: #f3f4f6;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.icon-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #f8fafc;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  color: #374151;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.icon-button:hover {
  background: #f1f5f9;
}

.icon {
  width: 1rem;
  height: 1rem;
}

/* Messages */
.message {
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.message.error {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  margin: 0 0 0.5rem 0;
  color: #374151;
  font-size: 1.125rem;
}

.empty-state p {
  margin: 0;
  font-size: 0.875rem;
}

/* Section Header */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #374151;
}

.selection-controls {
  display: flex;
  gap: 0.75rem;
}

.text-button {
  background: none;
  border: none;
  color: #10b981;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  transition: background 0.2s;
}

.text-button:hover {
  background: #f0fdf4;
}

/* Invoices Grid */
.invoices-grid {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.invoice-card {
  display: flex;
  align-items: flex-start;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  background: white;
  gap: 0.75rem;
}

.invoice-card:hover {
  border-color: #10b981;
  background: #f0fdf4;
}

.invoice-card.selected {
  border-color: #10b981;
  background: #f0fdf4;
}

.invoice-checkbox {
  margin-top: 0.125rem;
  flex-shrink: 0;
}

.invoice-checkbox input {
  transform: scale(1.1);
}

.invoice-content {
  flex: 1;
  min-width: 0;
}

.invoice-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
  gap: 1rem;
}

.invoice-info {
  flex: 1;
  min-width: 0;
}

.invoice-title {
  margin: 0 0 0.25rem 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: #1f2937;
}

.invoice-customer {
  margin: 0;
  font-size: 0.75rem;
  color: #6b7280;
}

.invoice-amount {
  font-size: 1rem;
  font-weight: 700;
  color: #dc2626;
  white-space: nowrap;
}

.invoice-details {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.detail-label {
  font-size: 0.75rem;
  color: #6b7280;
}

.due-date {
  font-size: 0.75rem;
  font-weight: 500;
  color: #374151;
  background: #f3f4f6;
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
}

.outstanding-amount {
  font-size: 0.75rem;
  font-weight: 600;
  color: #dc2626;
}

/* Payment Section */
.payment-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.summary-item.total {
  text-align: right;
}

.summary-item.total strong {
  font-size: 1.25rem;
  color: #dc2626;
}

/* Form Groups */
.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

.select-input,
.input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.select-input:focus,
.input:focus {
  outline: none;
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

/* Payment Methods */
.payment-methods {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.payment-method-option {
  flex: 1;
  min-width: 80px;
}

.payment-radio {
  display: none;
}

.payment-radio:checked + .payment-label {
  border-color: #10b981;
  background: #f0fdf4;
}

.payment-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 0.5rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
  font-size: 0.875rem;
  font-weight: 500;
}

.payment-label:hover {
  border-color: #10b981;
}

.payment-icon {
  font-size: 1.5rem;
}

/* Cheque Fields */
.cheque-fields {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

/* Payment Action */
.payment-action {
  display: flex;
  justify-content: flex-end;
}

.pay-button {
  padding: 0.75rem 2rem;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  min-width: 140px;
}

.pay-button:hover:not(:disabled) {
  background: #059669;
}

.pay-button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.pay-button.online {
  background: #6366f1;
}

.pay-button.online:hover:not(:disabled) {
  background: #4f46e5;
}

.button-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  justify-content: center;
}

.spinner {
  display: inline-block;
  width: 1rem;
  height: 1rem;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Loading Overlay */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-modal {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  text-align: center;
  min-width: 200px;
}

.loading-spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid #e5e7eb;
  border-top: 3px solid #10b981;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

.loading-title {
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

/* Responsive Design */
@media (max-width: 768px) {
  .qr-payment-container {
    padding: 1rem;
  }

  .form-card {
    padding: 1rem;
  }

  .student-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .search-input-group {
    flex-direction: column;
  }

  .cheque-fields {
    grid-template-columns: 1fr;
  }

  .payment-methods {
    flex-direction: column;
  }

  .payment-method-option {
    min-width: auto;
  }

  .invoice-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .payment-summary {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }

  .summary-item.total {
    text-align: left;
  }
}

@media (max-width: 480px) {
  .title {
    font-size: 1.5rem;
  }

  .form-title {
    font-size: 1.125rem;
  }

  .invoices-grid {
    gap: 0.5rem;
  }

  .invoice-card {
    padding: 0.75rem;
  }
}
</style>