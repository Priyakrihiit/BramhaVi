import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { Book, PublishSubmission, CourseStructure, User } from '../../types';
import { BookOpen, Award, CheckCircle, Search, Star, CreditCard, Sparkles, Filter, Bookmark, PlusCircle, Trash, RefreshCw } from 'lucide-react';

interface BookstoreViewProps {
  currentUser: User | null;
  onRefreshWallet: () => void;
}

export const BookstoreView: React.FC<BookstoreViewProps> = ({ currentUser, onRefreshWallet }) => {
  const [books, setBooks] = useState<Book[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedBook, setSelectedBook] = useState<(Book & { reviews?: any[] }) | null>(null);
  const [reviewRating, setReviewRating] = useState(5);
  const [reviewComment, setReviewComment] = useState('');
  
  // Ebook generator state
  const [courses, setCourses] = useState<CourseStructure[]>([]);
  const [selectedCourseId, setSelectedCourseId] = useState('');
  const [isCompiling, setIsCompiling] = useState(false);
  const [compiledEbook, setCompiledEbook] = useState<any>(null);

  // Self Publishing states
  const [submissions, setSubmissions] = useState<PublishSubmission[]>([]);
  const [pubTitle, setPubTitle] = useState('');
  const [pubCategory, setPubCategory] = useState('Computer Science');
  const [pubDesc, setPubDesc] = useState('');
  const [pubFormat, setPubFormat] = useState<'PDF' | 'EPUB'>('PDF');
  const [pubMessage, setPubMessage] = useState({ text: '', type: '' });
  
  // Loading & tab state
  const [activeTab, setActiveTab] = useState<'catalog' | 'publish' | 'ai-compile' | 'admin-panel'>('catalog');
  const [loading, setLoading] = useState(false);

  const categories = ['All', 'Engineering', 'Artificial Intelligence', 'Computer Science', 'General', 'Academic Guide'];

  useEffect(() => {
    fetchBooks();
    fetchCourses();
    if (currentUser) {
      fetchSubmissions();
    }
  }, [currentUser]);

  const fetchBooks = async () => {
    setLoading(true);
    const res = await api.books.list({
      category: selectedCategory === 'All' ? undefined : selectedCategory,
      q: searchQuery || undefined
    });
    if (res.success && res.data) {
      setBooks(res.data);
    }
    setLoading(false);
  };

  const fetchCourses = async () => {
    const res = await api.courses.list();
    if (res.success && res.data) {
      setCourses(res.data.filter(c => c.type === 'COURSE'));
    }
  };

  const fetchSubmissions = async () => {
    // Admins see all submissions to approve, students see their own
    const isAdmin = currentUser?.email === 'admin@brahmavidya.edu';
    const res = await api.publishing.listSubmissions(isAdmin ? undefined : currentUser?.id);
    if (res.success && res.data) {
      setSubmissions(res.data);
    }
  };

  const handleBookSelect = async (book: Book) => {
    const res = await api.books.get(book.id);
    if (res.success && res.data) {
      setSelectedBook(res.data);
    } else {
      setSelectedBook(book);
    }
  };

  const submitReview = async () => {
    if (!selectedBook || !currentUser) return;
    const res = await api.books.addReview(selectedBook.id, {
      userId: currentUser.id,
      userName: currentUser.fullName,
      rating: reviewRating,
      comment: reviewComment
    });
    if (res.success) {
      handleBookSelect(selectedBook);
      setReviewComment('');
      fetchBooks();
    }
  };

  const compileAIEbook = async () => {
    if (!selectedCourseId) return;
    setIsCompiling(true);
    setCompiledEbook(null);
    const course = courses.find(c => c.id === selectedCourseId);
    const res = await api.books.generateEbook(selectedCourseId, course?.title);
    setIsCompiling(false);
    if (res.success && res.data) {
      setCompiledEbook(res.data);
      fetchBooks();
      setPubMessage({ text: 'Study Companion eBook compiled successfully by Vidya AI! It is now available free in the catalog.', type: 'success' });
    } else {
      setPubMessage({ text: 'Compilation failed.', type: 'error' });
    }
  };

  const submitSelfPub = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentUser) return;
    if (!pubTitle || !pubDesc) {
      setPubMessage({ text: 'Please fill out all fields.', type: 'error' });
      return;
    }
    const res = await api.publishing.submit({
      userId: currentUser.id,
      userName: currentUser.fullName,
      title: pubTitle,
      category: pubCategory,
      description: pubDesc,
      fileFormat: pubFormat
    });
    if (res.success) {
      setPubTitle('');
      setPubDesc('');
      setPubMessage({ text: 'Manuscript submitted successfully! Please fund the ₹149 processing fee to queue for review.', type: 'success' });
      fetchSubmissions();
    }
  };

  const payPublishingFee = async (subId: string) => {
    if (!currentUser) return;
    const res = await api.publishing.paySubmission(subId, currentUser.id);
    if (res.success) {
      setPubMessage({ text: 'Setup fee ₹149 debited successfully. Your submission is now queued for Chief Editor review!', type: 'success' });
      fetchSubmissions();
      onRefreshWallet();
    } else {
      setPubMessage({ text: res.message || 'Payment failed.', type: 'error' });
    }
  };

  const reviewSubmissionByAdmin = async (subId: string, status: 'APPROVED' | 'REJECTED') => {
    const notes = prompt(`Enter Reviewer Feedback for this manuscript submission:`);
    if (notes === null) return;
    const res = await api.publishing.reviewSubmission(subId, {
      status,
      adminNotes: notes || 'Reviewed by BrahmaVidya Academic Board.'
    });
    if (res.success) {
      setPubMessage({ text: `Manuscript status updated to: ${status}!`, type: 'success' });
      fetchSubmissions();
      fetchBooks();
    }
  };

  const toggleBookmark = (bookId: string) => {
    // Visually toggle
    setBooks(books.map(b => b.id === bookId ? { ...b, bookmarksCount: b.bookmarksCount + (b.bookmarksCount % 2 === 0 ? 1 : -1) } : b));
  };

  const isAdmin = currentUser?.email === 'admin@brahmavidya.edu';

  return (
    <div id="bookstore-root" className="min-h-screen bg-slate-50 text-slate-900 pb-12">
      {/* Upper Brand Jumbotron */}
      <div className="bg-slate-900 text-white py-12 px-6 shadow-sm border-b border-slate-800">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="bg-indigo-500 text-white text-xs font-mono px-2 py-0.5 rounded-full tracking-wider uppercase">V1.KP Production Ready</span>
            </div>
            <h1 className="text-3xl font-bold tracking-tight font-sans">BrahmaVidya Academic Bookstore</h1>
            <p className="text-slate-400 mt-2 max-w-2xl font-sans">
              Deploying peer-reviewed academic eBooks, companion syllabi guides, and our self-publishing pipeline.
              Sellers receive 95% royalty payouts directly to their academic ledgers.
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setActiveTab('catalog')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === 'catalog' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}`}
            >
              Bookstore Catalogue
            </button>
            <button
              onClick={() => setActiveTab('publish')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === 'publish' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}`}
            >
              Self Publishing Pipeline
            </button>
            <button
              onClick={() => setActiveTab('ai-compile')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-1.5 ${activeTab === 'ai-compile' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-indigo-400 hover:bg-slate-700'}`}
            >
              <Sparkles className="h-4 w-4" /> Vidya AI Ebook Compiler
            </button>
            {isAdmin && (
              <button
                onClick={() => setActiveTab('admin-panel')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === 'admin-panel' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-emerald-400 hover:bg-slate-700'}`}
              >
                Chief Editor Desk ({submissions.filter(s => s.status === 'PENDING' && s.isPaid).length})
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 mt-8">
        {pubMessage.text && (
          <div className={`p-4 rounded-xl mb-6 flex items-center justify-between border ${pubMessage.type === 'success' ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-rose-50 border-rose-200 text-rose-800'}`}>
            <span className="text-sm font-medium">{pubMessage.text}</span>
            <button onClick={() => setPubMessage({ text: '', type: '' })} className="text-xs underline font-semibold cursor-pointer">Dismiss</button>
          </div>
        )}

        {/* 1. CATALOG TAB */}
        {activeTab === 'catalog' && (
          <div>
            {/* Catalog Controls */}
            <div className="flex flex-col md:flex-row gap-4 mb-8 justify-between items-stretch">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-3.5 h-4 w-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search eBooks, textbook companions, research papers..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && fetchBooks()}
                  className="w-full pl-10 pr-4 py-3 bg-white rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-sans text-sm shadow-sm"
                />
              </div>
              <div className="flex items-center gap-2 overflow-x-auto pb-1 md:pb-0">
                <span className="text-xs font-mono font-semibold text-slate-500 flex items-center gap-1">
                  <Filter className="h-3.5 w-3.5" /> Filter:
                </span>
                {categories.map(cat => (
                  <button
                    key={cat}
                    onClick={() => { setSelectedCategory(cat); setTimeout(fetchBooks, 10); }}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${selectedCategory === cat ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'}`}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>

            {/* Book Cards Grid */}
            {loading ? (
              <div className="flex flex-col items-center justify-center py-20">
                <RefreshCw className="h-8 w-8 text-indigo-500 animate-spin mb-2" />
                <p className="text-sm text-slate-500">Querying digital library catalog...</p>
              </div>
            ) : books.length === 0 ? (
              <div className="bg-white rounded-2xl p-12 text-center border border-slate-200 max-w-lg mx-auto mt-8">
                <BookOpen className="h-12 w-12 text-slate-300 mx-auto mb-3" />
                <h3 className="font-semibold text-lg text-slate-800">No books found</h3>
                <p className="text-sm text-slate-500 mt-1">Try refining your search terms or selecting a different category.</p>
                <button onClick={() => { setSearchQuery(''); setSelectedCategory('All'); setTimeout(fetchBooks, 50); }} className="mt-4 text-sm text-indigo-600 font-semibold underline">Reset Filters</button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
                {books.map(book => (
                  <div key={book.id} className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden flex flex-col hover:shadow-md transition-all">
                    <div className="relative aspect-4/3 bg-slate-100 overflow-hidden">
                      <img src={book.coverUrl} alt={book.title} className="w-full h-full object-cover" />
                      <div className="absolute top-2 left-2 bg-slate-900/85 text-white text-[10px] font-mono px-2 py-0.5 rounded font-semibold tracking-wide uppercase">
                        {book.fileFormat}
                      </div>
                      {book.isGeneratedEbook && (
                        <div className="absolute top-2 right-2 bg-indigo-600 text-white text-[10px] font-mono px-2 py-0.5 rounded font-semibold flex items-center gap-0.5 shadow">
                          <Sparkles className="h-2.5 w-2.5" /> AI Generated
                        </div>
                      )}
                    </div>
                    <div className="p-4 flex-1 flex flex-col justify-between">
                      <div>
                        <div className="flex items-center gap-1 text-xs text-slate-500 mb-1">
                          <span className="font-medium text-indigo-600">{book.category}</span>
                          <span>•</span>
                          <span>By {book.authorName}</span>
                        </div>
                        <h3 className="font-semibold text-slate-900 leading-tight tracking-tight hover:text-indigo-600 cursor-pointer" onClick={() => handleBookSelect(book)}>
                          {book.title}
                        </h3>
                        <p className="text-xs text-slate-500 line-clamp-2 mt-2 leading-relaxed">
                          {book.description}
                        </p>
                      </div>

                      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                        <div className="flex items-center gap-1">
                          <Star className="h-3.5 w-3.5 text-amber-400 fill-amber-400" />
                          <span className="text-xs font-mono font-bold text-slate-700">{book.rating}</span>
                          <span className="text-[10px] text-slate-400">({book.reviewsCount})</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <button onClick={() => toggleBookmark(book.id)} className="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-slate-50 rounded-lg">
                            <Bookmark className={`h-4 w-4 ${book.bookmarksCount % 2 !== 0 ? 'fill-indigo-600 text-indigo-600' : ''}`} />
                          </button>
                          <button
                            onClick={() => handleBookSelect(book)}
                            className="bg-slate-900 text-white text-xs font-medium px-3 py-1.5 rounded-lg hover:bg-slate-800 transition-all cursor-pointer"
                          >
                            {book.price === 0 ? 'Read Free' : `₹${book.price}`}
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* 2. SELF PUBLISHING TAB */}
        {activeTab === 'publish' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Publish Form */}
            <div className="lg:col-span-1 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
              <div className="flex items-center gap-2 mb-4">
                <PlusCircle className="h-5 w-5 text-indigo-600" />
                <h3 className="font-bold text-lg text-slate-900">Submit New Manuscript</h3>
              </div>
              <p className="text-xs text-slate-500 mb-6 leading-relaxed">
                Publishing on BrahmaVidya costs a standard review fee of ₹149. Approved manuscripts instantly deploy to the academic bookstore and centralized marketplace. Authors earn 95% revenue on each download.
              </p>
              
              <form onSubmit={submitSelfPub} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Book Title *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g., Guide to Compiler Construction"
                    value={pubTitle}
                    onChange={(e) => setPubTitle(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 font-sans"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Category *</label>
                  <select
                    value={pubCategory}
                    onChange={(e) => setPubCategory(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 font-sans bg-white"
                  >
                    <option value="Computer Science">Computer Science</option>
                    <option value="Engineering">Engineering</option>
                    <option value="Artificial Intelligence">Artificial Intelligence</option>
                    <option value="Mathematics">Mathematics</option>
                    <option value="Literature">Literature</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Target Format *</label>
                  <div className="flex gap-4">
                    <label className="flex items-center gap-1.5 text-xs font-medium cursor-pointer">
                      <input type="radio" checked={pubFormat === 'PDF'} onChange={() => setPubFormat('PDF')} /> PDF Document
                    </label>
                    <label className="flex items-center gap-1.5 text-xs font-medium cursor-pointer">
                      <input type="radio" checked={pubFormat === 'EPUB'} onChange={() => setPubFormat('EPUB')} /> EPUB Ebook
                    </label>
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Description & Abstracts *</label>
                  <textarea
                    required
                    rows={4}
                    placeholder="Provide a deep description, layout block listings, and learning objectives..."
                    value={pubDesc}
                    onChange={(e) => setPubDesc(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 font-sans"
                  />
                </div>
                <button
                  type="submit"
                  className="w-full py-2.5 bg-slate-900 text-white text-xs font-semibold rounded-lg hover:bg-slate-800 transition-all cursor-pointer"
                >
                  Submit Manuscript & Metadata
                </button>
              </form>
            </div>

            {/* Submissions Pipeline list */}
            <div className="lg:col-span-2 space-y-6">
              <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                <h3 className="font-bold text-lg text-slate-900 mb-4 flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-indigo-500" />
                  Your Publishing Pipeline Status
                </h3>
                {submissions.length === 0 ? (
                  <div className="text-center py-12 text-slate-400">
                    <BookOpen className="h-8 w-8 mx-auto mb-2 opacity-50" />
                    <p className="text-xs">No active self-publishing history tracked on this account.</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {submissions.map(sub => (
                      <div key={sub.id} className="p-4 border border-slate-100 rounded-xl bg-slate-50 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                        <div>
                          <div className="flex items-center gap-2 mb-1.5">
                            <span className="text-xs font-mono font-bold text-slate-500">ID: {sub.id}</span>
                            <span className="text-[10px] bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded font-medium">{sub.category}</span>
                            <span className={`text-[10px] px-2 py-0.5 rounded font-mono font-semibold ${
                              sub.status === 'APPROVED' ? 'bg-emerald-100 text-emerald-800' :
                              sub.status === 'REJECTED' ? 'bg-rose-100 text-rose-800' : 'bg-amber-100 text-amber-800'
                            }`}>
                              {sub.status}
                            </span>
                          </div>
                          <h4 className="font-bold text-slate-800 text-sm leading-tight">{sub.title}</h4>
                          <p className="text-xs text-slate-500 mt-1 line-clamp-1">{sub.description}</p>
                          {sub.adminNotes && (
                            <p className="text-[11px] text-slate-600 bg-white border border-slate-200 px-2 py-1 rounded mt-2 font-mono">
                              <strong>Editor Notes:</strong> {sub.adminNotes}
                            </p>
                          )}
                        </div>
                        <div className="flex flex-col items-end gap-2 w-full md:w-auto">
                          {!sub.isPaid ? (
                            <button
                              onClick={() => payPublishingFee(sub.id)}
                              className="bg-indigo-600 text-white text-xs font-bold px-3 py-1.5 rounded-lg hover:bg-indigo-700 transition-all flex items-center gap-1.5 shadow-sm"
                            >
                              <CreditCard className="h-3.5 w-3.5" /> Pay ₹149 Setup Fee
                            </button>
                          ) : (
                            <span className="text-xs text-emerald-600 font-bold flex items-center gap-1 bg-white border border-emerald-100 px-2 py-1 rounded">
                              <CheckCircle className="h-3.5 w-3.5" /> Setup Paid (₹149)
                            </span>
                          )}
                          <span className="text-[10px] text-slate-400 font-mono">Submitted: {new Date(sub.createdAt).toLocaleDateString()}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* 3. AI EBOOK COMPILER TAB */}
        {activeTab === 'ai-compile' && (
          <div className="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm max-w-3xl mx-auto">
            <div className="flex items-center gap-2 mb-4 justify-center md:justify-start">
              <Sparkles className="h-6 w-6 text-indigo-600 animate-pulse" />
              <h2 className="text-xl font-bold text-slate-900">Vidya AI eBook Compiler & Companion Generator</h2>
            </div>
            <p className="text-sm text-slate-600 mb-6 leading-relaxed">
              Leverage Google Gemini API to instantly generate structured companion textbook guides based on our active course program structures. Simply pick a course below, and let Vidya AI synthesize the eBook chapters, conceptual summaries, code templates, and academic notes instantly.
            </p>

            <div className="bg-indigo-50 border border-indigo-100 p-4 rounded-xl mb-6">
              <h4 className="text-xs font-bold text-indigo-800 uppercase tracking-wide mb-1 font-mono">AI Capability Standard</h4>
              <p className="text-xs text-indigo-700 leading-relaxed font-sans">
                This utilizes a server-side Gemini 3.5 Flash connection proxying requests safely to hide API credentials. Resulting books are appended to the public bookstore catalog automatically.
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase">Select Academic Program Course *</label>
                <select
                  value={selectedCourseId}
                  onChange={(e) => setSelectedCourseId(e.target.value)}
                  className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white font-medium text-sm"
                >
                  <option value="">-- Choose Course Syllabus --</option>
                  {courses.map(course => (
                    <option key={course.id} value={course.id}>{course.title} (Syllabus Draft)</option>
                  ))}
                </select>
              </div>

              <button
                onClick={compileAIEbook}
                disabled={isCompiling || !selectedCourseId}
                className={`w-full py-3.5 rounded-xl font-semibold text-sm transition-all flex items-center justify-center gap-2 ${
                  isCompiling || !selectedCourseId ? 'bg-slate-100 text-slate-400 cursor-not-allowed' : 'bg-slate-900 text-white hover:bg-slate-800 cursor-pointer shadow-sm'
                }`}
              >
                {isCompiling ? (
                  <>
                    <RefreshCw className="h-4 w-4 animate-spin" />
                    Executing Gemini Core, Synthesizing Chapters (ETA ~15s)...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4 text-indigo-400" />
                    Compile Certified Course eBook Now
                  </>
                )}
              </button>
            </div>

            {compiledEbook && (
              <div className="mt-8 border-t border-slate-100 pt-6">
                <div className="bg-emerald-50 border border-emerald-100 p-4 rounded-xl mb-6 flex items-center gap-2 text-emerald-800">
                  <CheckCircle className="h-5 w-5 shrink-0" />
                  <span className="text-sm font-semibold">eBook Generated Successfully! Placed in store catalog.</span>
                </div>
                <div className="border border-slate-200 rounded-2xl overflow-hidden shadow-sm bg-slate-900 text-slate-100 font-mono text-xs">
                  <div className="bg-slate-800 px-4 py-2 flex items-center justify-between border-b border-slate-700">
                    <span className="font-semibold text-slate-300">Certified Book Output Preview</span>
                    <span className="text-[10px] bg-indigo-600 text-white px-2 py-0.5 rounded font-semibold uppercase">Markdown Format</span>
                  </div>
                  <div className="p-4 max-h-80 overflow-y-auto leading-relaxed space-y-2 whitespace-pre-wrap">
                    {compiledEbook.markdownContent || `# ${compiledEbook.title}\n\nGenerated Guide is loaded into Catalogue.`}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* 4. CHIEF EDITOR DESK TAB */}
        {activeTab === 'admin-panel' && (
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
            <h3 className="font-bold text-lg text-slate-900 mb-6 flex items-center gap-2">
              <Award className="h-6 w-6 text-indigo-600" />
              Chief Editor Academic Review Console
            </h3>
            <p className="text-xs text-slate-500 mb-6 leading-relaxed">
              Verify paid self-publishing proposals, evaluate content standards, and trigger automatic eBook publishing to the decentralized marketplace.
            </p>

            <div className="space-y-4">
              {submissions.filter(s => s.status === 'PENDING' && s.isPaid).length === 0 ? (
                <div className="text-center py-12 text-slate-400">
                  <CheckCircle className="h-8 w-8 mx-auto mb-2 text-emerald-500" />
                  <p className="text-xs font-semibold text-slate-600">All submissions have been peer-reviewed.</p>
                </div>
              ) : (
                submissions.filter(s => s.status === 'PENDING' && s.isPaid).map(sub => (
                  <div key={sub.id} className="p-6 border border-slate-200 rounded-xl bg-slate-50/50 flex flex-col md:flex-row justify-between items-start gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs font-mono font-bold text-indigo-600">ID: {sub.id}</span>
                        <span className="text-[10px] bg-slate-200 text-slate-700 px-2 py-0.5 rounded font-bold uppercase">{sub.fileFormat}</span>
                        <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-bold">FEES PAID</span>
                      </div>
                      <h4 className="font-bold text-slate-800 text-base leading-tight">{sub.title}</h4>
                      <div className="text-xs text-slate-500 mt-1">Author: <strong>{sub.userName}</strong> ({sub.userId})</div>
                      <p className="text-xs text-slate-600 mt-2 bg-white p-3 border border-slate-150 rounded-lg max-w-3xl leading-relaxed italic">
                        "{sub.description}"
                      </p>
                    </div>
                    <div className="flex md:flex-col gap-2 w-full md:w-auto self-stretch justify-end">
                      <button
                        onClick={() => reviewSubmissionByAdmin(sub.id, 'APPROVED')}
                        className="bg-emerald-600 text-white text-xs font-bold px-4 py-2 rounded-lg hover:bg-emerald-700 transition-all cursor-pointer shadow-sm"
                      >
                        Approve & Publish
                      </button>
                      <button
                        onClick={() => reviewSubmissionByAdmin(sub.id, 'REJECTED')}
                        className="bg-rose-600 text-white text-xs font-bold px-4 py-2 rounded-lg hover:bg-rose-700 transition-all cursor-pointer shadow-sm"
                      >
                        Reject Proposal
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>

      {/* eBook Details Modal */}
      {selectedBook && (
        <div className="fixed inset-0 bg-slate-950/70 flex items-center justify-center p-4 z-50 animate-fade-in backdrop-blur-xs">
          <div className="bg-white rounded-3xl overflow-hidden shadow-2xl max-w-2xl w-full max-h-[85vh] flex flex-col border border-slate-100">
            <div className="bg-slate-900 text-white p-6 flex items-start justify-between">
              <div>
                <span className="bg-indigo-500/30 text-indigo-300 text-[10px] font-mono px-2 py-0.5 rounded font-semibold tracking-wider uppercase">
                  {selectedBook.category}
                </span>
                <h3 className="text-xl font-bold tracking-tight mt-1 leading-tight">{selectedBook.title}</h3>
                <p className="text-xs text-slate-400 mt-1">Author: <strong>{selectedBook.authorName}</strong></p>
              </div>
              <button onClick={() => setSelectedBook(null)} className="text-slate-400 hover:text-white text-lg font-bold p-1 cursor-pointer">✕</button>
            </div>

            <div className="p-6 overflow-y-auto space-y-6 flex-1">
              <div>
                <h4 className="text-xs font-bold uppercase text-slate-500 tracking-wide mb-2 font-mono">Abstract & Overview</h4>
                <p className="text-xs text-slate-600 leading-relaxed font-sans">{selectedBook.description}</p>
              </div>

              <div>
                <h4 className="text-xs font-bold uppercase text-slate-500 tracking-wide mb-3 font-mono">Reviews & Ratings</h4>
                <div className="space-y-3">
                  {!selectedBook.reviews || selectedBook.reviews.length === 0 ? (
                    <p className="text-xs text-slate-400 italic">No reviews compiled for this eBook yet. Be the first to leave feedback!</p>
                  ) : (
                    selectedBook.reviews.map((rev: any) => (
                      <div key={rev.id} className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-bold text-slate-700">{rev.userName}</span>
                          <div className="flex items-center gap-0.5">
                            {Array.from({ length: 5 }).map((_, i) => (
                              <Star key={i} className={`h-3 w-3 ${i < rev.rating ? 'text-amber-400 fill-amber-400' : 'text-slate-300'}`} />
                            ))}
                          </div>
                        </div>
                        <p className="text-xs text-slate-600 italic font-sans">"{rev.comment}"</p>
                        <span className="text-[9px] text-slate-400 font-mono mt-1 block">{new Date(rev.createdAt).toLocaleDateString()}</span>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {currentUser && (
                <div className="border-t border-slate-100 pt-4 space-y-3">
                  <h4 className="text-xs font-bold uppercase text-slate-500 tracking-wide font-mono">Submit Academic Review</h4>
                  <div className="flex gap-4 items-center">
                    <label className="text-xs text-slate-600 font-medium font-sans">Your Rating:</label>
                    <div className="flex gap-1.5">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <button
                          key={star}
                          onClick={() => setReviewRating(star)}
                          className="p-1 hover:scale-110 transition-transform cursor-pointer"
                        >
                          <Star className={`h-5 w-5 ${star <= reviewRating ? 'text-amber-400 fill-amber-400' : 'text-slate-300'}`} />
                        </button>
                      ))}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      placeholder="Compile comment text here..."
                      value={reviewComment}
                      onChange={(e) => setReviewComment(e.target.value)}
                      className="flex-1 text-xs border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-sans"
                    />
                    <button
                      onClick={submitReview}
                      className="bg-slate-900 text-white text-xs font-semibold px-4 py-2 rounded-lg hover:bg-slate-800 transition-all cursor-pointer"
                    >
                      Post Review
                    </button>
                  </div>
                </div>
              )}
            </div>

            <div className="bg-slate-50 p-4 border-t border-slate-100 flex items-center justify-between">
              <span className="text-xs text-slate-500 font-mono font-bold uppercase">Format: {selectedBook.fileFormat}</span>
              <div className="flex gap-2">
                <button
                  onClick={() => setSelectedBook(null)}
                  className="bg-slate-200 text-slate-700 text-xs font-semibold px-4 py-2 rounded-lg hover:bg-slate-300 cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    alert(`Your eBook file is compiling. Certified secure download link: ${selectedBook.title}.${selectedBook.fileFormat.toLowerCase()}`);
                    setSelectedBook(null);
                  }}
                  className="bg-indigo-600 text-white text-xs font-semibold px-4 py-2 rounded-lg hover:bg-indigo-700 shadow-sm cursor-pointer"
                >
                  {selectedBook.price === 0 ? 'Download Free' : `Purchase for ₹${selectedBook.price}`}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
