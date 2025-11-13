<template>
  <div class="enrollment-container">
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

    <div class="scroll-view-content">
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
                  ref="searchInputRef"
                  v-model="searchQuery"
                  type="text"
                  class="input"
                  placeholder="Enter Student ID or GR Number"
                  @keyup.enter="searchStudent"
                >
              </div>
              <button 
                @click="searchStudent" 
                class="primary-button"
                :disabled="!searchQuery"
              >
                Search
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Enhanced Student Info & Invoices -->
      <div v-if="scannedStudentId" class="form-card">
        <!-- Student Profile Header -->
        <div class="student-profile-header">
          <StudentAvatar 
            :imageUrl="studentInfo.image"
            :studentName="studentInfo.student_name"
            class="student-avatar-large"
          />
          <div class="student-main-info">
            <h2 class="student-name">{{ studentInfo.student_name || scannedStudentId }}</h2>
            <div class="student-meta">
              <span class="student-id">ID: {{ scannedStudentId }}</span>
              <span v-if="studentInfo.name" class="student-name-id">System ID: {{ studentInfo.name }}</span>
            </div>
            
            <!-- Contact Info -->
            <div v-if="studentInfo.student_email_id || studentInfo.student_mobile_number" class="contact-info">
              <div v-if="studentInfo.student_email_id" class="contact-item">
                <span class="contact-label">Email:</span>
                <span class="contact-value">{{ studentInfo.student_email_id }}</span>
              </div>
              <div v-if="studentInfo.student_mobile_number" class="contact-item">
                <span class="contact-label">Mobile:</span>
                <span class="contact-value">{{ studentInfo.student_mobile_number }}</span>
              </div>
            </div>
          </div>
          <button @click="resetScanner" class="secondary-button">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
            Scan Another
          </button>
        </div>

        <!-- Guardian Information -->
        <div v-if="studentInfo.guardians && studentInfo.guardians.length > 0" class="guardians-section">
          <h3 class="section-title">Guardian Information</h3>
          <div class="guardians-grid">
            <div 
              v-for="guardian in studentInfo.guardians" 
              :key="guardian.name"
              class="guardian-card"
            >
              <div class="guardian-name">{{ guardian.guardian_name }}</div>
              <div class="guardian-relation">{{ guardian.relation }}</div>
              <div v-if="guardian.mobile_number" class="guardian-contact">
                <span class="contact-icon">📱</span>
                {{ guardian.mobile_number }}
              </div>
              <div v-if="guardian.email_address" class="guardian-contact">
                <span class="contact-icon">✉️</span>
                {{ guardian.email_address }}
              </div>
            </div>
          </div>
        </div>

        <!-- Student Groups -->
        <div v-if="studentInfo.student_groups && studentInfo.student_groups.length > 0" class="student-groups-section">
          <h3 class="section-title">Student Groups</h3>
          <div class="groups-list">
            <span 
              v-for="group in studentInfo.student_groups" 
              :key="group.student_group"
              class="group-tag"
            >
              {{ group.student_group }}
              <span v-if="group.group_roll_number" class="group-roll">(Roll: {{ group.group_roll_number }})</span>
            </span>
          </div>
        </div>

        <!-- No Invoices -->
        <div v-if="invoicesResource && invoicesResource.data && invoicesResource.data.count === 0" class="empty-state">
          <div class="success-icon">✅</div>
          <h3>No Unpaid Invoices</h3>
          <p>All invoices are paid for this student</p>
        </div>

        <!-- Invoices List -->
        <div v-if="invoicesResource && invoicesResource.data && unpaidInvoicesCount > 0" class="invoices-section">
          <div class="section-header">
            <h3 class="section-title">Unpaid Invoices ({{ unpaidInvoicesCount }})</h3>
            <div class="selection-controls">
              <button @click="selectAllUnpaidInvoices" class="text-button">
                Select All
              </button>
              <button @click="deselectAllInvoices" class="text-button">
                Clear
              </button>
            </div>
          </div>

          <div class="invoices-grid">
            <div 
              v-for="invoice in unpaidInvoices" 
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
                    <p class="invoice-date">{{ formatDate(invoice.posting_date) }}</p>
                  </div>
                  <div class="invoice-amounts">
                    <div class="invoice-total">₹{{ invoice.grand_total }}</div>
                    <div class="outstanding-amount">Due: ₹{{ invoice.outstanding_amount }}</div>
                  </div>
                </div>
                
              <!-- Invoice Items -->
              <div v-if="invoice.items && invoice.items.length > 0" class="invoice-items">
                <div class="items-header">
                  <span>Items</span>
                  <span class="items-count">{{ invoice.items.length }} item(s)</span>
                </div>
                <div class="items-list">
                  <div 
                    v-for="item in invoice.items" 
                    :key="item.name || item.item_code" 
                    class="item-row"
                  >
                    <div class="item-info">
                      <div class="item-name">{{ item.item_name || item.item_code }}</div>
                      <div v-if="item.description" class="item-description">{{ item.description }}</div>
                      <div class="item-details">
                        <span v-if="item.qty" class="item-qty">Qty: {{ item.qty }}</span>
                        <span v-if="item.rate" class="item-rate">Rate: ₹{{ item.rate }}</span>
                      </div>
                    </div>
                    <div class="item-pricing">
                      <div class="item-amount">₹{{ item.amount || 0 }}</div>
                    </div>
                  </div>
                </div>
              </div>

                <div class="invoice-details">
                  <div class="detail-row">
                    <span class="detail-label">Due Date:</span>
                    <span class="due-date">{{ formatDate(invoice.due_date) }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">Status:</span>
                    <span :class="['status-badge', invoice.status.toLowerCase()]">
                      {{ invoice.status }}
                    </span>
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
            class="picker"
            :disabled="accountsResource && accountsResource.loading"
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
        <div class="form-section">
          <h3 class="section-title">Payment Method</h3>
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
        <div class="form-actions">
          <button 
            v-if="selectedPaymentMethod === 'razorpay'"
            @click="initiateRazorpayPayment" 
            class="success-button"
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
            class="success-button"
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
    <Toast ref="toastRef" />
  </div>
</template>

<script>
import { createResource } from 'frappe-ui';
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';
import QRScanner from '@/components/QRScanner.vue';
import StudentAvatar from '@/components/StudentAvatar.vue';
import '@/styles/form.css';
import Toast from '@/components/Toast.vue';

export default {
  name: 'QRPaymentPage',
  components: {
    QRScanner,
    StudentAvatar,
    Toast
  },
  
  setup() {
    // Initialize all reactive variables first
    const scannedStudentId = ref('');
    const searchQuery = ref('');
    const selectedInvoices = ref([]);
    const errorMessage = ref('');
    const loading = ref(false);
    const processingPayment = ref(false);
    const qrScannerRef = ref(null);
    const searchInputRef = ref(null);
    const selectedPaymentMethod = ref('cash');
    const razorpayLoaded = ref(false);
    const razorpayInstance = ref(null);
    const razorpaySettingsConfigured = ref(false);
    const studentInfo = ref({});
    const toastRef = ref(null);
    const lastErrorShown = ref('');


    // Payment form data
    const paymentData = ref({
      paid_to_account: '',
      paid_amount: '',
      cheque_no: '',
      cheque_date: ''
    });

    // Define computed properties first
    const unpaidInvoices = computed(() => {
      if (!invoicesResource?.data?.invoices) return [];
      return invoicesResource.data.invoices.filter(invoice => 
        invoice.outstanding_amount > 0 && invoice.status.toLowerCase() !== 'paid'
      );
    });

    const unpaidInvoicesCount = computed(() => {
      return unpaidInvoices.value.length;
    });

    const totalSelectedAmount = computed(() => {
      if (!invoicesResource?.data?.invoices) return 0;
      
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
      if (accountsResource?.data?.accounts) {
        return accountsResource.data.accounts;
      }
      return [];
    });

    const getStudentMobileNumber = computed(() => {
      if (studentInfo.value.student_mobile_number) {
        return studentInfo.value.student_mobile_number;
      }
      if (studentInfo.value.guardians && studentInfo.value.guardians.length > 0) {
        const guardianWithMobile = studentInfo.value.guardians.find(g => g.mobile_number);
        return guardianWithMobile ? guardianWithMobile.mobile_number : null;
      }
      return null;
    });

    // Define API resources after computed properties
    const invoicesResource = createResource({
      url: 'school.al_ummah.api4.get_sales_invoices_by_student',
      params: { student_id: scannedStudentId },
      onSuccess: (data) => {
        loading.value = false;
        studentInfo.value = data.student_data || {};
        
        // Check for paid invoices and show toast messages
        if (data.invoices && data.invoices.length) {
          data.invoices.forEach(invoice => {
            if (invoice.outstanding_amount <= 0 || invoice.status.toLowerCase() === 'paid') {
              showToast(`Invoice ${invoice.name} is already paid`, 'info', 5000);
            }
          });
        }
      },
      onError: (err) => {
        loading.value = false;
        showError(err.messages?.[0] || 'Failed to fetch invoices');
      }
    });

    const accountsResource = createResource({
      url: 'school.al_ummah.api4.get_all_paid_to_accounts',
      auto: true,
      onSuccess: (data) => {
        console.log('Accounts loaded:', data);
        // Auto-select cash account if available
        if (data.accounts && data.accounts.length && selectedPaymentMethod.value === 'cash') {
          const cashAccount = data.accounts.find(account => 
            account.account_name && account.account_name.toLowerCase().includes('cash')
          );
          if (cashAccount) {
            paymentData.value.paid_to_account = cashAccount.name;
          }
        }
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
        // Refresh invoices to remove paid ones from UI
        if (invoicesResource && invoicesResource.reload) {
          invoicesResource.reload();
        }
      },
      onError: (err) => {
        processingPayment.value = false;
        showError(err.messages?.[0] || 'Payment processing failed');
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
          showError(data.message || 'Failed to create payment order');
        }
      },
      onError: (err) => {
        processingPayment.value = false;
        showError(err.messages?.[0] || 'Failed to create payment order');
      }
    });

    const verifyPaymentResource = createResource({
      url: 'school.al_ummah.api4.verify_razorpay_payment',
      method: 'POST',
      onSuccess: (data) => {
        processingPayment.value = false;
        if (data.success) {
          showSuccessMessage(data);
          // Refresh invoices to remove paid ones from UI
          if (invoicesResource && invoicesResource.reload) {
            invoicesResource.reload();
          }
        } else {
          showError(data.message || 'Payment verification failed');
        }
      },
      onError: (err) => {
        processingPayment.value = false;
        showError(err.messages?.[0] || 'Payment verification failed');
      }
    });

    // Define functions after resources
    function showToast(message, type = 'success', duration = 6000, actions = []) {
      if (toastRef.value && toastRef.value.showToast) {
        toastRef.value.showToast(message, type, duration, actions);
      } else {
        // Fallback for toast errors
        if (type === 'error') {
          errorMessage.value = message;
        }
      }
    }

    function showError(message) {
      // Prevent showing the same error multiple times in quick succession
      if (lastErrorShown.value === message) return;
      
      lastErrorShown.value = message;
      showToast(message, 'error', 6000);
      
      // Clear after a short time to allow the same error to show again if genuinely repeated
      setTimeout(() => {
        lastErrorShown.value = '';
      }, 1000);
    }

    function showSuccessMessage(data) {
      const message = `Payment processed successfully!\nPayment Entry: ${data.payment_entry}\nAmount: ₹${data.amount || data.total_amount}\nInvoices Processed: ${data.invoices_processed ? data.invoices_processed.length : data.processed_invoices.length}`;
      
      showToast(
        message,
        'success',
        10000,
        data.pdf_download_url ? [
          {
            label: '📄 Download Receipt (Landscape)',
            url: data.pdf_download_url,
            target: '_blank',
            type: 'primary',
            closeOnClick: false
          }
        ] : []
      );
    }

    function formatDate(dateString) {
      if (!dateString) return 'N/A';
      try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-IN', {
          day: '2-digit',
          month: 'short',
          year: 'numeric'
        });
      } catch (error) {
        return 'Invalid Date';
      }
    }

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
        showError('Please select Account Paid To');
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
        showError('Razorpay payment gateway not loaded. Please refresh the page.');
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
          contact: getStudentMobileNumber.value || '',
          email: studentInfo.value.student_email_id || ''
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
        showError('Failed to open payment gateway. Please try again.');
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

    function extractStudentId(input) {
      if (!input) return '';
      const studentIdMatch = input.match(/^(EDU-STU-\d{4}-\d+)/);
      if (studentIdMatch) return studentIdMatch[1];
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
        showError('Invalid QR code format');
      }
    }

    function onScannerError(error) {
      console.error('Scanner error:', error);
      showError(`Scanner error: ${error}`);
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

    function selectAllUnpaidInvoices() {
      if (unpaidInvoices.value.length > 0) {
        selectedInvoices.value = unpaidInvoices.value.map(inv => inv.name);
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
      
      // Focus on search input after reset
      nextTick(() => {
        if (searchInputRef.value) {
          searchInputRef.value.focus();
        }
        if (qrScannerRef.value) {
          setTimeout(() => {
            qrScannerRef.value.startScanner();
          }, 500);
        }
      });
    }

    function getTodayDate() {
      return new Date().toISOString().split('T')[0];
    }

    // Set up watchers after all functions are defined
    watch(selectedPaymentMethod, (newMethod) => {
      if (newMethod === 'cash' && accountsList.value.length > 0) {
        const cashAccount = accountsList.value.find(account => 
          account.account_name && account.account_name.toLowerCase().includes('cash')
        );
        if (cashAccount) {
          paymentData.value.paid_to_account = cashAccount.name;
        }
      }
    });

    watch(accountsList, (newAccounts) => {
      if (newAccounts.length > 0 && selectedPaymentMethod.value === 'cash') {
        const cashAccount = newAccounts.find(account => 
          account.account_name && account.account_name.toLowerCase().includes('cash')
        );
        if (cashAccount) {
          paymentData.value.paid_to_account = cashAccount.name;
        }
      }
    });

    watch(selectedInvoices, (newVal) => {
      if (newVal.length > 0) {
        paymentData.value.paid_amount = totalSelectedAmount.value;
      } else {
        paymentData.value.paid_amount = '';
      }
    }, { deep: true });

    // Auto-focus on search input when page loads
    onMounted(() => {
      nextTick(() => {
        if (searchInputRef.value) {
          searchInputRef.value.focus();
        }
      });
    });

    return {
      scannedStudentId,
      searchQuery,
      selectedInvoices,
      errorMessage,
      loading,
      processingPayment,
      paymentData,
      qrScannerRef,
      searchInputRef,
      selectedPaymentMethod,
      razorpaySettingsConfigured,
      studentInfo,
      invoicesResource,
      accountsResource,
      processPaymentResource,
      razorpayOrderResource,
      verifyPaymentResource,
      razorpaySettingsResource,
      totalSelectedAmount,
      isManualPaymentValid,
      accountsList,
      toastRef,
      unpaidInvoices,
      unpaidInvoicesCount,
      onQRCodeScanned,
      onScannerError,
      searchStudent,
      toggleInvoiceSelection,
      selectAllUnpaidInvoices,
      deselectAllInvoices,
      resetScanner,
      processManualPayment,
      initiateRazorpayPayment,
      getTodayDate,
      formatDate
    };
  }
};
</script>

