export const dynamic = "force-dynamic";

import Link from "next/link";
import ProjectCard from "@/components/ProjectCard";
import { getProjects, getTechnologies, getFeaturedProjects } from "@/lib/api";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Portfolio",
  description: "Projects and work showcase.",
};

export default async function PortfolioPage({
  searchParams,
}: {
  searchParams: Promise<{ tech?: string }>;
}) {
  const params = await searchParams;
  const tech = params.tech || "";

  const [projects, technologies, featured] = await Promise.all([
    getProjects(tech || undefined),
    getTechnologies(),
    tech ? Promise.resolve([]) : getFeaturedProjects(),
  ]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-3xl font-bold text-white mb-8">Portfolio</h1>

      {/* Technology Filter */}
      <div className="flex flex-wrap gap-2 mb-8">
        <Link
          href="/portfolio"
          className={`text-sm px-3 py-1 rounded-full transition ${
            !tech
              ? "bg-primary-600 text-white"
              : "bg-gray-700 text-gray-300 hover:text-white"
          }`}
        >
          All
        </Link>
        {technologies.map((t) => (
          <Link
            key={t.slug}
            href={`/portfolio?tech=${t.slug}`}
            className={`text-sm px-3 py-1 rounded-full transition ${
              tech === t.slug
                ? "bg-primary-600 text-white"
                : "bg-gray-700 text-gray-300 hover:text-white"
            }`}
          >
            {t.name}
          </Link>
        ))}
      </div>

      {/* Featured */}
      {featured.length > 0 && (
        <section className="mb-12">
          <h2 className="text-xl font-semibold text-white mb-4">Featured</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {featured.map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </div>
        </section>
      )}

      {/* All Projects */}
      {projects.length === 0 ? (
        <p className="text-gray-400">No projects found.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      )}
    </div>
  );
}
