/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import * as fs from 'fs';
import * as path from 'path';
import { DatabaseState, User, Role, Permission, NavigationMenu, Page, CourseStructure, Certificate, SystemSettings, Blog, Tutorial, Book, BookReview, PublishSubmission, RoyaltyStatement, WithdrawalRequest, Product, Order, ServiceRequest, Quotation, Transaction, Invoice } from './types';

const DB_FILE = path.join(process.cwd(), 'brahmavidya_db.json');

const DEFAULT_PERMISSIONS: Permission[] = [
  { code: 'SUPER_ADMIN', description: 'Full administrative override of all platform controls.' },
  { code: 'MENU_READ', description: 'View system navigation menus.' },
  { code: 'MENU_WRITE', description: 'Add, modify, delete system menus and order configurations.' },
  { code: 'PAGE_READ', description: 'View public website pages and structure.' },
  { code: 'PAGE_WRITE', description: 'Compose layouts, schedule releases, and edit SEO parameters.' },
  { code: 'COURSE_READ', description: 'Browse and view academic programs, courses, and curricula.' },
  { code: 'COURSE_WRITE', description: 'Design programs, construct course outline trees, and assign instructors.' },
  { code: 'CERT_READ', description: 'Verify academic credentials and digital certifications.' },
  { code: 'CERT_WRITE', description: 'Generate badges, issue micro-credentials, and adjust templates.' },
  { code: 'USER_READ', description: 'Observe accounts, verification registries, and track learning logs.' },
  { code: 'USER_WRITE', description: 'Verify instructors, suspend bad actors, and approve payouts.' },
  { code: 'AI_ACCESS', description: 'Execute Vidya AI queries, design curricula with Gemini, and map models.' }
];

const DEFAULT_ROLES: Role[] = [
  {
    id: 'role-super-admin',
    name: 'Super Admin',
    description: 'Autonomous control center supervisor with permission bypass privileges.',
    permissions: ['SUPER_ADMIN', 'MENU_READ', 'MENU_WRITE', 'PAGE_READ', 'PAGE_WRITE', 'COURSE_READ', 'COURSE_WRITE', 'CERT_READ', 'CERT_WRITE', 'USER_READ', 'USER_WRITE', 'AI_ACCESS']
  },
  {
    id: 'role-teacher',
    name: 'Teacher',
    description: 'Dynamic content proprietor with ownership of specific courses, structures, and analytics.',
    permissions: ['MENU_READ', 'PAGE_READ', 'COURSE_READ', 'COURSE_WRITE', 'CERT_READ', 'CERT_WRITE', 'USER_READ', 'AI_ACCESS']
  },
  {
    id: 'role-student',
    name: 'Student',
    description: 'Enrolled learner accessing interactive syllabus blocks, earning credentials, and utilizing Vidya AI.',
    permissions: ['MENU_READ', 'PAGE_READ', 'COURSE_READ', 'CERT_READ', 'AI_ACCESS']
  }
];

const DEFAULT_USERS: User[] = [
  {
    id: 'user-admin',
    email: 'admin@brahmavidya.edu',
    fullName: 'Super Admin',
    roleId: 'role-super-admin',
    status: 'ACTIVE',
    avatarUrl: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=150',
    walletBalance: 875420
  },
  {
    id: 'user-teacher',
    email: 'teacher@brahmavidya.edu',
    fullName: 'Dr. Ananya Iyer',
    roleId: 'role-teacher',
    status: 'ACTIVE',
    avatarUrl: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&q=80&w=150',
    walletBalance: 124500
  },
  {
    id: 'user-student',
    email: 'student@brahmavidya.edu',
    fullName: 'Rahul Sharma',
    roleId: 'role-student',
    status: 'ACTIVE',
    avatarUrl: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=150',
    walletBalance: 5000
  }
];

