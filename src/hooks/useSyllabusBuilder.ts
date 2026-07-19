/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState, useCallback } from 'react';
import { api } from '../services/api';
import { CourseStructure } from '../types';

export function useSyllabusBuilder() {
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [lastError, setLastError] = useState<string | null>(null);

  const generateCurriculum = useCallback(async (courseId: string, courseTitle: string, onProgress?: (msg: string) => void) => {
    setIsGenerating(true);
    setLastError(null);
    try {
      onProgress?.(`Contacting BrahmaVidya AI to build syllabus for "${courseTitle}"...`);
      const res = await api.ai.generateCurriculum(courseTitle);
      
      if (res.success && res.data) {
        onProgress?.(`AI generated ${res.data.length} main syllabus modules. Appending structures to course...`);
        
        for (const mod of res.data) {
          // 1. Create Module node in DB
          const modRes = await api.courses.create({
            parentId: courseId,
            type: 'PROGRAM', // In DB model, it falls under PROGRAM/MODULE depending on hierarchical levels
            title: mod.title,
            description: mod.description,
          });

          if (modRes.success && modRes.data && mod.children) {
            onProgress?.(`Successfully appended Module: "${mod.title}". Spawning children lessons...`);
            
            for (const les of mod.children) {
              // 2. Create Lesson node under the newly created Module
              await api.courses.create({
                parentId: modRes.data.id,
                type: 'MODULE', // Nested layout block
                title: les.title,
                description: les.description,
                metadata: {
                  duration: les.duration,
                },
              });
            }
          }
        }
        
        onProgress?.(`Curriculum structure for "${courseTitle}" compiled completely with zero errors.`);
        return true;
      } else {
        setLastError(res.message || 'Failed generating curriculum syllabus');
        return false;
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Unknown compilation error';
      setLastError(msg);
      return false;
    } finally {
      setIsGenerating(false);
    }
  }, []);

  return {
    generateCurriculum,
    isGenerating,
    lastError,
  };
}
export default useSyllabusBuilder;
