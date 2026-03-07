export const dynamic = "force-dynamic";

import Link from "next/link";
import Image from "next/image";
import { getPost, getRelatedPosts } from "@/lib/api";
import PostCard from "@/components/PostCard";
import type { Metadata } from "next";
import Highlight from "@/components/Highlight";

type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const post = await getPost(slug);
  return {
    title: post.title,
    description: post.meta_description || post.excerpt,
    keywords: post.meta_keywords || undefined,
    openGraph: {
      title: post.title,
      description: post.meta_description || post.excerpt,
      type: "article",
      ...(post.featured_image && { images: [post.featured_image] }),
    },
  };
}

export default async function PostPage({ params }: Props) {
  const { slug } = await params;
  const [post, related] = await Promise.all([
    getPost(slug),
    getRelatedPosts(slug),
  ]);

  const date = post.published_at
    ? new Date(post.published_at).toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
      })
    : "";

  const shareUrl = `https://richardnixon.dev/blog/${post.slug}`;

  return (
    <article className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="mb-8">
        {post.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {post.tags.map((tag) => (
              <Link
                key={tag.slug}
                href={`/blog?tag=${tag.slug}`}
                className="text-xs px-2 py-1 bg-primary-900/50 text-primary-300 rounded hover:bg-primary-800/50 transition"
              >
                {tag.name}
              </Link>
            ))}
          </div>
        )}
        <h1 className="text-3xl md:text-4xl font-bold text-white mb-4">{post.title}</h1>
        <div className="flex items-center text-sm text-gray-400 gap-4">
          <span>{date}</span>
          <span>{post.reading_time} min read</span>
          {post.author_name && <span>by {post.author_name}</span>}
        </div>
      </div>

      {/* Featured Image */}
      {post.featured_image && (
        <div className="relative w-full h-64 md:h-96 mb-8 rounded-lg overflow-hidden">
          <Image
            src={post.featured_image}
            alt={post.title}
            fill
            className="object-cover"
            priority
          />
        </div>
      )}

      {/* Content */}
      <div
        className="prose text-gray-300 max-w-none mb-12"
        dangerouslySetInnerHTML={{ __html: post.content }}
      />
      <Highlight />

      {/* Share */}
      <div className="flex items-center gap-4 py-6 border-t border-gray-700">
        <span className="text-sm text-gray-400">Share:</span>
        <a
          href={`https://twitter.com/intent/tweet?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(post.title)}`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm text-gray-400 hover:text-white transition"
        >
          Twitter
        </a>
        <a
          href={`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm text-gray-400 hover:text-white transition"
        >
          LinkedIn
        </a>
      </div>

      {/* Back */}
      <Link href="/blog" className="inline-block text-primary-400 hover:text-primary-300 text-sm transition mt-4">
        &larr; Back to Blog
      </Link>

      {/* Related Posts */}
      {related.length > 0 && (
        <section className="mt-16">
          <h2 className="text-2xl font-bold text-white mb-6">Related Posts</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {related.map((p) => (
              <PostCard key={p.id} post={p} />
            ))}
          </div>
        </section>
      )}
    </article>
  );
}
