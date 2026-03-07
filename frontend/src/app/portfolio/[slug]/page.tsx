export const dynamic = "force-dynamic";

import Link from "next/link";
import Image from "next/image";
import { getProject, getRelatedProjects } from "@/lib/api";
import ProjectCard from "@/components/ProjectCard";
import type { Metadata } from "next";

type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const project = await getProject(slug);
  return {
    title: project.title,
    description: project.tagline,
    openGraph: {
      title: project.title,
      description: project.tagline,
      ...(project.featured_image && { images: [project.featured_image] }),
    },
  };
}

export default async function ProjectPage({ params }: Props) {
  const { slug } = await params;
  const [project, related] = await Promise.all([
    getProject(slug),
    getRelatedProjects(slug),
  ]);

  const formatDate = (d: string | null) =>
    d ? new Date(d).toLocaleDateString("en-US", { year: "numeric", month: "short" }) : null;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <Link href="/portfolio" className="text-primary-400 hover:text-primary-300 text-sm transition">
        &larr; Back to Portfolio
      </Link>

      {/* Header */}
      <div className="mt-6 mb-8">
        <h1 className="text-3xl md:text-4xl font-bold text-white mb-2">{project.title}</h1>
        <p className="text-xl text-gray-400 mb-4">{project.tagline}</p>

        {/* Technologies */}
        <div className="flex flex-wrap gap-2 mb-4">
          {project.technologies.map((tech) => (
            <span
              key={tech.slug}
              className="text-sm px-3 py-1 rounded-full"
              style={{ backgroundColor: `${tech.color}20`, color: tech.color }}
            >
              {tech.name}
            </span>
          ))}
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-3">
          {project.live_url && (
            <a
              href={project.live_url}
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition text-sm"
            >
              Live Demo
            </a>
          )}
          {project.github_url && (
            <a
              href={project.github_url}
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition text-sm"
            >
              View Code
            </a>
          )}
          {project.documentation_url && (
            <a
              href={project.documentation_url}
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition text-sm"
            >
              Documentation
            </a>
          )}
        </div>
      </div>

      {/* Featured Image */}
      {project.featured_image && (
        <div className="relative w-full h-64 md:h-96 mb-8 rounded-lg overflow-hidden shadow-xl">
          <Image
            src={project.featured_image}
            alt={project.title}
            fill
            className="object-cover"
            priority
          />
        </div>
      )}

      {/* Description */}
      <div
        className="prose text-gray-300 max-w-none mb-8"
        dangerouslySetInnerHTML={{ __html: project.description }}
      />

      {/* Gallery */}
      {project.images.length > 0 && (
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-4">Gallery</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {project.images.map((img, i) => (
              <div key={i} className="relative h-64 rounded-lg overflow-hidden">
                <Image
                  src={img.image}
                  alt={img.caption || `${project.title} screenshot ${i + 1}`}
                  fill
                  className="object-cover"
                />
                {img.caption && (
                  <div className="absolute bottom-0 left-0 right-0 bg-black/60 px-3 py-2 text-sm text-gray-200">
                    {img.caption}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Project Details */}
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-5 mb-8">
        <h3 className="text-lg font-semibold text-white mb-3">Project Details</h3>
        <dl className="grid grid-cols-2 gap-3 text-sm">
          {project.start_date && (
            <>
              <dt className="text-gray-400">Started</dt>
              <dd className="text-gray-200">{formatDate(project.start_date)}</dd>
            </>
          )}
          <dt className="text-gray-400">Status</dt>
          <dd className="text-gray-200">
            {project.is_ongoing ? (
              <span className="text-green-400">Ongoing</span>
            ) : (
              formatDate(project.end_date) || "Completed"
            )}
          </dd>
        </dl>
      </div>

      {/* Related Projects */}
      {related.length > 0 && (
        <section>
          <h2 className="text-2xl font-bold text-white mb-6">Related Projects</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {related.map((p) => (
              <ProjectCard key={p.id} project={p} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
