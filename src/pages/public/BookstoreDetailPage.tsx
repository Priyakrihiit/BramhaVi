import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { useLayoutStore } from '../../stores/layoutStore';
import { useAuthStore } from '../../stores/authStore';
import { Book, BookReview, CourseStructure } from '../../types';
import { Button, Input, Dialog, LoadingSpinner } from '../../components/DesignSystem';
import { ArrowLeft, Star, ShoppingCart, BookOpen, AlertCircle, Sparkles, ChevronRight, BookOpen as ReaderIcon } from 'lucide-react';
import { OnlineReader } from '../../components/bookstore/OnlineReader';

export const BookstoreDetailPage: React.FC = () => {
  const { currentPath, navigateTo } = useLayoutStore();
  const { currentUser } = useAuthStore();
  const [book, setBook] = useState<(Book & { reviews: BookReview[] }) | null>(null);
  const [relatedCourses, setRelatedCourses] = useState<CourseStructure[]>([]);
  const [loading, setLoading] = useState(true);

  // Review states
  const [isReviewOpen, setIsReviewOpen] = useState(false);
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');
  const [submittingReview, setSubmittingReview] = useState(false);
  const [isReaderOpen, setIsReaderOpen] = useState(false);

  // Extract ID virtual route parameter: /bookstore/:id
  const match = currentPath.match(/^\/bookstore\/([^/]+)/);
  const bookId = match ? match[1] : null;

  useEffect(() => {
    if (bookId) {
      setLoading(true);
      Promise.all([
        api.books.get(bookId),
        api.courses.list()
      ])
        .then(([bookRes, coursesRes]) => {
          if (bookRes.success && bookRes.data) {
            setBook(bookRes.data);
          }
          if (coursesRes.success && coursesRes.data) {
            setRelatedCourses(coursesRes.data.slice(0, 2));
          }
        })
        .finally(() => setLoading(false));
    }
  }, [bookId]);

  const handleBuy = () => {
    if (!currentUser) {
      alert('Authentication required to purchase publications. Redirecting to login desk...');
      navigateTo('/auth');
    } else {
      alert('Book added to checkout shopping cart queue.');
    }
  };

  const handleAddReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentUser) {
      alert('You must be authenticated to write book reviews. Redirecting to login desk...');
      navigateTo('/auth');
      return;
    }
    if (!bookId) return;
    setSubmittingReview(true);
    try {
      const res = await api.books.addReview(bookId, {
        userId: currentUser.id,
        userName: currentUser.fullName,
        rating,
        comment,
      });
      if (res.success && res.data) {
        // Refresh book reviews
        const refreshRes = await api.books.get(bookId);
        if (refreshRes.success && refreshRes.data) {
          setBook(refreshRes.data);
        }
        setIsReviewOpen(false);
        setComment('');
        setRating(5);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setSubmittingReview(false);
    }
  };

  if (loading) {
    return <LoadingSpinner text="Retrieving ebook parameters..." />;
  }

  if (!book) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 bg-[#070b19] text-slate-500 font-mono text-xs">
        <AlertCircle size={24} className="text-rose-500 mb-2" />
        Ebook profile signature not found.
        <Button size="sm" variant="outline" className="mt-4" onClick={() => navigateTo('/bookstore')}>
          Return to Bookstore
        </Button>
      </div>
    );
  }

  if (isReaderOpen) {
    return <OnlineReader bookTitle={book.title} onClose={() => setIsReaderOpen(false)} />;
  }

  return (
    <div className="flex-1 flex flex-col bg-[#070b19]">
      {/* Breadcrumb Header */}
      <div className="bg-[#0b1329] border-b border-indigo-950/40 px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between gap-4 text-xs">
          <button 
            onClick={() => navigateTo('/bookstore')}
            className="flex items-center gap-1.5 text-slate-400 hover:text-white transition font-bold cursor-pointer"
          >
            <ArrowLeft size={13} /> Bookstore Catalog
          </button>
          <div className="text-slate-500 font-mono hidden sm:block">
            Home &gt; Bookstore &gt; {book.title.substring(0, 30)}...
          </div>
        </div>
      </div>

      {/* Main Details Screen */}
      <section className="py-12 px-6 max-w-4xl mx-auto w-full text-left grid grid-cols-1 md:grid-cols-12 gap-8">
        
        {/* Cover Thumbnail Column */}
        <div className="md:col-span-4 space-y-4">
          <div className="aspect-[3/4] w-full bg-slate-900 border border-indigo-950 rounded-2xl flex items-center justify-center relative overflow-hidden shadow-2xl">
            <div className="absolute inset-0 bg-gradient-to-tr from-indigo-900/10 via-slate-900 to-indigo-900/10"></div>
            <BookOpen size={64} className="text-indigo-500/50 animate-pulse" />
            <div className="absolute bottom-4 left-4 right-4 text-center bg-slate-950/80 p-2.5 rounded-xl border border-indigo-900/40">
              <span className="block text-[9px] uppercase font-bold text-indigo-400 tracking-widest">Ebook Edition</span>
            </div>
          </div>

          <div className="p-4 bg-slate-900/60 border border-indigo-950 rounded-xl space-y-2.5 text-xs text-slate-400 font-mono">
            <div className="flex justify-between">
              <span>FORMAT:</span> <span className="text-slate-200">{book.bookType}</span>
            </div>
            <div className="flex justify-between">
              <span>STOCK:</span> <span className="text-slate-250 font-bold">{book.inventoryCount > 0 ? `${book.inventoryCount} Available` : 'Sold Out'}</span>
            </div>
            <div className="flex justify-between">
              <span>ISBN:</span> <span className="text-slate-300">{book.isbn || '978-0-1249-1'}</span>
            </div>
          </div>
        </div>

        {/* Content Metadata Column */}
        <div className="md:col-span-8 space-y-6">
          <div className="space-y-3">
            <span className="px-2.5 py-0.5 rounded bg-indigo-950 text-indigo-400 font-mono text-[9px] uppercase tracking-wider font-bold">
              {book.status}
            </span>
            <h1 className="text-2xl md:text-3xl font-black text-white leading-tight">{book.title}</h1>
            <p className="text-xs text-slate-500 font-mono">Author ID: {book.author} // Publisher ID: {book.publisher || 'Direct BVG'}</p>
          </div>

          <p className="text-xs text-slate-350 leading-relaxed border-t border-b border-indigo-950/40 py-4">
            {book.description || 'Access structured technical written learning guides compiled by professional authors.'}
          </p>

          <div className="flex flex-wrap items-center gap-4">
            <div>
              <span className="block text-[9px] uppercase font-bold text-slate-500">Retail Price</span>
              <strong className="text-2xl font-black text-white">₹{book.price.toLocaleString()}</strong>
            </div>
            <div className="flex gap-2">
              <Button className="flex items-center gap-2 px-6" onClick={handleBuy}>
                <ShoppingCart size={15} /> Buy eBook
              </Button>
              <Button variant="outline" className="flex items-center gap-2 text-xs py-2.5" onClick={() => setIsReaderOpen(true)}>
                <ReaderIcon size={14} /> Start Reading Preview
              </Button>
            </div>
          </div>

          {/* Reviews Section */}
          <div className="space-y-4 pt-6 border-t border-indigo-950/40">
            <div className="flex justify-between items-center">
              <h4 className="text-xs font-bold text-white uppercase tracking-wider">Customer Reviews</h4>
              <Button size="sm" variant="outline" className="text-[10px]" onClick={() => setIsReviewOpen(true)}>
                Write Review
              </Button>
            </div>

            {book.reviews && book.reviews.length > 0 ? (
              <div className="space-y-3">
                {book.reviews.map((rev, rIdx) => (
                  <div key={rIdx} className="p-4 bg-slate-900 border border-indigo-950 rounded-xl space-y-2">
                    <div className="flex justify-between items-center text-xs">
                      <strong className="text-slate-200">{rev.userName}</strong>
                      <div className="flex items-center gap-0.5 text-amber-400">
                        {Array.from({ length: rev.rating }).map((_, starIdx) => (
                          <Star key={starIdx} size={11} fill="currentColor" />
                        ))}
                      </div>
                    </div>
                    <p className="text-xs text-slate-400 leading-relaxed">{rev.comment}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-6 bg-slate-900/10 border border-dashed border-indigo-950 rounded-xl text-center text-xs text-slate-500 font-mono italic">
                No reviews yet. Be the first to review this publication!
              </div>
            )}
          </div>

        </div>
      </section>

      {/* Recommended Syllabus Courses */}
      <section className="py-12 border-t border-indigo-950/30 max-w-4xl mx-auto w-full px-6 text-left space-y-6">
        <div>
          <span className="text-[10px] uppercase font-bold tracking-widest text-indigo-400 font-mono flex items-center gap-1">
            <Sparkles size={11} /> Next-Step Recommendations
          </span>
          <h3 className="text-lg font-bold text-white tracking-tight mt-0.5">Academic courses matching this eBook</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {relatedCourses.map((c, idx) => (
            <div key={c.id || idx} className="p-5 bg-slate-900 border border-indigo-950 rounded-2xl flex justify-between items-center hover:border-indigo-900 transition">
              <div>
                <h4 className="text-xs font-bold text-white leading-snug">{c.title}</h4>
                <span className="text-[9px] text-slate-500 font-mono uppercase tracking-wider block mt-1">Difficulty: {c.metadata?.difficulty || 'Beginner'}</span>
              </div>
              <button 
                onClick={() => navigateTo(`/courses/${c.id}`)}
                className="p-2 bg-indigo-950/40 border border-indigo-900/40 rounded-xl text-indigo-400 hover:text-white hover:bg-indigo-650 transition cursor-pointer"
              >
                <ChevronRight size={14} />
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* Review Dialog */}
      <Dialog isOpen={isReviewOpen} onClose={() => setIsReviewOpen(false)} title="Write Book Review">
        <form onSubmit={handleAddReview} className="space-y-4 text-left">
          <div className="flex flex-col gap-1 text-xs">
            <span className="font-bold text-slate-400 uppercase tracking-wider text-[10px]">Select Rating</span>
            <div className="flex items-center gap-1.5 pt-1">
              {[1, 2, 3, 4, 5].map(val => (
                <button
                  key={val}
                  type="button"
                  onClick={() => setRating(val)}
                  className={`p-1 transition ${rating >= val ? 'text-amber-400' : 'text-slate-655'}`}
                >
                  <Star size={18} fill={rating >= val ? 'currentColor' : 'none'} />
                </button>
              ))}
            </div>
          </div>
          <div className="flex flex-col gap-1.5">
            <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Comment</label>
            <textarea
              required
              placeholder="What did you think of the ebook structure and blueprints?"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              className="w-full bg-slate-900 border border-indigo-950 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 min-h-[90px]"
            />
          </div>
          <Button type="submit" isLoading={submittingReview} className="w-full">
            Submit Review
          </Button>
        </form>
      </Dialog>

    </div>
  );
};

export default BookstoreDetailPage;
