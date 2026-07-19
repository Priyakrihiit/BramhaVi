# Student Dashboard Architecture — Sprint 20 Phase 1
## BrahmaVidya Galaxy — Complete Design Specification

**Date:** 2026-07-12  
**Sprint:** 20 — Student Portal & Learning Dashboard  
**Status:** ✅ Phase 1 Complete — Awaiting Approval

---

## 1. Overview

The Student Dashboard is a **dedicated, full-screen learning hub** mounted at `/student` in the React application. It provides a unified view of a student's learning journey, progress, goals, achievements, notes, bookmarks, and upcoming events — all integrated with the existing LMS, Notifications, Analytics, Wallet, Search, CMS, AI, and Media modules.

### Design Philosophy
- **Mobile-first responsive** — works across 320px to 4K
- **Dark mode native** — respects system + manual toggle from themeStore
- **Data-driven widgets** — all cards pull from live `/api/v1/student/` APIs
- **Zero dependency on EnhancedDashboardView** — completely independent component tree
- **Backward compatible** — `/dashboard` still works as before

---

## 2. Route & Entry Point

```
New route added to App.tsx:
/student  →  <StudentDashboard currentUser={currentUser} />

Existing unchanged:
/dashboard → <EnhancedDashboardView currentUser={currentUser} onRefreshWallet={...} />
```

**Navigation link added** to `PortalLayout.tsx` sidebar: `My Learning` → `/student`

---

## 3. Top-Level Component Architecture

```
StudentDashboard.tsx           ← Root component (layout orchestrator)
├── StudentTopNav.tsx           ← Top navigation bar
├── StudentSidebar.tsx          ← Collapsible left sidebar
└── StudentMainContent.tsx      ← Dynamic content area
    ├── DashboardHome.tsx        ← Default landing view (widgets grid)
    ├── ContinueLearning.tsx     ← Resume last lesson cards
    ├── LearningProgress.tsx     ← Progress charts per course
    ├── Bookmarks.tsx            ← Saved content bookmarks
    ├── Notes.tsx                ← In-lesson notes manager
    ├── Downloads.tsx            ← Offline content / resources
    ├── Calendar.tsx             ← Study calendar & events
    ├── Achievements.tsx         ← Badges + achievements gallery
    ├── StudyGoals.tsx           ← Goal setting & tracking
    ├── RecentActivity.tsx       ← Activity feed
    ├── LearningHistory.tsx      ← Full lesson visit history
    ├── Recommendations.tsx      ← AI-powered recommendations
    └── StudentSettings.tsx      ← Dashboard preferences

Shared sub-directories:
├── Widgets/
│   ├── StreakWidget.tsx
│   ├── WalletWidget.tsx
│   ├── NotificationWidget.tsx
│   ├── QuickActionsWidget.tsx
│   ├── UpcomingExamsWidget.tsx
│   ├── AssignmentsWidget.tsx
│   ├── LiveClassWidget.tsx
│   └── StudyTimeWidget.tsx
├── Charts/
│   ├── ProgressRadialChart.tsx
│   ├── WeeklyActivityChart.tsx
│   ├── SubjectBreakdownChart.tsx
│   └── StreakCalendarHeatmap.tsx
├── Cards/
│   ├── CourseCard.tsx
│   ├── LessonCard.tsx
│   ├── AchievementCard.tsx
│   ├── GoalCard.tsx
│   ├── BookmarkCard.tsx
│   └── NoteCard.tsx
└── Services/
    └── studentApi.ts           ← All /api/v1/student/ calls
```

---

## 4. Dashboard Layout Specification

### 4.1 Overall Layout Grid