const DEFAULT_MENUS: NavigationMenu[] = [
  // Primary Navigation
  { id: 'menu-courses', parentId: null, title: 'Courses', url: '/courses', icon: 'BookOpen', displayOrder: 1, isActive: true, requiredPermission: null },
  { id: 'menu-bookstore', parentId: null, title: 'Bookstore', url: '/bookstore', icon: 'Book', displayOrder: 2, isActive: true, requiredPermission: null },
  { id: 'menu-marketplace', parentId: null, title: 'Marketplace', url: '/marketplace', icon: 'ShoppingCart', displayOrder: 3, isActive: true, requiredPermission: null },
  { id: 'menu-search', parentId: null, title: 'Search', url: '/search', icon: 'Search', displayOrder: 4, isActive: true, requiredPermission: null },
  { id: 'menu-saas', parentId: null, title: 'SaaS Hub', url: '/saas', icon: 'Layers', displayOrder: 4.5, isActive: true, requiredPermission: null },
  { id: 'menu-dashboard', parentId: null, title: 'Dashboard', url: '/dashboard', icon: 'LayoutDashboard', displayOrder: 5, isActive: true, requiredPermission: null },
  { id: 'menu-tutorials', parentId: null, title: 'Tutorials', url: '/tutorials', icon: 'Layers', displayOrder: 6, isActive: true, requiredPermission: null },
  { id: 'menu-practice', parentId: null, title: 'Practice', url: '/practice', icon: 'CheckSquare', displayOrder: 7, isActive: true, requiredPermission: null },
  { id: 'menu-projects', parentId: null, title: 'Projects', url: '/projects', icon: 'Code', displayOrder: 8, isActive: true, requiredPermission: null },
  { id: 'menu-certificates', parentId: null, title: 'Certificates', url: '/certificates', icon: 'Award', displayOrder: 9, isActive: true, requiredPermission: null },
  { id: 'menu-community', parentId: null, title: 'Community', url: '/community', icon: 'Users', displayOrder: 10, isActive: true, requiredPermission: null },
  { id: 'menu-vidya-ai', parentId: null, title: 'Vidya AI Guide', url: '/vidya-guide', icon: 'Bot', displayOrder: 11, isActive: true, requiredPermission: null },

  // Secondary submenus mapping exactly the exam buttons
  { id: 'sub-10th', parentId: 'menu-courses', title: '10th', url: '/exams/10th', icon: 'GraduationCap', displayOrder: 1, isActive: true, requiredPermission: null },
  { id: 'sub-12th', parentId: 'menu-courses', title: '12th', url: '/exams/12th', icon: 'GraduationCap', displayOrder: 2, isActive: true, requiredPermission: null },
  { id: 'sub-neet', parentId: 'menu-courses', title: 'NEET', url: '/exams/neet', icon: 'Activity', displayOrder: 3, isActive: true, requiredPermission: null },
  { id: 'sub-jee-main', parentId: 'menu-courses', title: 'JEE (Main)', url: '/exams/jee-main', icon: 'Zap', displayOrder: 4, isActive: true, requiredPermission: null },
  { id: 'sub-jee-adv', parentId: 'menu-courses', title: 'JEE (Advanced)', url: '/exams/jee-adv', icon: 'Cpu', displayOrder: 5, isActive: true, requiredPermission: null },
  { id: 'sub-iit', parentId: 'menu-courses', title: 'IIT', icon: 'Library', url: '/exams/iit', displayOrder: 6, isActive: true, requiredPermission: null },
  { id: 'sub-iim', parentId: 'menu-courses', title: 'IIM', icon: 'Briefcase', url: '/exams/iim', displayOrder: 7, isActive: true, requiredPermission: null },
  { id: 'sub-cat', parentId: 'menu-courses', title: 'CAT', icon: 'TrendingUp', url: '/exams/cat', displayOrder: 8, isActive: true, requiredPermission: null },
  { id: 'sub-net-jrf', parentId: 'menu-courses', title: 'NET JRF', icon: 'FileText', url: '/exams/net-jrf', displayOrder: 9, isActive: true, requiredPermission: null },
  { id: 'sub-upsc', parentId: 'menu-courses', title: 'UPSC', icon: 'Compass', url: '/exams/upsc', displayOrder: 10, isActive: true, requiredPermission: null },
  { id: 'sub-ssc', parentId: 'menu-courses', title: 'SSC', icon: 'Clipboard', url: '/exams/ssc', displayOrder: 11, isActive: true, requiredPermission: null },
  { id: 'sub-banking', parentId: 'menu-courses', title: 'Banking', icon: 'DollarSign', url: '/exams/banking', displayOrder: 12, isActive: true, requiredPermission: null },
  { id: 'sub-railways', parentId: 'menu-courses', title: 'Railways', icon: 'Train', url: '/exams/railways', displayOrder: 13, isActive: true, requiredPermission: null },
  { id: 'sub-state-exams', parentId: 'menu-courses', title: 'State Exams', icon: 'Map', url: '/exams/state-exams', displayOrder: 14, isActive: true, requiredPermission: null }
];

