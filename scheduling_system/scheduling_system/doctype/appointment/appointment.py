from datetime import timedelta
import frappe
from frappe.model.document import Document

class Appointment(Document):
    def validate(self):
        if self.start_date and self.duration:
            # duration is of type "Time", so we get hours and minutes
            hours, minutes, _ = map(int, self.duration.split(':'))
            self.end_date = frappe.utils.add_to_date(
                self.start_date,
                hours=hours,
                minutes=minutes
            )

        # Validação de conflitos
        if not (self.seller and self.start_date and self.end_date):
            return

        overlapping_appointments = frappe.db.get_all(
            'Appointment',
            filters={
                'seller': self.seller,
                'name': ['!=', self.name],
                'start_date': ['<', self.end_date],
                'end_date': ['>', self.start_date]
            },
            fields=['name', 'start_date', 'end_date']
        )

        if overlapping_appointments:
            conflict = overlapping_appointments[0]
            frappe.throw(
                f"Conflito com compromisso existente: {conflict['name']} "
                f"({conflict['start_date']} até {conflict['end_date']})"
            )
