import Link from "next/link";
import Image from "next/image";
import type { Post } from "@/lib/types";

export default function PostCard({ post }: { post: Post }) {
  const date = post.published_at
    ? new Date(post.published_at).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      })
    : "";

  return (
    <article className="bg-gray-800 rounded-lg overflow-hidden border border-gray-700 hover:border-primary-500 transition group">
      {post.featured_image && (
        <Link href={`/blog/${post.slug}`}>
          <div className="relative h-48 overflow-hidden">
            <Image
              src={post.featured_image}
              alt={post.title}
              fill
              className="object-cover group-hover:scale-105 transition-transform duration-300"
            />
          </div>
        </Link>
      )}
      <div className="p-5">
        {post.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-3">
            {post.tags.slice(0, 3).map((tag) => (
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
        <Link href={`/blog/${post.slug}`}>
          <h3 className="text-lg font-semibold text-white group-hover:text-primary-400 transition mb-2">
            {post.title}
          </h3>
        </Link>
        <p className="text-gray-400 text-sm line-clamp-2 mb-3">{post.excerpt}</p>
        <div className="flex items-center text-xs text-gray-500 gap-3">
          <span>{date}</span>
          <span>{post.reading_time} min read</span>
        </div>
      </div>
    </article>
  );
}
