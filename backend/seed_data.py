import os
import sys
import django

# Setup Django Environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")
django.setup()

from django.contrib.auth import get_user_model
from apps.users.models import Role, Permission, RolePermission, UserProfile
from apps.cms.models import Page, Blog, Tutorial
from apps.lms.models import CourseStructure
from apps.wallets.models import Wallet

User = get_user_model()

def seed_db():
    print("Starting BrahmaVidya Galaxy Seeding script...")

    # 1. Create Roles
    superadmin_role, _ = Role.objects.get_or_create(
        name="SUPERADMIN",
        defaults={"description": "Platform owner with total system sovereignty."}
    )
    teacher_role, _ = Role.objects.get_or_create(
        name="TEACHER",
        defaults={"description": "Educator workspace access and course publisher."}
    )
    student_role, _ = Role.objects.get_or_create(
        name="STUDENT",
        defaults={"description": "Student learner account and academic explorer."}
    )

    print("Roles created.")

    # 2. Create Users and UserProfiles
    # Admin User
    admin_user = User.objects.filter(email="admin@brahmavidya.edu").first()
    if not admin_user:
        admin_user = User.objects.create_user(
            email="admin@brahmavidya.edu",
            password="adminpassword123",
            role=superadmin_role,
            is_staff=True,
            is_superuser=True
        )
        UserProfile.objects.create(
            user=admin_user,
            first_name="Brahma",
            last_name="Admin",
            avatar_url="https://api.dicebear.com/7.x/bottts/svg?seed=admin",
            bio="Systems administrator and enterprise architect.",
            settings={"theme": "dark", "notifications": True}
        )
        print("Admin user seeded.")
    else:
        admin_user.role = superadmin_role
        admin_user.save()

    # Teacher User
    teacher_user = User.objects.filter(email="teacher@brahmavidya.edu").first()
    if not teacher_user:
        teacher_user = User.objects.create_user(
            email="teacher@brahmavidya.edu",
            password="teacherpassword123",
            role=teacher_role
        )
        UserProfile.objects.create(
            user=teacher_user,
            first_name="Aacharya",
            last_name="Saraswati",
            avatar_url="https://api.dicebear.com/7.x/avataaars/svg?seed=teacher",
            bio="Vedantic philosophy and quantum mechanics scholar.",
            settings={"theme": "light", "notifications": True}
        )
        print("Teacher user seeded.")
    else:
        teacher_user.role = teacher_role
        teacher_user.save()

    # Student User
    student_user = User.objects.filter(email="student@brahmavidya.edu").first()
    if not student_user:
        student_user = User.objects.create_user(
            email="student@brahmavidya.edu",
            password="studentpassword123",
            role=student_role
        )
        UserProfile.objects.create(
            user=student_user,
            first_name="Shishya",
            last_name="Arjuna",
            avatar_url="https://api.dicebear.com/7.x/pixel-art/svg?seed=student",
            bio="Student explorer seeking wisdom in cosmic systems.",
            settings={"theme": "light", "notifications": True}
        )
        print("Student user seeded.")
    else:
        student_user.role = student_role
        student_user.save()

    # 3. Create Wallets automatically if not created
    for u in User.objects.all():
        wallet, created = Wallet.objects.get_or_create(
            user=u,
            defaults={"currency": "INR", "balance": 1000.00}
        )
        if created:
            print(f"Wallet seeded for user: {u.email}")

    print("Seeding completed successfully!")

if __name__ == "__main__":
    seed_db()
