// Utility to extract csrf_token from cookies
const getCSRFToken = () => {
  const cookies = document.cookie.split('; ');
  const token = cookies.find(row => row.startsWith('csrf_token='));
  return token ? decodeURIComponent(token.split('=')[1]) : '';
}

// Base API caller with standardized response format
const makeApiCall = async (endpoint, payload = {}) => {
  try {
    const csrfToken = getCSRFToken();

    const response = await fetch(`/api/method/${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Frappe-CSRF-Token': csrfToken
      },
      credentials: 'include',
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (!response.ok) {
      const errorMessage = data.message || data.exc || 'API request failed';
      console.error(`API Error (${endpoint}):`, errorMessage);
      return {
        success: false,
        error: errorMessage,
        message: errorMessage,
        exc: data.exc,
        data: null
      };
    }

    return {
      success: true,
      data: data.message || data,
      message: data.message || 'Operation completed successfully',
      error: null
    };
  } catch (error) {
    console.error(`Error in API call to ${endpoint}:`, error);
    return {
      success: false,
      error: error.message,
      message: error.message || 'API request failed',
      data: null
    };
  }
}

// School-specific API functions with consistent response handling
export const registerCreateSite = async (params) => 
  await makeApiCall("school.al_ummah.api3.register_and_create_site", params);

export const setWebsiteInfo = async (params) => 
  await makeApiCall("school.al_ummah.api3.set_institution_details", params);

export const setInstructorToken = async (params) => 
  await makeApiCall("school.al_ummah.api3.set_instructor_token", params);

export const setEmailAcc = async (params) => 
  await makeApiCall("school.al_ummah.api3.create_email_account", params);

export const enrollTeachers = async (params) => 
  await makeApiCall("school.al_ummah.api3.bulk_enroll_instructors", params);

export const enrollTeacher = async (params) => 
  await makeApiCall("school.al_ummah.api3.enroll_single_instructor", params);

export const enrollStudents = async (params) => 
  await makeApiCall("school.al_ummah.api3.bulk_enroll_students", params);

export const getStudents = async (params) => 
  await makeApiCall("education.education.doctype.student_group.student_group.get_students", params);

export const enrollStudent = async (params) => 
  await makeApiCall("school.al_ummah.api3.enroll_single_student", params);

export const getClasses = async (params) => 
  await makeApiCall("school.al_ummah.api3.get_classes", params);

export const getDivisions1 = async (params) => 
  await makeApiCall("school.al_ummah.api3.get_divisions1", params);

export const getDivisions2 = async (params) => 
  await makeApiCall("school.al_ummah.api3.get_divisions2", params);

export const getAcademicYears = async (params) => 
  await makeApiCall("school.al_ummah.api3.get_academic_years", params);

export const previousData = async (params) => 
  await makeApiCall("school.al_ummah.api3.get_previous_data", params);

export const quickSetup = async (params) => 
  await makeApiCall("school.al_ummah.api3.quick_setup", params);

export const fetchAttendanceRecords = async (params) => 
  await makeApiCall("school.al_ummah.api2.get_student_attendance_records", params);

export const fetchNoticeRecords = async (params) => 
  await makeApiCall("school.al_ummah.api2.get_notice_list", params);

export const getLeaveApplications = async (params) => 
  await makeApiCall("school.al_ummah.api2.get_leave_application_list", params);

export const fetchStudentRecord = async (params) => 
  await makeApiCall("school.al_ummah.api2.get_student_app_data", params);

export default makeApiCall;