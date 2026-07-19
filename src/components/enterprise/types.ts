/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export type SubscriptionPlanType = 'FREE' | 'PREMIUM' | 'PROFESSIONAL' | 'BUSINESS' | 'ENTERPRISE' | 'INSTITUTION';

export interface SubscriptionPlan {
  id: string;
  name: SubscriptionPlanType;
  priceMonthly: number;
  priceYearly: number;
  features: string[];
  maxUsers: number;
  permissions: string[];
}

export interface UserSubscription {
  id: string;
  userId: string;
  plan: SubscriptionPlanType;
  billingCycle: 'MONTHLY' | 'YEARLY';
  startDate: string;
  expiryDate: string;
  isActive: boolean;
  autoRenew: boolean;
  gstNumber?: string;
  couponApplied?: string;
}

export interface SaaSInvoice {
  id: string;
  userId: string;
  planName: SubscriptionPlanType;
  amount: number;
  gstAmount: number;
  totalAmount: number;
  status: 'PAID' | 'PENDING' | 'FAILED';
  billingCycle: 'MONTHLY' | 'YEARLY';
  createdAt: string;
  pdfUrl: string;
}

export interface Coupon {
  code: string;
  discountPercentage: number;
  description: string;
  expiresAt: string;
}

export type OrgType = 'SCHOOL' | 'COLLEGE' | 'UNIVERSITY' | 'COACHING' | 'COMPANY' | 'NGO' | 'INSTITUTE';

export interface Organization {
  id: string;
  name: string;
  type: OrgType;
  domain: string;
  ownerId: string;
  createdAt: string;
  departments: string[];
  employeeCount: number;
  teacherCount: number;
  studentCount: number;
}

export interface OrgInvitation {
  id: string;
  orgId: string;
  email: string;
  role: 'ADMIN' | 'TEACHER' | 'EMPLOYEE' | 'MEMBER';
  department?: string;
  status: 'PENDING' | 'ACCEPTED' | 'DECLINED';
  createdAt: string;
}

export interface OrgRoster {
  id: string;
  orgId: string;
  userId: string;
  fullName: string;
  email: string;
  role: 'ADMIN' | 'TEACHER' | 'EMPLOYEE' | 'MEMBER';
  department: string;
  joinedAt: string;
}

export interface LedgerEntry {
  id: string;
  type: 'INCOME' | 'EXPENSE' | 'COMMISSION' | 'ROYALTY' | 'PUBLISHING_REVENUE' | 'WALLET_TX';
  amount: number;
  description: string;
  gstAmount: number;
  tdsAmount: number;
  netAmount: number;
  referenceId: string; // Order ID or withdrawal request ID
  createdAt: string;
  audited: boolean;
}

export interface AffiliateProfile {
  userId: string;
  referralCode: string;
  referralLink: string;
  commissionWalletBalance: number;
  referredCount: number;
  totalEarnings: number;
  tierLevel: 1 | 2 | 3; // Multi-level reward tracking
}

export interface ReferralReward {
  id: string;
  referrerId: string;
  refereeName: string;
  planPurchased: SubscriptionPlanType;
  commissionAmount: number;
  tierLevel: number;
  status: 'PAID' | 'PENDING';
  createdAt: string;
}

export interface ChatMessage {
  id: string;
  senderId: string;
  receiverId: string;
  text: string;
  createdAt: string;
  readStatus: 'SENT' | 'DELIVERED' | 'READ';
  attachment?: {
    type: 'IMAGE' | 'DOCUMENT' | 'VOICE';
    name: string;
    url: string;
    durationSeconds?: number;
  };
}

export interface LiveClass {
  id: string;
  title: string;
  teacherId: string;
  teacherName: string;
  scheduledAt: string;
  durationMins: number;
  meetingLink: string;
  status: 'SCHEDULED' | 'LIVE' | 'COMPLETED';
  recordingUrl?: string;
}

export interface LiveClassPoll {
  id: string;
  question: string;
  options: string[];
  votes: number[]; // Index aligned with options
  isActive: boolean;
}

export interface WhiteboardStroke {
  color: string;
  points: { x: number; y: number }[];
}

export interface VideoStreamAsset {
  id: string;
  title: string;
  description: string;
  duration: number; // in seconds
  thumbnailUrl: string;
  videoUrl: string;
  playbackSpeed: number;
  lastPosition: number; // in seconds, for "Continue Watching"
  bookmarks: number[]; // seconds marked
  notes: { id: string; timestamp: number; text: string }[];
}

