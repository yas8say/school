<template>
  <div class="container">
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
    </div>
    <div v-else-if="students.length > 0" class="student-list">
      <ul>
        <li v-for="student in students" :key="student.student" class="student-item">
          <span>{{ student.student_name }}</span>
          <span>Roll: {{ student.group_roll_number }}</span>
          <input
            type="checkbox"
            :checked="presentStudents.includes(student.student)"
            @change="togglePresent(student.student)"
          >
        </li>
      </ul>
    </div>
    <div v-else class="no-students">
      <p>No students available</p>
    </div>

    <div class="buttons">
      <button class="btn cancel" @click="navigateToTeacherHome">Cancel</button>
      <button class="btn refresh" @click="fetchAndSaveAttendanceData">Refresh</button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { fetchAttendanceRecords } from '../utils/apiUtils';

export default {
  name: 'Attendance',
  setup() {
    const router = useRouter();
    const students = ref([]);
    const presentStudents = ref([]);
    const loading = ref(true);
    const userDetails = ref(null);

    // Load user details from localStorage
    const loadUserDetails = () => {
      try {
        const userDetailsData = localStorage.getItem('user_details');
        if (userDetailsData) {
          userDetails.value = JSON.parse(userDetailsData);
        } else {
          console.log('User details not found in localStorage.');
        }
      } catch (error) {
        console.error('Error loading user details:', error);
      }
    };

    // Load attendance data from localStorage
    const loadAttendanceData = async () => {
      loading.value = true;
      try {
        const attendanceData = localStorage.getItem('attendance_data');
        if (attendanceData) {
          const parsedData = JSON.parse(attendanceData);
          const studentData = parsedData?.attendance || [];

          if (studentData.length > 0) {
            students.value = studentData;
            presentStudents.value = studentData.map(student => student.student);
            console.log('Loaded attendance data from localStorage.');
          } else {
            console.log('Attendance data is empty. Fetching from API...');
            await fetchAndSaveAttendanceData(true);
          }
        } else {
          console.log('Attendance data not found in localStorage. Fetching from API...');
          await fetchAndSaveAttendanceData(true);
        }
      } catch (error) {
        console.error('Error loading attendance data:', error);
        alert('Failed to load attendance data.');
      } finally {
        loading.value = false;
      }
    };

    // Fetch attendance data from API and save to localStorage
    const fetchAndSaveAttendanceData = async (isRetry = false) => {
      try {
        const group = localStorage.getItem('selected_student_group');
        if (!group) {
          alert('Student group information is missing.');
          return;
        }

        const params = {
          based_on: 'Batch',
          student_group: group
        };

        const attendanceRecords = await fetchAttendanceRecords(params);

        if (!attendanceRecords || attendanceRecords.length === 0) {
          console.log('No attendance data found from API.');
          if (isRetry) {
            alert('No attendance records found for the selected class.');
          }
          students.value = [];
          return;
        }

        localStorage.setItem('attendance_data', JSON.stringify({ attendance: attendanceRecords }));
        console.log('Attendance data saved successfully.');

        students.value = attendanceRecords;
        presentStudents.value = attendanceRecords.map(student => student.student);
      } catch (error) {
        console.error('Error fetching and saving attendance data:', error);
        alert('Failed to fetch attendance data.');
      }
    };

    // Toggle student presence
    const togglePresent = (studentId) => {
      if (presentStudents.value.includes(studentId)) {
        presentStudents.value = presentStudents.value.filter(id => id !== studentId);
      } else {
        presentStudents.value = [...presentStudents.value, studentId];
      }
    };

    // Navigation
    const navigateToTeacherHome = () => {
      router.push('/teacher-home');
    };

    // Lifecycle hooks
    onMounted(() => {
      loadUserDetails();
    });

    watch(userDetails, () => {
      if (userDetails.value) {
        loadAttendanceData();
      }
    });

    return {
      students,
      presentStudents,
      loading,
      userDetails,
      fetchAndSaveAttendanceData,
      togglePresent,
      navigateToTeacherHome
    };
  }
};
</script>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
}

.student-list ul {
  list-style: none;
  padding: 0;
}

.student-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #e8e8e8;
}

.student-item span {
  flex: 1;
}

.student-item input {
  margin-left: 10px;
}

.buttons {
  display: flex;
  gap: 10px;
  margin-top: 20px;
  justify-content: center;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.cancel {
  background-color: #ff4d4f;
  color: white;
}

.refresh {
  background-color: #1890ff;
  color: white;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #1890ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.no-students {
  text-align: center;
  padding: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>