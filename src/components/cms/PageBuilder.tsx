import React, { useEffect, useState } from 'react';
import { cmsApi } from '../../services/cmsApi';
import { Layout, Plus, Trash2, Edit, Save, FileCode } from 'lucide-react';

export const PageBuilder: React.FC = () => {
  const [blocks, setBlocks] = useState<any[]>([]);
  const [templates, setTemplates] = useState<any[]>([]);
  const [selectedBlock, setSelectedBlock] = useState<any | null>(null);

  // Form
  const [blockName, setBlockName] = useState('');
  const [blockType, setBlockType] = useState('hero');
  const [displayOrder, setDisplayOrder] = useState(0);

  const loadData = async () => {
    try {
      const blockRes = await cmsApi.blocks.list();
      const templateRes = await cmsApi.templates.list();
      if (blockRes.success && blockRes.data) {
        setBlocks(blockRes.data);
      }
      if (templateRes.success && templateRes.data) {
        setTemplates(templateRes.data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateBlock = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await cmsApi.blocks.create({
      name: blockName,
      block_type: blockType,
      display_order: displayOrder,
      content_data: {}
    });
    if (res.success) {
      setBlockName('');
      loadData();
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <div className="lg:col-span-8 p-5 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono text-indigo-400">Content Blocks Canvas</h3>
            <p className="text-xs text-slate-500">Structured layout modules on page instances</p>
          </div>
        </div>

        <div className="space-y-3">
          {blocks.length === 0 ? (
            <div className="p-8 text-center bg-slate-950 border border-slate-850 rounded-xl text-slate-500 text-xs italic">
              No page content blocks built yet. Create one on the right.
            </div>
          ) : (
            blocks.map((block: any) => (
              <div key={block.id} className="p-4 bg-slate-950 border border-slate-800 rounded-xl flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Layout className="text-indigo-400" size={16} />
                  <div>
                    <span className="block font-semibold text-slate-200 text-xs">{block.name}</span>
                    <span className="block text-[10px] text-slate-500 font-mono">TYPE: {block.block_type} | ORDER: {block.display_order}</span>
                  </div>
                </div>
                <button
                  onClick={async () => {
                    await cmsApi.blocks.delete(block.id);
                    loadData();
                  }}
                  className="p-1.5 hover:bg-red-950/30 text-slate-500 hover:text-red-400 rounded-lg transition"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="lg:col-span-4 p-5 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
        <h4 className="text-xs font-bold text-white uppercase tracking-widest font-mono text-indigo-400">Add Content Block</h4>
        <form onSubmit={handleCreateBlock} className="space-y-4">
          <div>
            <label className="block text-[10px] uppercase font-bold text-slate-400 font-mono mb-1">Block Name</label>
            <input
              type="text"
              required
              value={blockName}
              onChange={e => setBlockName(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
              placeholder="E.g. Header Welcome Banner"
            />
          </div>

          <div>
            <label className="block text-[10px] uppercase font-bold text-slate-400 font-mono mb-1">Block Type</label>
            <select
              value={blockType}
              onChange={e => setBlockType(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
            >
              <option value="hero">Hero Segment</option>
              <option value="features">Feature Grid</option>
              <option value="text">Rich Text Blocks</option>
              <option value="stats">Telemetry Statistics</option>
            </select>
          </div>

          <div>
            <label className="block text-[10px] uppercase font-bold text-slate-400 font-mono mb-1">Order</label>
            <input
              type="number"
              value={displayOrder}
              onChange={e => setDisplayOrder(parseInt(e.target.value) || 0)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
            />
          </div>

          <button
            type="submit"
            className="w-full py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-xl shadow-lg shadow-indigo-600/20 transition flex items-center justify-center gap-2"
          >
            <Plus size={14} />
            Build Module
          </button>
        </form>
      </div>
    </div>
  );
};