```
┌────────────────────────────────────────────────────────────┐
│  StudentTopNav                                              │
│  [Logo] [Search] [Streak 🔥] [Wallet] [Notifications] [👤] │
├──────────────┬─────────────────────────────────────────────┤
│              │                                             │
│  Sidebar     │   MainContent Area                          │
│  (240px)     │   (fluid, max 1400px centered)              │
│              │                                             │
│  • Home      │   ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  • Learning  │   │ Continue │ │ Progress │ │ Streak   │  │
│  • Progress  │   │ Learning │ │ This Week│ │ 🔥 14d   │  │
│  • Calendar  │   └──────────┘ └──────────┘ └──────────┘  │
│  • Goals     │                                             │
│  • Bookmarks │   ┌─────────────────────┐ ┌────────────┐  │
│  • Notes     │   │ Weekly Activity     │ │ Upcoming   │  │
│  • Achievements│  │ [Bar Chart]         │ │ Exams      │  │
│  • History   │   └─────────────────────┘ └────────────┘  │
│  • Downloads │                                             │
│  • Recs      │   ┌─────────────────────────────────────┐  │
│  • Settings  │   │ Continue Learning (Course Cards)    │  │
│              │   └─────────────────────────────────────┘  │
│  [Vidya AI]  │                                             │
│              │   ┌──────────────┐ ┌──────────────────────┐│
│              │   │ Assignments  │ │ Recommendations      ││
│              │   │ Due Soon     │ │ (AI-powered)         ││
│              │   └──────────────┘ └──────────────────────┘│
└──────────────┴─────────────────────────────────────────────┘
```

### 4.2 Responsive Breakpoints

| Breakpoint | Layout |
|---|---|
| `< 640px` (mobile) | Sidebar hidden, hamburger menu, single-column cards |
| `640–1024px` (tablet) | Sidebar as drawer overlay, 2-column cards |
| `1024–1280px` (laptop) | Collapsible sidebar (icons only), 2–3 column cards |
| `> 1280px` (desktop) | Full sidebar (240px), 3–4 column card grids |

---

## 5. StudentTopNav Specification

```tsx
<StudentTopNav>
  ├── Left: BrahmaVidya logo + "My Learning" breadcrumb
  ├── Center: GlobalSearchBar (calls /api/v1/search/)
  ├── Right group:
  │   ├── StreakBadge      (🔥 14 days — from /api/v1/student/streak/)
  │   ├── WalletBalance    (💎 1,240 VIDYA — from /api/v1/wallets/)
  │   ├── NotificationBell (unread count badge — from /api/v1/notifications/)
  │   ├── ThemeToggle      (☀️/🌙 — uses themeStore)
  │   └── AvatarMenu       (profile, settings, logout)
</StudentTopNav>
```

---

## 6. StudentSidebar Specification

```
LEARN
  📚  Home                /student
  ▶️  Continue Learning   /student/continue
  📊  My Progress         /student/progress
  📅  Calendar            /student/calendar
  🎯  Study Goals         /student/goals

CONTENT
  🔖  Bookmarks           /student/bookmarks
  📝  My Notes            /student/notes
  ⬇️  Downloads           /student/downloads
  📜  Learning History    /student/history

ACHIEVEMENTS
  🏆  Achievements        /student/achievements
  💡  Recommendations     /student/recommendations
  📈  Recent Activity     /student/activity

ACCOUNT
  ⚙️  Settings            /student/settings

──────────────────────
  🤖  Ask Vidya AI        (panel toggle)
```

**Sidebar behaviors:**
- Collapsible to icon-only mode (64px)
- Active item highlighted with accent gradient
- Tooltip on icon-only mode
- Mobile: Drawer overlay with backdrop

---

## 7. DashboardHome — Widget Grid

The home view renders a **responsive widget grid**:

### Row 1 — Stat Cards (4-column)
```
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ 🔥 Streak   │ │ 📚 Courses  │ │ ✅ Completed│ │ ⏱ Study    │
│  14 days    │ │  6 enrolled │ │  2 courses  │ │  42h total  │
│ +2 this wk  │ │  3 active   │ │  🎓 Cert    │ │  3.2h today │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
```

