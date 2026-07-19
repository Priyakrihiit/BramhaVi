/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import * as Lucide from 'lucide-react';

interface DynamicIconProps {
  name: string;
  className?: string;
  size?: number;
}

export default function DynamicIcon({ name, className = '', size = 18 }: DynamicIconProps) {
  // Map strings to Lucide icon components dynamically
  const IconComponent = (Lucide as any)[name];
  
  if (!IconComponent) {
    // Return a fallback icon
    return <Lucide.HelpCircle className={className} size={size} />;
  }

  return <IconComponent className={className} size={size} />;
}
