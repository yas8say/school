// Copyright (c) 2025, Yaseen and contributors
// For license information, please see license.txt

frappe.ui.form.on('Instructor Applicant', {
    refresh: function (frm) {
      if (!frm.is_new() && frm.doc.application_status === 'Applied') {
        frm.add_custom_button(
          __('Approve'),
          function () {
            frm.set_value('application_status', 'Approved');
            frm.save_or_update();
            frm.events.onboard(frm); // Automatically hire when approved
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
            frm.events.onboard(frm); // Automatically hire when approved
          },
          'Actions'
        );
      }

      frappe.realtime.on('onboard_instructor_progress', function (data) {
        if (data.progress) {
          frappe.hide_msgprint(true);
          frappe.show_progress(
            __('Onboarding Instructor'),
            data.progress[0],
            data.progress[1]
          );
        }
      });
    },

    onboard: function (frm) {
      frappe.model.open_mapped_doc({
        method: 'school.al_ummah.api.onboard_instructor',
        frm: frm,
      });
    },
});