### Row 2 — Charts (2/3 + 1/3 split)
```
┌──────────────────────────────┐  ┌──────────────────┐
│  Weekly Activity Chart       │  │  Upcoming Exams  │
│  [7-day bar: study hours]    │  │  • Physics T3    │
│  Mon Tue Wed Thu Fri Sat Sun │  │    in 2 days     │
│   2h  3h  0h  4h  1h  5h  2h│  │  • Math Finals   │
└──────────────────────────────┘  │    in 5 days     │
                                  └──────────────────┘
```

### Row 3 — Continue Learning (horizontal scroll)
```
[▶ Course Card 1] [▶ Course Card 2] [▶ Course Card 3] [+ View All →]
Each card shows: thumbnail, course name, chapter, lesson, progress bar, Resume button
```

### Row 4 — Two-column
```
┌─────────────────────┐  ┌──────────────────────────────┐
│  Assignments Due    │  │  AI Recommendations          │
│  • Physics Lab      │  │  Based on your progress in   │
│    Due: Tomorrow    │  │  "Data Structures"           │
│  • React Project    │  │  → Advanced Algorithms       │
│    Due: 3 days      │  │  → System Design             │
└─────────────────────┘  └──────────────────────────────┘
```

### Row 5 — Recent Activity feed
```
[🔖 Bookmarked] "Django ORM Deep Dive"              2m ago
[✅ Completed]  Lesson: "React Hooks Advanced"      1h ago
[📝 Note added] "Remember: useCallback memoizes..." 3h ago
[🏆 Badge]      Earned "Week Warrior" badge         Yesterday
```

---

## 8. ContinueLearning Page

**Purpose:** Shows all in-progress enrollments with last-accessed lesson.

```tsx
<ContinueLearning>
  ├── FilterBar: [All] [In Progress] [Not Started] [Completed]
  ├── SortBar:   [Last Accessed] [Progress] [Alphabetical]
  └── CourseGrid:
      └── CourseCard (per enrollment):
          ├── Thumbnail + Overlay Play button
          ├── Course title + Subject badge
          ├── Progress bar (e.g., 68% complete)
          ├── Last lesson: "Chapter 3 → Topic 2 → Lesson 5"
          ├── Time spent: "12.5 hours"
          └── [Resume →] button (navigates to lesson)
```

**API:** `GET /api/v1/student/continue-learning/`

---

## 9. LearningProgress Page

**Purpose:** Detailed progress analytics per course.

```tsx
<LearningProgress>
  ├── CourseSelector dropdown
  ├── ProgressRadialChart  (overall completion %)
  ├── ChapterProgressList:
  │   └── Per chapter: title, lessons completed / total, progress bar
  ├── SubjectBreakdownChart (radar chart: subjects vs completion)
  ├── TimeSpentSection:
  │   ├── DailyProgress bars (last 30 days)
  │   └── WeeklyProgress trend line
  └── MilestonesSection:
      ├── Certificates earned
      └── Badges unlocked per course
```

**APIs:** 
- `GET /api/v1/student/progress/`
- `GET /api/v1/student/daily-progress/`
- `GET /api/v1/student/weekly-progress/`

---

## 10. Calendar Page

**Purpose:** Unified study calendar with events, exams, live classes, reminders.

```tsx
<Calendar>
  ├── MonthView / WeekView / DayView toggle
  ├── EventTypes:
  │   ├── 🔴 Exams          (from LMS ExamAttempt scheduled_at)
  │   ├── 🟡 Assignments Due (from Assignment deadline)
  │   ├── 🟢 Live Classes    (from LiveClass scheduled_at)
  │   ├── 🔵 Study Goals     (from StudyGoal target_date)
  │   └── 🟣 Reminders       (from LearningReminder remind_at)
  ├── EventDetailModal on click
  ├── AddReminderButton → POST /api/v1/student/reminders/
  └── StreakCalendarHeatmap (bottom: past 3 months activity grid)
```

