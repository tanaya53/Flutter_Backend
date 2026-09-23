"""
Seed rich demo data for Mazi Shala multi-tenant Ashram School platform.
Creates two isolated schools: ASH001 (Palghar) and ASH002 (Nandurbar)
with comprehensive (3-4+ items) functional data across all roles and features:
- Principal: Metrics, Staff Approvals, Student Directory, Reports, Inventory, Scholarships, Welfare, Announcements
- Teacher: Mentee Wards, Classroom Attendance, Academic Remarks, Student Concerns, Health Alerts
- Warden: Dorms & Bed Allocations, Night Roll Call, Leave Passes, Meals Tracking, Low-Stock Food Alerts, Incidents
- Parent: Child Profile, Attendance Calendar, Medical Checkups, Vaccinations, Circulars & Notices
"""

import os
import sys
import django
from datetime import date, timedelta
from django.utils import timezone

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.schools.models import School
from apps.accounts.models import User, SchoolJoinRequest, TeacherProfile, WardenProfile
from apps.students.models import Student, Guardian, AcademicRemark, StudentConcern
from apps.attendance.models import DailyAttendance, HostelAttendance
from apps.health.models import HealthRecord, MedicalCheckup, Vaccination, EmergencyMedicalAlert
from apps.hostel.models import Hostel, Room, Bed, LeaveRequest, HostelIncident, Meal, FoodStock
from apps.scholarships.models import Scholarship, WelfareScheme
from apps.inventory.models import InventoryItem, InventoryTransaction
from apps.announcements.models import Announcement, Notification

