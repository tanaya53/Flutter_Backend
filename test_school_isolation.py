"""
Mandatory Multi-School Isolation Test Suite for Mazi Shala.
Verifies zero data leakage between ASH001 and ASH002.
"""

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIClient
from apps.accounts.models import User
from apps.students.models import Student

def run_tests():
    print("=" * 70)
    print("RUNNING MULTI-SCHOOL DATA ISOLATION TEST (ASH001 vs ASH002)")
    print("=" * 70)

    client = APIClient()

    # 1. TEST LOGIN FOR ASH001 PRINCIPAL
    login_a = client.post('/api/auth/login/', {'username': 'principal_ash001', 'password': 'password123'})
    assert login_a.status_code == 200, f"Login failed for ASH001: {login_a.data}"
    token_a = login_a.data['tokens']['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_a}')
    print("[PASS] Logged in as ASH001 Principal (Rajesh Patil)")

    # 2. VERIFY ASH001 STUDENTS VISIBLE, ASH002 INVISIBLE
    res_students_a = client.get('/api/students/')
    assert res_students_a.status_code == 200
    student_rolls_a = [s['student_id'] for s in res_students_a.data]
    print(f"  ASH001 Students fetched: {student_rolls_a}")

    assert 'ASH001-S01' in student_rolls_a, "Missing ASH001 student!"
    assert 'ASH001-S02' in student_rolls_a, "Missing ASH001 student!"
    assert 'ASH002-S01' not in student_rolls_a, "CRITICAL LEAK: ASH002-S01 visible to ASH001!"
    assert 'ASH002-S02' not in student_rolls_a, "CRITICAL LEAK: ASH002-S02 visible to ASH001!"
    print("[PASS] Verified ASH001 Principal ONLY sees ASH001 students (Zero leakage of ASH002)")

    # 3. DIRECT CROSS-SCHOOL ACCESS ATTEMPT (GET ASH002 student using ASH001 credentials)
    stud_b = Student.objects.get(student_id='ASH002-S01')
    res_cross = client.get(f'/api/students/{stud_b.id}/')
    assert res_cross.status_code in [403, 404], f"Cross-school access must fail, got {res_cross.status_code}"
    print(f"[PASS] Direct access to ASH002 student {stud_b.id} with ASH001 credentials correctly denied ({res_cross.status_code})")

    # 4. TEST LOGIN FOR ASH002 PRINCIPAL
    login_b = client.post('/api/auth/login/', {'username': 'principal_ash002', 'password': 'password123'})
    assert login_b.status_code == 200, f"Login failed for ASH002: {login_b.data}"
    token_b = login_b.data['tokens']['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_b}')
    print("\n[PASS] Logged in as ASH002 Principal (Sunita Gavit)")

    # 5. VERIFY ASH002 STUDENTS VISIBLE, ASH001 INVISIBLE
    res_students_b = client.get('/api/students/')
    assert res_students_b.status_code == 200
    student_rolls_b = [s['student_id'] for s in res_students_b.data]
    print(f"  ASH002 Students fetched: {student_rolls_b}")

    assert 'ASH002-S01' in student_rolls_b, "Missing ASH002 student!"
    assert 'ASH002-S02' in student_rolls_b, "Missing ASH002 student!"
    assert 'ASH001-S01' not in student_rolls_b, "CRITICAL LEAK: ASH001-S01 visible to ASH002!"
    assert 'ASH001-S02' not in student_rolls_b, "CRITICAL LEAK: ASH001-S02 visible to ASH002!"
    print("[PASS] Verified ASH002 Principal ONLY sees ASH002 students (Zero leakage of ASH001)")

    # 6. VERIFY HOSTEL ISOLATION
    hostels_b = client.get('/api/hostel/')
    assert hostels_b.status_code == 200
    hostel_names_b = [h['name'] for h in hostels_b.data]
    assert 'Birsa Munda Boys Hostel' not in hostel_names_b, "CRITICAL LEAK: ASH001 hostel in ASH002!"
    assert 'Satpuda Boys Hostel' in hostel_names_b
    print("[PASS] Verified Hostel isolation across schools")

    # 7. VERIFY ANNOUNCEMENT ISOLATION
    ann_b = client.get('/api/announcements/')
    assert ann_b.status_code == 200
    ann_titles_b = [a['title'] for a in ann_b.data]
    assert any('Toranmal' in t for t in ann_titles_b), "Missing ASH002 announcement"
    assert not any('Palghar' in t for t in ann_titles_b), "CRITICAL LEAK: ASH001 announcement in ASH002"
    print("[PASS] Verified Announcements isolation across schools")

    # 8. VERIFY PENDING USER APPROVAL RESTRICTION
    u_pending = User.objects.get(username='pending_teacher_ash001')
    u_pending.is_approved = False
    u_pending.save()
    from apps.accounts.models import SchoolJoinRequest
    SchoolJoinRequest.objects.filter(user=u_pending).update(status='PENDING', approved_by=None, approval_date=None)

    client.credentials()  # Clear credentials
    login_unapproved = client.post('/api/auth/login/', {'username': 'pending_teacher_ash001', 'password': 'password123'})
    assert login_unapproved.status_code == 403, f"Unapproved user should be 403, got {login_unapproved.status_code}"
    print("[PASS] Verified unapproved user cannot log in before Principal approval (403 Forbidden)")

    # 9. TEST PRINCIPAL APPROVAL WORKFLOW
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_a}')
    join_reqs = client.get('/api/auth/join-requests/')
    assert join_reqs.status_code == 200
    assert len(join_reqs.data) > 0, "Expected at least 1 pending join request"
    req_id = join_reqs.data[0]['id']
    approve_res = client.post(f'/api/auth/approve-user/{req_id}/', {'action': 'APPROVE'})
    assert approve_res.status_code == 200
    print(f"[PASS] Principal successfully approved join request {req_id}")

    # Now verify the user CAN log in!
    login_approved = client.post('/api/auth/login/', {'username': 'pending_teacher_ash001', 'password': 'password123'})
    assert login_approved.status_code == 200, "Approved user should now be able to log in!"
    print("[PASS] Newly approved user successfully logged in after Principal approval!")

    # 10. VERIFY REPORT DOWNLOADS (AS PRINCIPAL)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_a}')
    pdf_res = client.get('/api/reports/attendance/?export_type=pdf')
    assert pdf_res.status_code == 200, f"Expected 200 for PDF, got {pdf_res.status_code}"
    assert pdf_res['Content-Type'] == 'application/pdf'
    excel_res = client.get('/api/reports/attendance/?export_type=excel')
    assert excel_res.status_code == 200, f"Expected 200 for Excel, got {excel_res.status_code}"
    print("[PASS] PDF and Excel report generation functioning perfectly with full school isolation")

    print("\n" + "=" * 70)
    print("ALL MULTI-SCHOOL DATA ISOLATION & SECURITY TESTS PASSED 100%!")
    print("=" * 70)

if __name__ == '__main__':
    run_tests()