**APIs:**
- `GET /api/v1/student/calendar/`
- `POST /api/v1/student/reminders/`

---

## 11. StudyGoals Page

**Purpose:** Personal study goal setting and progress tracking.

```tsx
<StudyGoals>
  ├── ActiveGoals:
  │   └── GoalCard:
  │       ├── Title ("Complete React Course")
  │       ├── Target date + countdown
  │       ├── Progress bar (lessons done / target)
  │       ├── Daily target hours
  │       └── [Mark Complete] [Edit] [Delete]
  ├── AddGoalForm:
  │   ├── Goal title
  │   ├── Target course (dropdown from enrollments)
  │   ├── Target date picker
  │   ├── Daily study hours target
  │   └── [Create Goal]
  └── CompletedGoals (collapsed accordion)
```

**APIs:**
- `GET /api/v1/student/goals/`
- `POST /api/v1/student/goals/`
- `PATCH /api/v1/student/goals/{id}/`
- `DELETE /api/v1/student/goals/{id}/`

---

## 12. Bookmarks Page

**Purpose:** Saved lessons, articles, and content.

```tsx
<Bookmarks>
  ├── FilterTabs: [All] [Lessons] [Articles] [Tutorials]
  ├── SearchBar (client-side filter)
  └── BookmarkGrid:
      └── BookmarkCard:
          ├── Content type icon + title
          ├── Source (course name / CMS section)
          ├── Date bookmarked
          ├── Notes snippet (if attached)
          └── [Open] [Remove bookmark]
```

**APIs:**
- `GET /api/v1/student/bookmarks/`
- `POST /api/v1/student/bookmarks/`
- `DELETE /api/v1/student/bookmarks/{id}/`

---

## 13. Notes Page

**Purpose:** In-lesson notes manager.

```tsx
<Notes>
  ├── NotesList (left panel):
  │   ├── SearchNotes
  │   ├── FilterByLesson
  │   └── NoteCard per note (title, lesson, date, preview)
  └── NoteEditor (right panel):
      ├── Textarea with markdown support
      ├── Linked lesson reference
      ├── Tags input
      └── [Save] [Delete]
```

**APIs:**
- `GET /api/v1/student/notes/`
- `POST /api/v1/student/notes/`
- `PATCH /api/v1/student/notes/{id}/`
- `DELETE /api/v1/student/notes/{id}/`

---

## 14. Achievements Page

**Purpose:** Badges and extended achievements gallery.

```tsx
<Achievements>
  ├── AchievementStats:
  │   ├── Total badges: 12
  │   ├── Total achievements: 8
  │   └── XP points: 4,200
  ├── BadgeGallery (from UserBadge):
  │   └── BadgeCard: icon, title, description, earned date
  ├── AchievementList (from Achievement model):
  │   └── AchievementCard: title, progress (if in-progress), reward
  └── LeaderboardSnippet (top 5 peers by XP — optional)
```

**APIs:**
- `GET /api/v1/student/achievements/`
- `GET /api/v1/lms/user-badges/` (existing)

---

## 15. Recommendations Page

**Purpose:** AI-powered content recommendations.

```tsx
<Recommendations>
  ├── SectionHeader: "Based on your learning history"
  ├── RecommendationGrid:
  │   └── CourseCard (recommended courses not yet enrolled)
  ├── SectionHeader: "Trending in your subjects"
  ├── TrendingContent (CMS articles/tutorials)
  └── SectionHeader: "Complete your learning path"
      └── NextLessonCards (suggested next steps in enrolled courses)
```

**API:** `GET /api/v1/student/recommendations/`

---

## 16. LearningHistory Page

**Purpose:** Auditable log of all lesson visits.

```tsx
<LearningHistory>
  ├── DateRangeFilter (last 7d / 30d / 90d / custom)
  ├── CourseFilter dropdown
  ├── HistoryTable:
  │   └── Row: date, lesson title, course, time spent, completion status
  ├── ExportButton (CSV download)
  └── PaginatedList (50 per page)
```

