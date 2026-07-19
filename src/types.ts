/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export interface Permission {
  code: string;
  description: string;
}

export interface Role {
  id: string;
  name: string;
  description: string;
  permissions: string[]; // List of permission codes
}

export interface UserCapability {
  id: string;
  capabilityCode: string;
  capabilityName: string;
  status: 'ACTIVE' | 'PENDING' | 'SUSPENDED' | 'DEACTIVATED' | 'REJECTED';
  activatedAt?: string;
  settings: Record<string, any>;
}

export interface User {
  id: string;
  email: string;
  fullName: string;
  roleId?: string;
  status: 'ACTIVE' | 'PENDING' | 'SUSPENDED';
  avatarUrl?: string;
  walletBalance: number;
  capabilities?: UserCapability[];
}

export interface NavigationMenu {
  id: string;
  parentId: string | null;
  title: string;
  url: string;
  icon: string; // Lucide icon key name
  displayOrder: number;
  isActive: boolean;
  requiredPermission: string | null;
}

export interface LayoutBlock {
  id: string;
  type: 'hero' | 'grid' | 'text' | 'features' | 'stats' | 'banner';
  title: string;
  subtitle?: string;
  content?: string;
  items?: Array<{
    title: string;
    description: string;
    icon?: string;
    link?: string;
  }>;
  styleSettings?: {
    theme?: 'light' | 'dark' | 'gold';
    padding?: string;
  };
}

export interface Page {
  id: string;
  title: string;
  slug: string;
  seoTitle?: string;
  seoDescription?: string;
  keywords?: string;
  layoutData: LayoutBlock[];
  isPublished: boolean;
  publishedAt?: string;
}

export interface CourseStructure {
  id: string;
  parentId: string | null;
  type: 'PROGRAM' | 'SUBJECT' | 'COURSE' | 'MODULE' | 'LESSON' | 'TASK';
  title: string;
  description: string;
  metadata?: {
    duration?: string;
    difficulty?: 'Beginner' | 'Intermediate' | 'Advanced';
    requirements?: string[];
    price?: number;
    lessonsCount?: number;
    videoUrl?: string;
    authorId?: string;
  };
}

export interface LearningProgress {
  userId: string;
  structureId: string;
  progressPercentage: number;
  status: 'NOT_STARTED' | 'IN_PROGRESS' | 'COMPLETED';
  lastAccessedAt: string;
}

export interface Certificate {
  id: string;
  recipientId: string;
  courseId: string;
  recipientName: string;
  courseTitle: string;
  certificateHash: string;
  qrCodeUrl: string;
  issuedAt: string;
  metadata?: {
    grade?: string;
    accreditationCode?: string;
  };
}

export interface SystemSettings {
  platformName: string;
  platformDescription: string;
  logoText: string;
  accentColor: string;
  activeAIProvider: 'gemini' | 'openai' | 'claude' | 'local';
  commissionRate: number; // Percentage, e.g. 15 for 15%
}

export interface Blog {
  id: string;
  title: string;
  slug: string;
  content: string;
  authorId: string;
  authorEmail?: string;
  isPublished: boolean;
  publishedAt?: string;
  isDeleted?: boolean;
}

export interface Tutorial {
  id: string;
  title: string;
  slug: string;
  content: string; // markdown format
  authorId: string;
  authorEmail?: string;
  isPublished: boolean;
  publishedAt?: string;
  isDeleted?: boolean;
}

export interface Book {
  id: string;
  title: string;
  authorId: string;
  authorName: string;
  category: string;
  tags: string[];
  description: string;
  price: number;
  coverUrl: string;
  fileFormat: 'PDF' | 'EPUB';
  fileUrl: string;
  isGeneratedEbook?: boolean;
  rating: number;
  reviewsCount: number;
  bookmarksCount: number;
  isPublished: boolean;
  createdAt: string;
}

export interface BookReview {
  id: string;
  bookId: string;
  userId: string;
  userName: string;
  rating: number;
  comment: string;
  createdAt: string;
}

export interface PublishSubmission {
  id: string;
  userId: string;
  userName: string;
  title: string;
  category: string;
  description: string;
  coverUrl: string;
  fileFormat: 'PDF' | 'EPUB';
  fileUrl: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  isPaid: boolean;
  paymentTransactionId?: string;
  adminNotes?: string;
  createdAt: string;
  updatedAt: string;
}

export interface RoyaltyStatement {
  id: string;
  authorId: string;
  authorName: string;
  month: string; // e.g., "2026-07"
  totalSales: number;
  grossRevenue: number;
  commission: number; // 5% BV Galaxy commission
  netRoyalty: number;
  isPaid: boolean;
  paidAt?: string;
}

export interface WithdrawalRequest {
  id: string;
  userId: string;
  userName: string;
  amount: number;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  bankDetails?: string;
  createdAt: string;
  processedAt?: string;
}

export interface Product {
  id: string;
  name: string;
  type: 'BOOK' | 'COURSE' | 'PORTFOLIO_TEMPLATE' | 'RESUME_TEMPLATE' | 'DIGITAL_ASSET' | 'SERVICE';
  category: string;
  description: string;
  price: number;
  originalPrice?: number;
  imageUrl: string;
  rating: number;
  sellerId: string;
  sellerName: string;
  tags: string[];
  createdAt: string;
}

export interface OrderItem {
  productId: string;
  productName: string;
  productType: string;
  price: number;
  quantity: number;
}

export interface Order {
  id: string;
  userId: string;
  userName: string;
  items: OrderItem[];
  subtotal: number;
  discount: number;
  gst: number;
  total: number;
  couponCode?: string;
  status: 'COMPLETED' | 'REFUNDED';
  createdAt: string;
}

export interface ServiceRequest {
  id: string;
  userId: string;
  userName: string;
  serviceType: string; // "Performance Marketing", "Web Development", etc.
  description: string;
  budget: number;
  status: 'PENDING' | 'QUOTED' | 'ACCEPTED' | 'COMPLETED' | 'CANCELLED';
  createdAt: string;
}

export interface Quotation {
  id: string;
  requestId: string;
  teacherId: string;
  teacherName: string;
  amount: number;
  timelineDays: number;
  notes: string;
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED';
  createdAt: string;
}

export interface Transaction {
  id: string;
  userId: string;
  userName: string;
  type: 'CREDIT' | 'DEBIT';
  amount: number;
  purpose: string; // e.g., "Book Sale Royalty", "Course Purchase", "Withdrawal"
  status: 'SUCCESS' | 'FAILED' | 'PENDING';
  createdAt: string;
}

export interface Invoice {
  id: string;
  orderId: string;
  userId: string;
  userName: string;
  userEmail: string;
  billingAddress?: string;
  subtotal: number;
  gstAmount: number;
  total: number;
  pdfUrl?: string;
  createdAt: string;
}

export interface DatabaseState {
  users: User[];
  roles: Role[];
  permissions: Permission[];
  navigationMenus: NavigationMenu[];
  pages: Page[];
  courseStructures: CourseStructure[];
  learningProgress: LearningProgress[];
  certificates: Certificate[];
  settings: SystemSettings;
  blogs?: Blog[];
  tutorials?: Tutorial[];
  books?: Book[];
  bookReviews?: BookReview[];
  submissions?: PublishSubmission[];
  royaltyStatements?: RoyaltyStatement[];
  withdrawals?: WithdrawalRequest[];
  products?: Product[];
  orders?: Order[];
  serviceRequests?: ServiceRequest[];
  quotations?: Quotation[];
  transactions?: Transaction[];
  invoices?: Invoice[];
}
