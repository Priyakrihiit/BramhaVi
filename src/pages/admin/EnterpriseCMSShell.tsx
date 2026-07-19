import React, { useState } from 'react';
import { CMSDashboard } from '../../components/cms/CMSDashboard';
import { PageBuilder } from '../../components/cms/PageBuilder';
import { ArticleEditor } from '../../components/cms/ArticleEditor';
import { BlogEditor } from '../../components/cms/BlogEditor';
import { EnterpriseMediaLibrary } from '../../components/cms/EnterpriseMediaLibrary';
import { CategoryManager } from '../../components/cms/CategoryManager';
import { TagManager } from '../../components/cms/TagManager';
import { WorkflowManager } from '../../components/cms/WorkflowManager';
import { RevisionHistory } from '../../components/cms/RevisionHistory';
import { SEODashboard } from '../../components/cms/SEODashboard';
import { CMSSettings } from '../../components/cms/CMSSettings';
import { CommentModeration } from '../../components/cms/CommentModeration';
import { Search } from '../../components/cms/Search';
import { FAQManager } from '../../components/cms/FAQManager';

import { LayoutDashboard, FileText, Layout, FolderTree, Tag, ShieldAlert, History, Globe, Settings, MessageSquare, Search as SearchIcon, HelpCircle, Image } from 'lucide-react';

const TABS = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, component: CMSDashboard },
  { id: 'pagebuilder', label: 'Page Builder', icon: Layout, component: PageBuilder },
  { id: 'articles', label: 'Articles', icon: FileText, component: ArticleEditor },
  { id: 'blogs', label: 'Blogs', icon: FileText, component: BlogEditor },
  { id: 'media', label: 'Media Library', icon: Image, component: EnterpriseMediaLibrary },
  { id: 'categories', label: 'Categories', icon: FolderTree, component: CategoryManager },
  { id: 'tags', label: 'Tags', icon: Tag, component: TagManager },
  { id: 'workflow', label: 'Workflow', icon: ShieldAlert, component: WorkflowManager },
  { id: 'revisions', label: 'Revisions', icon: History, component: RevisionHistory },
  { id: 'seo', label: 'SEO', icon: Globe, component: SEODashboard },
  { id: 'settings', label: 'Settings', icon: Settings, component: CMSSettings },
  { id: 'moderation', label: 'Moderation', icon: MessageSquare, component: CommentModeration },
  { id: 'search', label: 'Search Index', icon: SearchIcon, component: Search },
  { id: 'faq', label: 'FAQ', icon: HelpCircle, component: FAQManager },
];

export const EnterpriseCMSShell: React.FC = () => {
  const [activeTab, setActiveTab] = useState('dashboard');

  const ActiveComponent = TABS.find(t => t.id === activeTab)?.component || CMSDashboard;

  return (
    <div className="space-y-6">
      {/* Tab Navigation header */}
      <div className="flex flex-wrap gap-2 border-b border-indigo-950/80 pb-4">
        {TABS.map(tab => {
          const Icon = tab.icon;
          const isActive = tab.id === activeTab;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-3 py-2 text-xs font-semibold rounded-xl border transition ${isActive ? 'bg-indigo-600/20 text-indigo-200 border-indigo-500' : 'bg-slate-900 border-slate-800 text-slate-400 hover:bg-slate-850 hover:text-white'}`}
            >
              <Icon size={14} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Workspace panel */}
      <div className="bg-slate-950/30 rounded-2xl">
        <ActiveComponent />
      </div>
    </div>
  );
};

export default EnterpriseCMSShell;
