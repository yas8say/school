<template>
  <div class="container">
    <form class="login-form" @submit.prevent="submit">
      <div class="form-group">
        <label for="username">Username</label>
        <input
          id="username"
          type="text"
          v-model="username"
          placeholder="Enter username"
          required
        />
      </div>
      <div class="form-group">
        <label for="password">Password</label>
        <input
          id="password"
          type="password"
          v-model="password"
          placeholder="Enter password"
          required
        />
      </div>
      <button type="submit" :disabled="loading">
        {{ loading ? 'Logging in...' : 'Sign in' }}
      </button>
    </form>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import { FrappeApp } from 'frappe-js-sdk';

// Initialize Frappe
const frappe = new FrappeApp('https://alummah.awami.in');
const auth = frappe.auth();
const call = frappe.call();

const username = ref('');
const password = ref('');
const loading = ref(false);

// Log localStorage data
const logLocalStorageData = async (key) => {
  try {
    const data = localStorage.getItem(key);
    if (data !== null) {
      console.log(`Data for key "${key}":`, JSON.parse(data));
    } else {
      console.log(`No data found for key "${key}"`);
    }
  } catch (error) {
    console.error('Error retrieving data from localStorage:', error);
  }
};

const submit = async () => {
  if (!username.value || !password.value) {
    alert('Please fill out all fields');
    return;
  }

  loading.value = true;
  try {
    // Clear existing localStorage data
    localStorage.removeItem('user_details');

    // Login with Frappe
    console.log('Attempting login with username:', username.value);
    await auth.loginWithUsernamePassword({ username: username.value, password: password.value });
    console.log('Login successful');

    // Get logged-in user
    const loggedInUser = await auth.getLoggedInUser();
    console.log('Logged-in user:', loggedInUser);

    // Fetch user details
    const userDetailsResponse = await call.get('school.al_ummah.api2.get_user_details', {
      username: loggedInUser,
    });
    console.log('User details response:', userDetailsResponse);

    // Check if response is valid
    if (!userDetailsResponse || !userDetailsResponse.message || !userDetailsResponse.message.user_details) {
      throw new Error('Invalid user details response from API');
    }

    const userDetails = userDetailsResponse.message.user_details;

    // Save user details to localStorage
    await localStorage.setItem('user_details', JSON.stringify(userDetails));
    console.log('User details saved to localStorage');
    await logLocalStorageData('user_details');

    alert('Login successful!');
  } catch (error) {
    console.error('Login failed:', error);
    if (error.message.includes('ERR_CONNECTION_REFUSED') || error.message.includes('Network Error')) {
      alert('Cannot connect to the server. Please check if https://alummah.awami.in is accessible.');
    } else {
      alert(`Login failed: ${error.message || 'Invalid username or password'}`);
    }
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.container {
  max-width: 400px;
  margin: 20px auto;
  padding: 20px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

label {
  font-size: 14px;
  margin-bottom: 5px;
}

input {
  padding: 8px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

button {
  padding: 10px;
  font-size: 16px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}
</style>