**API:** `GET /api/v1/student/history/`

---

## 17. RecentActivity Feed

**Purpose:** Unified activity stream (last 50 events).

```tsx
<RecentActivity>
  └── ActivityFeed:
      └── ActivityItem:
          ├── Icon (by event type)
          ├── Description ("Completed lesson: React Hooks")
          ├── Timestamp (relative: "2 hours ago")
          └── Link to content
```

Event types:
- `lesson_completed` → ✅
- `lesson_started` → ▶️
- `bookmark_added` → 🔖
- `note_created` → 📝
- `badge_earned` → 🏆
- `exam_attempted` → 📋
- `goal_created` → 🎯
- `streak_milestone` → 🔥

**API:** `GET /api/v1/student/activity/`

---

## 18. StudentSettings Page

**Purpose:** Dashboard preferences and notification settings.

```tsx
<StudentSettings>
  ├── DisplaySection:
  │   ├── Theme toggle (dark/light)
  │   ├── Sidebar default state (expanded/collapsed)
  │   └── Dashboard layout (compact/comfortable)
  ├── NotificationSection:
  │   ├── Email notifications toggle per category
  │   ├── Push notification toggles
  │   └── Study reminder time preferences
  ├── PrivacySection:
  │   ├── Show profile to peers
  │   └── Show activity on leaderboard
  └── StudySection:
      ├── Daily study goal (hours)
      ├── Weekly study goal (hours)
      └── Preferred study time (morning/afternoon/evening)
```

**APIs:**
- `GET/PATCH /api/v1/student/preferences/`
- `GET/PATCH /api/v1/notifications/preferences/`

---

## 19. Widget Specifications

### StreakWidget
```
🔥 14-Day Streak
▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░  14/30 days
Best: 21 days
API: GET /api/v1/student/streak/
```

### WalletWidget
```
💎 VIDYA Points
1,240 tokens
+50 today (lesson completion bonus)
API: GET /api/v1/wallets/wallets/me/
```

### UpcomingExamsWidget
```
📋 Upcoming Exams
• Physics Midterm  — in 2 days
• Math Finals      — in 5 days
• CS Project       — in 12 days
API: GET /api/v1/student/upcoming-exams/
```

### AssignmentsWidget
```
📌 Assignments Due
• Lab Report       — Tomorrow    [Submit]
• React Project    — 3 days      [View]
• Essay Draft      — 1 week      [View]
API: GET /api/v1/student/assignments/
```

### StudyTimeWidget
```
⏱ Study Time Today
3.2 hours
━━━━━━━━░░  80% of daily goal (4h)
This week: 14.5 hours
API: GET /api/v1/student/stats/
```

### QuickActionsWidget
```
⚡ Quick Actions
[▶ Resume Learning] [📅 Add Reminder]
[🎯 Set Goal]       [🔍 Search Content]
```

### LiveClassWidget
```
📺 Next Live Class
"Advanced Django" with Prof. Sharma
Tomorrow at 10:00 AM
[Join Stream →]
API: GET /api/v1/student/live-classes/
```

---

## 20. Charts Specification

### ProgressRadialChart
- Library: inline SVG with animated stroke-dasharray
- Shows: course completion % as radial arc
- Colors: gradient from `indigo-500` to `purple-600`

### WeeklyActivityChart
- Type: Bar chart (7 columns, one per weekday)
- Y-axis: hours studied
- Color: bars filled proportionally, today highlighted
- Data: from `DailyProgress` model

### SubjectBreakdownChart
- Type: Radar/Spider chart
- Axes: each enrolled subject
- Shows: completion % per subject
- Uses: inline SVG polygon

### StreakCalendarHeatmap
- Type: GitHub-style contribution grid
- Last 90 days, colored by study intensity
- Green shades: 0/light/medium/intense

