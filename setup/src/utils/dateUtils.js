// utils/dateUtils.js

export function parseDate(dateString) {
  if (!dateString) return null;
  
  // If it's already a Date object or timestamp
  if (dateString instanceof Date) return dateString;
  if (!isNaN(dateString)) return new Date(Number(dateString));
  
  // Handle Excel serial date numbers (common in XLSX files)
  if (!isNaN(parseFloat(dateString)) && isFinite(dateString)) {
    const excelEpoch = new Date(1900, 0, 1);
    const excelDate = parseFloat(dateString);
    // Excel incorrectly treats 1900 as a leap year
    const days = excelDate > 60 ? excelDate - 1 : excelDate;
    return new Date(excelEpoch.getTime() + (days - 1) * 24 * 60 * 60 * 1000);
  }
  
  // Try parsing various date formats
  const formats = [
    /^(\d{1,2})[-/](\d{1,2})[-/](\d{4})$/, // dd-mm-yyyy, dd/mm/yyyy
    /^(\d{4})[-/](\d{1,2})[-/](\d{1,2})$/, // yyyy-mm-dd, yyyy/mm/dd
    /^(\d{1,2})[-/](\d{1,2})[-/](\d{2})$/, // dd-mm-yy, dd/mm/yy
  ];
  
  for (const format of formats) {
    const match = dateString.toString().trim().match(format);
    if (match) {
      if (format === formats[0]) { // dd-mm-yyyy or dd/mm/yyyy
        const day = parseInt(match[1], 10);
        const month = parseInt(match[2], 10) - 1;
        const year = parseInt(match[3], 10);
        const date = new Date(year, month, day);
        // Validate the date to handle invalid dates like 31-02-2023
        if (date.getDate() === day && date.getMonth() === month && date.getFullYear() === year) {
          return date;
        }
      } else if (format === formats[1]) { // yyyy-mm-dd or yyyy/mm/dd
        const year = parseInt(match[1], 10);
        const month = parseInt(match[2], 10) - 1;
        const day = parseInt(match[3], 10);
        const date = new Date(year, month, day);
        if (date.getDate() === day && date.getMonth() === month && date.getFullYear() === year) {
          return date;
        }
      } else if (format === formats[2]) { // dd-mm-yy or dd/mm/yy
        const day = parseInt(match[1], 10);
        const month = parseInt(match[2], 10) - 1;
        const year = parseInt(match[3], 10) + 2000; // assuming 2000s
        const date = new Date(year, month, day);
        if (date.getDate() === day && date.getMonth() === month && date.getFullYear() === year) {
          return date;
        }
      }
    }
  }
  
  // Fallback to native Date parsing
  const parsed = new Date(dateString);
  return isNaN(parsed.getTime()) ? null : parsed;
}

export function formatDateForAPI(date) {
  if (!date) return '';
  
  // If it's already in YYYY-MM-DD format, return as is
  if (typeof date === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(date)) {
    return date;
  }
  
  const d = new Date(date);
  if (isNaN(d.getTime())) return '';
  
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`; // YYYY-MM-DD format (ISO)
}

export function validateDateField(dateString, fieldName) {
  if (!dateString || dateString.toString().trim() === '') {
    return { isValid: false, error: `${fieldName} is required` };
  }
  
  const date = parseDate(dateString);
  if (!date || isNaN(date.getTime())) {
    return { isValid: false, error: `${fieldName} is not a valid date` };
  }
  
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  if (date > today) {
    return { isValid: false, error: `${fieldName} cannot be in the future` };
  }
  
  return { isValid: true };
}

export function validDate(dateString) {
  if (!dateString) return false; // Dates are now required
  const inputDate = parseDate(dateString);
  if (!inputDate || isNaN(inputDate.getTime())) return false;
  
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  inputDate.setHours(0, 0, 0, 0);
  return inputDate <= today;
}

export function getTodayDate() {
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, '0');
  const day = String(today.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

// Optional: Common date formats for display
export const dateFormats = {
  DISPLAY: 'DD-MM-YYYY',
  API: 'YYYY-MM-DD',
  EXCEL: 'MM/DD/YYYY'
};

export default {
  parseDate,
  formatDateForAPI,
  validateDateField,
  validDate,
  getTodayDate,
  dateFormats
};