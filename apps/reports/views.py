import io
from datetime import datetime
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import views, status, permissions
from rest_framework.response import Response

from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

from apps.accounts.permissions import IsPrincipal, IsApprovedUser
from apps.accounts.models import User, SchoolJoinRequest
from apps.students.models import Student
from apps.attendance.models import DailyAttendance
from apps.health.models import EmergencyMedicalAlert, MedicalCheckup
from apps.hostel.models import Hostel, Bed, LeaveRequest, FoodStock
from apps.scholarships.models import Scholarship
from apps.inventory.models import InventoryItem

class PrincipalDashboardAnalyticsView(views.APIView):
    """
    Main aggregated dashboard analytics for School Principal.
    Strictly isolated to request.user.school.
    """
    permission_classes = [IsPrincipal]

    def get(self, request):
        school = request.user.school
        today = timezone.now().date()

        # Staff counts
        total_teachers = User.objects.filter(school=school, role='teacher', is_approved=True).count()
        total_wardens = User.objects.filter(school=school, role='warden', is_approved=True).count()
        pending_approvals = SchoolJoinRequest.objects.filter(school=school, status='PENDING').count()

        # Student counts
        students_qs = Student.objects.filter(school=school, is_active=True)
        total_students = students_qs.count()
        male_students = students_qs.filter(gender='MALE').count()
        female_students = students_qs.filter(gender='FEMALE').count()

        # Attendance today
        attendances_today = DailyAttendance.objects.filter(school=school, date=today)
        present_today = attendances_today.filter(status='PRESENT').count()
        absent_today = attendances_today.filter(status='ABSENT').count()
        attendance_percentage = round((present_today / total_students * 100), 1) if total_students > 0 else 0.0

        # Hostel occupancy
        total_beds = Bed.objects.filter(room__hostel__school=school).count()
        occupied_beds = Bed.objects.filter(room__hostel__school=school, is_occupied=True).count()
        hostel_occupancy_percentage = round((occupied_beds / total_beds * 100), 1) if total_beds > 0 else 0.0
        pending_leaves = LeaveRequest.objects.filter(school=school, status='PENDING').count()

        # Health Alerts
        active_health_alerts = EmergencyMedicalAlert.objects.filter(
            school=school,
            status__in=['ACTIVE', 'UNDER_CARE']
        ).count()

        # Inventory Alerts
        low_inventory_count = sum(1 for it in InventoryItem.objects.filter(school=school) if it.is_low_stock)
        low_food_count = sum(1 for fs in FoodStock.objects.filter(school=school) if fs.is_low_stock)

        # Scholarships
        pending_scholarships = Scholarship.objects.filter(school=school, status__in=['PENDING', 'SUBMITTED', 'UNDER_REVIEW']).count()

        return Response({
            'school_name': school.name,
            'school_id': school.school_id,
            'district': school.district,
            'total_students': total_students,
            'male_students': male_students,
            'female_students': female_students,
            'total_teachers': total_teachers,
            'total_wardens': total_wardens,
            'pending_staff_approvals': pending_approvals,
            'attendance_percentage': attendance_percentage,
            'present_today': present_today,
            'absent_today': absent_today,
            'total_beds': total_beds,
            'occupied_beds': occupied_beds,
            'hostel_occupancy_percentage': hostel_occupancy_percentage,
            'pending_leaves': pending_leaves,
            'active_health_alerts': active_health_alerts,
            'low_inventory_alerts': low_inventory_count + low_food_count,
            'pending_scholarships': pending_scholarships,
        })

