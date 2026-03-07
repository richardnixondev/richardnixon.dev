"use client";

import { useState } from "react";
import { submitContact } from "@/lib/api";

export default function ContactPage() {
  const [form, setForm] = useState({ name: "", email: "", subject: "", message: "" });
  const [status, setStatus] = useState<"idle" | "sending" | "sent" | "error">("idle");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus("sending");
    try {
      await submitContact(form);
      setStatus("sent");
      setForm({ name: "", email: "", subject: "", message: "" });
    } catch {
      setStatus("error");
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-3xl font-bold text-white mb-2">Contact</h1>
      <p className="text-gray-400 mb-8">
        Feel free to reach out. I&apos;ll get back to you as soon as possible.
      </p>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Form */}
        <div className="flex-1">
          {status === "sent" && (
            <div className="mb-6 p-4 rounded-lg bg-green-900 text-green-100">
              Message sent successfully!
            </div>
          )}
          {status === "error" && (
            <div className="mb-6 p-4 rounded-lg bg-red-900 text-red-100">
              Something went wrong. Please try again.
            </div>
          )}
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-300 mb-1">
                  Name
                </label>
                <input
                  id="name"
                  type="text"
                  required
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-gray-100 focus:outline-none focus:border-primary-500"
                />
              </div>
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-1">
                  Email
                </label>
                <input
                  id="email"
                  type="email"
                  required
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-gray-100 focus:outline-none focus:border-primary-500"
                />
              </div>
            </div>
            <div>
              <label htmlFor="subject" className="block text-sm font-medium text-gray-300 mb-1">
                Subject
              </label>
              <input
                id="subject"
                type="text"
                required
                value={form.subject}
                onChange={(e) => setForm({ ...form, subject: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-gray-100 focus:outline-none focus:border-primary-500"
              />
            </div>
            <div>
              <label htmlFor="message" className="block text-sm font-medium text-gray-300 mb-1">
                Message
              </label>
              <textarea
                id="message"
                rows={6}
                required
                value={form.message}
                onChange={(e) => setForm({ ...form, message: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-gray-100 focus:outline-none focus:border-primary-500 resize-none"
              />
            </div>
            <button
              type="submit"
              disabled={status === "sending"}
              className="px-6 py-3 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white rounded-lg transition font-medium"
            >
              {status === "sending" ? "Sending..." : "Send Message"}
            </button>
          </form>
        </div>

        {/* Sidebar */}
        <aside className="lg:w-72 space-y-4">
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-5">
            <h3 className="text-lg font-semibold text-white mb-3">Resume</h3>
            <p className="text-gray-400 text-sm mb-3">Download my latest resume.</p>
            <a
              href={`${process.env.NEXT_PUBLIC_API_URL || ""}/contact/resume`}
              className="inline-block px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition text-sm"
            >
              Download Resume
            </a>
          </div>
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-5">
            <h3 className="text-lg font-semibold text-white mb-3">Social</h3>
            <ul className="space-y-2">
              <li>
                <a
                  href="https://github.com/richardnixondev"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-400 hover:text-white text-sm transition"
                >
                  GitHub
                </a>
              </li>
              <li>
                <a
                  href="https://linkedin.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-400 hover:text-white text-sm transition"
                >
                  LinkedIn
                </a>
              </li>
            </ul>
          </div>
        </aside>
      </div>
    </div>
  );
}
