/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { AuthProvider, useAuthStore } from './stores/authStore';
import { ThemeProvider } from './stores/themeStore';
import { MenuProvider } from './stores/menuStore';
import { LayoutProvider, useLayoutStore } from './stores/layoutStore';
import { GlobalSystemProvider } from './stores/globalSystemStore';

// Layouts
import PortalLayout from './layouts/PortalLayout';
import AdminLayout from './layouts/AdminLayout';

// Pages Shells
import HomeShell from './pages/public/HomeShell';
import CoursesShell from './pages/public/CoursesShell';
import CertificatesShell from './pages/public/CertificatesShell';
import DashboardShell from './pages/admin/DashboardShell';
import PageBuilderShell from './pages/admin/PageBuilderShell';
import EnterpriseCMSShell from './pages/admin/EnterpriseCMSShell';
import MenusManagerShell from './pages/admin/MenusManagerShell';
import BlogsManagerShell from './pages/admin/BlogsManagerShell';
import TutorialsManagerShell from './pages/admin/TutorialsManagerShell';

import AuthPage from './pages/public/AuthPage';
import SimplePages from './pages/public/SimplePages';
import TutorialsPage from './pages/public/TutorialsPage';
import BookstoreDetailPage from './pages/public/BookstoreDetailPage';
import ServicesPage from './pages/public/ServicesPage';
import TemplatesPage from './pages/public/TemplatesPage';
import BlogsPage from './pages/public/BlogsPage';
import CommunityPage from './pages/public/CommunityPage';
import BecomePartnerPage from './pages/public/BecomePartnerPage';
import { PaymentsDashboard } from './pages/public/PaymentsDashboard';

// Dynamic Subsystems V1.KP
import { BookstoreView } from './components/bookstore/BookstoreView';
import { MarketplaceView } from './components/marketplace/MarketplaceView';
import { EnhancedDashboardView } from './components/dashboard/EnhancedDashboardView';
import { StudentDashboard } from './components/student/StudentDashboard';
import { GlobalSearchView } from './components/search/GlobalSearchView';
import { SaaSSuiteView } from './components/enterprise/SaaSSuiteView';
import { EnterpriseAnalyticsView } from './components/analytics/EnterpriseAnalyticsView';

// Main Router Switch
const RouterDispatcher: React.FC = () => {
  const { currentPath, currentView } = useLayoutStore();
  const { currentUser, refreshProfile } = useAuthStore();

  // 1. Dispatch Administrative Views
  if (currentView === 'admin') {
    return (
      <AdminLayout>
        {(() => {
          if (currentPath === '/admin/pages') {
            return <PageBuilderShell />;
          }
          if (currentPath === '/admin/cms') {
            return <EnterpriseCMSShell />;
          }
          if (currentPath === '/admin/menus') {
            return <MenusManagerShell />;
          }
          if (currentPath === '/admin/blogs') {
            return <BlogsManagerShell />;
          }
          if (currentPath === '/admin/tutorials') {
            return <TutorialsManagerShell />;
          }
          if (currentPath === '/admin/analytics') {
            return <EnterpriseAnalyticsView />;
          }
          // Default fallback administrative tab is Dashboard controls
          return <DashboardShell />;
        })()}
      </AdminLayout>
    );
  }

  // 2. Dispatch Public Views
  return (
    <PortalLayout>
      {(() => {
        if (currentPath === '/auth') {
          return <AuthPage />;
        }
        if (['/about', '/pricing', '/faq', '/careers', '/contact', '/privacy', '/terms'].includes(currentPath)) {
          return <SimplePages />;
        }
        if (currentPath === '/tutorials' || currentPath.startsWith('/tutorials/')) {
          return <TutorialsPage />;
        }
        if (currentPath === '/certificates') {
          return <CertificatesShell />;
        }
        if (currentPath === '/courses' || currentPath.startsWith('/courses/')) {
          return <CoursesShell />;
        }
        if (currentPath === '/bookstore') {
          return <BookstoreView currentUser={currentUser} onRefreshWallet={refreshProfile} />;
        }
        if (currentPath === '/payments' || currentPath.startsWith('/payments/')) {
          return <PaymentsDashboard currentUser={currentUser} onRefreshWallet={refreshProfile} />;
        }
        if (currentPath.startsWith('/bookstore/')) {
          return <BookstoreDetailPage />;
        }
        if (currentPath === '/marketplace') {
          return <MarketplaceView currentUser={currentUser} onRefreshWallet={refreshProfile} />;
        }
        if (currentPath === '/services' || currentPath.startsWith('/services/')) {
          return <ServicesPage />;
        }
        if (currentPath === '/portfolio' || currentPath === '/resumes') {
          return <TemplatesPage />;
        }
        if (currentPath === '/blogs' || currentPath.startsWith('/blogs/')) {
          return <BlogsPage />;
        }
        if (currentPath === '/community' || currentPath.startsWith('/community/')) {
          return <CommunityPage />;
        }
        if (['/become-teacher', '/become-author', '/become-provider'].includes(currentPath)) {
          return <BecomePartnerPage />;
        }
        if (currentPath === '/dashboard' || currentPath.startsWith('/teacher')) {
          return <EnhancedDashboardView currentUser={currentUser} onRefreshWallet={refreshProfile} />;
        }
        if (currentPath === '/student') {
          return <StudentDashboard currentUser={currentUser} />;
        }
        if (currentPath === '/saas') {
          return <SaaSSuiteView />;
        }
        if (currentPath === '/search') {
          return <GlobalSearchView />;
        }
        // Fallback default landing view
        return <HomeShell />;
      })()}
    </PortalLayout>
  );
};

export default function App() {
  return (
    <React.Fragment>
      <GlobalSystemProvider>
        <AuthProvider>
          <ThemeProvider>
            <MenuProvider>
              <LayoutProvider>
                <RouterDispatcher />
              </LayoutProvider>
            </MenuProvider>
          </ThemeProvider>
        </AuthProvider>
      </GlobalSystemProvider>
    </React.Fragment>
  );
}
