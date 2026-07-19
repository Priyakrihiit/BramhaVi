/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import {
  Globe,
  RefreshCw,
  Layout,
  DollarSign,
  Clock,
  CheckCircle,
  HelpCircle,
  Sliders,
  Sparkles
} from 'lucide-react';

export const ProdModule11I18n: React.FC = () => {
  const [lang, setLang] = useState<'EN' | 'HI' | 'AR'>('EN');
  const [isRtl, setIsRtl] = useState<boolean>(false);
  const [currency, setCurrency] = useState<'INR' | 'USD'>('INR');
  const [timezone, setTimezone] = useState<string>('IST');

  // Multi-lingual translation mapping dictionary
  const TRANSLATIONS = {
    EN: {
      title: 'Welcome to BrahmaVidya SaaS Hub',
      desc: 'Interact with all 15 operational business modules from our comprehensive enterprise roadmap.',
      btn: 'Deploy Cluster Instance',
      currencySym: '₹',
      price: '₹14,999'
    },
    HI: {
      title: 'ब्रह्मविद्या SaaS हब में आपका स्वागत है',
      desc: 'हमारे व्यापक उद्यम रोडमैप से सभी १५ परिचालन व्यावसायिक मॉड्यूल के साथ बातचीत करें।',
      btn: 'क्लस्टर इंस्टेंस तैनात करें',
      currencySym: '₹',
      price: '₹१४,९९९'
    },
    AR: {
      title: 'مرحباً بك في مركز بوابة براهمابيديا',
      desc: 'تفاعل مع جميع وحدات الأعمال التشغيلية الـ 15 من خريطة طريق المؤسسة الشاملة لدينا.',
      btn: 'نشر مثيل المجموعة',
      currencySym: '$',
      price: '$180'
    }
  };

  const handleLangChange = (selected: 'EN' | 'HI' | 'AR') => {
    setLang(selected);
    if (selected === 'AR') {
      setIsRtl(true);
    } else {
      setIsRtl(false);
    }
  };

  const currentText = TRANSLATIONS[lang];

  return (
    <div id="i18n-root" className="space-y-6">
      {/* Settings Panel Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-left">
        <div className="bg-slate-950/50 border border-slate-900 rounded-xl p-4 space-y-2">
          <div className="flex justify-between items-start">
            <span className="text-[10px] text-slate-500 font-mono font-bold uppercase">Language Selection</span>
            <Globe className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="flex gap-1.5 mt-2">
            {(['EN', 'HI', 'AR'] as const).map(l => (
              <button
                key={l}
                onClick={() => handleLangChange(l)}
                className={`flex-1 text-[10px] font-mono font-bold px-2 py-1 rounded border transition ${lang === l ? 'bg-indigo-600 border-indigo-500 text-white' : 'bg-slate-900 border-slate-800 text-slate-400'}`}
              >
                {l === 'EN' ? 'English' : l === 'HI' ? 'हिंदी' : 'العربية'}
              </button>
            ))}
          </div>
        </div>

        <div className="bg-slate-950/50 border border-slate-900 rounded-xl p-4 space-y-2">
          <div className="flex justify-between items-start">
            <span className="text-[10px] text-slate-500 font-mono font-bold uppercase">RTL Layout Mirroring</span>
            <Layout className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="flex items-center gap-2 mt-3">
            <input
              type="checkbox"
              id="rtl-toggle"
              checked={isRtl}
              onChange={(e) => setIsRtl(e.target.checked)}
              className="rounded border-slate-900 bg-slate-950 text-indigo-600 focus:ring-indigo-500 w-4 h-4"
            />
            <label htmlFor="rtl-toggle" className="text-xs text-slate-300 font-sans cursor-pointer select-none">
              Enable Right-To-Left Layout
            </label>
          </div>
        </div>

        <div className="bg-slate-950/50 border border-slate-900 rounded-xl p-4 space-y-2">
          <div className="flex justify-between items-start">
            <span className="text-[10px] text-slate-500 font-mono font-bold uppercase">Currency Format</span>
            <DollarSign className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="flex gap-2 mt-2">
            <button
              onClick={() => setCurrency('INR')}
              className={`flex-1 text-[10px] font-mono font-bold py-1 rounded border transition ${currency === 'INR' ? 'bg-indigo-600 border-indigo-500 text-white' : 'bg-slate-900 border-slate-800 text-slate-400'}`}
            >
              INR (₹)
            </button>
            <button
              onClick={() => setCurrency('USD')}
              className={`flex-1 text-[10px] font-mono font-bold py-1 rounded border transition ${currency === 'USD' ? 'bg-indigo-600 border-indigo-500 text-white' : 'bg-slate-900 border-slate-800 text-slate-400'}`}
            >
              USD ($)
            </button>
          </div>
        </div>

        <div className="bg-slate-950/50 border border-slate-900 rounded-xl p-4 space-y-2">
          <div className="flex justify-between items-start">
            <span className="text-[10px] text-slate-500 font-mono font-bold uppercase">Timezone Engine</span>
            <Clock className="w-4 h-4 text-indigo-400" />
          </div>
          <select
            value={timezone}
            onChange={(e) => setTimezone(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1 text-[10px] text-slate-300 focus:outline-none font-mono"
          >
            <option value="IST">India Standard Time (IST)</option>
            <option value="EST">Eastern Standard Time (EST)</option>
            <option value="GMT">Greenwich Mean Time (GMT)</option>
          </select>
        </div>
      </div>

      {/* Rendered Live Preview Sandbox */}
      <div className="bg-slate-950/40 border border-indigo-950/30 rounded-xl p-6 text-left">
        <div className="border-b border-slate-900 pb-2 mb-4">
          <h4 className="text-xs font-black text-white uppercase tracking-wider font-mono">Live Sandbox Preview</h4>
        </div>

        <div
          dir={isRtl ? 'rtl' : 'ltr'}
          className={`bg-[#050914] border border-slate-900 p-6 rounded-xl space-y-4 text-left transition-all duration-300 ${isRtl ? 'text-right' : 'text-left'}`}
        >
          <div className="space-y-1">
            <span className="text-[10px] bg-indigo-500/10 text-indigo-400 px-3 py-0.5 rounded border border-indigo-950 font-mono font-bold">
              {timezone} TIMEZONE ACTIVE
            </span>
            <h2 className="text-base font-black text-white mt-2 leading-snug">{currentText.title}</h2>
            <p className="text-xs text-slate-400 leading-relaxed max-w-2xl">{currentText.desc}</p>
          </div>

          <div className="flex items-center justify-between pt-4 border-t border-slate-900/60 max-w-lg gap-4">
            <div>
              <p className="text-[10px] text-slate-500">Tier Price</p>
              <p className="text-sm font-black text-emerald-400 font-mono">
                {currency === 'INR' ? currentText.price : '$180'}
              </p>
            </div>

            <button className="bg-indigo-600 hover:bg-indigo-500 text-white text-[11px] font-bold font-sans px-4 py-1.5 rounded-lg transition">
              {currentText.btn}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProdModule11I18n;