const DEFAULT_PAGES: Page[] = [
  {
    id: 'page-home',
    title: 'BrahmaVidya Galaxy Home',
    slug: 'home',
    seoTitle: 'One Platform. Unlimited Learning | BrahmaVidya Galaxy',
    seoDescription: 'Enterprise educational content-agnostic platform managing comprehensive, customized dynamic CMS/LMS systems with interactive Vidya AI and real-time ledger validations.',
    isPublished: true,
    publishedAt: '2025-06-05T00:00:00Z',
    layoutData: [
      {
        id: 'block-hero',
        type: 'hero',
        title: 'One Platform. Unlimited Learning.',
        subtitle: 'BrahmaVidya Galaxy is your complete digital university. Learn, Practice, Build, and Grow with AI-powered guidance.',
        styleSettings: { theme: 'dark', padding: 'py-20 px-8' }
      },
      {
        id: 'block-stats',
        type: 'stats',
        title: 'Platform Momentum',
        items: [
          { title: '5000+', description: 'Courses' },
          { title: '100K+', description: 'Tutorials' },
          { title: '2M+', description: 'Practice Questions' },
          { title: '50K+', description: 'Active Students' },
          { title: '25K+', description: 'Certificates Issued' },
          { title: '20+', description: 'Learning Categories' }
        ]
      },
      {
        id: 'block-popular',
        type: 'features',
        title: 'Popular Courses',
        subtitle: 'Access top-rated high-integrity dynamic syllabi',
        items: [
          { title: 'Python Programming', description: 'Beginner to Advanced • 4.8 Rating • 12,500 Learners', link: '/courses/python' },
          { title: 'Data Structures & Algorithms', description: 'Master logic structures • 4.9 Rating • 8,700 Learners', link: '/courses/dsa' },
          { title: 'Full Stack Web Development', description: 'Next.js, Node, and SQL databases • 4.7 Rating • 9,300 Learners', link: '/courses/fullstack' },
          { title: 'Machine Learning A-Z', description: 'Deep learning & neural architectures • 4.8 Rating • 6,400 Learners', link: '/courses/ml' }
        ]
      }
    ]
  }
];

const DEFAULT_COURSES: CourseStructure[] = [
  {
    id: 'course-python',
    parentId: null,
    type: 'COURSE',
    title: 'Python Programming',
    description: 'Full program covering fundamentals, OOP, database design, and web scrapers.',
    metadata: {
      duration: '40 Hours',
      difficulty: 'Beginner',
      price: 0,
      lessonsCount: 12,
      videoUrl: 'https://www.w3schools.com/html/mov_bbb.mp4',
      authorId: 'user-teacher'
    }
  },
  {
    id: 'course-dsa',
    parentId: null,
    type: 'COURSE',
    title: 'Data Structures & Algorithms',
    description: 'Comprehensive curriculum on arrays, linked lists, binary trees, recursion, and algorithm efficiency.',
    metadata: {
      duration: '60 Hours',
      difficulty: 'Intermediate',
      price: 0,
      lessonsCount: 20,
      authorId: 'user-teacher'
    }
  },
  {
    id: 'course-fullstack',
    parentId: null,
    type: 'COURSE',
    title: 'Full Stack Web Development',
    description: 'Construct end-to-end applications from database indexing to responsive dynamic clients.',
    metadata: {
      duration: '80 Hours',
      difficulty: 'Advanced',
      price: 0,
      lessonsCount: 35,
      authorId: 'user-teacher'
    }
  },
  {
    id: 'course-ml',
    parentId: null,
    type: 'COURSE',
    title: 'Machine Learning A-Z',
    description: 'A mathematical and programmatic exploration of regression, classification, clustering, and Deep Neural Networks.',
    metadata: {
      duration: '50 Hours',
      difficulty: 'Advanced',
      price: 0,
      lessonsCount: 15,
      authorId: 'user-teacher'
    }
  }
];