---

## 21. Loading States & Skeletons

Every data-fetching component renders a skeleton while loading:

```tsx
// Example skeleton pattern
if (loading) return <SkeletonLoader rows={3} height="120px" />;

// Skeleton visual:
┌──────────────────────────────────┐
│ ████████████████░░░░░░░░░░░░░░░░ │ ← animated shimmer
│ ████████░░░░░░░░░░░░░░░░░░░░░░░░ │
│ ████████████░░░░░░░░░░░░░░░░░░░░ │
└──────────────────────────────────┘
```

---

## 22. Error Boundaries & Empty States

### Error Boundary (per section)
```tsx
<StudentErrorBoundary fallback={<ErrorCard message="Failed to load..." onRetry={refetch} />}>
  <ContinueLearning />
</StudentErrorBoundary>
```

### Empty States
Each section handles the zero-data case gracefully:

```
📚 Continue Learning (empty):
  "You haven't enrolled in any courses yet."
  [Browse Courses →]

🔖 Bookmarks (empty):
  "Save lessons and articles to find them quickly."
  [Explore Content →]

🎯 Goals (empty):
  "Set a study goal to stay on track."
  [Create First Goal →]
```

---

## 23. Dark Mode Implementation

Using existing `themeStore`:
```tsx
const { theme } = useThemeStore();
const isDark = theme === 'dark';

// CSS classes conditionally applied:
className={`${isDark ? 'bg-gray-900 text-white' : 'bg-gray-50 text-gray-900'}`}
```

Color palette:
| Token | Light | Dark |
|---|---|---|
| Background | `bg-gray-50` | `bg-gray-950` |
| Card | `bg-white` | `bg-gray-900` |
| Sidebar | `bg-white border-r` | `bg-gray-900 border-gray-800` |
| Accent | `indigo-600` | `indigo-400` |
| Text primary | `gray-900` | `gray-50` |
| Text secondary | `gray-500` | `gray-400` |
| Border | `gray-200` | `gray-800` |

---

## 24. Student API Service (`studentApi.ts`)

New dedicated service file:

```typescript
// src/services/studentApi.ts
export const studentApi = {
  dashboard:       () => GET('/api/v1/student/dashboard/'),
  stats:           () => GET('/api/v1/student/stats/'),
  continueLearning:() => GET('/api/v1/student/continue-learning/'),
  history:         (params?) => GET('/api/v1/student/history/', params),
  bookmarks:       () => GET('/api/v1/student/bookmarks/'),
  addBookmark:     (data) => POST('/api/v1/student/bookmarks/', data),
  removeBookmark:  (id) => DELETE(`/api/v1/student/bookmarks/${id}/`),
  notes:           () => GET('/api/v1/student/notes/'),
  createNote:      (data) => POST('/api/v1/student/notes/', data),
  updateNote:      (id, data) => PATCH(`/api/v1/student/notes/${id}/`, data),
  deleteNote:      (id) => DELETE(`/api/v1/student/notes/${id}/`),
  goals:           () => GET('/api/v1/student/goals/'),
  createGoal:      (data) => POST('/api/v1/student/goals/', data),
  updateGoal:      (id, data) => PATCH(`/api/v1/student/goals/${id}/`, data),
  calendar:        (month, year) => GET('/api/v1/student/calendar/', {month, year}),
  reminders:       () => GET('/api/v1/student/reminders/'),
  createReminder:  (data) => POST('/api/v1/student/reminders/', data),
  achievements:    () => GET('/api/v1/student/achievements/'),
  progress:        (courseId?) => GET('/api/v1/student/progress/', {courseId}),
  dailyProgress:   () => GET('/api/v1/student/daily-progress/'),
  weeklyProgress:  () => GET('/api/v1/student/weekly-progress/'),
  recommendations: () => GET('/api/v1/student/recommendations/'),
  activity:        () => GET('/api/v1/student/activity/'),
  streak:          () => GET('/api/v1/student/streak/'),
  preferences:     () => GET('/api/v1/student/preferences/'),
  updatePreferences:(data) => PATCH('/api/v1/student/preferences/', data),
  upcomingExams:   () => GET('/api/v1/student/upcoming-exams/'),
  assignments:     () => GET('/api/v1/student/assignments/'),
  studySessions:   () => GET('/api/v1/student/study-sessions/'),
  startSession:    (data) => POST('/api/v1/student/study-sessions/', data),
  endSession:      (id, data) => PATCH(`/api/v1/student/study-sessions/${id}/`, data),
};
```

