export const dynamic = "force-dynamic";

import Link from "next/link";
import PostCard from "@/components/PostCard";
import { getHomeData } from "@/lib/api";

export default async function Home() {
  const { recent_posts } = await getHomeData();

  return (
    <>
      {/* Hero */}
      <section className="bg-gradient-to-br from-gray-900 via-gray-800 to-primary-900/20 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
            Hi, I&apos;m{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-primary-600">
              Richard Nixon
            </span>
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            Software Engineer sharing thoughts, projects, and data visualizations.
          </p>
          <div className="flex justify-center gap-4">
            <Link
              href="/blog"
              className="px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition font-medium"
            >
              Read Blog
            </Link>
            <Link
              href="/portfolio"
              className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition font-medium"
            >
              View Portfolio
            </Link>
          </div>
        </div>
      </section>

      {/* Recent Posts */}
      {recent_posts.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-2xl font-bold text-white">Recent Posts</h2>
            <Link href="/blog" className="text-primary-400 hover:text-primary-300 text-sm transition">
              View all &rarr;
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {recent_posts.slice(0, 3).map((post) => (
              <PostCard key={post.id} post={post} />
            ))}
          </div>
        </section>
      )}

      {/* Quick Links */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { href: "/portfolio", title: "Portfolio", desc: "Check out my projects and work." },
            { href: "/blog", title: "Blog", desc: "Read my latest articles and thoughts." },
            { href: "/contact", title: "Contact", desc: "Get in touch or download my resume." },
          ].map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="block bg-gray-800 border border-gray-700 rounded-lg p-6 hover:border-primary-500 transition group"
            >
              <h3 className="text-lg font-semibold text-white group-hover:text-primary-400 transition mb-2">
                {item.title}
              </h3>
              <p className="text-gray-400 text-sm">{item.desc}</p>
            </Link>
          ))}
        </div>
      </section>
    </>
  );
}