// Prepopulate hierarchical syllabus items for Python Programming
const PYTHON_SYLLABUS: CourseStructure[] = [
  {
    id: 'module-py-intro',
    parentId: 'course-python',
    type: 'MODULE',
    title: 'Module 1: Introduction and Environment Setup',
    description: 'Getting started with runtime environments and standard variable declarations.'
  },
  {
    id: 'lesson-py-variables',
    parentId: 'module-py-intro',
    type: 'LESSON',
    title: 'Lesson 1.1: Standard Variables and Dynamic Typings',
    description: 'Understand integers, floats, strings, and garbage collection mechanisms in Python.',
    metadata: {
      duration: '25 Mins',
      videoUrl: 'https://www.w3schools.com/html/mov_bbb.mp4'
    }
  },
  {
    id: 'task-py-write-calc',
    parentId: 'lesson-py-variables',
    type: 'TASK',
    title: 'Exercise: Build a dynamic CLI arithmetic compiler',
    description: 'Create a console script that parses inputs and executes operations.'
  }
];

const DEFAULT_CERTIFICATES: Certificate[] = [
  {
    id: 'cert-python-rahul',
    recipientId: 'user-student',
    courseId: 'course-python',
    recipientName: 'Rahul Sharma',
    courseTitle: 'Python Programming',
    certificateHash: 'ea0f885f8c85350c37bb1a1820b22a013f9f9dcd87239cc841203582ba93d7cb',
    qrCodeUrl: '/verify/ea0f885f8c85350c37bb1a1820b22a013f9f9dcd87239cc841203582ba93d7cb',
    issuedAt: '2025-06-01T15:30:00Z',
    metadata: { grade: 'A+', accreditationCode: 'BVG-2025-0199' }
  }
];

const DEFAULT_BLOGS: Blog[] = [
  {
    id: 'blog-1',
    title: 'Introducing BrahmaVidya: The Future of Modular Learning Platforms',
    slug: 'introducing-brahmavidya',
    content: 'BrahmaVidya is an enterprise educational platform built to facilitate custom curriculum design, secure blockchain ledger certificate issuing, and state-of-the-art AI-powered tutoring helpers.',
    authorId: 'user-admin',
    authorEmail: 'admin@brahmavidya.edu',
    isPublished: true,
    publishedAt: '2025-06-01T12:00:00Z',
    isDeleted: false
  },
  {
    id: 'blog-2',
    title: 'The Role of AI Guidelines in Constructive Modern Classrooms',
    slug: 'ai-guidelines-modern-classrooms',
    content: 'Integrate artificial intelligence guides to serve as interactive teachers assistants, aiding curriculum mapping, quiz generation, and fast content synthesis while keeping human mentors at the core.',
    authorId: 'user-teacher',
    authorEmail: 'teacher@brahmavidya.edu',
    isPublished: false,
    isDeleted: false
  }
];

const DEFAULT_TUTORIALS: Tutorial[] = [
  {
    id: 'tutorial-1',
    title: 'Getting Started with Markdown Formats on BrahmaVidya CMS',
    slug: 'getting-started-markdown',
    content: '# Markdown Essentials\nLearn how to use **bolding**, *italics*, `code lines`, and lists in our CMS page builder.',
    authorId: 'user-admin',
    authorEmail: 'admin@brahmavidya.edu',
    isPublished: true,
    publishedAt: '2025-06-02T10:00:00Z',
    isDeleted: false
  }
];

const DEFAULT_SETTINGS: SystemSettings = {
  platformName: 'BrahmaVidya Galaxy',
  platformDescription: 'Enterprise educational content-agnostic CMS/LMS with real-time Control Center audits.',
  logoText: 'BrahmaVidya',
  accentColor: '#4f46e5',
  activeAIProvider: 'gemini',
  commissionRate: 15
};

const DEFAULT_BOOKS: Book[] = [
  {
    id: 'book-1',
    title: 'Mastering Full-Stack Django Architecture',
    authorId: 'user-teacher',
    authorName: 'Dr. Ananya Iyer',
    category: 'Engineering',
    tags: ['Django', 'Python', 'Architecture'],
    description: 'An enterprise-grade deep dive into modular Django structures, celery pipelines, and high-performance Postgres optimizations.',
    price: 399,
    coverUrl: 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&q=80&w=300',
    fileFormat: 'PDF',
    fileUrl: '/api/downloads/book-1',
    rating: 4.8,
    reviewsCount: 12,
    bookmarksCount: 45,
    isPublished: true,
    createdAt: '2025-06-10T12:00:00Z'
  },
  {
    id: 'book-2',
    title: 'Vidya AI Guide: Course Syllabus Architectures',
    authorId: 'user-admin',
    authorName: 'Super Admin',
    category: 'Artificial Intelligence',
    tags: ['AI', 'LMS', 'Gemini'],
    description: 'How to use Google Gemini models to automatically generate high-integrity, content-agnostic syllabi for any exam program.',
    price: 199,
    coverUrl: 'https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&q=80&w=300',
    fileFormat: 'EPUB',
    fileUrl: '/api/downloads/book-2',
    rating: 4.9,
    reviewsCount: 8,
    bookmarksCount: 22,
    isPublished: true,
    createdAt: '2025-06-12T15:30:00Z'
  }
];

