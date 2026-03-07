export const dynamic = "force-dynamic";

import Link from "next/link";
import PostCard from "@/components/PostCard";
import { getPosts, getTags, getPostsCount } from "@/lib/api";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Blog",
  description: "Articles about software engineering, technology, and more.",
};

export default async function BlogPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string; search?: string; tag?: string }>;
}) {
  const params = await searchParams;
  const page = Number(params.page) || 1;
  const search = params.search || "";
  const tag = params.tag || "";

  const [posts, tags, total] = await Promise.all([
    getPosts({ page, search, tag }),
    getTags(),
    getPostsCount({ search, tag }),
  ]);

  const totalPages = Math.ceil(total / 10);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-3xl font-bold text-white mb-8">Blog</h1>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Posts */}
        <div className="flex-1">
          {/* Search */}
          <form className="mb-8">
            <div className="flex gap-2">
              <input
                type="text"
                name="search"
                defaultValue={search}
                placeholder="Search posts..."
                className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-gray-100 placeholder-gray-500 focus:outline-none focus:border-primary-500"
              />
              <button
                type="submit"
                className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition"
              >
                Search
              </button>
            </div>
          </form>

          {posts.length === 0 ? (
            <p className="text-gray-400">No posts found.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {posts.map((post) => (
                <PostCard key={post.id} post={post} />
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center gap-2 mt-8">
              {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
                <Link
                  key={p}
                  href={`/blog?page=${p}${search ? `&search=${search}` : ""}${tag ? `&tag=${tag}` : ""}`}
                  className={`px-3 py-1 rounded ${
                    p === page
                      ? "bg-primary-600 text-white"
                      : "bg-gray-800 text-gray-400 hover:text-white"
                  }`}
                >
                  {p}
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Sidebar */}
        <aside className="lg:w-72">
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-5">
            <h3 className="text-lg font-semibold text-white mb-4">Tags</h3>
            <div className="flex flex-wrap gap-2">
              <Link
                href="/blog"
                className={`text-sm px-3 py-1 rounded-full transition ${
                  !tag
                    ? "bg-primary-600 text-white"
                    : "bg-gray-700 text-gray-300 hover:text-white"
                }`}
              >
                All
              </Link>
              {tags.map((t) => (
                <Link
                  key={t.slug}
                  href={`/blog?tag=${t.slug}`}
                  className={`text-sm px-3 py-1 rounded-full transition ${
                    tag === t.slug
                      ? "bg-primary-600 text-white"
                      : "bg-gray-700 text-gray-300 hover:text-white"
                  }`}
                >
                  {t.name}
                </Link>
              ))}
            </div>
          </div>
          <div className="mt-4 bg-gray-800 border border-gray-700 rounded-lg p-5">
            <h3 className="text-lg font-semibold text-white mb-2">Subscribe</h3>
            <p className="text-gray-400 text-sm mb-3">Stay updated with the RSS feed.</p>
            <a
              href="/feed/"
              className="inline-block text-sm text-primary-400 hover:text-primary-300 transition"
            >
              RSS Feed &rarr;
            </a>
          </div>
        </aside>
      </div>
    </div>
  );
}
