# verify_sprint12.py
import os
import sys
import django
import urllib.request
import urllib.error
import json

sys.path.append(os.path.abspath("backend"))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")
django.setup()

from django.contrib.auth import get_user_model
from apps.users.models import Role, Permission, RolePermission
from apps.lms.models import (
    CourseStructure, Exam, QuestionBank, ExamQuestion, ExamAttempt, 
    Certificate, Badge, UserBadge
)

User = get_user_model()
base_url = "http://127.0.0.1:8000"

def make_request(path, method="GET", payload=None, token=None):
    url = f"{base_url}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    data = json.dumps(payload).encode("utf-8") if payload else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            err_data = json.loads(e.read().decode("utf-8"))
        except:
            err_data = e.reason
        return e.code, err_data
    except Exception as e:
        return 500, str(e)

def seed_sprint12_permissions():
    print("Seeding Sprint 12 LMS Exams & Progress permissions...")
    roles = {
        "SUPERADMIN": [
            "lms:exam:view", "lms:exam:create", "lms:exam:update", "lms:exam:delete",
            "lms:question:view", "lms:question:create", "lms:question:update", "lms:question:delete",
            "lms:progress:view", "lms:progress:create", "lms:progress:update", "lms:progress:delete",
            "lms:certificate:view", "lms:certificate:create", "lms:badge:view"
        ],
        "ADMIN": [
            "lms:exam:view", "lms:exam:create", "lms:exam:update", "lms:exam:delete",
            "lms:question:view", "lms:question:create", "lms:question:update", "lms:question:delete",
            "lms:progress:view", "lms:progress:create", "lms:progress:update", "lms:progress:delete",
            "lms:certificate:view", "lms:certificate:create", "lms:badge:view"
        ],
        "TEACHER": [
            "lms:exam:view", "lms:exam:create", "lms:exam:update",
            "lms:question:view", "lms:question:create", "lms:question:update",
            "lms:progress:view", "lms:progress:create",
            "lms:certificate:view", "lms:badge:view"
        ],
        "STUDENT": [
            "lms:exam:view", "lms:progress:create", "lms:progress:view", 
            "lms:certificate:view", "lms:badge:view"
        ]
    }
    for role_name, codenames in roles.items():
        try:
            role = Role.objects.get(name=role_name)
            for code in codenames:
                perm, _ = Permission.objects.get_or_create(codename=code, defaults={"description": f"Enables {code}"})
                RolePermission.objects.get_or_create(role=role, permission=perm)
        except Exception as e:
            print(f"Skipping role {role_name}: {e}")
    print("Permissions seeding complete.")

def run_tests():
    print("--- STARTING SPRINT 12 LMS EXAMS, GRADING & GAMIFICATION TESTS ---")
    seed_sprint12_permissions()
    
    # 1. Authenticate users
    print("\n1. Authenticating Admin & Student users...")
    status, res_admin = make_request("/api/v1/users/users/login/", "POST", {"email": "admin@brahmavidya.edu", "password": "adminpassword123"})
    admin_token = res_admin.get("token")
    assert status == 200
    
    status, res_student = make_request("/api/v1/users/users/login/", "POST", {"email": "student@brahmavidya.edu", "password": "studentpassword123"})
    student_token = res_student.get("token")
    assert status == 200

    # 2. Setup Course Structure & Exam Nodes
    print("\n2. Seeding test course & exam structures...")
    # Clean up first
    ExamAttempt.objects.all().delete()
    Exam.objects.filter(title="Sprint 12 Verification Exam").delete()
    CourseStructure.objects.filter(slug="sprint12-verif-course").delete()
    
    course_node = CourseStructure.objects.create(
        node_type="COURSE",
        title="Sprint 12 Verification Course",
        slug="sprint12-verif-course",
        description="Course designed for validating exam scoring logic."
    )
    
    exam = Exam.objects.create(
        course=course_node,
        title="Sprint 12 Verification Exam",
        passing_score=75.00,
        duration_minutes=30
    )
    
    # Seed QuestionBank
    q1 = QuestionBank.objects.create(
        course=course_node,
        question_text="What is the non-dual witness in Vedanta?",
        question_type="MULTIPLE_CHOICE",
        options=["Sakshi", "Prakriti", "Manas", "Buddhi"],
        correct_answers=[0]
    )
    
    q2 = QuestionBank.objects.create(
        course=course_node,
        question_text="What represents superposition in Quantum mechanics?",
        question_type="MULTIPLE_CHOICE",
        options=["Coexistence of multiple potential states", "Singular localized target", "Dynamic entropy vectors"],
        correct_answers=[0]
    )
    
    # Link questions to Exam
    ExamQuestion.objects.create(exam=exam, question=q1)
    ExamQuestion.objects.create(exam=exam, question=q2)

    # 3. Start Exam Attempt
    print("\n3. Starting Exam Attempt (POST /exams/{id}/start/)...")
    status, attempt = make_request(f"/api/v1/lms/exams/{exam.id}/start/", "POST", token=student_token)
    print(f"Start attempt response: Status {status}, Attempt ID: {attempt.get('id')}, Status: {attempt.get('status')}")
    assert status == 201
    assert attempt.get("status") == "STARTED"
    
    attempt_id = attempt.get("id")

    # 4. Submit Exam Attempt (100% Score)
    print("\n4. Submitting Exam answers for scoring (POST /exams/{id}/submit/)...")
    payload = {
        "answers": {
            str(q1.id): [0],
            str(q2.id): [0]
        }
    }
    status, graded = make_request(f"/api/v1/lms/exams/{exam.id}/submit/", "POST", payload=payload, token=student_token)
    print(f"Submit attempt response: Status {status}, Score: {graded.get('score')}%, Passed: {graded.get('passed')}, Status: {graded.get('status')}")
    assert status == 200
    assert float(graded.get("score")) == 100.00
    assert graded.get("passed") is True
    assert graded.get("status") == "SUBMITTED"

    # 5. Verify Certificates Generation
    print("\n5. Checking dynamic certificate creation...")
    cert = Certificate.objects.filter(user=res_student.get("user", {}).get("id"), course=course_node).first()
    print(f"Certificate issued found: {cert is not None}")
    assert cert is not None
    print(f"Certificate signature hash: {cert.signature_hash}")
    assert len(cert.signature_hash) == 64

    # 6. Verify Badges achievements unlocking
    print("\n6. Checking gamified badges rewards unlocked...")
    user_badges = UserBadge.objects.filter(user=res_student.get("user", {}).get("id"))
    badge_titles = [ub.badge.title for ub in user_badges]
    print(f"Unlocked Badges: {badge_titles}")
    assert "Knowledge Seeker" in badge_titles
    assert "Perfect Sage" in badge_titles or "Exam Conqueror" in badge_titles

    print("\n--- SPRINT 12 LMS EXAMS, GRADING & GAMIFICATION TESTS PASSED ---")

if __name__ == "__main__":
    run_tests()
