/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import express from 'express';
import { createServer as createViteServer } from 'vite';
import path from 'path';
import * as fs from 'fs';
import { GoogleGenAI } from '@google/genai';
import { dbInstance } from './src/db';
import { NavigationMenu, Page, Role, CourseStructure, Certificate, User, Blog, Tutorial } from './src/types';

import { spawn } from 'child_process';
import dotenv from 'dotenv';

// Centralized configuration and environment validation
dotenv.config();
const REQUIRED_ENV_VARS = ['DJANGO_SECRET_KEY', 'JWT_SECRET_KEY'];
const missingVars = REQUIRED_ENV_VARS.filter(v => !process.env[v]);
if (missingVars.length > 0) {
  console.warn(`[WARNING] Missing environment variables in process.env: ${missingVars.join(', ')}`);
  console.warn(`Please configure them in your .env file for production security.`);
}

// Lazy init Gemini SDK
let geminiClient: GoogleGenAI | null = null;
function getGemini(): GoogleGenAI | null {
  if (!geminiClient) {
    const key = process.env.GEMINI_API_KEY;
    if (key && key !== 'MY_GEMINI_API_KEY') {
      geminiClient = new GoogleGenAI({ apiKey: key });
    }
  }
  return geminiClient;
}

// Map from client paths to Django REST Framework paths
const PATH_MAP: Record<string, string> = {
  '/api/auth/login': '/api/v1/users/users/login/',
  '/api/auth/me': '/api/v1/users/users/me/',
  '/api/pages': '/api/v1/cms/pages/',
  '/api/menus': '/api/v1/cms/menus/',
  '/api/blogs': '/api/v1/cms/blogs/',
  '/api/tutorials': '/api/v1/cms/tutorials/',
  
  // Appended CMS Gateway proxies
  '/api/v1/cms/articles': '/api/v1/cms/articles/',
  '/api/v1/cms/categories': '/api/v1/cms/categories/',
  '/api/v1/cms/tags': '/api/v1/cms/tags/',
  '/api/v1/cms/workflow': '/api/v1/cms/workflow/',
  '/api/v1/cms/media': '/api/v1/cms/media/',
  '/api/v1/cms/search': '/api/v1/cms/search/',
  '/api/v1/cms/faq': '/api/v1/cms/faq/',
  '/api/v1/cms/redirects': '/api/v1/cms/redirects/',
  '/api/v1/cms/audit': '/api/v1/cms/audit/',
  '/api/v1/cms/publish': '/api/v1/cms/publish/',
  '/api/v1/cms/revisions': '/api/v1/cms/revisions/',
  '/api/v1/cms/reactions': '/api/v1/cms/reactions/',
  '/api/v1/cms/authors': '/api/v1/cms/authors/',
  '/api/v1/cms/blocks': '/api/v1/cms/blocks/',
  '/api/v1/cms/templates': '/api/v1/cms/templates/',
  
  // DAM Gateway proxies
  '/api/v1/cms/folders': '/api/v1/cms/folders/',
  '/api/v1/cms/collections': '/api/v1/cms/collections/',
  '/api/v1/cms/media-versions': '/api/v1/cms/media-versions/',
  '/api/v1/cms/media-shares': '/api/v1/cms/media-shares/',
  '/api/v1/cms/media-audits': '/api/v1/cms/media-audits/',
  '/api/v1/cms/media-favorites': '/api/v1/cms/media-favorites/',
  '/api/v1/cms/media-comments': '/api/v1/cms/media-comments/',
  '/api/v1/cms/media-search': '/api/v1/cms/media-search/',
  '/api/v1/cms/media-workflows': '/api/v1/cms/media-workflows/',

  '/api/courses': '/api/v1/lms/courses/',
  '/api/roles': '/api/v1/users/roles/',
  '/api/permissions': '/api/v1/users/permissions/',
  '/api/activities': '/api/v1/control-center/activities/',
  '/api/tasks': '/api/v1/control-center/tasks/',
  '/api/settings': '/api/v1/control-center/settings/',
  '/api/certificates': '/api/v1/lms/certificates/',
  '/api/exams': '/api/v1/lms/exams/',
  '/api/exam-attempts': '/api/v1/lms/exam-attempts/',
  '/api/wallets': '/api/v1/wallets/wallets/',
  '/api/organizations': '/api/v1/users/organizations/',
  '/api/organization-members': '/api/v1/users/organization-members/',
  '/api/login-history': '/api/v1/users/login-history/',
  '/api/media': '/api/v1/control-center/media/',
  '/api/live-classes': '/api/v1/lms/live-classes/',
  '/api/authors': '/api/v1/publishing/authors/',
  '/api/publishers': '/api/v1/publishing/publishers/',
  '/api/books': '/api/v1/publishing/books/',
  '/api/ownerships': '/api/v1/publishing/ownerships/',
  '/api/orders': '/api/v1/publishing/orders/',
  '/api/reading-progress': '/api/v1/publishing/reading-progress/',
  '/api/services/catalog': '/api/v1/services/catalog/',
  '/api/services/leads': '/api/v1/services/leads/',
  '/api/services/projects': '/api/v1/services/projects/',
  '/api/services/milestones': '/api/v1/services/milestones/',
  '/api/portfolio/resumes': '/api/v1/portfolio/resumes/',
  '/api/portfolio/jobs': '/api/v1/portfolio/jobs/',
  '/api/portfolio/roadmaps': '/api/v1/portfolio/roadmaps/',
  '/api/portfolio/ai-assistant': '/api/v1/portfolio/ai-assistant/',
  '/api/subscriptions': '/api/v1/wallets/subscriptions/',
  '/api/coupons': '/api/v1/wallets/coupons/',
  '/api/invoices': '/api/v1/wallets/invoices/',
  '/api/revenue-analytics': '/api/v1/wallets/revenue-analytics/',
  '/api/payment-gateway': '/api/v1/wallets/payment-gateway/',
  '/api/subscription-gateway': '/api/v1/wallets/subscription-gateway/',
  '/api/coupon-gateway': '/api/v1/wallets/coupon-gateway/',
  '/api/v1/payments': '/api/v1/wallets/payments/',
  '/api/ai/conversations': '/api/v1/ai/conversations/',
  '/api/ai/messages': '/api/v1/ai/messages/',
  '/api/ai/feedback': '/api/v1/ai/feedback/',
  '/api/ai/prompts': '/api/v1/ai/prompts/',
  '/api/ai/models': '/api/v1/ai/models/',
  '/api/ai/sessions': '/api/v1/ai/sessions/',
  '/api/ai/usage': '/api/v1/ai/usage/',
  '/api/ai/analytics': '/api/v1/ai/analytics/',
  '/api/v1/ai': '/api/v1/ai/',
  '/api/admin/dashboard': '/api/v1/control-center/admin/dashboard/',
  '/api/admin/analytics-reports': '/api/v1/control-center/admin/analytics-reports/',
  '/api/control-center/analytics': '/api/v1/control-center/analytics/',
  '/api/seo': '/api/v1/seo/',
  '/api/stats': '/api/v1/control-center/stats/',
  '/api/users/capabilities': '/api/v1/users/capabilities/',
  '/api/users/me/capabilities': '/api/v1/users/me/capabilities/',
  '/api/admin/capability-applications': '/api/v1/users/admin/capability-applications/',
  '/api/admin/users': '/api/v1/users/admin/users/',
  '/api/notifications/records': '/api/v1/notifications/records/',
  '/api/notifications/templates': '/api/v1/notifications/templates/',
  '/api/notifications/preferences': '/api/v1/notifications/preferences/',
  '/api/notifications/announcements': '/api/v1/notifications/announcements/',
  '/api/notifications/analytics': '/api/v1/notifications/analytics/',
  '/api/v1/search': '/api/v1/search/',
  '/api/v1/analytics': '/api/v1/analytics/',
  '/api/student': '/api/v1/student/',
  '/api/v1/student': '/api/v1/student/',
  '/api/student/dashboard/summary': '/api/v1/student/dashboard/summary/',
  '/api/student/history': '/api/v1/student/history/',
  '/api/student/continue-learning': '/api/v1/student/continue-learning/',
  '/api/student/bookmarks': '/api/v1/student/bookmarks/',
  '/api/student/notes': '/api/v1/student/notes/',
  '/api/student/goals': '/api/v1/student/goals/',
  '/api/student/sessions': '/api/v1/student/sessions/',
  '/api/student/calendar-events': '/api/v1/student/calendar-events/',
  '/api/student/progress/daily': '/api/v1/student/progress/daily/',
  '/api/student/progress/weekly': '/api/v1/student/progress/weekly/',
  '/api/student/progress/monthly': '/api/v1/student/progress/monthly/',
  '/api/student/streaks': '/api/v1/student/streaks/',
  '/api/student/achievements': '/api/v1/student/achievements/',
  '/api/student/student-achievements': '/api/v1/student/student-achievements/',
  '/api/student/preferences': '/api/v1/student/preferences/',
  '/api/student/recently-viewed': '/api/v1/student/recently-viewed/',
  '/api/student/reminders': '/api/v1/student/reminders/',
  
  // Sprint 21 — Teacher Portal Gateway Proxies
  '/api/teacher': '/api/v1/teacher/',
  '/api/v1/teacher': '/api/v1/teacher/',

  // Sprint 22 — Live Classes Gateway Proxies
  '/api/v1/live': '/api/v1/lms/',
};

