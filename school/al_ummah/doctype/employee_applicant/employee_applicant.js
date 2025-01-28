
// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Applicant', {
    refresh: function (frm) {
      if (!frm.is_new() && frm.doc.application_status === 'Applied') {
        frm.add_custom_button(
          __('Approve'),
          function () {
            frm.set_value('application_status', 'Approved');
            frm.save_or_update();
            frm.events.hire(frm); // Automatically hire when approved
          },
          'Actions'
        );

        frm.add_custom_button(
          __('Reject'),
          function () {
            frm.set_value('application_status', 'Rejected');
            frm.save_or_update();
          },
          'Actions'
        );
      }

      if (!frm.is_new() && frm.doc.application_status === 'Rejected') {
        frm.add_custom_button(
          __('Approve'),
          function () {
            frm.set_value('application_status', 'Approved');
            frm.save_or_update();
            frm.events.hire(frm); // Automatically hire when approved
          },
          'Actions'
        );
      }

      frappe.realtime.on('hire_employee_progress', function (data) {
        if (data.progress) {
          frappe.hide_msgprint(true);
          frappe.show_progress(
            __('Hiring employee'),
            data.progress[0],
            data.progress[1]
          );
        }
      });
    },

    hire: function (frm) {
      frappe.model.open_mapped_doc({
        method: 'school.al_ummah.api.hire_employee',
        frm: frm,
      });
    },
});