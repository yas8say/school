<template>
  <div class="card">
    <div class="field">
      <label>Email Address</label>
      <input 
        type="email" 
        v-model="email" 
        placeholder="Enter your email address"
        @input="updateField('email', $event.target.value)"
      />
    </div>

    <div class="field">
      <label>Google App Password</label>
      <input 
        type="password" 
        v-model="googleAppPassword" 
        placeholder="Enter your Google app password"
        @input="updateField('googleAppPassword', $event.target.value)"
      />
    </div>

    <button @click="$emit('submit-email')">Submit Email Account</button>
  </div>
</template>

<script>
export default {
  props: {
    values: Object
  },
  computed: {
    email: {
      get() {
        return this.values.email;
      },
      set(value) {
        this.$emit('update-field', { field: 'email', value });
      }
    },
    googleAppPassword: {
      get() {
        return this.values.googleAppPassword;
      },
      set(value) {
        this.$emit('update-field', { field: 'googleAppPassword', value });
      }
    }
  },
  methods: {
    updateField(field, value) {
      this.$emit('update-field', { field, value });
    }
  }
};
</script>

<style scoped>
/* Similar styles to InstitutionDetails */
.card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.field {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
}

input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  padding: 10px 15px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #45a049;
}
</style>