---

## 25. State Management Strategy

Using React Context (consistent with existing stores):

```tsx
// New: StudentDashboardContext
interface StudentDashboardState {
  activeSection: string;
  sidebarCollapsed: boolean;
  dashboardData: DashboardData | null;
  loading: boolean;
  error: string | null;
}

// Sections enum
type StudentSection = 
  | 'home' | 'continue' | 'progress' | 'calendar'
  | 'goals' | 'bookmarks' | 'notes' | 'downloads'
  | 'achievements' | 'history' | 'activity' 
  | 'recommendations' | 'settings';
```

---

## 26. TypeScript Types (additions to `types.ts`)

```typescript
// New types to add to src/types.ts
export interface StudentDashboardData {
  stats: StudentStats;
  continueLearning: ContinueLearningItem[];
  upcomingExams: UpcomingExam[];
  assignments: StudentAssignment[];
  recentActivity: ActivityItem[];
  recommendations: RecommendedCourse[];
  streak: LearningStreak;
}

export interface StudentStats {
  enrolledCourses: number;
  completedCourses: number;
  totalStudyHours: number;
  todayStudyHours: number;
  streakDays: number;
  badgesEarned: number;
  xpPoints: number;
}

export interface ContinueLearningItem {
  enrollmentId: string;
  courseId: string;
  courseTitle: string;
  courseThumbnail?: string;
  lastLessonId: string;
  lastLessonTitle: string;
  progressPercentage: number;
  lastAccessedAt: string;
}

export interface LearningStreak {
  currentStreak: number;
  longestStreak: number;
  lastStudiedAt: string;
  activeDays: string[];  // ISO date strings
}

export interface StudentBookmark {
  id: string;
  contentType: 'lesson' | 'article' | 'tutorial' | 'video';
  contentId: string;
  title: string;
  sourceName: string;
  note?: string;
  createdAt: string;
}

export interface StudentNote {
  id: string;
  lessonId: string;
  lessonTitle: string;
  courseTitle: string;
  content: string;
  tags: string[];
  createdAt: string;
  updatedAt: string;
}

export interface StudyGoal {
  id: string;
  title: string;
  courseId?: string;
  courseTitle?: string;
  targetDate: string;
  dailyTargetHours: number;
  status: 'ACTIVE' | 'COMPLETED' | 'ABANDONED';
  progressPercentage: number;
}

export interface ActivityItem {
  id: string;
  eventType: string;
  description: string;
  metadata: Record<string, any>;
  createdAt: string;
}
```

---

## 27. Backend Django App Structure (`apps/student/`)

```
backend/apps/student/
├── __init__.py
├── apps.py
├── models.py           ← 15 new models (see Phase 2)
├── serializers.py      ← DRF serializers for all models
├── views.py            ← ViewSets for all student endpoints
├── urls.py             ← /api/v1/student/ router
├── permissions.py      ← IsStudentUser permission class
├── services.py         ← Business logic (recommendation engine, etc.)
├── selectors.py        ← Complex ORM queries
├── validators.py       ← Input validation
├── filters.py          ← Django-filter FilterSets
├── signals.py          ← Cross-app signal handlers
├── tasks.py            ← Celery async tasks (streak update, reminders)
└── migrations/
    └── 0001_initial.py
```