async function proxyToDjango(req: express.Request, res: express.Response, djangoPath: string) {
  const targetUrl = `http://127.0.0.1:8000${djangoPath}`;
  
  // Logging proxied gateway requests
  console.log(`[GATEWAY INFO] Proxying ${req.method} request to Django: ${djangoPath}`);

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (req.headers.authorization) {
    headers['Authorization'] = req.headers.authorization;
  }
  if (req.headers.cookie) {
    headers['Cookie'] = req.headers.cookie as string;
  }

  // Preserve tracing and request correlation headers
  const traceHeaders = ['x-request-id', 'x-correlation-id', 'x-trace-id', 'x-span-id'];
  traceHeaders.forEach(h => {
    if (req.headers[h]) {
      headers[h] = req.headers[h] as string;
    }
  });

  try {
    const fetchOptions: RequestInit = {
      method: req.method,
      headers,
    };

    if (['POST', 'PUT', 'PATCH'].includes(req.method)) {
      fetchOptions.body = JSON.stringify(req.body);
    }

    const dRes = await fetch(targetUrl, fetchOptions);
    const contentType = dRes.headers.get('content-type');
    
    if (contentType && contentType.includes('application/json')) {
      const data = await dRes.json();
      res.status(dRes.status).json(data);
    } else {
      const text = await dRes.text();
      res.status(dRes.status).send(text);
    }
  } catch (err) {
    console.error(`Proxy to Django failed on ${targetUrl}:`, err);
    res.status(502).json({ success: false, message: 'Django backend service is booting or unavailable.' });
  }
}

import { createClient } from 'redis';

const redisUrl = process.env.REDIS_URL || 'redis://127.0.0.1:6379';
const redisClient = createClient({
  url: redisUrl,
  socket: {
    reconnectStrategy: (retries) => {
      // Try up to 2 times to see if local Redis is booting, then stop to prevent continuous ECONNREFUSED log pollution
      if (retries >= 2) {
        return false;
      }
      return 1000; // retry after 1 second
    }
  }
});

let hasLoggedRedisError = false;
redisClient.on('error', (err) => {
  if (!hasLoggedRedisError) {
    console.warn('[REDIS WARNING] Distributed Rate Limiter Redis client error:', err.message);
    hasLoggedRedisError = true;
  }
});

let isRedisConnected = false;
async function connectRedis() {
  try {
    await redisClient.connect();
    isRedisConnected = true;
    console.log('[REDIS INFO] Connected to Redis for Distributed Rate Limiter.');
  } catch (err: any) {
    isRedisConnected = false;
    console.warn(`[REDIS WARNING] Failed to connect to Redis (${err.message}). Falling back to in-memory rate limiter.`);
  }
}
connectRedis();

const rateLimitWindowMs = parseInt(process.env.RATE_LIMIT_WINDOW_MS || '60000', 10);
const rateLimitMaxRequests = parseInt(process.env.RATE_LIMIT_MAX_REQUESTS || '100', 10);
const ipRequestCounts = new Map<string, { count: number; resetTime: number }>();

async function rateLimiter(req: express.Request, res: express.Response, next: express.NextFunction) {
  let identifier = req.ip || req.socket.remoteAddress || 'unknown';
  const authHeader = req.headers.authorization;
  if (authHeader && authHeader.startsWith('Bearer ')) {
    identifier = authHeader.split(' ')[1];
  }

  const now = Date.now();

  if (isRedisConnected) {
    const key = `ratelimit:${identifier}`;
    const clearBefore = now - rateLimitWindowMs;

    try {
      const multi = redisClient.multi();
      multi.zRemRangeByScore(key, 0, clearBefore);
      multi.zAdd(key, { score: now, value: `${now}-${Math.random()}` });
      multi.zCard(key);
      multi.expire(key, Math.ceil(rateLimitWindowMs / 1000));
      
      const results = await multi.exec();
      const requestCount = results[2] as unknown as number;

      if (requestCount > rateLimitMaxRequests) {
        return res.status(429).json({
          success: false,
          message: 'Too many requests. Please try again later.'
        });
      }
      return next();
    } catch (err: any) {
      console.warn('[REDIS WARNING] Rate limiting transaction failed, using memory fallback:', err.message);
    }
  }

  const limitInfo = ipRequestCounts.get(identifier);
  if (!limitInfo || now > limitInfo.resetTime) {
    ipRequestCounts.set(identifier, { count: 1, resetTime: now + rateLimitWindowMs });
    return next();
  }

  limitInfo.count += 1;
  if (limitInfo.count > rateLimitMaxRequests) {
    return res.status(429).json({
      success: false,
      message: 'Too many requests. Please try again later.'
    });
  }

  next();
}