<style scoped>
/* Your existing CSS styles remain the same */
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

.input-with-icon .input {
  width: 100%;
  padding-left: 2.5rem !important;
  padding-right: 0.75rem;
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background: white;
}

.input-with-icon .input:focus {
  outline: none;
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  width: 1.25rem;
  height: 1.25rem;
  color: #9ca3af;
  pointer-events: none;
  z-index: 10;
}

.student-profile-header {
  display: flex;
  align-items: flex-start;
  gap: 1.5rem;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.student-avatar-large {
  flex-shrink: 0;
}

.student-main-info {
  flex: 1;
}

.student-name {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.75rem 0;
}

.student-meta {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.student-id,
.student-name-id {
  font-size: 0.875rem;
  color: #6b7280;
  background: #f3f4f6;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.student-name-id {
  background: #faf5ff;
  color: #7c3aed;
  border: 1px solid #ddd6fe;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.contact-label {
  font-weight: 500;
  color: #374151;
}

.contact-value {
  color: #6b7280;
}

.guardians-section {
  margin-bottom: 1.5rem;
}

.guardians-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.guardian-card {
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.guardian-name {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.guardian-relation {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.75rem;
  font-style: italic;
}

.guardian-contact {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #374151;
  margin-bottom: 0.25rem;
}

.contact-icon {
  font-size: 1rem;
}

.student-groups-section {
  margin-bottom: 1.5rem;
}

.groups-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.group-tag {
  background: #e0f2fe;
  color: #0369a1;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  font-size: 0.875rem;
  border: 1px solid #bae6fd;
}

.group-roll {
  color: #0c4a6e;
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
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

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
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

.invoice-date {
  font-size: 0.75rem;
  color: #6b7280;
  margin: 0.25rem 0 0 0;
}

.invoice-amounts {
  text-align: right;
}

.invoice-total {
  font-size: 1.125rem;
  font-weight: 700;
  color: #dc2626;
  margin-bottom: 0.25rem;
}

.outstanding-amount {
  font-size: 0.875rem;
  color: #ef4444;
  font-weight: 600;
}

.invoice-items {
  margin: 1rem 0;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.items-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
}

.items-count {
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: normal;
}

.items-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.item-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: white;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-name {
  font-weight: 500;
  color: #1f2937;
  font-size: 0.875rem;
  line-height: 1.4;
}

.item-pricing {
  text-align: right;
  flex-shrink: 0;
  margin-left: 1rem;
}

.item-amount {
  font-weight: 600;
  color: #dc2626;
  font-size: 0.875rem;
  line-height: 1.4;
}

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

.cheque-fields {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
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

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.paid {
  background: #f0fdf4;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.status-badge.unpaid {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.status-badge.draft {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

@media (max-width: 768px) {
  .student-profile-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .guardians-grid {
    grid-template-columns: 1fr;
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

  .invoices-grid {
    gap: 0.5rem;
  }

  .invoice-card {
    padding: 0.75rem;
  }
}
</style>