---

## 28. Security Architecture

| Layer | Implementation |
|---|---|
| Authentication | JWT `Bearer` token via `IsAuthenticated` |
| Student check | Custom `IsStudentOrAdmin` permission class |
| Object ownership | All queries filtered by `student=request.user` |
| Rate limiting | Gateway Redis rate limiter (existing) |
| CBAC check | `user.is_student_cbac` on sensitive endpoints |
| Data isolation | No cross-student data exposure possible |

---

## 29. Performance Strategy

| Feature | Strategy |
|---|---|
| Dashboard stats | Cached 5 min in Redis/cache framework |
| Activity feed | Paginated (20 items), cursor-based |
| Recommendations | Computed async via Celery task daily |
| Charts data | Aggregated and cached at midnight |
| Skeleton loading | Immediate UI response, data streams in |
| Images | Lazy loading with `loading="lazy"` |

---

## 30. File Creation Plan Summary

### New Backend Files
```
backend/apps/student/__init__.py
backend/apps/student/apps.py
backend/apps/student/models.py
backend/apps/student/serializers.py
backend/apps/student/views.py
backend/apps/student/urls.py
backend/apps/student/permissions.py
backend/apps/student/services.py
backend/apps/student/selectors.py
backend/apps/student/validators.py
backend/apps/student/filters.py
backend/apps/student/signals.py
backend/apps/student/tasks.py
backend/apps/student/migrations/0001_initial.py
```

### Modified Backend Files (minimal edits only)
```
backend/django_project/settings.py   ← Add "apps.student.apps.StudentConfig"
backend/django_project/urls.py       ← Add path("student/", include(...))
```

### New Frontend Files
```
src/pages/student/StudentDashboard.tsx
src/pages/student/DashboardHome.tsx
src/pages/student/ContinueLearning.tsx
src/pages/student/LearningProgress.tsx
src/pages/student/Bookmarks.tsx
src/pages/student/Notes.tsx
src/pages/student/Downloads.tsx
src/pages/student/Calendar.tsx
src/pages/student/Achievements.tsx
src/pages/student/StudyGoals.tsx
src/pages/student/RecentActivity.tsx
src/pages/student/LearningHistory.tsx
src/pages/student/Recommendations.tsx
src/pages/student/StudentSettings.tsx
src/pages/student/Widgets/StreakWidget.tsx
src/pages/student/Widgets/WalletWidget.tsx
src/pages/student/Widgets/NotificationWidget.tsx
src/pages/student/Widgets/QuickActionsWidget.tsx
src/pages/student/Widgets/UpcomingExamsWidget.tsx
src/pages/student/Widgets/AssignmentsWidget.tsx
src/pages/student/Widgets/LiveClassWidget.tsx
src/pages/student/Widgets/StudyTimeWidget.tsx
src/pages/student/Charts/ProgressRadialChart.tsx
src/pages/student/Charts/WeeklyActivityChart.tsx
src/pages/student/Charts/SubjectBreakdownChart.tsx
src/pages/student/Charts/StreakCalendarHeatmap.tsx
src/pages/student/Cards/CourseCard.tsx
src/pages/student/Cards/LessonCard.tsx
src/pages/student/Cards/AchievementCard.tsx
src/pages/student/Cards/GoalCard.tsx
src/pages/student/Cards/BookmarkCard.tsx
src/pages/student/Cards/NoteCard.tsx
src/services/studentApi.ts
```

### Modified Frontend Files (minimal edits only)
```
src/App.tsx              ← Add /student route
src/layouts/PortalLayout.tsx  ← Add "My Learning" nav link
src/types.ts             ← Add student-related type definitions
```

### Modified Gateway
```
server.ts  ← Add /api/v1/student/* proxy entries in PATH_MAP
```

---

**Phase 1 — COMPLETE.**  
**Awaiting approval to proceed to Phase 2 (Database Extension).**
