/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { Page, CourseStructure } from '../types';
import { api } from '../services/api';

export type PlatformView = 'portal' | 'admin';

interface LayoutContextType {
  currentView: PlatformView;
  setView: (view: PlatformView) => void;
  activeAdminTab: string;
  setAdminTab: (tab: string) => void;
  pages: Page[];
  isLoadingPages: boolean;
  refreshPages: () => Promise<void>;
  selectedCourse: CourseStructure | null;
  setSelectedCourse: (course: CourseStructure | null) => void;
  activeLesson: CourseStructure | null;
  setActiveLesson: (lesson: CourseStructure | null) => void;
  activeQuiz: any[] | null;
  setActiveQuiz: (quiz: any[] | null) => void;
  currentPath: string;
  navigateTo: (path: string) => void;
}

const LayoutContext = createContext<LayoutContextType | undefined>(undefined);

export const LayoutProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentView, setView] = useState<PlatformView>('portal');
  const [activeAdminTab, setAdminTab] = useState<string>('dashboard');
  const [pages, setPages] = useState<Page[]>([]);
  const [isLoadingPages, setIsLoadingPages] = useState<boolean>(true);
  
  // LMS Interactive State
  const [selectedCourse, setSelectedCourseState] = useState<CourseStructure | null>(null);
  const [activeLesson, setActiveLessonState] = useState<CourseStructure | null>(null);
  const [activeQuiz, setActiveQuiz] = useState<any[] | null>(null);

  // Client Routing State (Hash-based router for seamless iframe safety and zero page reloads)
  const [currentPath, setCurrentPath] = useState<string>(() => {
    return window.location.hash.replace('#', '') || '/';
  });

  const navigateTo = useCallback((path: string) => {
    window.location.hash = path;
    setCurrentPath(path);
    // Auto coordinate portal vs admin view based on prefix
    if (path.startsWith('/admin')) {
      setView('admin');
      const tab = path.replace('/admin/', '') || 'dashboard';
      setAdminTab(tab);
    } else {
      setView('portal');
    }
  }, []);

  const setSelectedCourse = useCallback((course: CourseStructure | null) => {
    setSelectedCourseState(course);
    if (course) {
      navigateTo(`/courses/${course.id}`);
    } else {
      navigateTo('/courses');
    }
  }, [navigateTo]);

  const setActiveLesson = useCallback((lesson: CourseStructure | null) => {
    setActiveLessonState(lesson);
    setActiveQuiz(null); // Clear quiz on lesson switch
    if (lesson && selectedCourse) {
      navigateTo(`/courses/${selectedCourse.id}/lessons/${lesson.id}`);
    }
  }, [selectedCourse, navigateTo]);

  const refreshPages = useCallback(async () => {
    setIsLoadingPages(true);
    try {
      const res = await api.pages.list();
      if (res.success && res.data) {
        setPages(res.data);
      }
    } catch (err) {
      console.error('Failed to fetch pages:', err);
    } finally {
      setIsLoadingPages(false);
    }
  }, []);

  // Listen to hash changes for routing
  useEffect(() => {
    const handleHashChange = () => {
      const path = window.location.hash.replace('#', '') || '/';
      setCurrentPath(path);
      if (path.startsWith('/admin')) {
        setView('admin');
        const tab = path.replace('/admin/', '') || 'dashboard';
        setAdminTab(tab);
      } else {
        setView('portal');
      }
    };

    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  useEffect(() => {
    refreshPages();
  }, [refreshPages]);

  return (
    <React.Fragment>
      <LayoutContext.Provider
        value={{
          currentView,
          setView,
          activeAdminTab,
          setAdminTab,
          pages,
          isLoadingPages,
          refreshPages,
          selectedCourse,
          setSelectedCourse,
          activeLesson,
          setActiveLesson,
          activeQuiz,
          setActiveQuiz,
          currentPath,
          navigateTo,
        }}
      >
        {children}
      </LayoutContext.Provider>
    </React.Fragment>
  );
};

export const useLayoutStore = () => {
  const context = useContext(LayoutContext);
  if (!context) {
    throw new Error('useLayoutStore must be used within a LayoutProvider');
  }
  return context;
};