const DEFAULT_BOOK_REVIEWS: BookReview[] = [
  {
    id: 'rev-1',
    bookId: 'book-1',
    userId: 'user-student',
    userName: 'Rahul Sharma',
    rating: 5,
    comment: 'Incredible book! The chapters on connection pooling and index structures saved me days of troubleshooting.',
    createdAt: '2025-06-11T10:20:00Z'
  }
];

const DEFAULT_SUBMISSIONS: PublishSubmission[] = [
  {
    id: 'subm-1',
    userId: 'user-student',
    userName: 'Rahul Sharma',
    title: 'My Journey in Competitive Coding',
    category: 'Computer Science',
    description: 'A comprehensive guide on solving over 1000 problems with optimal runtime complexities.',
    coverUrl: 'https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&q=80&w=300',
    fileFormat: 'PDF',
    fileUrl: '/api/downloads/subm-1',
    status: 'APPROVED',
    isPaid: true,
    paymentTransactionId: 'tx-pub-1',
    adminNotes: 'Excellent work. Covers binary heaps and dynamic programming beautifully.',
    createdAt: '2025-06-15T09:00:00Z',
    updatedAt: '2025-06-16T14:00:00Z'
  }
];

const DEFAULT_ROYALTY_STATEMENTS: RoyaltyStatement[] = [
  {
    id: 'stmt-1',
    authorId: 'user-teacher',
    authorName: 'Dr. Ananya Iyer',
    month: '2026-06',
    totalSales: 15,
    grossRevenue: 5985,
    commission: 299.25,
    netRoyalty: 5685.75,
    isPaid: true,
    paidAt: '2026-07-01T10:00:00Z'
  }
];

const DEFAULT_WITHDRAWALS: WithdrawalRequest[] = [
  {
    id: 'wd-1',
    userId: 'user-teacher',
    userName: 'Dr. Ananya Iyer',
    amount: 12000,
    status: 'APPROVED',
    bankDetails: 'SBI A/C ...9876, IFSC SBIN0001234',
    createdAt: '2026-06-28T11:00:00Z',
    processedAt: '2026-07-01T12:00:00Z'
  }
];

