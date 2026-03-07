import Link from "next/link";
import Image from "next/image";
import type { Project } from "@/lib/types";

export default function ProjectCard({ project }: { project: Project }) {
  const image = project.thumbnail || project.featured_image;

  return (
    <article className="bg-gray-800 rounded-lg overflow-hidden border border-gray-700 hover:border-primary-500 transition group">
      {image && (
        <Link href={`/portfolio/${project.slug}`}>
          <div className="relative h-48 overflow-hidden">
            <Image
              src={image}
              alt={project.title}
              fill
              className="object-cover group-hover:scale-105 transition-transform duration-300"
            />
          </div>
        </Link>
      )}
      <div className="p-5">
        <Link href={`/portfolio/${project.slug}`}>
          <h3 className="text-lg font-semibold text-white group-hover:text-primary-400 transition mb-1">
            {project.title}
          </h3>
        </Link>
        <p className="text-gray-400 text-sm mb-3">{project.tagline}</p>
        <div className="flex flex-wrap gap-2 mb-4">
          {project.technologies.slice(0, 4).map((tech) => (
            <span
              key={tech.slug}
              className="text-xs px-2 py-1 rounded"
              style={{ backgroundColor: `${tech.color}20`, color: tech.color }}
            >
              {tech.name}
            </span>
          ))}
        </div>
        <div className="flex gap-3">
          {project.github_url && (
            <a
              href={project.github_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-gray-400 hover:text-white transition"
            >
              GitHub
            </a>
          )}
          {project.live_url && (
            <a
              href={project.live_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-primary-400 hover:text-primary-300 transition"
            >
              Live Demo
            </a>
          )}
        </div>
      </div>
    </article>
  );
}