async function startServer() {
  const app = express();
  app.use(rateLimiter);
  app.use(express.json());

  // Boot Django REST Framework Backend in background on port 8000
  console.log('Booting Django REST Framework server on http://127.0.0.1:8000...');
  const pythonCmd = process.env.PYTHON_CMD || 'python';
  const djangoProcess = spawn(pythonCmd, ['backend/manage.py', 'runserver', '127.0.0.1:8000'], {
    stdio: 'inherit',
    shell: true
  });

  djangoProcess.on('error', (err) => {
    console.error('Failed to start Django backend subprocess:', err);
  });

  // Ensure Django subprocess is terminated when main Node process exits
  process.on('exit', () => {
    djangoProcess.kill();
  });
  process.on('SIGINT', () => {
    djangoProcess.kill();
    process.exit();
  });

  // Dynamic API Gateway Routing middleware targeting Django REST Framework
  app.use('/api', async (req, res, next) => {
    const fullUrl = req.baseUrl + req.path;
    
    // Normalize trailing slash for exact mapping checks
    const normalizedUrl = fullUrl.endsWith('/') ? fullUrl.slice(0, -1) : fullUrl;
    
    // Find matching exact key (with or without trailing slash)
    const matchedKey = Object.keys(PATH_MAP).find(k => {
      const normK = k.endsWith('/') ? k.slice(0, -1) : k;
      return normK === normalizedUrl;
    });

    if (matchedKey) {
      const baseTarget = PATH_MAP[matchedKey];
      const djangoPath = baseTarget + (req.url.includes('?') ? req.url.substring(req.url.indexOf('?')) : '');
      return proxyToDjango(req, res, djangoPath);
    }

    // Match prefix (handling trailing slashes gracefully)
    for (const [key, value] of Object.entries(PATH_MAP)) {
      const normKey = key.endsWith('/') ? key.slice(0, -1) : key;
      if (fullUrl.startsWith(normKey + '/')) {
        const remainingPath = fullUrl.substring(normKey.length);
        const targetBase = value.endsWith('/') ? value : value + '/';
        const cleanRemaining = remainingPath.replace(/^\//, '');
        const djangoPath = targetBase + cleanRemaining + (req.url.includes('?') ? req.url.substring(req.url.indexOf('?')) : '');
        return proxyToDjango(req, res, djangoPath);
      }
    }

    // Fallback to Express mock DB
    next();
  });

  app.get('/seo/sitemap.xml', (req, res) => {
    proxyToDjango(req, res, '/api/v1/seo/sitemap.xml');
  });

  app.get('/robots.txt', (req, res) => {
    proxyToDjango(req, res, '/api/v1/seo/robots.txt');
  });

  // --- LOG FEED MANAGER ---
  const activityLogs: Array<{ text: string; time: string; timestamp: Date }> = [
    { text: 'Super Admin logged in from Secure Session.', time: 'Just now', timestamp: new Date() },
    { text: 'New student registered: Rahul Sharma has joined the platform.', time: '2 mins ago', timestamp: new Date(Date.now() - 120000) },
    { text: 'Teacher application received: Dr. Ananya Iyer (Data Sciences)', time: '15 mins ago', timestamp: new Date(Date.now() - 900000) },
    { text: 'New course proposal submitted: Data Structures & Algorithms', time: '1 hour ago', timestamp: new Date(Date.now() - 3600000) },
    { text: 'Payout request processed: ₹1,24,500 to teacher ledger.', time: '4 hours ago', timestamp: new Date(Date.now() - 14400000) }
  ];

  function addLog(text: string) {
    activityLogs.unshift({ text, time: 'Just now', timestamp: new Date() });
    if (activityLogs.length > 50) activityLogs.pop();
  }

  // --- REST ENDPOINTS ---

  // AUTH API
  app.post('/api/auth/login', (req, res) => {
    const { email } = req.body;
    const db = dbInstance.getState();
    const user = db.users.find(u => u.email === email);
    if (!user) {
      return res.status(401).json({ success: false, message: 'Invalid credentials. Please use admin@brahmavidya.edu, teacher@brahmavidya.edu or student@brahmavidya.edu.' });
    }
    addLog(`User logged in: ${user.fullName} (${email})`);
    res.json({ success: true, token: `simulated-token-for-${user.id}`, user });
  });

  app.get('/api/auth/me', (req, res) => {
    const token = req.headers.authorization?.replace('Bearer ', '');
    if (!token) {
      return res.status(401).json({ success: false, message: 'Unauthorized' });
    }
    const userId = token.replace('simulated-token-for-', '');
    const db = dbInstance.getState();
    const user = db.users.find(u => u.id === userId);
    if (!user) {
      return res.status(401).json({ success: false, message: 'User not found' });
    }
    const role = db.roles.find(r => r.id === user.roleId);
    res.json({
      success: true,
      user,
      permissions: role ? role.permissions : []
    });
  });

  // STATS & SUMMARY
  app.get('/api/stats', (req, res) => {
    const db = dbInstance.getState();
    const studentsCount = db.users.filter(u => u.roleId === 'role-student').length + 12585;
    const teachersCount = db.users.filter(u => u.roleId === 'role-teacher').length + 1243;
    const coursesCount = db.courseStructures.filter(c => c.type === 'COURSE').length + 2354;

    res.json({
      success: true,
      data: {
        totalStudents: { value: studentsCount.toLocaleString(), change: '+12.5%' },
        totalTeachers: { value: teachersCount.toLocaleString(), change: '+8.3%' },
        totalCourses: { value: coursesCount.toLocaleString(), change: '+15.2%' },
        totalRevenue: { value: '₹34,75,680', change: '+18.7%' },
        activeUsers: { value: '8,975', change: '+11.3%' }
      }
    });
  });

  // SYSTEM SETTINGS
  app.get('/api/settings', (req, res) => {
    res.json({ success: true, data: dbInstance.getState().settings });
  });

  app.put('/api/settings', (req, res) => {
    dbInstance.updateState(state => {
      state.settings = { ...state.settings, ...req.body };
    });
    addLog('System settings updated in the Control Center.');
    res.json({ success: true, data: dbInstance.getState().settings });
  });

  // NAVIGATION MENUS
  app.get('/api/menus', (req, res) => {
    res.json({ success: true, data: dbInstance.getState().navigationMenus });
  });

  app.post('/api/menus', (req, res) => {
    const newMenu: NavigationMenu = {
      id: `menu-${Date.now()}`,
      parentId: req.body.parentId || null,
      title: req.body.title,
      url: req.body.url,
      icon: req.body.icon || 'BookOpen',
      displayOrder: parseInt(req.body.displayOrder) || 0,
      isActive: req.body.isActive !== false,
      requiredPermission: req.body.requiredPermission || null
    };

    dbInstance.updateState(state => {
      state.navigationMenus.push(newMenu);
    });
    addLog(`Menu node created: "${newMenu.title}" mapped to ${newMenu.url}`);
    res.json({ success: true, data: newMenu });
  });

  app.put('/api/menus/:id', (req, res) => {
    let updated: NavigationMenu | null = null;
    dbInstance.updateState(state => {
      const index = state.navigationMenus.findIndex(m => m.id === req.params.id);
      if (index !== -1) {
        state.navigationMenus[index] = { ...state.navigationMenus[index], ...req.body };
        updated = state.navigationMenus[index];
      }
    });
    if (updated) {
      addLog(`Menu node modified: "${(updated as NavigationMenu).title}"`);
      res.json({ success: true, data: updated });
    } else {
      res.status(404).json({ success: false, message: 'Menu not found' });
    }
  });

  app.delete('/api/menus/:id', (req, res) => {
    let deletedTitle = '';
    dbInstance.updateState(state => {
      const item = state.navigationMenus.find(m => m.id === req.params.id);
      if (item) deletedTitle = item.title;
      state.navigationMenus = state.navigationMenus.filter(m => m.id !== req.params.id && m.parentId !== req.params.id);
    });
    addLog(`Menu node deleted: "${deletedTitle}" (including dependent submenus)`);
    res.json({ success: true, message: 'Menu deleted' });
  });

  // PAGE BUILDER
  app.get('/api/pages', (req, res) => {
    res.json({ success: true, data: dbInstance.getState().pages });
  });

  app.post('/api/pages', (req, res) => {
    const newPage: Page = {
      id: `page-${Date.now()}`,
      title: req.body.title,
      slug: req.body.slug,
      seoTitle: req.body.seoTitle || req.body.title,
      seoDescription: req.body.seoDescription || '',
      keywords: req.body.keywords || '',
      layoutData: req.body.layoutData || [],
      isPublished: req.body.isPublished !== false,
      publishedAt: req.body.isPublished ? new Date().toISOString() : undefined
    };

    dbInstance.updateState(state => {
      state.pages.push(newPage);
    });
    addLog(`Page created: "${newPage.title}" registered on slug "/p/${newPage.slug}"`);
    res.json({ success: true, data: newPage });
  });

  app.put('/api/pages/:id', (req, res) => {
    let updated: Page | null = null;
    dbInstance.updateState(state => {
      const index = state.pages.findIndex(p => p.id === req.params.id);
      if (index !== -1) {
        state.pages[index] = { ...state.pages[index], ...req.body };
        updated = state.pages[index];
      }
    });
    if (updated) {
      addLog(`Page structure modified: "${(updated as Page).title}"`);
      res.json({ success: true, data: updated });
    } else {
      res.status(404).json({ success: false, message: 'Page not found' });
    }
  });

  app.delete('/api/pages/:id', (req, res) => {
    dbInstance.updateState(state => {
      state.pages = state.pages.filter(p => p.id !== req.params.id);
    });
    addLog(`Page layout deleted.`);
    res.json({ success: true, message: 'Page deleted' });
  });

  // --- BLOGS CMS ---
  app.get('/api/blogs', (req, res) => {
    const { search, author, isPublished, includeDeleted, page = 1, limit = 10 } = req.query;
    let blogs = dbInstance.getState().blogs || [];

    // Filter soft deleted unless includeDeleted is true
    if (includeDeleted !== 'true') {
      blogs = blogs.filter(b => !b.isDeleted);
    }

    // Search filter
    if (search) {
      const query = String(search).toLowerCase();
      blogs = blogs.filter(b => 
        b.title.toLowerCase().includes(query) || 
        b.slug.toLowerCase().includes(query) || 
        b.content.toLowerCase().includes(query)
      );
    }

    // Author filter
    if (author) {
      blogs = blogs.filter(b => b.authorId === author);
    }

    // Publish status filter
    if (isPublished !== undefined) {
      const isPub = isPublished === 'true';
      blogs = blogs.filter(b => b.isPublished === isPub);
    }

    // Simple Pagination
    const pageNum = parseInt(String(page)) || 1;
    const limitNum = parseInt(String(limit)) || 10;
    const total = blogs.length;
    const startIdx = (pageNum - 1) * limitNum;
    const paginatedBlogs = blogs.slice(startIdx, startIdx + limitNum);

    res.json({
      success: true,
      total,
      page: pageNum,
      limit: limitNum,
      data: paginatedBlogs
    });
  });

  app.get('/api/blogs/:idOrSlug', (req, res) => {
    const { idOrSlug } = req.params;
    const blogs = dbInstance.getState().blogs || [];
    const blog = blogs.find(b => (b.id === idOrSlug || b.slug === idOrSlug) && !b.isDeleted);
    if (!blog) {
      return res.status(404).json({ success: false, message: 'Blog not found' });
    }
    res.json({ success: true, data: blog });
  });

  app.post('/api/blogs', (req, res) => {
    const { title, slug, content, authorId, authorEmail, isPublished } = req.body;
    if (!title || !slug) {
      return res.status(400).json({ success: false, message: 'Title and slug are required' });
    }

    const newBlog: Blog = {
      id: `blog-${Date.now()}`,
      title,
      slug,
      content: content || '',
      authorId: authorId || 'user-admin',
      authorEmail: authorEmail || 'admin@brahmavidya.edu',
      isPublished: isPublished || false,
      publishedAt: isPublished ? new Date().toISOString() : undefined,
      isDeleted: false
    };

    dbInstance.updateState(state => {
      if (!state.blogs) state.blogs = [];
      state.blogs.push(newBlog);
    });

    addLog(`Blog post created: "${newBlog.title}" on slug "/blog/${newBlog.slug}"`);
    res.json({ success: true, data: newBlog });
  });

  app.put('/api/blogs/:idOrSlug', (req, res) => {
    const { idOrSlug } = req.params;
    let updated: Blog | null = null;

    dbInstance.updateState(state => {
      if (!state.blogs) state.blogs = [];
      const index = state.blogs.findIndex(b => (b.id === idOrSlug || b.slug === idOrSlug) && !b.isDeleted);
      if (index !== -1) {
        const originalPub = state.blogs[index].isPublished;
        const newPub = req.body.isPublished !== undefined ? req.body.isPublished : originalPub;
        
        let publishedAt = state.blogs[index].publishedAt;
        if (newPub && !originalPub) {
          publishedAt = new Date().toISOString();
        }

        state.blogs[index] = {
          ...state.blogs[index],
          ...req.body,
          publishedAt
        };
        updated = state.blogs[index];
      }
    });

    if (updated) {
      addLog(`Blog post modified: "${(updated as Blog).title}"`);
      res.json({ success: true, data: updated });
    } else {
      res.status(404).json({ success: false, message: 'Blog not found' });
    }
  });

  app.delete('/api/blogs/:idOrSlug', (req, res) => {
    const { idOrSlug } = req.params;
    let deletedTitle = '';

    dbInstance.updateState(state => {
      if (!state.blogs) state.blogs = [];
      const index = state.blogs.findIndex(b => (b.id === idOrSlug || b.slug === idOrSlug) && !b.isDeleted);
      if (index !== -1) {
        deletedTitle = state.blogs[index].title;
        state.blogs[index].isDeleted = true; // Soft delete
      }
    });

    if (deletedTitle) {
      addLog(`Blog post soft-deleted: "${deletedTitle}"`);
      res.json({ success: true, message: 'Blog soft-deleted successfully' });
    } else {
      res.status(404).json({ success: false, message: 'Blog not found' });
    }
  });

  app.post('/api/blogs/:idOrSlug/restore', (req, res) => {
    const { idOrSlug } = req.params;
    let restoredTitle = '';

    dbInstance.updateState(state => {
      if (!state.blogs) state.blogs = [];
      const index = state.blogs.findIndex(b => (b.id === idOrSlug || b.slug === idOrSlug) && b.isDeleted);
      if (index !== -1) {
        restoredTitle = state.blogs[index].title;
        state.blogs[index].isDeleted = false; // Restore
      }
    });

    if (restoredTitle) {
      addLog(`Blog post restored: "${restoredTitle}"`);
      res.json({ success: true, message: 'Blog restored successfully' });
    } else {
      res.status(404).json({ success: false, message: 'Deleted blog not found' });
    }
  });


  // --- TUTORIALS CMS ---
  app.get('/api/tutorials', (req, res) => {
    const { search, author, isPublished, includeDeleted, page = 1, limit = 10 } = req.query;
    let tutorials = dbInstance.getState().tutorials || [];

    // Filter soft deleted unless includeDeleted is true
    if (includeDeleted !== 'true') {
      tutorials = tutorials.filter(t => !t.isDeleted);
    }

    // Search filter
    if (search) {
      const query = String(search).toLowerCase();
      tutorials = tutorials.filter(t => 
        t.title.toLowerCase().includes(query) || 
        t.slug.toLowerCase().includes(query) || 
        t.content.toLowerCase().includes(query)
      );
    }

    // Author filter
    if (author) {
      tutorials = tutorials.filter(t => t.authorId === author);
    }

    // Publish status filter
    if (isPublished !== undefined) {
      const isPub = isPublished === 'true';
      tutorials = tutorials.filter(t => t.isPublished === isPub);
    }

    // Simple Pagination
    const pageNum = parseInt(String(page)) || 1;
    const limitNum = parseInt(String(limit)) || 10;
    const total = tutorials.length;
    const startIdx = (pageNum - 1) * limitNum;
    const paginatedTutorials = tutorials.slice(startIdx, startIdx + limitNum);

    res.json({
      success: true,
      total,
      page: pageNum,
      limit: limitNum,
      data: paginatedTutorials
    });
  });

  app.get('/api/tutorials/:idOrSlug', (req, res) => {
    const { idOrSlug } = req.params;
    const tutorials = dbInstance.getState().tutorials || [];
    const tutorial = tutorials.find(t => (t.id === idOrSlug || t.slug === idOrSlug) && !t.isDeleted);
    if (!tutorial) {
      return res.status(404).json({ success: false, message: 'Tutorial not found' });
    }
    res.json({ success: true, data: tutorial });
  });

  app.post('/api/tutorials', (req, res) => {
    const { title, slug, content, authorId, authorEmail, isPublished } = req.body;
    if (!title || !slug) {
      return res.status(400).json({ success: false, message: 'Title and slug are required' });
    }

    const newTutorial: Tutorial = {
      id: `tutorial-${Date.now()}`,
      title,
      slug,
      content: content || '',
      authorId: authorId || 'user-admin',
      authorEmail: authorEmail || 'admin@brahmavidya.edu',
      isPublished: isPublished || false,
      publishedAt: isPublished ? new Date().toISOString() : undefined,
      isDeleted: false
    };

    dbInstance.updateState(state => {
      if (!state.tutorials) state.tutorials = [];
      state.tutorials.push(newTutorial);
    });

    addLog(`Tutorial created: "${newTutorial.title}" on slug "/tutorial/${newTutorial.slug}"`);
    res.json({ success: true, data: newTutorial });
  });

  app.put('/api/tutorials/:idOrSlug', (req, res) => {
    const { idOrSlug } = req.params;
    let updated: Tutorial | null = null;

    dbInstance.updateState(state => {
      if (!state.tutorials) state.tutorials = [];
      const index = state.tutorials.findIndex(t => (t.id === idOrSlug || t.slug === idOrSlug) && !t.isDeleted);
      if (index !== -1) {
        const originalPub = state.tutorials[index].isPublished;
        const newPub = req.body.isPublished !== undefined ? req.body.isPublished : originalPub;
        
        let publishedAt = state.tutorials[index].publishedAt;
        if (newPub && !originalPub) {
          publishedAt = new Date().toISOString();
        }

        state.tutorials[index] = {
          ...state.tutorials[index],
          ...req.body,
          publishedAt
        };
        updated = state.tutorials[index];
      }
    });

    if (updated) {
      addLog(`Tutorial modified: "${(updated as Tutorial).title}"`);
      res.json({ success: true, data: updated });
    } else {
      res.status(404).json({ success: false, message: 'Tutorial not found' });
    }
  });

  app.delete('/api/tutorials/:idOrSlug', (req, res) => {
    const { idOrSlug } = req.params;
    let deletedTitle = '';

    dbInstance.updateState(state => {
      if (!state.tutorials) state.tutorials = [];
      const index = state.tutorials.findIndex(t => (t.id === idOrSlug || t.slug === idOrSlug) && !t.isDeleted);
      if (index !== -1) {
        deletedTitle = state.tutorials[index].title;
        state.tutorials[index].isDeleted = true; // Soft delete
      }
    });

    if (deletedTitle) {
      addLog(`Tutorial soft-deleted: "${deletedTitle}"`);
      res.json({ success: true, message: 'Tutorial soft-deleted successfully' });
    } else {
      res.status(404).json({ success: false, message: 'Tutorial not found' });
    }
  });

  app.post('/api/tutorials/:idOrSlug/restore', (req, res) => {
    const { idOrSlug } = req.params;
    let restoredTitle = '';

    dbInstance.updateState(state => {
      if (!state.tutorials) state.tutorials = [];
      const index = state.tutorials.findIndex(t => (t.id === idOrSlug || t.slug === idOrSlug) && t.isDeleted);
      if (index !== -1) {
        restoredTitle = state.tutorials[index].title;
        state.tutorials[index].isDeleted = false; // Restore
      }
    });

    if (restoredTitle) {
      addLog(`Tutorial restored: "${restoredTitle}"`);
      res.json({ success: true, message: 'Tutorial restored successfully' });
    } else {
      res.status(404).json({ success: false, message: 'Deleted tutorial not found' });
    }
  });

  // RBAC & ROLES
  app.get('/api/roles', (req, res) => {
    res.json({ success: true, data: dbInstance.getState().roles });
  });

  app.get('/api/permissions', (req, res) => {
    res.json({ success: true, data: dbInstance.getState().permissions });
  });

  app.post('/api/roles', (req, res) => {
    const newRole: Role = {
      id: `role-${Date.now()}`,
      name: req.body.name,
      description: req.body.description || '',
      permissions: req.body.permissions || []
    };

    dbInstance.updateState(state => {
      state.roles.push(newRole);
    });
    addLog(`Custom permission role created: "${newRole.name}" with ${newRole.permissions.length} nodes.`);
    res.json({ success: true, data: newRole });
  });

  app.put('/api/roles/:id', (req, res) => {
    let updated: Role | null = null;
    dbInstance.updateState(state => {
      const index = state.roles.findIndex(r => r.id === req.params.id);
      if (index !== -1) {
        state.roles[index] = { ...state.roles[index], ...req.body };
        updated = state.roles[index];
      }
    });
    if (updated) {
      addLog(`Role permissions modified: "${(updated as Role).name}" matrix updated.`);
      res.json({ success: true, data: updated });
    } else {
      res.status(404).json({ success: false, message: 'Role not found' });
    }
  });

  // ACADEMIC COURSE STRUCTURES
  app.get('/api/courses', (req, res) => {
    res.json({ success: true, data: dbInstance.getState().courseStructures });
  });

  app.post('/api/courses', (req, res) => {
    const newCourse: CourseStructure = {
      id: `course-${Date.now()}`,
      parentId: req.body.parentId || null,
      type: req.body.type || 'COURSE',
      title: req.body.title,
      description: req.body.description || '',
      metadata: req.body.metadata || {}
    };

    dbInstance.updateState(state => {
      state.courseStructures.push(newCourse);
    });
    addLog(`Academic unit appended: [${newCourse.type}] "${newCourse.title}"`);
    res.json({ success: true, data: newCourse });
  });

  app.put('/api/courses/:id', (req, res) => {
    let updated: CourseStructure | null = null;
    dbInstance.updateState(state => {
      const index = state.courseStructures.findIndex(c => c.id === req.params.id);
      if (index !== -1) {
        state.courseStructures[index] = { ...state.courseStructures[index], ...req.body };
        updated = state.courseStructures[index];
      }
    });
    if (updated) {
      addLog(`Curriculum node edited: "${(updated as CourseStructure).title}"`);
      res.json({ success: true, data: updated });
    } else {
      res.status(404).json({ success: false, message: 'Course node not found' });
    }
  });

  app.delete('/api/courses/:id', (req, res) => {
    dbInstance.updateState(state => {
      state.courseStructures = state.courseStructures.filter(c => c.id !== req.params.id && c.parentId !== req.params.id);
    });
    addLog('Academic structure branch and dependencies deleted.');
    res.json({ success: true, message: 'Course structure and its child nodes removed' });
  });

  // DIGITAL CERTIFICATE LEDGER
  app.get('/api/certificates', (req, res) => {
    res.json({ success: true, data: dbInstance.getState().certificates });
  });

  app.get('/api/certificates/verify/:hash', (req, res) => {
    const db = dbInstance.getState();
    const certificate = db.certificates.find(c => c.certificateHash === req.params.hash);
    if (!certificate) {
      return res.status(404).json({ success: false, message: 'Certificate verification failed: Ledger hash not registered.' });
    }
    res.json({ success: true, data: certificate });
  });

  app.post('/api/certificates', (req, res) => {
    const hash = Math.random().toString(36).substring(2) + Math.random().toString(36).substring(2);
    const newCert: Certificate = {
      id: `cert-${Date.now()}`,
      recipientId: req.body.recipientId || 'user-student',
      courseId: req.body.courseId || 'course-python',
      recipientName: req.body.recipientName || 'Rahul Sharma',
      courseTitle: req.body.courseTitle || 'Python Programming',
      certificateHash: hash,
      qrCodeUrl: `/verify/${hash}`,
      issuedAt: new Date().toISOString(),
      metadata: req.body.metadata || { grade: 'A', accreditationCode: `BVG-CR-${Date.now().toString().slice(-4)}` }
    };

    dbInstance.updateState(state => {
      state.certificates.push(newCert);
    });
    addLog(`Cryptographic certificate generated and signed for: ${newCert.recipientName}`);
    res.json({ success: true, data: newCert });
  });

  // ACTIVITY LOGS API
  app.get('/api/activities', (req, res) => {
    res.json({ success: true, data: activityLogs });
  });

  // PENDING AUDIT TASKS
  app.get('/api/tasks', (req, res) => {
    res.json({
      success: true,
      data: [
        { id: 't1', name: 'Course Approval Request', count: 18, color: 'text-indigo-600' },
        { id: 't2', name: 'Teacher Registrations', count: 24, color: 'text-amber-600' },
        { id: 't3', name: 'Flagged Community Threads', count: 7, color: 'text-rose-600' },
        { id: 't4', name: 'Pending Certificate Signings', count: 11, color: 'text-teal-600' },
        { id: 't5', name: 'Pending Refund Audits', count: 5, color: 'text-red-600' }
      ]
    });
  });

  // --- GEMINI POWERED VIDYA AI GATEWAY ---
  app.post('/api/gemini/tutor', async (req, res) => {
    const { prompt } = req.body;
    const ai = getGemini();

    if (!ai) {
      return res.status(400).json({ success: false, message: 'GEMINI_API_KEY missing from system configurations.' });
    }

    try {
      const response = await ai.models.generateContent({
        model: 'gemini-3.5-flash',
        contents: `You are Vidya, the official intelligent educational guide of the BrahmaVidya Galaxy Platform.
Our platform is a dynamic, multi-tier CMS & LMS.
Respond helpfully, authoritatively, and with exceptional clarity about educational concepts, computer science, mathematics, exam strategies, or system configurations.
Keep answers structured using professional markdown headers and clean bullet points.
User query: ${prompt}`
      });
      res.json({ success: true, reply: response.text });
    } catch (e: any) {
      res.status(500).json({ success: false, message: `Gemini API execution error: ${e.message}` });
    }
  });

  app.post('/api/ai/chat', async (req, res) => {
    const { message, history = [] } = req.body;
    const ai = getGemini();

    if (!ai) {
      // Graceful fallback when API key is missing or not configured
      return res.json({
        success: true,
        text: `🙏 **Welcome to BrahmaVidya!** I'm **Vidya**, your digital educational guide.\n\nTo unlock my full enterprise potential, please configure your **GEMINI_API_KEY** in the Secrets tab of the AI Studio workspace.\n\n*Interactive simulation response:*\nYou asked: "${message}". I can help design custom academic curriculum, format lesson schedules, generate mock exam tasks, and auto-moderate community forums instantly!`
      });
    }

    try {
      const response = await ai.models.generateContent({
        model: 'gemini-3.5-flash',
        contents: `You are Vidya, the official intelligent educational guide of the BrahmaVidya Galaxy Platform. 
Our platform is a dynamic, multi-tier CMS & LMS.
Respond helpfully, authoritatively, and with exceptional clarity about educational concepts, computer science, mathematics, exam strategies, or system configurations.
Keep answers structured using professional markdown headers and clean bullet points.
User query: ${message}`
      });
      res.json({ success: true, text: response.text });
    } catch (e: any) {
      res.status(500).json({ success: false, message: `Gemini API execution error: ${e.message}` });
    }
  });

  app.post('/api/ai/generate-curriculum', async (req, res) => {
    const { title } = req.body;
    const ai = getGemini();

    if (!ai) {
      // Simulate high-fidelity structured layout automatically
      const mockResult = [
        {
          type: 'MODULE',
          title: `Module 1: Introductory Foundations of ${title}`,
          description: 'A conceptual overview of core architectures and parameters.',
          children: [
            {
              type: 'LESSON',
              title: `Lesson 1.1: Syntax & Environment Setup for ${title}`,
              description: 'Bootstrapping runtime configurations and hello world compilations.',
              duration: '30 Mins'
            }
          ]
        },
        {
          type: 'MODULE',
          title: 'Module 2: Advanced Dynamic Layout Frameworks',
          description: 'Deep diving into memory structures and algorithmic scaling patterns.',
          children: [
            {
              type: 'LESSON',
              title: 'Lesson 2.1: Performance Optimizations',
              description: 'Designing sub-second rendering threads and minimizing resource overhead.',
              duration: '45 Mins'
            }
          ]
        }
      ];
      return res.json({ success: true, data: mockResult, simulated: true });
    }

    try {
      const prompt = `You are a curriculum design engine for BrahmaVidya Galaxy platform.
Generate a structured learning path for the course topic: "${title}".
Respond with raw JSON strictly following this schema structure:
[
  {
    "type": "MODULE",
    "title": "Module Title Here",
    "description": "Module description",
    "children": [
      {
        "type": "LESSON",
        "title": "Lesson Title Here",
        "description": "Lesson description here",
        "duration": "Duration here (e.g. 30 Mins)"
      }
    ]
  }
]
Do not wrap in markdown \`\`\`json block. Just output the raw parseable JSON list.`;

      const response = await ai.models.generateContent({
        model: 'gemini-3.5-flash',
        contents: prompt
      });

      let cleanText = response.text || '';
      // Sanitize standard LLM markdown syntax if generated
      cleanText = cleanText.replace(/```json/g, '').replace(/```/g, '').trim();

      const parsed = JSON.parse(cleanText);
      res.json({ success: true, data: parsed });
    } catch (e: any) {
      res.status(500).json({ success: false, message: `Curriculum generation failed: ${e.message}` });
    }
  });

  app.post('/api/ai/generate-quiz', async (req, res) => {
    const { topic } = req.body;
    const ai = getGemini();

    if (!ai) {
      const mockQuiz = [
        {
          question: `What is the primary constraint of scaling ${topic}?`,
          options: ['Network roundtrip latency', 'Static compile limitations', 'Sub-optimal CPU thread caching', 'Dynamic memory leakage'],
          answer: 'Network roundtrip latency'
        },
        {
          question: `Which architectural pattern is preferred for ${topic}?`,
          options: ['Modular Monolith', 'Tight-coupled distributed layout', 'Unstructured static script blocks', 'Stateless client rendering only'],
          answer: 'Modular Monolith'
        }
      ];
      return res.json({ success: true, data: mockQuiz, simulated: true });
    }

    try {
      const prompt = `Generate a 3-question multiple choice quiz for the educational topic: "${topic}".
Respond with raw parseable JSON of this schema:
[
  {
    "question": "Question text?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "answer": "Option A"
  }
]
Do not include any formatting or markdown blocks. Only output raw JSON.`;

      const response = await ai.models.generateContent({
        model: 'gemini-3.5-flash',
        contents: prompt
      });

      let cleanText = response.text || '';
      cleanText = cleanText.replace(/```json/g, '').replace(/```/g, '').trim();

      const parsed = JSON.parse(cleanText);
      res.json({ success: true, data: parsed });
    } catch (e: any) {
      res.status(500).json({ success: false, message: `Quiz generation failed: ${e.message}` });
    }
  });


  // --- BOOKSTORE API ---
  app.get('/api/books', (req, res) => {
    const db = dbInstance.getState();
    const books = db.books || [];
    const { category, tag, q } = req.query;
    let filtered = [...books];

    if (category) {
      filtered = filtered.filter(b => b.category.toLowerCase() === (category as string).toLowerCase());
    }
    if (tag) {
      filtered = filtered.filter(b => b.tags.some(t => t.toLowerCase() === (tag as string).toLowerCase()));
    }
    if (q) {
      const searchStr = (q as string).toLowerCase();
      filtered = filtered.filter(b => b.title.toLowerCase().includes(searchStr) || b.description.toLowerCase().includes(searchStr));
    }
    res.json({ success: true, data: filtered });
  });

  app.get('/api/books/:id', (req, res) => {
    const db = dbInstance.getState();
    const book = (db.books || []).find(b => b.id === req.params.id);
    if (!book) return res.status(404).json({ success: false, message: 'Book not found' });
    
    const reviews = (db.bookReviews || []).filter(r => r.bookId === book.id);
    res.json({ success: true, data: { ...book, reviews } });
  });

  app.post('/api/books/:id/reviews', (req, res) => {
    const { userId, userName, rating, comment } = req.body;
    const db = dbInstance.getState();
    const bookIndex = (db.books || []).findIndex(b => b.id === req.params.id);
    if (bookIndex === -1) return res.status(404).json({ success: false, message: 'Book not found' });

    const newReview = {
      id: `rev-${Date.now()}`,
      bookId: req.params.id,
      userId: userId || 'user-student',
      userName: userName || 'Rahul Sharma',
      rating: parseInt(rating) || 5,
      comment: comment || '',
      createdAt: new Date().toISOString()
    };

    dbInstance.updateState(state => {
      if (!state.bookReviews) state.bookReviews = [];
      state.bookReviews.push(newReview);

      const bReviews = state.bookReviews.filter(r => r.bookId === req.params.id);
      const totalRating = bReviews.reduce((acc, r) => acc + r.rating, 0);
      const avgRating = parseFloat((totalRating / bReviews.length).toFixed(1));

      if (state.books) {
        state.books[bookIndex].rating = avgRating;
        state.books[bookIndex].reviewsCount = bReviews.length;
      }
    });

    addLog(`Review added to "${db.books?.[bookIndex].title}" by ${userName}`);
    res.json({ success: true, data: newReview });
  });

  app.post('/api/books/generate-ebook', async (req, res) => {
    const { courseId, title } = req.body;
    const db = dbInstance.getState();
    const course = db.courseStructures.find(c => c.id === courseId);
    
    const ai = getGemini();
    let bookContent = '';
    
    if (ai) {
      try {
        const response = await ai.models.generateContent({
          model: 'gemini-3.5-flash',
          contents: `Generate a high-integrity study guide companion eBook based on the course program: "${course?.title || title}". Provide detailed introduction, core concepts chapters, and practice outlines. Return in beautiful clean markdown format.`
        });
        bookContent = response.text || '';
      } catch (err: any) {
        bookContent = `# ${title || course?.title}\n\nCompiled by Vidya AI Companion.\n\nCould not fetch deeper intelligence. Standard syllabus blueprint loaded correctly.`;
      }
    } else {
      bookContent = `# ${title || course?.title || 'Academic Companion Guide'}\n\nCompiled by Vidya AI Guide.\n\n## Chapter 1: Introduction\nBrahmaVidya platform facilitates content-agnostic curriculum generation with automatic digital micro-credential issuing.\n\n## Chapter 2: Key Concepts\nLearn about relational PostgreSQL indexing, Redis memory stores, and Celery workflow orchestration.`;
    }

    const newBook = {
      id: `book-gen-${Date.now()}`,
      title: `${course?.title || title} - Certified Companion eBook`,
      authorId: 'user-admin',
      authorName: 'Vidya AI Guide',
      category: 'Academic Guide',
      tags: ['AI-Generated', 'eBook', 'Companion'],
      description: `AI-generated study companion book compiled for syllabus: ${course?.title || title}. Includes certified concepts and reference guidelines.`,
      price: 0,
      coverUrl: 'https://images.unsplash.com/photo-1543002588-bfa74002ed7e?auto=format&fit=crop&q=80&w=300',
      fileFormat: 'PDF' as const,
      fileUrl: '#',
      isGeneratedEbook: true,
      rating: 5.0,
      reviewsCount: 0,
      bookmarksCount: 0,
      isPublished: true,
      createdAt: new Date().toISOString()
    };

    dbInstance.updateState(state => {
      if (!state.books) state.books = [];
      state.books.push(newBook);

      // Add to marketplace too
      if (!state.products) state.products = [];
      state.products.push({
        id: `prod-${newBook.id}`,
        name: newBook.title,
        type: 'BOOK',
        category: 'AI-Generated',
        description: newBook.description,
        price: 0,
        imageUrl: newBook.coverUrl,
        rating: 5.0,
        sellerId: 'user-admin',
        sellerName: 'Vidya AI Guide',
        tags: ['AI-Generated', 'Free'],
        createdAt: newBook.createdAt
      });
    });

    addLog(`Vidya AI successfully compiled companion eBook for: "${course?.title || title}"`);
    res.json({ success: true, data: { ...newBook, markdownContent: bookContent } });
  });


  // --- SELF PUBLISHING PLATFORM API ---
  app.get('/api/publishing/submissions', (req, res) => {
    const db = dbInstance.getState();
    const subs = db.submissions || [];
    const { userId } = req.query;
    
    let filtered = [...subs];
    if (userId) {
      filtered = filtered.filter(s => s.userId === userId);
    }
    res.json({ success: true, data: filtered });
  });

  app.post('/api/publishing/submissions', (req, res) => {
    const { userId, userName, title, category, description, fileFormat } = req.body;
    
    const newSub = {
      id: `subm-${Date.now()}`,
      userId: userId || 'user-student',
      userName: userName || 'Rahul Sharma',
      title: title || 'My Academic Thesis',
      category: category || 'General',
      description: description || '',
      coverUrl: 'https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&q=80&w=300',
      fileFormat: (fileFormat || 'PDF') as 'PDF' | 'EPUB',
      fileUrl: '#',
      status: 'PENDING' as const,
      isPaid: false,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    dbInstance.updateState(state => {
      if (!state.submissions) state.submissions = [];
      state.submissions.push(newSub);
    });

    addLog(`New book submission proposed by ${userName}: "${title}"`);
    res.json({ success: true, data: newSub });
  });

  app.post('/api/publishing/submissions/:id/pay', (req, res) => {
    const { userId } = req.body;
    const fee = 149;
    let error: string | null = null;
    let updatedSub: any = null;

    dbInstance.updateState(state => {
      const sub = (state.submissions || []).find(s => s.id === req.params.id);
      if (!sub) {
        error = 'Submission not found';
        return;
      }
      if (sub.isPaid) {
        error = 'Already paid';
        return;
      }

      const user = state.users.find(u => u.id === userId);
      if (!user) {
        error = 'User not found';
        return;
      }
      if (user.walletBalance < fee) {
        error = `Insufficient funds in academic wallet. Balance is ₹${user.walletBalance}. Required: ₹149.`;
        return;
      }

      // Deduct fee & log transaction
      user.walletBalance -= fee;
      sub.isPaid = true;
      sub.paymentTransactionId = `tx-pub-${Date.now()}`;
      sub.status = 'PENDING';
      sub.updatedAt = new Date().toISOString();

      if (!state.transactions) state.transactions = [];
      state.transactions.push({
        id: sub.paymentTransactionId,
        userId: user.id,
        userName: user.fullName,
        type: 'DEBIT',
        amount: fee,
        purpose: `₹149 Self Publishing Fee for "${sub.title}"`,
        status: 'SUCCESS',
        createdAt: new Date().toISOString()
      });

      updatedSub = sub;
    });

    if (error) {
      return res.status(400).json({ success: false, message: error });
    }

    addLog(`Self publishing setup fee ₹149 debited successfully for submission: "${updatedSub?.title}"`);
    res.json({ success: true, data: updatedSub });
  });

  app.post('/api/publishing/submissions/:id/review', (req, res) => {
    const { status, adminNotes } = req.body; // APPROVED or REJECTED
    let error: string | null = null;
    let updatedSub: any = null;

    dbInstance.updateState(state => {
      const sub = (state.submissions || []).find(s => s.id === req.params.id);
      if (!sub) {
        error = 'Submission not found';
        return;
      }
      sub.status = status;
      sub.adminNotes = adminNotes;
      sub.updatedAt = new Date().toISOString();

      if (status === 'APPROVED') {
        const newBook = {
          id: `book-${Date.now()}`,
          title: sub.title,
          authorId: sub.userId,
          authorName: sub.userName,
          category: sub.category,
          tags: ['Published', 'Self-Pub'],
          description: sub.description,
          price: 299, // default self-pub price
          coverUrl: sub.coverUrl,
          fileFormat: sub.fileFormat,
          fileUrl: sub.fileUrl,
          rating: 5.0,
          reviewsCount: 0,
          bookmarksCount: 0,
          isPublished: true,
          createdAt: new Date().toISOString()
        };

        if (!state.books) state.books = [];
        state.books.push(newBook);

        // Add to unified marketplace products catalog
        if (!state.products) state.products = [];
        state.products.push({
          id: `prod-${newBook.id}`,
          name: newBook.title,
          type: 'BOOK',
          category: newBook.category,
          description: newBook.description,
          price: newBook.price,
          imageUrl: newBook.coverUrl,
          rating: 5.0,
          sellerId: newBook.authorId,
          sellerName: newBook.authorName,
          tags: ['eBook', 'Self-Pub'],
          createdAt: newBook.createdAt
        });
      }
      updatedSub = sub;
    });

    if (error) {
      return res.status(400).json({ success: false, message: error });
    }

    addLog(`Self publishing book submission reviewed: "${updatedSub?.title}" -> ${status}`);
    res.json({ success: true, data: updatedSub });
  });


  // --- ROYALTY & REVENUE ENGINE API ---
  app.get('/api/royalties/statements', (req, res) => {
    const db = dbInstance.getState();
    const { authorId } = req.query;
    let stmts = db.royaltyStatements || [];
    
    if (authorId) {
      stmts = stmts.filter(s => s.authorId === authorId);
    }
    res.json({ success: true, data: stmts });
  });

  app.get('/api/royalties/withdrawals', (req, res) => {
    const db = dbInstance.getState();
    const { userId } = req.query;
    let wds = db.withdrawals || [];

    if (userId) {
      wds = wds.filter(w => w.userId === userId);
    }
    res.json({ success: true, data: wds });
  });

  app.post('/api/royalties/withdraw', (req, res) => {
    const { userId, amount, bankDetails } = req.body;
    let error: string | null = null;
    let newWd: any = null;

    dbInstance.updateState(state => {
      const user = state.users.find(u => u.id === userId);
      if (!user) {
        error = 'User not found';
        return;
      }
      if (user.walletBalance < amount) {
        error = `Insufficient wallet ledger balance. Requested: ₹${amount}, Balance: ₹${user.walletBalance}`;
        return;
      }

      user.walletBalance -= amount;

      newWd = {
        id: `wd-${Date.now()}`,
        userId: user.id,
        userName: user.fullName,
        amount: amount,
        status: 'PENDING' as const,
        bankDetails: bankDetails || 'Academic Settlement Account',
        createdAt: new Date().toISOString()
      };

      if (!state.withdrawals) state.withdrawals = [];
      state.withdrawals.push(newWd);

      if (!state.transactions) state.transactions = [];
      state.transactions.push({
        id: `tx-wd-${Date.now()}`,
        userId: user.id,
        userName: user.fullName,
        type: 'DEBIT',
        amount: amount,
        purpose: `Withdrawal Settlement Payout (Pending Bank Transfer)`,
        status: 'SUCCESS',
        createdAt: new Date().toISOString()
      });
    });

    if (error) {
      return res.status(400).json({ success: false, message: error });
    }

    addLog(`Withdrawal settlement request initiated for ${newWd?.userName} of ₹${amount}`);
    res.json({ success: true, data: newWd });
  });

  app.post('/api/royalties/withdrawals/:id/approve', (req, res) => {
    let error: string | null = null;
    let updatedWd: any = null;

    dbInstance.updateState(state => {
      const wd = (state.withdrawals || []).find(w => w.id === req.params.id);
      if (!wd) {
        error = 'Withdrawal request not found';
        return;
      }
      wd.status = 'APPROVED';
      wd.processedAt = new Date().toISOString();
      updatedWd = wd;
    });

    if (error) {
      return res.status(400).json({ success: false, message: error });
    }

    addLog(`Admin approved withdrawal payout: ₹${updatedWd?.amount} transferred to ${updatedWd?.userName}`);
    res.json({ success: true, data: updatedWd });
  });


  // --- MARKETPLACE & CART CHECKOUT API ---
  app.get('/api/marketplace/products', (req, res) => {
    const db = dbInstance.getState();
    const prods = db.products || [];
    const { type, q } = req.query;
    let filtered = [...prods];

    if (type) {
      filtered = filtered.filter(p => p.type === type);
    }
    if (q) {
      const searchStr = (q as string).toLowerCase();
      filtered = filtered.filter(p => p.name.toLowerCase().includes(searchStr) || p.description.toLowerCase().includes(searchStr));
    }
    res.json({ success: true, data: filtered });
  });

  app.post('/api/marketplace/cart/checkout', (req, res) => {
    const { userId, items, couponCode, billingAddress } = req.body;
    let error: string | null = null;
    let receipt: any = null;

    dbInstance.updateState(state => {
      const user = state.users.find(u => u.id === userId);
      if (!user) {
        error = 'User not found';
        return;
      }

      let subtotal = 0;
      const orderItems = [];

      for (const cartItem of items) {
        const prod = (state.products || []).find(p => p.id === cartItem.id);
        if (!prod) {
          error = `Product not found: ${cartItem.name}`;
          return;
        }
        subtotal += prod.price * (cartItem.quantity || 1);
        orderItems.push({
          productId: prod.id,
          productName: prod.name,
          productType: prod.type,
          price: prod.price,
          quantity: cartItem.quantity || 1
        });
      }

      let discount = 0;
      if (couponCode && couponCode.toUpperCase() === 'BVG10') {
        discount = parseFloat((subtotal * 0.1).toFixed(2));
      }

      const netPrice = subtotal - discount;
      const gst = parseFloat((netPrice * 0.18).toFixed(2)); // 18% GST standard accounting
      const total = parseFloat((netPrice + gst).toFixed(2));

      if (user.walletBalance < total) {
        error = `Insufficient Academic Wallet Balance. Required: ₹${total.toLocaleString()}, Balance: ₹${user.walletBalance.toLocaleString()}`;
        return;
      }

      // Deduct from buyer
      user.walletBalance = parseFloat((user.walletBalance - total).toFixed(2));

      const orderId = `ord-${Date.now()}`;
      const newOrder = {
        id: orderId,
        userId: user.id,
        userName: user.fullName,
        items: orderItems,
        subtotal,
        discount,
        gst,
        total,
        couponCode,
        status: 'COMPLETED' as const,
        createdAt: new Date().toISOString()
      };

      if (!state.orders) state.orders = [];
      state.orders.push(newOrder);

      // Create Invoice
      const invoiceId = `inv-${Date.now()}`;
      const newInvoice = {
        id: invoiceId,
        orderId: orderId,
        userId: user.id,
        userName: user.fullName,
        userEmail: user.email,
        billingAddress: billingAddress || 'Not Provided',
        subtotal,
        gstAmount: gst,
        total,
        pdfUrl: `/api/invoices/${invoiceId}/pdf`,
        createdAt: new Date().toISOString()
      };

      if (!state.invoices) state.invoices = [];
      state.invoices.push(newInvoice);

      // Distribute Payouts & Commission Engine (5% system commission, 95% royalty)
      if (!state.transactions) state.transactions = [];
      state.transactions.push({
        id: `tx-debit-${Date.now()}`,
        userId: user.id,
        userName: user.fullName,
        type: 'DEBIT',
        amount: total,
        purpose: `Purchased ${orderItems.length} items from BrahmaVidya catalog (Order: ${orderId})`,
        status: 'SUCCESS',
        createdAt: new Date().toISOString()
      });

      for (const item of orderItems) {
        const prod = (state.products || []).find(p => p.id === item.productId);
        if (prod) {
          const itemNet = item.price; // payout on base item price
          const commission = parseFloat((itemNet * 0.05).toFixed(2)); // 5% flat commission
          const sellerRoyalty = parseFloat((itemNet - commission).toFixed(2));

          const seller = state.users.find(u => u.id === prod.sellerId);
          if (seller) {
            seller.walletBalance = parseFloat((seller.walletBalance + sellerRoyalty).toFixed(2));

            // Log Seller Credit
            state.transactions.push({
              id: `tx-cred-${Date.now()}-${item.productId}`,
              userId: seller.id,
              userName: seller.fullName,
              type: 'CREDIT',
              amount: sellerRoyalty,
              purpose: `Royalty for "${item.productName}" (5% commission debited)`,
              status: 'SUCCESS',
              createdAt: new Date().toISOString()
            });

            // Create Royalty Statement
            if (!state.royaltyStatements) state.royaltyStatements = [];
            state.royaltyStatements.push({
              id: `stmt-${Date.now()}-${item.productId}`,
              authorId: seller.id,
              authorName: seller.fullName,
              month: new Date().toISOString().substring(0, 7),
              totalSales: 1,
              grossRevenue: itemNet,
              commission: commission,
              netRoyalty: sellerRoyalty,
              isPaid: true,
              paidAt: new Date().toISOString()
            });
          }
        }
      }

      receipt = { order: newOrder, invoice: newInvoice };
    });

    if (error) {
      return res.status(400).json({ success: false, message: error });
    }

    addLog(`Marketplace order processed successfully. Order ID: ${receipt?.order.id}. Total debited: ₹${receipt?.order.total}`);
    res.json({ success: true, data: receipt });
  });

  app.get('/api/marketplace/orders', (req, res) => {
    const db = dbInstance.getState();
    const { userId } = req.query;
    let ords = db.orders || [];

    if (userId) {
      ords = ords.filter(o => o.userId === userId);
    }
    res.json({ success: true, data: ords });
  });

  app.get('/api/marketplace/invoices', (req, res) => {
    const db = dbInstance.getState();
    const { userId } = req.query;
    let invs = db.invoices || [];

    if (userId) {
      invs = invs.filter(i => i.userId === userId);
    }
    res.json({ success: true, data: invs });
  });


  // --- SERVICE MARKETPLACE API ---
  app.post('/api/marketplace/services/request', (req, res) => {
    const { userId, userName, serviceType, description, budget } = req.body;
    const newReq = {
      id: `req-${Date.now()}`,
      userId: userId || 'user-student',
      userName: userName || 'Rahul Sharma',
      serviceType: serviceType || 'Branding',
      description: description || '',
      budget: parseInt(budget) || 1000,
      status: 'PENDING' as const,
      createdAt: new Date().toISOString()
    };

    dbInstance.updateState(state => {
      if (!state.serviceRequests) state.serviceRequests = [];
      state.serviceRequests.push(newReq);
    });

    addLog(`New Service Request created by ${userName}: "${serviceType}"`);
    res.json({ success: true, data: newReq });
  });

  app.get('/api/marketplace/services/requests', (req, res) => {
    const db = dbInstance.getState();
    const { userId } = req.query;
    let reqs = db.serviceRequests || [];

    if (userId) {
      reqs = reqs.filter(r => r.userId === userId);
    }
    res.json({ success: true, data: reqs });
  });

  app.post('/api/marketplace/services/quotations', (req, res) => {
    const { requestId, teacherId, teacherName, amount, timelineDays, notes } = req.body;
    let error: string | null = null;
    let newQ: any = null;

    dbInstance.updateState(state => {
      const sRequest = (state.serviceRequests || []).find(r => r.id === requestId);
      if (!sRequest) {
        error = 'Service request not found';
        return;
      }

      newQ = {
        id: `q-${Date.now()}`,
        requestId,
        teacherId,
        teacherName,
        amount: parseInt(amount),
        timelineDays: parseInt(timelineDays),
        notes: notes || '',
        status: 'PENDING' as const,
        createdAt: new Date().toISOString()
      };

      if (!state.quotations) state.quotations = [];
      state.quotations.push(newQ);

      sRequest.status = 'QUOTED';
    });

    if (error) {
      return res.status(400).json({ success: false, message: error });
    }

    addLog(`Teacher ${teacherName} submitted project quotation of ₹${amount} for service request ${requestId}`);
    res.json({ success: true, data: newQ });
  });

  app.get('/api/marketplace/services/quotations', (req, res) => {
    const db = dbInstance.getState();
    const { requestId } = req.query;
    let qts = db.quotations || [];

    if (requestId) {
      qts = qts.filter(q => q.requestId === requestId);
    }
    res.json({ success: true, data: qts });
  });

  app.post('/api/marketplace/services/quotations/:id/accept', (req, res) => {
    const { userId } = req.body;
    let error: string | null = null;
    let updatedQuote: any = null;

    dbInstance.updateState(state => {
      const quote = (state.quotations || []).find(q => q.id === req.params.id);
      if (!quote) {
        error = 'Quotation not found';
        return;
      }

      const sReq = (state.serviceRequests || []).find(r => r.id === quote.requestId);
      if (!sReq) {
        error = 'Request not found';
        return;
      }

      const user = state.users.find(u => u.id === userId);
      if (!user) {
        error = 'User not found';
        return;
      }

      if (user.walletBalance < quote.amount) {
        error = `Insufficient wallet ledger balance. Required quotation budget: ₹${quote.amount}, Balance: ₹${user.walletBalance}`;
        return;
      }

      const teacher = state.users.find(u => u.id === quote.teacherId);
      if (!teacher) {
        error = 'Service provider not found';
        return;
      }

      // Debit student, credit teacher (95% to teacher, 5% commission)
      const commission = parseFloat((quote.amount * 0.05).toFixed(2));
      const netPay = parseFloat((quote.amount - commission).toFixed(2));

      user.walletBalance = parseFloat((user.walletBalance - quote.amount).toFixed(2));
      teacher.walletBalance = parseFloat((teacher.walletBalance + netPay).toFixed(2));

      quote.status = 'ACCEPTED';
      sReq.status = 'ACCEPTED';

      // Log transactions
      if (!state.transactions) state.transactions = [];
      state.transactions.push({
        id: `tx-serv-deb-${Date.now()}`,
        userId: user.id,
        userName: user.fullName,
        type: 'DEBIT',
        amount: quote.amount,
        purpose: `Accepted Quotation for Service: ${sReq.serviceType}`,
        status: 'SUCCESS',
        createdAt: new Date().toISOString()
      });

      state.transactions.push({
        id: `tx-serv-cred-${Date.now()}`,
        userId: teacher.id,
        userName: teacher.fullName,
        type: 'CREDIT',
        amount: netPay,
        purpose: `Client accepted quotation for Service: ${sReq.serviceType} (5% flat commission debited)`,
        status: 'SUCCESS',
        createdAt: new Date().toISOString()
      });

      updatedQuote = quote;
    });

    if (error) {
      return res.status(400).json({ success: false, message: error });
    }

    addLog(`Quotation accepted and project started! Client ${userId} funded ₹${updatedQuote?.amount}`);
    res.json({ success: true, data: updatedQuote });
  });


  // --- TRANSACTIONS API ---
  app.get('/api/finance/transactions', (req, res) => {
    const db = dbInstance.getState();
    const { userId } = req.query;
    let txs = db.transactions || [];

    if (userId) {
      txs = txs.filter(t => t.userId === userId);
    }
    res.json({ success: true, data: txs });
  });


  // --- GLOBAL SEARCH API ---
  app.get('/api/search', (req, res) => {
    const db = dbInstance.getState();
    const query = (req.query.q as string || '').toLowerCase();

    if (!query) {
      return res.json({ success: true, data: { books: [], courses: [], blogs: [], tutorials: [], services: [] } });
    }

    const books = (db.books || []).filter(b => b.title.toLowerCase().includes(query) || b.description.toLowerCase().includes(query));
    const courses = db.courseStructures.filter(c => c.type === 'COURSE' && (c.title.toLowerCase().includes(query) || c.description.toLowerCase().includes(query)));
    const blogs = (db.blogs || []).filter(b => b.title.toLowerCase().includes(query) || b.content.toLowerCase().includes(query));
    const tutorials = (db.tutorials || []).filter(t => t.title.toLowerCase().includes(query) || t.content.toLowerCase().includes(query));
    const services = (db.products || []).filter(p => p.type === 'SERVICE' && (p.name.toLowerCase().includes(query) || p.description.toLowerCase().includes(query)));

    res.json({
      success: true,
      data: { books, courses, blogs, tutorials, services }
    });
  });

  // --- REAL-TIME NOTIFICATIONS (SSE) ---
  interface SseClient {
    userId: string;
    res: express.Response;
  }
  let sseClients: SseClient[] = [];

  // Redis Pub/Sub receiver setup
  try {
    const { createClient } = require('redis');
    const client = createClient({ url: process.env.REDIS_URL || 'redis://localhost:6379' });
    client.on('error', (err: any) => console.debug('[REDIS CLIENT ERROR]', err.message));
    client.connect().then(() => {
      const redisSub = client.duplicate();
      redisSub.connect().then(() => {
        redisSub.subscribe('notifications_pubsub', (message: string) => {
          try {
            const payload = JSON.parse(message);
            const { user_id, event, data } = payload;
            const targets = sseClients.filter(c => c.userId === user_id);
            targets.forEach(tgt => {
              tgt.res.write(`data: ${JSON.stringify({ event, data })}\n\n`);
            });
          } catch (e) {
            console.error('Failed to parse pub/sub message:', e);
          }
        }).catch((e: any) => console.debug('Redis subscribe failed:', e.message));
      }).catch((e: any) => console.debug('Redis duplicate client connect failed:', e.message));
    }).catch((e: any) => console.debug('Redis main client connect failed:', e.message));
  } catch (e) {
    console.warn('[REDIS PUB/SUB WARN] Realtime engine running in fallback mode:', (e as Error).message);
  }

  app.get('/api/realtime/notifications', (req, res) => {
    const userId = req.query.userId as string;
    if (!userId) {
      return res.status(400).json({ error: 'Missing userId parameter' });
    }

    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
      'X-Accel-Buffering': 'no'
    });

    res.write('retry: 5000\n\n');
    res.write(`data: ${JSON.stringify({ event: 'connected', time: new Date().toISOString() })}\n\n`);

    const client: SseClient = { userId, res };
    sseClients.push(client);

    const heartbeat = setInterval(() => {
      res.write(':\n\n');
    }, 15000);

    req.on('close', () => {
      clearInterval(heartbeat);
      sseClients = sseClients.filter(c => c !== client);
    });
  });

  // --- VITE DEV MIDDLEWARE / STATIC SERVING ---
  const isProduction = process.env.NODE_ENV === 'production';
  
  if (!isProduction) {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'custom'
    });
    app.use(vite.middlewares);

    app.use('*', async (req, res, next) => {
      const url = req.originalUrl;
      try {
        let template = fs.readFileSync(path.resolve('.', 'index.html'), 'utf-8');
        template = await vite.transformIndexHtml(url, template);
        res.status(200).set({ 'Content-Type': 'text/html' }).end(template);
      } catch (e) {
        vite.ssrFixStacktrace(e as Error);
        next(e);
      }
    });
  } else {
    // Serve static files from built dist folder
    app.use(express.static(path.resolve('dist')));
    app.get('*', (req, res) => {
      res.sendFile(path.resolve('dist', 'index.html'));
    });
  }

  const port = 3000;
  app.listen(port, '0.0.0.0', () => {
    console.log(`BrahmaVidya Galaxy enterprise server running at http://localhost:${port}`);
  });
}

startServer().catch(err => {
  console.error('Fatal backend bootstrap crash:', err);
});
