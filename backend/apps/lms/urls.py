"""
LMS Endpoints Router - BrahmaVidya Galaxy
Purpose: Maps routing paths to LMS views.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.lms.views import (
    CourseStructureViewSet, LearningProgressViewSet, AssignmentViewSet, AssignmentSubmissionViewSet,
    ProjectViewSet, ProjectSubmissionViewSet, ExamViewSet, QuestionBankViewSet, ExamQuestionViewSet,
    CertificateViewSet, BadgeViewSet, UserBadgeViewSet, TeacherApplicationViewSet, TeacherClassViewSet,
    StudentEnrollmentViewSet, CourseViewSet, ChapterViewSet, LessonViewSet, ProgramViewSet, SubjectViewSet,
    TopicViewSet, SubtopicViewSet, PracticeViewSet, PracticeAttemptViewSet,
    StudentMeEnrollmentsView, StudentMeProgressView, StudentMeCertificatesView, StudentMeBadgesView,
    LiveClassViewSet, ExamAttemptViewSet,
    LiveSessionViewSet, MeetingParticipantViewSet, RecordingViewSet, WhiteboardViewSet,
    ChatMessageViewSet, PollViewSet, PollVoteViewSet, BreakoutRoomViewSet,
    CalendarEventViewSet, ReminderViewSet, MeetingAnalyticsViewSet
)

router = DefaultRouter()
router.register("programs", ProgramViewSet, basename="program")
router.register("subjects", SubjectViewSet, basename="subject")
router.register("course-structures", CourseStructureViewSet, basename="coursestructure")
router.register("courses", CourseViewSet, basename="course")
router.register("chapters", ChapterViewSet, basename="chapter")
router.register("topics", TopicViewSet, basename="topic")
router.register("subtopics", SubtopicViewSet, basename="subtopic")
router.register("lessons", LessonViewSet, basename="lesson")

router.register("learning-progress", LearningProgressViewSet, basename="learningprogress")
router.register("assignments", AssignmentViewSet, basename="assignment")
router.register("assignment-submissions", AssignmentSubmissionViewSet, basename="assignmentsubmission")
router.register("practice", PracticeViewSet, basename="practice")
router.register("practice-attempts", PracticeAttemptViewSet, basename="practiceattempt")
router.register("projects", ProjectViewSet, basename="project")
router.register("project-submissions", ProjectSubmissionViewSet, basename="projectsubmission")
router.register("exams", ExamViewSet, basename="exam")
router.register("exam-attempts", ExamAttemptViewSet, basename="examattempt")
router.register("question-banks", QuestionBankViewSet, basename="questionbank")
router.register("exam-questions", ExamQuestionViewSet, basename="examquestion")
router.register("certificates", CertificateViewSet, basename="certificate")
router.register("badges", BadgeViewSet, basename="badge")
router.register("user-badges", UserBadgeViewSet, basename="userbadge")
router.register("teacher-applications", TeacherApplicationViewSet, basename="teacherapplication")
router.register("teacher-classes", TeacherClassViewSet, basename="teacherclass")
router.register("student-enrollments", StudentEnrollmentViewSet, basename="studentenrollment")
router.register("live-classes", LiveClassViewSet, basename="liveclass")
router.register("live-sessions", LiveSessionViewSet, basename="livesession")
router.register("meeting-participants", MeetingParticipantViewSet, basename="meetingparticipant")
router.register("recordings", RecordingViewSet, basename="recording")
router.register("whiteboards", WhiteboardViewSet, basename="whiteboard")
router.register("chat-messages", ChatMessageViewSet, basename="chatmessage")
router.register("polls", PollViewSet, basename="poll")
router.register("poll-votes", PollVoteViewSet, basename="pollvote")
router.register("breakout-rooms", BreakoutRoomViewSet, basename="breakoutroom")
router.register("calendar-events", CalendarEventViewSet, basename="calendarevent")
router.register("reminders", ReminderViewSet, basename="reminder")
router.register("meeting-analytics", MeetingAnalyticsViewSet, basename="meetinganalytics")

app_name = "lms"

urlpatterns = [
    path("students/me/enrollments/", StudentMeEnrollmentsView.as_view(), name="student-me-enrollments"),
    path("students/me/progress/", StudentMeProgressView.as_view(), name="student-me-progress"),
    path("students/me/certificates/", StudentMeCertificatesView.as_view(), name="student-me-certificates"),
    path("students/me/badges/", StudentMeBadgesView.as_view(), name="student-me-badges"),
    path("", include(router.urls)),
]