const DEFAULT_PRODUCTS: Product[] = [
  {
    id: 'prod-1',
    name: 'Advanced Python Coding Blueprint',
    type: 'BOOK',
    category: 'Computer Science',
    description: 'Get the highest-rated eBook guide with 50+ enterprise engineering patterns.',
    price: 349,
    originalPrice: 499,
    imageUrl: 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&q=80&w=300',
    rating: 4.8,
    sellerId: 'user-teacher',
    sellerName: 'Dr. Ananya Iyer',
    tags: ['Python', 'eBook'],
    createdAt: '2025-06-10T12:00:00Z'
  },
  {
    id: 'prod-2',
    name: 'Modular Django Masterclass',
    type: 'COURSE',
    category: 'Web Development',
    description: 'Comprehensive, high-integrity course syllabus mapping Django channels and Postgres DB.',
    price: 1499,
    originalPrice: 2499,
    imageUrl: 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&q=80&w=300',
    rating: 4.9,
    sellerId: 'user-teacher',
    sellerName: 'Dr. Ananya Iyer',
    tags: ['Django', 'Course'],
    createdAt: '2025-06-11T12:00:00Z'
  },
  {
    id: 'prod-3',
    name: 'Elegant Portfolio React Template',
    type: 'PORTFOLIO_TEMPLATE',
    category: 'Design & Templates',
    description: 'A dark-mode ready portfolio template with interactive 3D cards and layout modules.',
    price: 299,
    originalPrice: 599,
    imageUrl: 'https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?auto=format&fit=crop&q=80&w=300',
    rating: 4.6,
    sellerId: 'user-admin',
    sellerName: 'Super Admin',
    tags: ['Portfolio', 'React'],
    createdAt: '2025-06-12T12:00:00Z'
  },
  {
    id: 'prod-4',
    name: 'AI-Powered Resume Builder PDF Export',
    type: 'RESUME_TEMPLATE',
    category: 'Templates',
    description: 'Minimalist, ATS-friendly resume template for engineering & technical leads.',
    price: 99,
    originalPrice: 199,
    imageUrl: 'https://images.unsplash.com/photo-1586281380349-632531db7ed4?auto=format&fit=crop&q=80&w=300',
    rating: 4.7,
    sellerId: 'user-admin',
    sellerName: 'Super Admin',
    tags: ['Resume', 'ATS'],
    createdAt: '2025-06-13T12:00:00Z'
  },
  {
    id: 'prod-5',
    name: 'Performance Marketing Campaign Management',
    type: 'SERVICE',
    category: 'Services',
    description: 'Drive high-conversion leads via automated campaigns and exact search terms.',
    price: 4999,
    imageUrl: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&q=80&w=300',
    rating: 4.8,
    sellerId: 'user-teacher',
    sellerName: 'Dr. Ananya Iyer',
    tags: ['Marketing', 'Services'],
    createdAt: '2025-06-14T12:00:00Z'
  },
  {
    id: 'prod-6',
    name: 'Enterprise Web Development Services',
    type: 'SERVICE',
    category: 'Services',
    description: 'Get a custom-built React + Django web application with full search and DB optimizations.',
    price: 19999,
    imageUrl: 'https://images.unsplash.com/photo-1547082299-de196ea013d6?auto=format&fit=crop&q=80&w=300',
    rating: 4.9,
    sellerId: 'user-teacher',
    sellerName: 'Dr. Ananya Iyer',
    tags: ['Development', 'Services'],
    createdAt: '2025-06-15T12:00:00Z'
  }
];

const DEFAULT_ORDERS: Order[] = [
  {
    id: 'ord-1',
    userId: 'user-student',
    userName: 'Rahul Sharma',
    items: [
      {
        productId: 'prod-1',
        productName: 'Advanced Python Coding Blueprint',
        productType: 'BOOK',
        price: 349,
        quantity: 1
      }
    ],
    subtotal: 349,
    discount: 0,
    gst: 62.82,
    total: 411.82,
    status: 'COMPLETED',
    createdAt: '2025-06-10T14:30:00Z'
  }
];

const DEFAULT_SERVICE_REQUESTS: ServiceRequest[] = [
  {
    id: 'req-1',
    userId: 'user-student',
    userName: 'Rahul Sharma',
    serviceType: 'Web Development',
    description: 'I need a portfolio website built in React & Tailwind with persistent client-side states.',
    budget: 8000,
    status: 'QUOTED',
    createdAt: '2026-07-01T10:00:00Z'
  }
];

const DEFAULT_QUOTATIONS: Quotation[] = [
  {
    id: 'q-1',
    requestId: 'req-1',
    teacherId: 'user-teacher',
    teacherName: 'Dr. Ananya Iyer',
    amount: 7500,
    timelineDays: 5,
    notes: 'I can deliver a highly polished, single-screen responsive canvas with complete custom layout blocks.',
    status: 'PENDING',
    createdAt: '2026-07-02T12:00:00Z'
  }
];

const DEFAULT_TRANSACTIONS: Transaction[] = [
  {
    id: 'tx-1',
    userId: 'user-student',
    userName: 'Rahul Sharma',
    type: 'DEBIT',
    amount: 411.82,
    purpose: 'Purchased Advanced Python Coding Blueprint (Order ord-1)',
    status: 'SUCCESS',
    createdAt: '2025-06-10T14:30:00Z'
  },
  {
    id: 'tx-2',
    userId: 'user-teacher',
    userName: 'Dr. Ananya Iyer',
    type: 'CREDIT',
    amount: 331.55,
    purpose: 'Royalty for Advanced Python Coding Blueprint (Order ord-1)',
    status: 'SUCCESS',
    createdAt: '2025-06-10T14:30:00Z'
  }
];

