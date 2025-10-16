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
  
  const username = ref('');
  const password = ref('');
  const loading = ref(false);
  
  const submit = async () => {
    if (!username.value || !password.value) {
      alert('Please fill out all fields');
      return;
    }
  
    loading.value = true;
    try {
      // Mock login API call (replacing frappe.auth.loginWithUsernamePassword)
      const loginResponse = await mockLoginApi(username.value, password.value);
  
      // Mock user details API call (replacing call.get for user details)
      const userDetails = await mockUserDetailsApi(loginResponse.username);
  
      // Save user details to localStorage
      await localStorage.setItem('user_details', JSON.stringify(userDetails));
      console.log('User details saved to localStorage:', userDetails);
  
      alert('Login successful!');
    } catch (error) {
      console.error('Login failed:', error);
      alert('Invalid username or password');
    } finally {
      loading.value = false;
    }
  };
  
  // Mock login API (simulating frappe.auth.loginWithUsernamePassword)
  const mockLoginApi = async (username, password) => {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (username && password) {
          resolve({ username });
        } else {
          reject(new Error('Invalid credentials'));
        }
      }, 1000);
    });
  };
  
  // Mock user details API (simulating call.get("school.al_ummah.api2.get_user_details"))
  const mockUserDetailsApi = async (username) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          username,
          full_name: username,
          email: username,
          roles: ['User'], // Generic role
        });
      }, 500);
    });
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