export interface CommunityThread {
  id: string;
  forumId: string; // community category
  title: string;
  content: string;
  authorId: string;
  authorName: string;
  authorAvatar?: string;
  upvotes: number;
  downvotes: number;
  userVote?: 'UP' | 'DOWN';
  bestAnswerId?: string;
  createdAt: string;
  answers: CommunityAnswer[];
}

export interface CommunityAnswer {
  id: string;
  threadId: string;
  content: string;
  authorId: string;
  authorName: string;
  authorAvatar?: string;
  upvotes: number;
  downvotes: number;
  isBestAnswer: boolean;
  createdAt: string;
}

export interface ForumCategory {
  id: string;
  name: string;
  description: string;
  icon: string;
  topicsCount: number;
  postsCount: number;
}

export interface JobPortalListing {
  id: string;
  companyName: string;
  logoUrl: string;
  title: string;
  description: string;
  requirements: string[];
  location: string;
  salaryRange: string;
  type: 'FULL_TIME' | 'PART_TIME' | 'CONTRACT' | 'INTERNSHIP';
  recommendations: { teacherName: string; studentName: string; studentId: string }[];
  status: 'OPEN' | 'CLOSED';
  createdAt: string;
}

export interface JobApplication {
  id: string;
  jobId: string;
  studentId: string;
  studentName: string;
  resumeUrl: string;
  portfolioUrl?: string;
  status: 'SUBMITTED' | 'UNDER_REVIEW' | 'INTERVIEW_SCHEDULED' | 'OFFERED' | 'REJECTED';
  interviewTime?: string;
  createdAt: string;
}

export interface InternshipOffer {
  id: string;
  companyName: string;
  title: string;
  mentorName: string;
  studentId: string;
  studentName: string;
  status: 'OFFERED' | 'ACCEPTED' | 'COMPLETED';
  offerLetterUrl: string;
  certificateUrl?: string;
  startDate: string;
  durationMonths: number;
}

export interface NotificationTemplate {
  id: string;
  title: string;
  bodyTemplate: string;
  channels: ('PUSH' | 'EMAIL' | 'SMS' | 'WHATSAPP')[];
  category: string;
}

export interface NotificationDispatchLog {
  id: string;
  recipientName: string;
  channel: 'PUSH' | 'EMAIL' | 'SMS' | 'WHATSAPP';
  title: string;
  body: string;
  status: 'SENT' | 'PENDING' | 'FAILED';
  scheduledFor?: string;
  sentAt: string;
}

export interface UnifiedSearchRecord {
  id: string;
  title: string;
  category: 'BOOK' | 'COURSE' | 'TEACHER' | 'BLOG' | 'ORGANIZATION' | 'USER' | 'SERVICE' | 'JOB' | 'PROJECT' | 'FORUM' | 'WEBSITE';
  description: string;
  url: string;
  imageUrl?: string;
}

export interface SecuritySession {
  id: string;
  device: string;
  ipAddress: string;
  location: string;
  lastActive: string;
  isCurrent: boolean;
}

export interface SecurityAuditLog {
  id: string;
  action: string;
  details: string;
  ipAddress: string;
  createdAt: string;
  severity: 'INFO' | 'WARNING' | 'CRITICAL';
}

// Module 10 - Internship
export interface InternshipOpportunity {
  id: string;
  title: string;
  department: string;
  mentorName: string;
  mentorEmail: string;
  durationMonths: number;
  stipendAmount: number;
  targetHours: number;
  loggedHours: number;
  status: 'ACTIVE' | 'PENDING' | 'COMPLETED';
}

export interface InternshipDeliverable {
  id: string;
  internshipId: string;
  weekNumber: number;
  tasksCompleted: string;
  hoursLogged: number;
  feedback?: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  createdAt: string;
}

// Module 11 - Notifications
export type NotificationChannel = 'IN_APP' | 'EMAIL' | 'SMS' | 'PUSH';
export type NotificationCategory = 'ACADEMIC' | 'TRANSACTIONAL' | 'COMMUNITY' | 'SECURITY';

export interface SaaSNotification {
  id: string;
  title: string;
  message: string;
  category: NotificationCategory;
  channels: NotificationChannel[];
  createdAt: string;
  read: boolean;
}

// Module 12 - Search
export type SearchCategory = 'COURSES' | 'BOOKS' | 'DISCUSSIONS' | 'CAREERS';

export interface UnifiedSearchResult {
  id: string;
  title: string;
  description: string;
  category: SearchCategory;
  matchType: string;
  url: string;
  relevanceScore: number;
}

// Module 14 - Security
export interface SecurityLogEntry {
  id: string;
  event: string;
  ipAddress: string;
  location: string;
  status: 'SUCCESS' | 'FAILED';
  createdAt: string;
}