const DEFAULT_INVOICES: Invoice[] = [
  {
    id: 'inv-1',
    orderId: 'ord-1',
    userId: 'user-student',
    userName: 'Rahul Sharma',
    userEmail: 'student@brahmavidya.edu',
    billingAddress: 'BrahmaVidya Academic Hostel, Bangalore, India',
    subtotal: 349,
    gstAmount: 62.82,
    total: 411.82,
    pdfUrl: '/api/invoices/inv-1/pdf',
    createdAt: '2025-06-10T14:30:00Z'
  }
];

export class MemoryDatabase {
  private state: DatabaseState;

  constructor() {
    this.state = this.load();
  }

  private load(): DatabaseState {
    try {
      if (fs.existsSync(DB_FILE)) {
        const fileContent = fs.readFileSync(DB_FILE, 'utf-8');
        const loadedState: DatabaseState = JSON.parse(fileContent);
        let updated = false;
        if (!loadedState.blogs) {
          loadedState.blogs = DEFAULT_BLOGS;
          updated = true;
        }
        if (!loadedState.tutorials) {
          loadedState.tutorials = DEFAULT_TUTORIALS;
          updated = true;
        }
        if (!loadedState.books) {
          loadedState.books = DEFAULT_BOOKS;
          updated = true;
        }
        if (!loadedState.bookReviews) {
          loadedState.bookReviews = DEFAULT_BOOK_REVIEWS;
          updated = true;
        }
        if (!loadedState.submissions) {
          loadedState.submissions = DEFAULT_SUBMISSIONS;
          updated = true;
        }
        if (!loadedState.royaltyStatements) {
          loadedState.royaltyStatements = DEFAULT_ROYALTY_STATEMENTS;
          updated = true;
        }
        if (!loadedState.withdrawals) {
          loadedState.withdrawals = DEFAULT_WITHDRAWALS;
          updated = true;
        }
        if (!loadedState.products) {
          loadedState.products = DEFAULT_PRODUCTS;
          updated = true;
        }
        if (!loadedState.orders) {
          loadedState.orders = DEFAULT_ORDERS;
          updated = true;
        }
        if (!loadedState.serviceRequests) {
          loadedState.serviceRequests = DEFAULT_SERVICE_REQUESTS;
          updated = true;
        }
        if (!loadedState.quotations) {
          loadedState.quotations = DEFAULT_QUOTATIONS;
          updated = true;
        }
        if (!loadedState.transactions) {
          loadedState.transactions = DEFAULT_TRANSACTIONS;
          updated = true;
        }
        if (!loadedState.invoices) {
          loadedState.invoices = DEFAULT_INVOICES;
          updated = true;
        }
        if (updated) {
          this.saveState(loadedState);
        }
        return loadedState;
      }
    } catch (e) {
      console.error('Error reading JSON DB file, initializing default fallback.', e);
    }

    const initialState: DatabaseState = {
      users: DEFAULT_USERS,
      roles: DEFAULT_ROLES,
      permissions: DEFAULT_PERMISSIONS,
      navigationMenus: DEFAULT_MENUS,
      pages: DEFAULT_PAGES,
      courseStructures: [...DEFAULT_COURSES, ...PYTHON_SYLLABUS],
      learningProgress: [],
      certificates: DEFAULT_CERTIFICATES,
      settings: DEFAULT_SETTINGS,
      blogs: DEFAULT_BLOGS,
      tutorials: DEFAULT_TUTORIALS,
      books: DEFAULT_BOOKS,
      bookReviews: DEFAULT_BOOK_REVIEWS,
      submissions: DEFAULT_SUBMISSIONS,
      royaltyStatements: DEFAULT_ROYALTY_STATEMENTS,
      withdrawals: DEFAULT_WITHDRAWALS,
      products: DEFAULT_PRODUCTS,
      orders: DEFAULT_ORDERS,
      serviceRequests: DEFAULT_SERVICE_REQUESTS,
      quotations: DEFAULT_QUOTATIONS,
      transactions: DEFAULT_TRANSACTIONS,
      invoices: DEFAULT_INVOICES
    };
    this.saveState(initialState);
    return initialState;
  }

  private saveState(state: DatabaseState) {
    try {
      fs.writeFileSync(DB_FILE, JSON.stringify(state, null, 2), 'utf-8');
    } catch (e) {
      console.error('Error writing DB file.', e);
    }
  }

  public getState(): DatabaseState {
    return this.state;
  }

  public updateState(updater: (state: DatabaseState) => void) {
    updater(this.state);
    this.saveState(this.state);
  }
}

export const dbInstance = new MemoryDatabase();