class ExportAttendanceReportView(views.APIView):
    """
    Exports Attendance Report in PDF or Excel.
    """
    permission_classes = [IsPrincipal]

    def get(self, request):
        export_format = (request.query_params.get('export_type') or request.query_params.get('type') or 'excel').lower()
        school = request.user.school
        records = DailyAttendance.objects.filter(school=school).order_by('-date', 'student__first_name')[:300]

        if export_format == 'pdf':
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
            elements = []
            styles = getSampleStyleSheet()

            elements.append(Paragraph(f"<b>MAZI SHALA - {school.name} ({school.school_id})</b>", styles['Title']))
            elements.append(Paragraph(f"Official Attendance Report - Generated on {datetime.now().strftime('%d %B %Y')}", styles['Normal']))
            elements.append(Spacer(1, 15))

            data = [['Date', 'Roll No', 'Student Name', 'Class', 'Status', 'Remarks']]
            for r in records:
                data.append([
                    str(r.date),
                    r.student.student_id,
                    r.student.full_name,
                    r.student.grade_class,
                    r.status,
                    r.remarks or '-'
                ])

            t = Table(data, colWidths=[80, 70, 180, 80, 80, 150])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A365D')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            elements.append(t)
            doc.build(elements)
            buffer.seek(0)

            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Attendance_Report_{school.school_id}.pdf"'
            return response

        else:
            # Excel
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Daily Attendance"

            ws.append([f"MAZI SHALA - {school.name} ({school.school_id})"])
            ws.append([f"Attendance Export - {datetime.now().strftime('%Y-%m-%d %H:%M')}"])
            ws.append([])

            headers = ['Date', 'Student ID', 'First Name', 'Last Name', 'Grade / Class', 'Status', 'Remarks']
            ws.append(headers)

            for cell in ws[4]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="1A365D", end_color="1A365D", fill_type="solid")

            for r in records:
                ws.append([
                    str(r.date),
                    r.student.student_id,
                    r.student.first_name,
                    r.student.last_name,
                    r.student.grade_class,
                    r.status,
                    r.remarks
                ])

            stream = io.BytesIO()
            wb.save(stream)
            stream.seek(0)

            response = HttpResponse(stream, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="Attendance_Report_{school.school_id}.xlsx"'
            return response

class ExportStudentRosterView(views.APIView):
    """
    Exports Student Roster in Excel or PDF.
    """
    permission_classes = [IsPrincipal]

    def get(self, request):
        export_format = (request.query_params.get('export_type') or request.query_params.get('type') or 'excel').lower()
        school = request.user.school
        students = Student.objects.filter(school=school, is_active=True).order_by('grade_class', 'first_name')

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Students Roster"

        ws.append([f"MAZI SHALA - {school.name} ({school.school_id}) - Student Roster"])
        ws.append([])

        headers = ['Roll No', 'Name', 'Gender', 'Class', 'Hostel Block', 'Room No', 'Bed No', 'Blood Group', 'Emergency Contact']
        ws.append(headers)
        for cell in ws[3]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="276749", end_color="276749", fill_type="solid")

        for s in students:
            ws.append([
                s.student_id,
                s.full_name,
                s.gender,
                s.grade_class,
                s.hostel_block or 'Day Scholar',
                s.room_number or '-',
                s.bed_number or '-',
                s.blood_group,
                s.emergency_contact
            ])

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)

        response = HttpResponse(stream, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="Student_Roster_{school.school_id}.xlsx"'
        return response

class ExportHostelReportView(views.APIView):
    """
    Exports Hostel Occupancy & Leave Summary.
    """
    permission_classes = [IsPrincipal]

    def get(self, request):
        school = request.user.school
        hostels = Hostel.objects.filter(school=school)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Hostel Status"

        ws.append([f"MAZI SHALA - {school.name} ({school.school_id}) - Hostel Occupancy Report"])
        ws.append([])
        headers = ['Hostel Name', 'Block Type', 'Room Number', 'Capacity', 'Occupied Beds', 'Available Beds', 'Status']
        ws.append(headers)

        for cell in ws[3]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="744210", end_color="744210", fill_type="solid")

        for h in hostels:
            for r in h.rooms.all():
                ws.append([
                    h.name,
                    h.block_type,
                    r.room_number,
                    r.capacity,
                    r.occupied_count,
                    r.available_count,
                    'FULL' if r.available_count == 0 else 'AVAILABLE'
                ])

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)

        response = HttpResponse(stream, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="Hostel_Report_{school.school_id}.xlsx"'
        return response

class ExportInventoryReportView(views.APIView):
    """
    Exports Inventory & Assets status.
    """
    permission_classes = [IsPrincipal]

    def get(self, request):
        school = request.user.school
        items = InventoryItem.objects.filter(school=school)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Inventory Items"

        ws.append([f"MAZI SHALA - {school.name} ({school.school_id}) - Inventory & Resources Report"])
        ws.append([])
        headers = ['Item Name', 'Category', 'Total Qty', 'Allocated / Issued', 'Available', 'Unit', 'Stock Status']
        ws.append(headers)

        for cell in ws[3]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="2C5282", end_color="2C5282", fill_type="solid")

        for it in items:
            ws.append([
                it.name,
                it.category,
                it.total_quantity,
                it.allocated_quantity,
                it.available_quantity,
                it.unit,
                'LOW STOCK' if it.is_low_stock else 'ADEQUATE'
            ])

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)

        response = HttpResponse(stream, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="Inventory_Report_{school.school_id}.xlsx"'
        return response

class ExportScholarshipReportView(views.APIView):
    """
    Exports Scholarship & Welfare distribution records.
    """
    permission_classes = [IsPrincipal]

    def get(self, request):
        school = request.user.school
        scholarships = Scholarship.objects.filter(school=school)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Scholarships"

        ws.append([f"MAZI SHALA - {school.name} ({school.school_id}) - Scholarship Report"])
        ws.append([])
        headers = ['Student Roll', 'Student Name', 'Class', 'Scheme Name', 'Application No', 'Amount (INR)', 'Status', 'Disbursement Date']
        ws.append(headers)

        for cell in ws[3]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="7B341E", end_color="7B341E", fill_type="solid")

        for sc in scholarships:
            ws.append([
                sc.student.student_id,
                sc.student.full_name,
                sc.student.grade_class,
                sc.scheme_name,
                sc.application_number or '-',
                float(sc.amount),
                sc.status,
                str(sc.disbursement_date) if sc.disbursement_date else '-'
            ])

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)

        response = HttpResponse(stream, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="Scholarship_Report_{school.school_id}.xlsx"'
        return response