def seed():
    print("=" * 70)
    print("Seeding Rich Mazi Shala Demo Data for Multi-Role Evaluation...")
    print("=" * 70)

    today = timezone.now().date()

    # =========================================================================
    # 1. SCHOOL A: ASH001 - Government Ashram School Manor (Palghar)
    # =========================================================================
    print("\n[1/2] Seeding School A: Government Ashram School Manor, Palghar (ASH001)...")
    school_a, _ = School.objects.get_or_create(
        school_id='ASH001',
        defaults={
            'name': 'Government Ashram School Manor (Palghar)',
            'address': 'Post Manor, Taluka Palghar, District Palghar',
            'district': 'Palghar',
            'state': 'Maharashtra',
            'school_type': 'GOVT_ASHRAM',
            'contact_email': 'ashram.manor@tribal.mah.gov.in',
            'contact_phone': '02525-245678',
        }
    )

    # 1.1 Users for School A
    # Principal
    p_a, _ = User.objects.get_or_create(
        username='principal_ash001',
        defaults={
            'first_name': 'Rajesh',
            'last_name': 'Patil',
            'email': 'principal.manor@tribal.mah.gov.in',
            'role': 'principal',
            'school': school_a,
            'is_approved': True,
            'phone_number': '9823012345'
        }
    )
    p_a.set_password('password123')
    p_a.save()

    # Teacher / Mentor
    t_a, _ = User.objects.get_or_create(
        username='teacher_ash001',
        defaults={
            'first_name': 'Sanjay',
            'last_name': 'More',
            'email': 'sanjay.more@tribal.mah.gov.in',
            'role': 'teacher',
            'school': school_a,
            'is_approved': True,
            'phone_number': '9823054321'
        }
    )
    t_a.set_password('password123')
    t_a.save()
    TeacherProfile.objects.get_or_create(
        user=t_a,
        school=school_a,
        defaults={'qualification': 'M.Sc., B.Ed.', 'specialization': 'Science & Mathematics'}
    )

    # Warden
    w_a, _ = User.objects.get_or_create(
        username='warden_ash001',
        defaults={
            'first_name': 'Maruti',
            'last_name': 'Bhoi',
            'email': 'warden.manor@tribal.mah.gov.in',
            'role': 'warden',
            'school': school_a,
            'is_approved': True,
            'phone_number': '9823098765'
        }
    )
    w_a.set_password('password123')
    w_a.save()
    WardenProfile.objects.get_or_create(
        user=w_a,
        school=school_a,
        defaults={'assigned_block': 'Birsa Munda Boys & Rani Gaidinliu Girls Blocks', 'contact_ext': '104'}
    )

    # Parent
    parent_a, _ = User.objects.get_or_create(
        username='parent_ash001',
        defaults={
            'first_name': 'Kashinath',
            'last_name': 'Patil',
            'email': 'kashinath.patil@example.com',
            'role': 'parent',
            'school': school_a,
            'is_approved': True,
            'phone_number': '9823077777'
        }
    )
    parent_a.set_password('password123')
    parent_a.save()

    # 1.2 Pending Join Requests for Staff Approvals (Principal Feature: 4 requests)
    pending_staff = [
        ('pending_teacher_ash001', 'Anita', 'Deshmukh', 'anita.deshmukh@example.com', 'teacher', 'B.A., B.Ed. (English Literature)', '9823011111'),
        ('pending_warden_ash001', 'Nilesh', 'Jadhav', 'nilesh.jadhav@example.com', 'warden', 'Residential Supervision Experience 4 yrs', '9823011122'),
        ('pending_parent_ash001', 'Ramesh', 'Kokane', 'ramesh.kokane@example.com', 'parent', 'Father of Mahesh Kokane (Class 8)', '9823011133'),
        ('pending_teacher2_ash001', 'Rekha', 'Thakar', 'rekha.thakar@example.com', 'teacher', 'M.A., D.T.Ed (Marathi & Social Science)', '9823011144'),
    ]
    for uname, fname, lname, email, role, qual, phone in pending_staff:
        u, _ = User.objects.get_or_create(
            username=uname,
            defaults={
                'first_name': fname,
                'last_name': lname,
                'email': email,
                'role': role,
                'school': school_a,
                'is_approved': False,
                'phone_number': phone
            }
        )
        u.set_password('password123')
        u.save()
        SchoolJoinRequest.objects.get_or_create(
            user=u,
            school=school_a,
            defaults={'requested_role': role, 'status': 'PENDING'}
        )

    # 1.3 Students for School A (7 students across Class 7, 8, 9)
    student_specs_a = [
        ('ASH001-S01', 'Rahul', 'Patil', 'MALE', 'Class 8', 'A', 'ADM-2024-001', date(2012, 5, 14), 'B+', 'Birsa Munda Boys Hostel', '101', 'Bed-1', '9823077777', 'At Post Kasa, Taluka Dahanu, District Palghar'),
        ('ASH001-S02', 'Sunita', 'Gavit', 'FEMALE', 'Class 9', 'A', 'ADM-2024-002', date(2011, 8, 22), 'O+', 'Rani Gaidinliu Girls Hostel', '201', 'Bed-1', '9823088888', 'At Post Jawhar, Taluka Jawhar, District Palghar'),
        ('ASH001-S03', 'Amit', 'Rathod', 'MALE', 'Class 8', 'A', 'ADM-2024-003', date(2012, 11, 3), 'A+', 'Birsa Munda Boys Hostel', '101', 'Bed-2', '9823099999', 'At Post Vikramgad, Taluka Vikramgad, District Palghar'),
        ('ASH001-S04', 'Pooja', 'Dhangar', 'FEMALE', 'Class 8', 'A', 'ADM-2024-004', date(2012, 4, 18), 'AB+', 'Rani Gaidinliu Girls Hostel', '201', 'Bed-2', '9823066661', 'At Post Wada, Taluka Wada, District Palghar'),
        ('ASH001-S05', 'Mahesh', 'Kokane', 'MALE', 'Class 8', 'A', 'ADM-2024-005', date(2012, 9, 27), 'O+', 'Birsa Munda Boys Hostel', '102', 'Bed-1', '9823066662', 'At Post Talasari, Taluka Talasari, District Palghar'),
        ('ASH001-S06', 'Kiran', 'Bhil', 'MALE', 'Class 7', 'A', 'ADM-2024-006', date(2013, 2, 11), 'B+', 'Birsa Munda Boys Hostel', '102', 'Bed-2', '9823066663', 'At Post Mokhada, Taluka Mokhada, District Palghar'),
        ('ASH001-S07', 'Sarita', 'Chaudhary', 'FEMALE', 'Class 9', 'A', 'ADM-2024-007', date(2011, 12, 5), 'A+', 'Rani Gaidinliu Girls Hostel', '202', 'Bed-1', '9823066664', 'At Post Palghar Rural, Taluka Palghar, District Palghar'),
    ]

    students_a = {}
    for sid, fn, ln, gnd, cls, div, adm, dob, bg, hst, rm, bd, emc, addr in student_specs_a:
        s, _ = Student.objects.get_or_create(
            school=school_a,
            student_id=sid,
            defaults={
                'first_name': fn,
                'last_name': ln,
                'gender': gnd,
                'grade_class': cls,
                'division': div,
                'admission_number': adm,
                'dob': dob,
                'blood_group': bg,
                'assigned_mentor': t_a,
                'hostel_block': hst,
                'room_number': rm,
                'bed_number': bd,
                'emergency_contact': emc,
                'address': addr
            }
        )
        students_a[sid] = s

    # Guardians
    Guardian.objects.get_or_create(
        school=school_a, student=students_a['ASH001-S01'],
        defaults={'name': 'Kashinath Patil', 'relationship': 'Father', 'contact_number': '9823077777', 'user': parent_a}
    )
    Guardian.objects.get_or_create(
        school=school_a, student=students_a['ASH001-S02'],
        defaults={'name': 'Shivaji Gavit', 'relationship': 'Father', 'contact_number': '9823088888'}
    )
    Guardian.objects.get_or_create(
        school=school_a, student=students_a['ASH001-S03'],
        defaults={'name': 'Vasant Rathod', 'relationship': 'Father', 'contact_number': '9823099999'}
    )
    Guardian.objects.get_or_create(
        school=school_a, student=students_a['ASH001-S04'],
        defaults={'name': 'Mangala Dhangar', 'relationship': 'Mother', 'contact_number': '9823066661'}
    )
    Guardian.objects.get_or_create(
        school=school_a, student=students_a['ASH001-S05'],
        defaults={'name': 'Ramesh Kokane', 'relationship': 'Father', 'contact_number': '9823066662'}
    )
    Guardian.objects.get_or_create(
        school=school_a, student=students_a['ASH001-S06'],
        defaults={'name': 'Tukaram Bhil', 'relationship': 'Father', 'contact_number': '9823066663'}
    )
    Guardian.objects.get_or_create(
        school=school_a, student=students_a['ASH001-S07'],
        defaults={'name': 'Dattu Chaudhary', 'relationship': 'Father', 'contact_number': '9823066664'}
    )

    # 1.4 Hostels, Rooms, and Beds for School A (Warden Feature)
    Bed.objects.filter(room__hostel__school=school_a).delete()
    Room.objects.filter(hostel__school=school_a).delete()

    hostel_a1, _ = Hostel.objects.get_or_create(
        school=school_a,
        name='Birsa Munda Boys Hostel',
        defaults={'block_type': 'BOYS', 'warden': w_a, 'total_capacity': 60}
    )
    # Room 101 (Boys)
    room_a101, _ = Room.objects.get_or_create(hostel=hostel_a1, room_number='101', defaults={'floor': 1, 'capacity': 4})
    Bed.objects.get_or_create(room=room_a101, bed_number='Bed-1', defaults={'allocated_student': students_a['ASH001-S01'], 'is_occupied': True})
    Bed.objects.get_or_create(room=room_a101, bed_number='Bed-2', defaults={'allocated_student': students_a['ASH001-S03'], 'is_occupied': True})
    Bed.objects.get_or_create(room=room_a101, bed_number='Bed-3', defaults={'is_occupied': False})
    Bed.objects.get_or_create(room=room_a101, bed_number='Bed-4', defaults={'is_occupied': False})

    # Room 102 (Boys)
    room_a102, _ = Room.objects.get_or_create(hostel=hostel_a1, room_number='102', defaults={'floor': 1, 'capacity': 4})
    Bed.objects.get_or_create(room=room_a102, bed_number='Bed-1', defaults={'allocated_student': students_a['ASH001-S05'], 'is_occupied': True})
    Bed.objects.get_or_create(room=room_a102, bed_number='Bed-2', defaults={'allocated_student': students_a['ASH001-S06'], 'is_occupied': True})
    Bed.objects.get_or_create(room=room_a102, bed_number='Bed-3', defaults={'is_occupied': False})
    Bed.objects.get_or_create(room=room_a102, bed_number='Bed-4', defaults={'is_occupied': False})

    # Room 103 (Boys - Newly refurbished)
    room_a103, _ = Room.objects.get_or_create(hostel=hostel_a1, room_number='103', defaults={'floor': 1, 'capacity': 4})
    Bed.objects.get_or_create(room=room_a103, bed_number='Bed-1', defaults={'is_occupied': False})
    Bed.objects.get_or_create(room=room_a103, bed_number='Bed-2', defaults={'is_occupied': False})
    Bed.objects.get_or_create(room=room_a103, bed_number='Bed-3', defaults={'is_occupied': False})
    Bed.objects.get_or_create(room=room_a103, bed_number='Bed-4', defaults={'is_occupied': False})

    hostel_a2, _ = Hostel.objects.get_or_create(
        school=school_a,
        name='Rani Gaidinliu Girls Hostel',
        defaults={'block_type': 'GIRLS', 'warden': w_a, 'total_capacity': 50}
    )
    # Room 201 (Girls)
    room_a201, _ = Room.objects.get_or_create(hostel=hostel_a2, room_number='201', defaults={'floor': 2, 'capacity': 4})
    Bed.objects.get_or_create(room=room_a201, bed_number='Bed-1', defaults={'allocated_student': students_a['ASH001-S02'], 'is_occupied': True})
    Bed.objects.get_or_create(room=room_a201, bed_number='Bed-2', defaults={'allocated_student': students_a['ASH001-S04'], 'is_occupied': True})
    Bed.objects.get_or_create(room=room_a201, bed_number='Bed-3', defaults={'is_occupied': False})
    Bed.objects.get_or_create(room=room_a201, bed_number='Bed-4', defaults={'is_occupied': False})

    # Room 202 (Girls)
    room_a202, _ = Room.objects.get_or_create(hostel=hostel_a2, room_number='202', defaults={'floor': 2, 'capacity': 4})
    Bed.objects.get_or_create(room=room_a202, bed_number='Bed-1', defaults={'allocated_student': students_a['ASH001-S07'], 'is_occupied': True})
    Bed.objects.get_or_create(room=room_a202, bed_number='Bed-2', defaults={'is_occupied': False})
    Bed.objects.get_or_create(room=room_a202, bed_number='Bed-3', defaults={'is_occupied': False})
    Bed.objects.get_or_create(room=room_a202, bed_number='Bed-4', defaults={'is_occupied': False})

    # 1.5 Attendance History for School A (Past 14 Days)
    # Daily classroom roll call
    for day_offset in range(14):
        att_date = today - timedelta(days=day_offset)
        # Skip Sundays
        if att_date.weekday() == 6:
            continue

        for sid, stud in students_a.items():
            status_val = 'PRESENT'
            remarks_val = ''

            if sid == 'ASH001-S03' and day_offset in [0, 1, 2]:
                status_val = 'ABSENT'
                remarks_val = 'Reported high grade fever - admitted in dispensary'
            elif sid == 'ASH001-S01' and day_offset == 7:
                status_val = 'ABSENT'
                remarks_val = 'Mild fever and rest'
            elif sid == 'ASH001-S05' and day_offset in [4, 5]:
                status_val = 'ON_LEAVE'
                remarks_val = 'Approved family leave'

            DailyAttendance.objects.get_or_create(
                school=school_a,
                student=stud,
                date=att_date,
                defaults={'status': status_val, 'remarks': remarks_val, 'marked_by': t_a}
            )

    # 1.6 Hostel Attendance (Night Roll Call for past 4 days - Warden Feature)
    for night_offset in range(4):
        roll_date = today - timedelta(days=night_offset)
        for sid, stud in students_a.items():
            h_status = 'PRESENT'
            h_rem = 'Verified in dormitory during 8:30 PM inspection'

            if sid == 'ASH001-S03' and night_offset in [0, 1]:
                h_status = 'PRESENT'
                h_rem = 'Dispensary bed - health monitoring'
            elif sid == 'ASH001-S05' and night_offset == 3:
                h_status = 'ON_LEAVE'
                h_rem = 'Official weekend pass with father'

            HostelAttendance.objects.get_or_create(
                school=school_a,
                student=stud,
                date=roll_date,
                session='NIGHT',
                defaults={'status': h_status, 'remarks': h_rem, 'marked_by': w_a}
            )

    # 1.7 Student Leave Requests (Warden Feature: 4 requests with diverse statuses)
    LeaveRequest.objects.get_or_create(
        school=school_a,
        student=students_a['ASH001-S01'],
        start_date=today + timedelta(days=2),
        end_date=today + timedelta(days=5),
        defaults={
            'reason': 'Attending annual tribal cultural festival (Bohada) with family in Kasa',
            'escort_name': 'Kashinath Patil (Father)',
            'escort_contact': '9823077777',
            'status': 'PENDING'
        }
    )
    LeaveRequest.objects.get_or_create(
        school=school_a,
        student=students_a['ASH001-S02'],
        start_date=today - timedelta(days=2),
        end_date=today + timedelta(days=1),
        defaults={
            'reason': 'Medical checkup and ophthalmology follow-up at District Civil Hospital',
            'escort_name': 'Shivaji Gavit (Father)',
            'escort_contact': '9823088888',
            'status': 'APPROVED',
            'approved_by': w_a
        }
    )
    LeaveRequest.objects.get_or_create(
        school=school_a,
        student=students_a['ASH001-S03'],
        start_date=today + timedelta(days=1),
        end_date=today + timedelta(days=4),
        defaults={
            'reason': 'Elder brother wedding ceremony in Vikramgad village',
            'escort_name': 'Vasant Rathod (Father)',
            'escort_contact': '9823099999',
            'status': 'PENDING'
        }
    )
    LeaveRequest.objects.get_or_create(
        school=school_a,
        student=students_a['ASH001-S05'],
        start_date=today - timedelta(days=6),
        end_date=today - timedelta(days=2),
        defaults={
            'reason': 'Weekend post-exam home visit with father',
            'escort_name': 'Ramesh Kokane (Father)',
            'escort_contact': '9823066662',
            'status': 'RETURNED',
            'approved_by': w_a
        }
    )

    # 1.8 Hostel Incidents & Security Logs (Warden Feature: 4 incidents)
    HostelIncident.objects.get_or_create(
        school=school_a,
        title='Curfew & Dorm Noise Violation',
        defaults={
            'student': students_a['ASH001-S03'],
            'incident_type': 'DISCIPLINARY',
            'description': 'Senior dorm students found talking loudly and using mobile phones past 10:30 PM curfew lights-out.',
            'action_taken': 'Students counseled on residential discipline and phones deposited with warden for safety.',
            'reported_by': w_a
        }
    )
    HostelIncident.objects.get_or_create(
        school=school_a,
        title='Solar Water Heater Pipe Leakage',
        defaults={
            'student': None,
            'incident_type': 'MAINTENANCE',
            'description': 'Hot water distribution pipeline on Birsa Munda Hostel 1st floor washroom detected leaking.',
            'action_taken': 'Emergency PWD maintenance plumber notified. Main overhead supply valve shut temporarily.',
            'reported_by': w_a
        }
    )
    HostelIncident.objects.get_or_create(
        school=school_a,
        title='Midnight Sickness & Dehydration Observation',
        defaults={
            'student': students_a['ASH001-S03'],
            'incident_type': 'HEALTH',
            'description': 'Student developed sudden 102F fever and shivering during midnight curfew hours.',
            'action_taken': 'Shifted to hostel medical dispensary, administered paracetamol & ORS under PHC doctor phone guidance.',
            'reported_by': w_a
        }
    )
    HostelIncident.objects.get_or_create(
        school=school_a,
        title='Perimeter Street Light Malfunction',
        defaults={
            'student': None,
            'incident_type': 'SECURITY',
            'description': 'Compound wall flood light near rear athletic grounds flickering and shut off creating blind spot.',
            'action_taken': 'Night watchman stationed at rear post. MSEDCL certified electrical repairman requisitioned.',
            'reported_by': w_a
        }
    )

    # 1.9 Meals and Food Stock (Warden Feature: 4 meals today + 2 yesterday + 7 stocks with low stock alerts)
    Meal.objects.get_or_create(
        school=school_a,
        date=today,
        meal_type='BREAKFAST',
        defaults={
            'menu_description': 'Poha with Roasted Peanuts, Sprouted Moong Usal, Boiled Egg / Fresh Banana, Hot Cow Milk',
            'students_served': 125,
            'quality_status': 'Nutritious & Fresh',
            'inspected_by': w_a
        }
    )
    Meal.objects.get_or_create(
        school=school_a,
        date=today,
        meal_type='LUNCH',
        defaults={
            'menu_description': 'Steamed Rice, Tur Dal Tadka, Chana Masala Curry, Fresh Wheat Chapati, Sliced Cucumber',
            'students_served': 122,
            'quality_status': 'Hot & Hygienic',
            'inspected_by': w_a
        }
    )
    Meal.objects.get_or_create(
        school=school_a,
        date=today,
        meal_type='SNACK',
        defaults={
            'menu_description': 'Roasted Chana with Organic Jaggery, Herbal Lemongrass Kadha',
            'students_served': 120,
            'quality_status': 'Standard Quality',
            'inspected_by': w_a
        }
    )
    Meal.objects.get_or_create(
        school=school_a,
        date=today,
        meal_type='DINNER',
        defaults={
            'menu_description': 'Jeera Rice, Matki Usal, Shevga Sambar, Jowar Bhakri, Fresh Curd',
            'students_served': 124,
            'quality_status': 'Inspected and Approved',
            'inspected_by': w_a
        }
    )
    # Yesterday's Meals
    Meal.objects.get_or_create(
        school=school_a,
        date=today - timedelta(days=1),
        meal_type='LUNCH',
        defaults={
            'menu_description': 'Rice, Masoor Dal, Aloo Gobi Green Pea Curry, Chapati, Fresh Fruit',
            'students_served': 121,
            'quality_status': 'Excellent Nutrition',
            'inspected_by': w_a
        }
    )
    Meal.objects.get_or_create(
        school=school_a,
        date=today - timedelta(days=1),
        meal_type='DINNER',
        defaults={
            'menu_description': 'Moong Dal Khichdi, Gujarati Kadhi, Mixed Vegetable Fry, Chapati',
            'students_served': 123,
            'quality_status': 'Nutritious & Fresh',
            'inspected_by': w_a
        }
    )

    # Food stocks (with 2 items in Low-Stock alert state)
    food_stocks_a = [
        ('Rice (BPT Kolam Grade A)', 450.0, 'kg', 50.0),
        ('Tur Dal (Unpolished Premium)', 18.0, 'kg', 25.0), # LOW STOCK ALERT!
        ('Wheat Atta (Chakki Fresh)', 340.0, 'kg', 40.0),
        ('Refined Sunflower Cooking Oil', 42.0, 'Liters', 15.0),
        ('Soyabean Pulses & Moong', 12.0, 'kg', 20.0),      # LOW STOCK ALERT!
        ('Fresh Cow Milk (Daily Supply)', 55.0, 'Liters', 10.0),
        ('Iodized Salt & Kitchen Spices', 32.0, 'kg', 8.0),
    ]
    for iname, qty, unt, thres in food_stocks_a:
        FoodStock.objects.get_or_create(
            school=school_a,
            item_name=iname,
            defaults={'quantity': qty, 'unit': unt, 'low_stock_threshold': thres}
        )

    # 1.10 Academic Remarks & Student Concerns (Teacher Feature)
    # 5 Academic Remarks
    AcademicRemark.objects.get_or_create(
        school=school_a,
        student=students_a['ASH001-S01'],
        subject='Mathematics',
        term='Unit Test 1',
        defaults={
            'teacher': t_a,
            'performance': 'EXCELLENT',
            'remark': 'Shows tremendous enthusiasm in geometry and mental arithmetic. Solves algebraic equations quickly with high accuracy.'
        }
    )
    AcademicRemark.objects.get_or_create(
        school=school_a,
        student=students_a['ASH001-S02'],
        subject='Science',
        term='Unit Test 1',
        defaults={
            'teacher': t_a,
            'performance': 'EXCELLENT',
            'remark': 'Outstanding observation skills during botanical science experiments. Prepared the top class herbarium project.'
        }
    )
    AcademicRemark.objects.get_or_create(
        school=school_a,
        student=students_a['ASH001-S03'],
        subject='English',
        term='Unit Test 1',
        defaults={
            'teacher': t_a,
            'performance': 'NEEDS_IMPROVEMENT',
            'remark': 'Struggles with English grammar structure and reading comprehension. Recommended for 30-min daily remedial clinic.'
        }
    )
    AcademicRemark.objects.get_or_create(
        school=school_a,
        student=students_a['ASH001-S04'],
        subject='Marathi',
        term='Unit Test 1',
        defaults={
            'teacher': t_a,
            'performance': 'GOOD',
            'remark': 'Very expressive essay writing and fluent recitation of Marathi poetry. Consistently participates in class discussions.'
        }
    )
    AcademicRemark.objects.get_or_create(
        school=school_a,
        student=students_a['ASH001-S05'],
        subject='Social Studies',
        term='Unit Test 1',
        defaults={
            'teacher': t_a,
            'performance': 'AVERAGE',
            'remark': 'Solid understanding of Maharashtra historical events. Needs additional reinforcement on geography topography mapping.'
        }
    )

    # 4 Student Concerns (Teacher & Warden Feature)
    StudentConcern.objects.get_or_create(
        school=school_a,
        student=students_a['ASH001-S03'],
        category='HOMESICKNESS',
        description='Student appears withdrawn during evening self-study hours and expressing frequent desire to visit home.',
        defaults={
            'reported_by': t_a,
            'severity': 'MEDIUM',
            'status': 'OPEN',
            'resolution_notes': 'Mentor teacher conducted one-on-one counseling; hostel warden keeping gentle supervision.'
        }
    )
    StudentConcern.objects.get_or_create(
        school=school_a,
        student=students_a['ASH001-S01'],
        category='ACADEMIC',
        description='Requesting advanced reference books and extra problem sets for Maharashtra Tribal Scholarship state competitive exam.',
        defaults={
            'reported_by': t_a,
            'severity': 'LOW',
            'status': 'UNDER_REVIEW',
            'resolution_notes': 'Library issued two dedicated scholarship study guides.'
        }
    )
    StudentConcern.objects.get_or_create(
        school=school_a,
        student=students_a['ASH001-S05'],
        category='HEALTH',
        description='Complained of squinting and headaches when attempting to read blackboard from back bench.',
        defaults={
            'reported_by': t_a,
            'severity': 'HIGH',
            'status': 'RESOLVED',
            'resolution_notes': 'Mobile Medical Unit ophthalmologist confirmed mild myopia. Prescription spectacles issued under Tribal Health Grant.'
        }
    )
    StudentConcern.objects.get_or_create(
        school=school_a,
        student=students_a['ASH001-S06'],
        category='FINANCIAL',
        description='Guardian bank account linkage pending for Aadhaar DBT pre-matric stipend disbursement.',
        defaults={
            'reported_by': t_a,
            'severity': 'MEDIUM',
            'status': 'OPEN',
            'resolution_notes': 'School head clerk assisting father with India Post Payment Bank e-KYC.'
        }
    )

    # 1.11 Health Profiles, Medical Checkups, Vaccinations, and Emergency Alerts
    # Health Records
    health_specs_a = [
        ('ASH001-S01', 'B+', 'Dust & Pollen', 'None', 148.5, 39.0, 'Keep mild inhaler on hand during long-distance athletics'),
        ('ASH001-S02', 'O+', 'None known', 'None', 152.0, 42.0, 'Annual dental checkup up to date'),
        ('ASH001-S03', 'A+', 'Penicillin Allergy', 'Prone to seasonal bronchial fever', 145.0, 36.5, 'Strictly avoid penicillin-based antibiotics'),
        ('ASH001-S04', 'AB+', 'None known', 'None', 147.0, 38.0, 'Normal vision and vitals'),
        ('ASH001-S05', 'O+', 'None known', 'Mild Myopia (Prescribed Spectacles)', 150.0, 41.5, 'Spectacles to be worn during study and lab classes'),
        ('ASH001-S06', 'B+', 'None known', 'None', 142.0, 34.0, 'Healthy child with high athletic stamina'),
        ('ASH001-S07', 'A+', 'Sulfa Drugs', 'None', 153.5, 43.0, 'Healthy growth parameters'),
    ]
    for sid, bg, allg, chrnc, hgt, wgt, nts in health_specs_a:
        HealthRecord.objects.get_or_create(
            school=school_a,
            student=students_a[sid],
            defaults={
                'blood_group': bg,
                'allergies': allg,
                'chronic_conditions': chrnc,
                'height_cm': hgt,
                'weight_kg': wgt,
                'last_checkup_date': today - timedelta(days=10),
                'emergency_medical_notes': nts
            }
        )

    # 5 Medical Checkups
    MedicalCheckup.objects.get_or_create(
        school=school_a,
        student=students_a['ASH001-S01'],
        date=today - timedelta(days=10),
        defaults={
            'doctor_name': 'Dr. V. K. Shinde, M.B.B.S. (Medical Officer, PHC Manor)',
            'findings': 'General physical health normal. Hemoglobin 12.4 gm/dl. Lungs clear, cardiac sounds normal.',
            'prescriptions': 'Iron and Folic Acid (IFA) weekly tablet, Vitamin C chewable 500mg',
            'next_checkup_date': today + timedelta(days=80)
        }
    )
    MedicalCheckup.objects.get_or_create(
        school=school_a,
        student=students_a['ASH001-S01'],
        date=today - timedelta(days=65),
        defaults={
            'doctor_name': 'Dr. Pratibha Patil, B.A.M.S. (Mobile Medical Unit Palghar)',
            'findings': 'Seasonal allergic rhinitis and dry cough following change of weather.',
            'prescriptions': 'Cetirizine 5mg at bedtime for 3 days, warm saline gargling',
            'next_checkup_date': today - timedelta(days=10)
        }
    )
    MedicalCheckup.objects.get_or_create(
        school=school_a,
        student=students_a['ASH001-S02'],
        date=today - timedelta(days=18),
        defaults={
            'doctor_name': 'Dr. V. K. Shinde (Medical Officer, PHC Manor)',
            'findings': 'Excellent growth trajectory. Hemoglobin 12.8 gm/dl. Dental hygiene very good.',
            'prescriptions': 'Multivitamin supplementation',
            'next_checkup_date': today + timedelta(days=72)
        }
    )
    MedicalCheckup.objects.get_or_create(
        school=school_a,
        student=students_a['ASH001-S03'],
        date=today - timedelta(days=2),
        defaults={
            'doctor_name': 'Dr. S. R. Joshi (Rural Hospital Palghar)',
            'findings': 'Acute viral pyrexia with throat congestion. Temperature 102F on admission, responding to antipyretics.',
            'prescriptions': 'Paracetamol 500mg TID, Azithromycin 250mg OD, Electrolyte ORS solution',
            'next_checkup_date': today + timedelta(days=5)
        }
    )
    MedicalCheckup.objects.get_or_create(
        school=school_a,
        student=students_a['ASH001-S05'],
        date=today - timedelta(days=28),
        defaults={
            'doctor_name': 'Dr. A. B. Deshmukh (Ophthalmologist, District Hospital)',
            'findings': 'Bilateral refraction error detected (OD -1.00 D, OS -1.25 D).',
            'prescriptions': 'Prescription spectacles provided; front desk classroom placement',
            'next_checkup_date': today + timedelta(days=150)
        }
    )

    # 5 Vaccinations
    Vaccination.objects.get_or_create(
        school=school_a,
        student=students_a['ASH001-S01'],
        vaccine_name='Tetanus Toxoid (TT) 10-Year Booster',
        administered_date=today - timedelta(days=90),
        defaults={'dosage': 'Single 0.5ml IM Dose', 'administered_by': 'PHC Manor Immunization Team'}
    )
    Vaccination.objects.get_or_create(
        school=school_a,
        student=students_a['ASH001-S01'],
        vaccine_name='Albendazole (National Deworming Program)',
        administered_date=today - timedelta(days=35),
        defaults={'dosage': '400mg Chewable', 'administered_by': 'Sister Sunita (School Health Nurse)'}
    )
    Vaccination.objects.get_or_create(
        school=school_a,
        student=students_a['ASH001-S01'],
        vaccine_name='Vitamin A Prophylactic Solution',
        administered_date=today - timedelta(days=180),
        defaults={'dosage': '200,000 IU Oral', 'administered_by': 'PHC Manor Health Team'}
    )
    Vaccination.objects.get_or_create(
        school=school_a,
        student=students_a['ASH001-S02'],
        vaccine_name='Tetanus Toxoid (TT) Booster',
        administered_date=today - timedelta(days=60),
        defaults={'dosage': 'Single 0.5ml Dose', 'administered_by': 'PHC Manor Immunization Team'}
    )
    Vaccination.objects.get_or_create(
        school=school_a,
        student=students_a['ASH001-S03'],
        vaccine_name='Typhoid Conjugate Vaccine (TCV)',
        administered_date=today - timedelta(days=120),
        defaults={'dosage': '0.5ml IM Dose', 'administered_by': 'District Health Officer Team'}
    )

    # 3 Emergency Health Alerts
    EmergencyMedicalAlert.objects.get_or_create(
        school=school_a,
        student=students_a['ASH001-S03'],
        title='High Grade Viral Fever & Dehydration',
        defaults={
            'description': 'Student developed 102F temperature with shivering during night hours. Monitored in dispensary with antipyretics and ORS.',
            'severity': 'HIGH',
            'status': 'ACTIVE',
            'hospital_admitted': False,
            'reported_by': w_a
        }
    )
    EmergencyMedicalAlert.objects.get_or_create(
        school=school_a,
        student=students_a['ASH001-S01'],
        title='Mild Asthma Wheeze Post Athletic Drill',
        defaults={
            'description': 'Mild respiratory breathlessness noted after 400m sprint. Promptly relieved with salbutamol inhaler.',
            'severity': 'MEDIUM',
            'status': 'RESOLVED',
            'hospital_admitted': False,
            'reported_by': t_a,
            'resolved_at': timezone.now() - timedelta(days=12)
        }
    )
    EmergencyMedicalAlert.objects.get_or_create(
        school=school_a,
        student=students_a['ASH001-S06'],
        title='Left Ankle Sprain on Playground',
        defaults={
            'description': 'Twisted ankle during evening kabaddi tournament practice. Cold ice compression and crepe bandage applied.',
            'severity': 'LOW',
            'status': 'UNDER_CARE',
            'hospital_admitted': False,
            'reported_by': w_a
        }
    )

    # 1.12 Scholarships & Welfare Schemes (Principal Feature: 4 scholarships + 4 welfare schemes)
    Scholarship.objects.get_or_create(
        school=school_a,
        student=students_a['ASH001-S01'],
        scheme_name='Suvarna Mahotsavi Tribal Pre-Matric Scholarship',
        defaults={
            'application_number': 'MH-TRB-2026-0891',
            'amount': 3500.00,
            'academic_year': '2026-2027',
            'status': 'APPROVED',
            'disbursement_date': today - timedelta(days=5),
            'remarks': 'Sanctioned by Integrated Tribal Development Project (ITDP) Jawhar'
        }
    )
    Scholarship.objects.get_or_create(
        school=school_a,
        student=students_a['ASH001-S02'],
        scheme_name='Savitribai Phule Tribal Girl Child Educational Assistance',
        defaults={
            'application_number': 'MH-TRB-2026-1104',
            'amount': 4000.00,
            'academic_year': '2026-2027',
            'status': 'DISTRIBUTED',
            'disbursement_date': today - timedelta(days=12),
            'remarks': 'Amount credited directly to Aadhaar linked nationalized bank account'
        }
    )
    Scholarship.objects.get_or_create(
        school=school_a,
        student=students_a['ASH001-S03'],
        scheme_name='Pandit Deendayal Upadhyay Tribal Hostel & Boarding Scheme',
        defaults={
            'application_number': 'MH-TRB-2026-2241',
            'amount': 6000.00,
            'academic_year': '2026-2027',
            'status': 'UNDER_REVIEW',
            'remarks': 'Scheduled Tribe caste validity certificate verification underway at ITDP'
        }
    )
    Scholarship.objects.get_or_create(
        school=school_a,
        student=students_a['ASH001-S04'],
        scheme_name='Post-Matric & Pre-Matric Meritorious Tribal Student Stipend',
        defaults={
            'application_number': 'MH-TRB-2026-3098',
            'amount': 5000.00,
            'academic_year': '2026-2027',
            'status': 'SUBMITTED',
            'remarks': 'Application documents verified by Principal and forwarded to District Tribal Officer'
        }
    )

    # 4 Welfare Schemes
    WelfareScheme.objects.get_or_create(
        school=school_a,
        name='Annual Free Uniform Distribution Drive 2026',
        defaults={
            'category': 'UNIFORM',
            'target_class': 'Class 5 to 10',
            'total_eligible': 120,
            'total_distributed': 110,
            'status': 'IN_PROGRESS',
            'distribution_date': today - timedelta(days=15)
        }
    )
    WelfareScheme.objects.get_or_create(
        school=school_a,
        name='Maharashtra State Board Free Textbooks Scheme',
        defaults={
            'category': 'TEXTBOOKS',
            'target_class': 'All Enrolled Ashram Students',
            'total_eligible': 140,
            'total_distributed': 140,
            'status': 'COMPLETED',
            'distribution_date': today - timedelta(days=40)
        }
    )
    WelfareScheme.objects.get_or_create(
        school=school_a,
        name='Tribal Hostel Bedding, Blanket & Hygiene Kit Distribution',
        defaults={
            'category': 'HOSTEL_KIT',
            'target_class': 'Residential Hostel Students',
            'total_eligible': 110,
            'total_distributed': 95,
            'status': 'IN_PROGRESS',
            'distribution_date': today - timedelta(days=8)
        }
    )
    WelfareScheme.objects.get_or_create(
        school=school_a,
        name='Tribal Youth Athletic & Physical Education Sports Kits',
        defaults={
            'category': 'OTHER',
            'target_class': 'Class 7 to 10 Inter-School Sports Teams',
            'total_eligible': 60,
            'total_distributed': 0,
            'status': 'PLANNED'
        }
    )

    # 1.13 Inventory & Asset Management (Principal Feature: 6 items + 4 transactions)
    inv_items_a = [
        ('Hostel Heavy Steel Bunk Beds', 'BEDDING', 60, 48, 'Units', 10, 'Hostel Dorm Blocks A & B'),
        ('Science Laboratory Chemistry Experiment Kits', 'LAB', 10, 8, 'Sets', 4, 'Senior Science Laboratory'), # LOW STOCK (2 avail <= 4)
        ('Ashram School Navy Blue Uniform Sets', 'UNIFORM', 200, 175, 'Pairs', 30, 'Central Logistics Store'),
        ('Leather Football & Cricket Athletic Kits', 'SPORTS', 15, 12, 'Kits', 5, 'Physical Education Depot'),  # LOW STOCK (3 avail <= 5)
        ('Digital Learning Tablets (8-inch ICT)', 'COMPUTER', 40, 35, 'Units', 8, 'ICT Digital Classroom 2'),
        ('Hostel Cotton Mattresses & Pillows', 'BEDDING', 80, 65, 'Sets', 15, 'Hostel Linen Store'),
    ]
    inv_map_a = {}
    for iname, cat, tot, alloc, unt, thres, loc in inv_items_a:
        item_obj, _ = InventoryItem.objects.get_or_create(
            school=school_a,
            name=iname,
            defaults={
                'category': cat,
                'total_quantity': tot,
                'allocated_quantity': alloc,
                'unit': unt,
                'low_stock_threshold': thres,
                'storage_location': loc
            }
        )
        inv_map_a[iname] = item_obj

    # 4 Transactions
    InventoryTransaction.objects.get_or_create(
        school=school_a,
        item=inv_map_a['Hostel Heavy Steel Bunk Beds'],
        transaction_type='STOCK_IN',
        quantity=60,
        defaults={
            'recipient_name': 'Hostel Blocks',
            'recipient_role': 'Warden',
            'handled_by': p_a,
            'remarks': 'Procured under ITDP Tribal Capital Infrastructure Grant 2026'
        }
    )
    InventoryTransaction.objects.get_or_create(
        school=school_a,
        item=inv_map_a['Science Laboratory Chemistry Experiment Kits'],
        transaction_type='ISSUE',
        quantity=8,
        defaults={
            'recipient_name': 'Sanjay More',
            'recipient_role': 'Teacher',
            'handled_by': p_a,
            'remarks': 'Issued for 8th and 9th grade curriculum practical demonstrations'
        }
    )
    InventoryTransaction.objects.get_or_create(
        school=school_a,
        item=inv_map_a['Ashram School Navy Blue Uniform Sets'],
        transaction_type='ISSUE',
        quantity=50,
        defaults={
            'recipient_name': 'Class 8 Boys & Girls',
            'recipient_role': 'Student',
            'handled_by': p_a,
            'remarks': 'Annual uniform distribution round 1 completed'
        }
    )
    InventoryTransaction.objects.get_or_create(
        school=school_a,
        item=inv_map_a['Leather Football & Cricket Athletic Kits'],
        transaction_type='DAMAGED',
        quantity=2,
        defaults={
            'recipient_name': 'Sports Grounds',
            'recipient_role': 'Staff',
            'handled_by': p_a,
            'remarks': 'Damaged during inter-ashram monsoon athletic trials; written off'
        }
    )

    # 1.14 Announcements (Principal & Parent Feature: 4 diverse circulars)
    Announcement.objects.get_or_create(
        school=school_a,
        title='Quarterly Integrated Health & Eye Camp Notice',
        defaults={
            'message': 'Integrated health checkup by Mobile Medical Unit and specialist ophthalmologists will be held this Thursday. All hostel and day-scholar students must attend.',
            'target_role': 'ALL',
            'is_emergency': False,
            'created_by': p_a
        }
    )
    Announcement.objects.get_or_create(
        school=school_a,
        title='URGENT: Red Alert Heavy Rainfall & Hostel Perimeter Protocol',
        defaults={
            'message': 'Palghar district administration has issued a Red Alert for torrential monsoon rainfall. Wardens must ensure no student exits the hostel boundary. Emergency diesel generator and medical supplies verified.',
            'target_role': 'ALL',
            'is_emergency': True,
            'created_by': p_a
        }
    )
    Announcement.objects.get_or_create(
        school=school_a,
        title='Parent-Teacher Association (PTA) Term Review Meeting',
        defaults={
            'message': 'All parents and guardians are cordially invited to attend the mid-term PTA review on Saturday at 10:30 AM to discuss student academic remarks, tribal scholarship status, and residential hostel facilities.',
            'target_role': 'PARENTS',
            'is_emergency': False,
            'created_by': p_a
        }
    )
    Announcement.objects.get_or_create(
        school=school_a,
        title='Hostel Night Curfew & Safety Protocol Instructions',
        defaults={
            'message': 'All residential hostel wardens must complete evening roll-call before 8:30 PM and record daily hostel attendance in the portal. Any unexcused absence must be escalated immediately to the Principal.',
            'target_role': 'WARDENS',
            'is_emergency': False,
            'created_by': p_a
        }
    )

    # =========================================================================
    # 2. SCHOOL B: ASH002 - Government Ashram School Toranmal (Nandurbar)
    # =========================================================================
    print("\n[2/2] Seeding School B: Government Ashram School Toranmal, Nandurbar (ASH002)...")
    school_b, _ = School.objects.get_or_create(
        school_id='ASH002',
        defaults={
            'name': 'Government Ashram School Toranmal (Nandurbar)',
            'address': 'Toranmal Hill Station, Taluka Shahada, District Nandurbar',
            'district': 'Nandurbar',
            'state': 'Maharashtra',
            'school_type': 'GOVT_ASHRAM',
            'contact_email': 'ashram.toranmal@tribal.mah.gov.in',
            'contact_phone': '02568-234567',
        }
    )

    # 2.1 Users for School B
    p_b, _ = User.objects.get_or_create(
        username='principal_ash002',
        defaults={
            'first_name': 'Sunita',
            'last_name': 'Gavit',
            'email': 'principal.toranmal@tribal.mah.gov.in',
            'role': 'principal',
            'school': school_b,
            'is_approved': True,
            'phone_number': '9823022222'
        }
    )
    p_b.set_password('password123')
    p_b.save()

    t_b, _ = User.objects.get_or_create(
        username='teacher_ash002',
        defaults={
            'first_name': 'Dilip',
            'last_name': 'Padvi',
            'email': 'dilip.padvi@tribal.mah.gov.in',
            'role': 'teacher',
            'school': school_b,
            'is_approved': True,
            'phone_number': '9823033333'
        }
    )
    t_b.set_password('password123')
    t_b.save()
    TeacherProfile.objects.get_or_create(
        user=t_b,
        school=school_b,
        defaults={'qualification': 'M.A., B.Ed.', 'specialization': 'Languages & Social Studies'}
    )

    w_b, _ = User.objects.get_or_create(
        username='warden_ash002',
        defaults={
            'first_name': 'Suresh',
            'last_name': 'Valvi',
            'email': 'suresh.valvi@tribal.mah.gov.in',
            'role': 'warden',
            'school': school_b,
            'is_approved': True,
            'phone_number': '9823044444'
        }
    )
    w_b.set_password('password123')
    w_b.save()
    WardenProfile.objects.get_or_create(
        user=w_b,
        school=school_b,
        defaults={'assigned_block': 'Satpuda Boys & Narmada Girls Blocks', 'contact_ext': '201'}
    )

    parent_b, _ = User.objects.get_or_create(
        username='parent_ash002',
        defaults={
            'first_name': 'Gopal',
            'last_name': 'Padvi',
            'email': 'gopal.padvi@example.com',
            'role': 'parent',
            'school': school_b,
            'is_approved': True,
            'phone_number': '9823055555'
        }
    )
    parent_b.set_password('password123')
    parent_b.save()

    # Pending Join Requests for School B
    pending_staff_b = [
        ('pending_teacher_ash002', 'Mahesh', 'Vasave', 'mahesh.vasave@example.com', 'teacher', 'B.Sc., B.Ed. (Physics & Math)', '9823022211'),
        ('pending_warden_ash002', 'Suman', 'Naik', 'suman.naik@example.com', 'warden', 'Hostel Warden & Sports Coach', '9823022233'),
        ('pending_parent_ash002', 'Somnath', 'Valvi', 'somnath.valvi@example.com', 'parent', 'Father of Kavita Valvi (Class 9)', '9823022244'),
    ]
    for uname, fname, lname, email, role, qual, phone in pending_staff_b:
        u, _ = User.objects.get_or_create(
            username=uname,
            defaults={
                'first_name': fname,
                'last_name': lname,
                'email': email,
                'role': role,
                'school': school_b,
                'is_approved': False,
                'phone_number': phone
            }
        )
        u.set_password('password123')
        u.save()
        SchoolJoinRequest.objects.get_or_create(
            user=u,
            school=school_b,
            defaults={'requested_role': role, 'status': 'PENDING'}
        )

    # 2.2 Students for School B (5 students)
    student_specs_b = [
        ('ASH002-S01', 'Vikrant', 'Padvi', 'MALE', 'Class 8', 'A', 'TOR-2024-001', date(2012, 3, 10), 'AB+', 'Satpuda Boys Hostel', '101', 'Bed-1', '9823055555', 'At Post Dhadgaon, District Nandurbar'),
        ('ASH002-S02', 'Kavita', 'Valvi', 'FEMALE', 'Class 9', 'A', 'TOR-2024-002', date(2011, 7, 19), 'B+', 'Narmada Girls Hostel', '201', 'Bed-1', '9823066666', 'At Post Molgi, District Nandurbar'),
        ('ASH002-S03', 'Sachin', 'Naik', 'MALE', 'Class 8', 'A', 'TOR-2024-003', date(2012, 6, 15), 'O+', 'Satpuda Boys Hostel', '101', 'Bed-2', '9823066667', 'At Post Bilgaon, District Nandurbar'),
        ('ASH002-S04', 'Rohini', 'Pawara', 'FEMALE', 'Class 8', 'A', 'TOR-2024-004', date(2012, 10, 29), 'A+', 'Narmada Girls Hostel', '201', 'Bed-2', '9823066668', 'At Post Akkalkuwa, District Nandurbar'),
        ('ASH002-S05', 'Ajay', 'Gavit', 'MALE', 'Class 7', 'A', 'TOR-2024-005', date(2013, 1, 14), 'B+', 'Satpuda Boys Hostel', '102', 'Bed-1', '9823066669', 'At Post Taloda, District Nandurbar'),
    ]

    students_b = {}
    for sid, fn, ln, gnd, cls, div, adm, dob, bg, hst, rm, bd, emc, addr in student_specs_b:
        s, _ = Student.objects.get_or_create(
            school=school_b,
            student_id=sid,
            defaults={
                'first_name': fn,
                'last_name': ln,
                'gender': gnd,
                'grade_class': cls,
                'division': div,
                'admission_number': adm,
                'dob': dob,
                'blood_group': bg,
                'assigned_mentor': t_b,
                'hostel_block': hst,
                'room_number': rm,
                'bed_number': bd,
                'emergency_contact': emc,
                'address': addr
            }
        )
        students_b[sid] = s

    Guardian.objects.get_or_create(
        school=school_b, student=students_b['ASH002-S01'],
        defaults={'name': 'Gopal Padvi', 'relationship': 'Father', 'contact_number': '9823055555', 'user': parent_b}
    )
    Guardian.objects.get_or_create(
        school=school_b, student=students_b['ASH002-S02'],
        defaults={'name': 'Somnath Valvi', 'relationship': 'Father', 'contact_number': '9823066666'}
    )
    Guardian.objects.get_or_create(
        school=school_b, student=students_b['ASH002-S03'],
        defaults={'name': 'Bharat Naik', 'relationship': 'Father', 'contact_number': '9823066667'}
    )
    Guardian.objects.get_or_create(
        school=school_b, student=students_b['ASH002-S04'],
        defaults={'name': 'Shantaram Pawara', 'relationship': 'Father', 'contact_number': '9823066668'}
    )
    Guardian.objects.get_or_create(
        school=school_b, student=students_b['ASH002-S05'],
        defaults={'name': 'Subhash Gavit', 'relationship': 'Father', 'contact_number': '9823066669'}
    )

    # 2.3 Hostels, Rooms, Beds for School B
    Bed.objects.filter(room__hostel__school=school_b).delete()
    Room.objects.filter(hostel__school=school_b).delete()

    hostel_b1, _ = Hostel.objects.get_or_create(
        school=school_b,
        name='Satpuda Boys Hostel',
        defaults={'block_type': 'BOYS', 'warden': w_b, 'total_capacity': 50}
    )
    room_b101, _ = Room.objects.get_or_create(hostel=hostel_b1, room_number='101', defaults={'floor': 1, 'capacity': 4})
    Bed.objects.get_or_create(room=room_b101, bed_number='Bed-1', defaults={'allocated_student': students_b['ASH002-S01'], 'is_occupied': True})
    Bed.objects.get_or_create(room=room_b101, bed_number='Bed-2', defaults={'allocated_student': students_b['ASH002-S03'], 'is_occupied': True})
    Bed.objects.get_or_create(room=room_b101, bed_number='Bed-3', defaults={'is_occupied': False})
    Bed.objects.get_or_create(room=room_b101, bed_number='Bed-4', defaults={'is_occupied': False})

    room_b102, _ = Room.objects.get_or_create(hostel=hostel_b1, room_number='102', defaults={'floor': 1, 'capacity': 4})
    Bed.objects.get_or_create(room=room_b102, bed_number='Bed-1', defaults={'allocated_student': students_b['ASH002-S05'], 'is_occupied': True})
    Bed.objects.get_or_create(room=room_b102, bed_number='Bed-2', defaults={'is_occupied': False})
    Bed.objects.get_or_create(room=room_b102, bed_number='Bed-3', defaults={'is_occupied': False})

    hostel_b2, _ = Hostel.objects.get_or_create(
        school=school_b,
        name='Narmada Girls Hostel',
        defaults={'block_type': 'GIRLS', 'warden': w_b, 'total_capacity': 40}
    )
    room_b201, _ = Room.objects.get_or_create(hostel=hostel_b2, room_number='201', defaults={'floor': 2, 'capacity': 4})
    Bed.objects.get_or_create(room=room_b201, bed_number='Bed-1', defaults={'allocated_student': students_b['ASH002-S02'], 'is_occupied': True})
    Bed.objects.get_or_create(room=room_b201, bed_number='Bed-2', defaults={'allocated_student': students_b['ASH002-S04'], 'is_occupied': True})
    Bed.objects.get_or_create(room=room_b201, bed_number='Bed-3', defaults={'is_occupied': False})

    # 2.4 Attendance for School B (Past 10 days)
    for day_offset in range(10):
        att_date = today - timedelta(days=day_offset)
        if att_date.weekday() == 6:
            continue
        for sid, stud in students_b.items():
            status_val = 'PRESENT'
            remarks_val = ''
            if sid == 'ASH002-S03' and day_offset in [1, 2]:
                status_val = 'ABSENT'
                remarks_val = 'Mild fever'
            DailyAttendance.objects.get_or_create(
                school=school_b,
                student=stud,
                date=att_date,
                defaults={'status': status_val, 'remarks': remarks_val, 'marked_by': t_b}
            )

    # Hostel Attendance for School B
    for night_offset in range(3):
        roll_date = today - timedelta(days=night_offset)
        for sid, stud in students_b.items():
            HostelAttendance.objects.get_or_create(
                school=school_b,
                student=stud,
                date=roll_date,
                session='NIGHT',
                defaults={'status': 'PRESENT', 'remarks': 'Roll call verified', 'marked_by': w_b}
            )

    # 2.5 Leave Requests for School B
    LeaveRequest.objects.get_or_create(
        school=school_b,
        student=students_b['ASH002-S01'],
        start_date=today + timedelta(days=1),
        end_date=today + timedelta(days=4),
        defaults={
            'reason': 'Family agricultural harvest assistance in Dhadgaon village',
            'escort_name': 'Gopal Padvi (Father)',
            'escort_contact': '9823055555',
            'status': 'PENDING'
        }
    )
    LeaveRequest.objects.get_or_create(
        school=school_b,
        student=students_b['ASH002-S02'],
        start_date=today - timedelta(days=3),
        end_date=today,
        defaults={
            'reason': 'Dental treatment appointment in Shahada town',
            'escort_name': 'Somnath Valvi (Father)',
            'escort_contact': '9823066666',
            'status': 'RETURNED',
            'approved_by': w_b
        }
    )

    # 2.6 Incidents for School B
    HostelIncident.objects.get_or_create(
        school=school_b,
        title='Drinking Water Filter Cartridge Replacement Due',
        defaults={
            'incident_type': 'MAINTENANCE',
            'description': 'Main RO drinking water plant filter indicator showing amber maintenance alert.',
            'action_taken': 'Authorized maintenance agency summoned from Shahada.',
            'reported_by': w_b
        }
    )

    # 2.7 Meals & Food Stock for School B
    Meal.objects.get_or_create(
        school=school_b,
        date=today,
        meal_type='LUNCH',
        defaults={
            'menu_description': 'Rice, Moong Dal, Shevga Sambar, Chapati, Fresh Fruit',
            'students_served': 95,
            'quality_status': 'Hot & Wholesome',
            'inspected_by': w_b
        }
    )
    Meal.objects.get_or_create(
        school=school_b,
        date=today,
        meal_type='DINNER',
        defaults={
            'menu_description': 'Steamed Rice, Tur Dal, Mixed Vegetable Sabzi, Bhakri',
            'students_served': 94,
            'quality_status': 'Inspected & Approved',
            'inspected_by': w_b
        }
    )
    FoodStock.objects.get_or_create(school=school_b, item_name='Rice (Kolam Grade B)', defaults={'quantity': 350.0, 'unit': 'kg', 'low_stock_threshold': 50.0})
    FoodStock.objects.get_or_create(school=school_b, item_name='Tur Dal', defaults={'quantity': 14.0, 'unit': 'kg', 'low_stock_threshold': 20.0}) # Low stock alert
    FoodStock.objects.get_or_create(school=school_b, item_name='Wheat Flour', defaults={'quantity': 220.0, 'unit': 'kg', 'low_stock_threshold': 30.0})

    # 2.8 Academic Remarks & Concerns for School B
    AcademicRemark.objects.get_or_create(
        school=school_b,
        student=students_b['ASH002-S01'],
        subject='Science',
        term='Unit Test 1',
        defaults={
            'teacher': t_b,
            'performance': 'EXCELLENT',
            'remark': 'Remarkable interest in nature conservation and environmental biology.'
        }
    )
    AcademicRemark.objects.get_or_create(
        school=school_b,
        student=students_b['ASH002-S02'],
        subject='Mathematics',
        term='Unit Test 1',
        defaults={
            'teacher': t_b,
            'performance': 'GOOD',
            'remark': 'Consistent arithmetic calculations, active homework submission.'
        }
    )
    StudentConcern.objects.get_or_create(
        school=school_b,
        student=students_b['ASH002-S01'],
        category='ACADEMIC',
        description='Requires extra coaching in Hindi grammar and vocabulary.',
        defaults={
            'reported_by': t_b,
            'severity': 'LOW',
            'status': 'OPEN'
        }
    )

    # 2.9 Health for School B
    for sid, stud in students_b.items():
        HealthRecord.objects.get_or_create(
            school=school_b,
            student=stud,
            defaults={'blood_group': stud.blood_group, 'allergies': 'None known', 'height_cm': 146.0, 'weight_kg': 38.0}
        )
    MedicalCheckup.objects.get_or_create(
        school=school_b,
        student=students_b['ASH002-S01'],
        date=today - timedelta(days=14),
        defaults={
            'doctor_name': 'Dr. N. T. Patil (PHC Toranmal)',
            'findings': 'Normal health and development. Hemoglobin 12.0 gm/dl.',
            'prescriptions': 'Iron and Folic acid supplements'
        }
    )
    Vaccination.objects.get_or_create(
        school=school_b,
        student=students_b['ASH002-S01'],
        vaccine_name='Tetanus Toxoid (TT) Booster',
        administered_date=today - timedelta(days=80),
        defaults={'dosage': 'Single Dose', 'administered_by': 'PHC Toranmal Health Nurse'}
    )
    Vaccination.objects.get_or_create(
        school=school_b,
        student=students_b['ASH002-S01'],
        vaccine_name='Albendazole Deworming',
        administered_date=today - timedelta(days=40),
        defaults={'dosage': '400mg Single Dose', 'administered_by': 'PHC Toranmal Health Nurse'}
    )

    # 2.10 Scholarships & Welfare for School B
    Scholarship.objects.get_or_create(
        school=school_b,
        student=students_b['ASH002-S01'],
        scheme_name='Suvarna Mahotsavi Tribal Pre-Matric Scholarship',
        defaults={
            'application_number': 'MH-TRB-2026-9012',
            'amount': 3500.00,
            'status': 'APPROVED',
            'disbursement_date': today - timedelta(days=6),
            'remarks': 'Approved by ITDP Nandurbar'
        }
    )
    WelfareScheme.objects.get_or_create(
        school=school_b,
        name='Toranmal Ashram Uniform Distribution 2026',
        defaults={
            'category': 'UNIFORM',
            'target_class': 'Class 5 to 10',
            'total_eligible': 90,
            'total_distributed': 82,
            'status': 'IN_PROGRESS'
        }
    )

    # 2.11 Inventory for School B
    it_b1, _ = InventoryItem.objects.get_or_create(
        school=school_b,
        name='Hostel Cots & Metal Beds',
        defaults={'category': 'BEDDING', 'total_quantity': 50, 'allocated_quantity': 42, 'unit': 'Units', 'low_stock_threshold': 5}
    )
    InventoryTransaction.objects.get_or_create(
        school=school_b,
        item=it_b1,
        transaction_type='STOCK_IN',
        quantity=50,
        defaults={'handled_by': p_b, 'remarks': 'Procured under Tribal Welfare Grant'}
    )

    # 2.12 Announcements for School B
    Announcement.objects.get_or_create(
        school=school_b,
        title='Welcome to Toranmal Ashram School Academic Term',
        defaults={
            'message': 'Welcome to all residential students, teachers and staff for the term at Government Ashram School Toranmal.',
            'target_role': 'ALL',
            'is_emergency': False,
            'created_by': p_b
        }
    )

    print("\n" + "=" * 70)
    print("SUCCESS: Rich demo dataset seeded successfully for both schools!")
    print("=" * 70)
    print("SCHOOL 1: Government Ashram School Palghar (ASH001)")
    print("  - Principal: principal_ash001 / password123")
    print("  - Teacher:   teacher_ash001   / password123")
    print("  - Warden:    warden_ash001    / password123")
    print("  - Parent:    parent_ash001    / password123")
    print("  * 4 Pending Staff Join Requests (Review in Principal Portal)")
    print("  * 7 Enrolled Students across Classes 7, 8, 9")
    print("  * 2 Hostel Blocks with 5 Rooms & Bed Allocations")
    print("  * 14 Days Attendance History & Night Roll-Calls")
    print("  * 4 Student Leave Requests (Pending, Approved, Returned)")
    print("  * 4 Hostel Incidents (Disciplinary, Maintenance, Health, Security)")
    print("  * 6 Daily Meals & 7 Food Stocks with Low Stock Alerts")
    print("  * 5 Academic Remarks & 4 Student Concerns")
    print("  * 7 Health Records, 5 Checkups, 5 Vaccinations, 3 Emergency Alerts")
    print("  * 4 Scholarships & 4 Welfare Schemes")
    print("  * 6 Inventory Assets with Transaction History")
    print("  * 4 School Announcements (Health Camp, Red Alert, PTA, Curfew)")
    print("----------------------------------------------------------------")
    print("SCHOOL 2: Government Ashram School Nandurbar (ASH002)")
    print("  - Principal: principal_ash002 / password123")
    print("  - Teacher:   teacher_ash002   / password123")
    print("  - Warden:    warden_ash002    / password123")
    print("  - Parent:    parent_ash002    / password123")
    print("=" * 70)

if __name__ == '__main__':
    seed()
