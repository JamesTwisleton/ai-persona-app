"use client";

import React from "react";
import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/Button";

export function Onboarding() {
  return (
    <div className="bg-white dark:bg-gray-900">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-16 pb-20 lg:pt-24 lg:pb-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center">
            <div className="flex justify-center mb-6">
              <div className="bg-indigo-50 dark:bg-indigo-900/30 rounded-2xl p-3 ring-1 ring-indigo-500/20">
                <Image src="/logo.jpeg" alt="PersonaComposer" width={64} height={64} className="rounded-xl" unoptimized />
              </div>
            </div>
            <h1 className="text-4xl sm:text-6xl font-extrabold text-gray-900 dark:text-white tracking-tight mb-6">
              Simulate Reality with <span className="text-indigo-600 dark:text-indigo-400">AI Focus Groups</span>
            </h1>
            <p className="max-w-2xl mx-auto text-lg sm:text-xl text-gray-600 dark:text-gray-400 mb-10">
              PersonaComposer lets you build psychologically realistic AI personas and test your ideas in instant, multi-persona focus group simulations.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/login">
                <Button className="w-full sm:w-auto px-8 py-4 text-lg rounded-full shadow-lg hover:scale-105 transition-transform">
                  Get Started Free
                </Button>
              </Link>
              <Link href="/feed">
                <Button
                  variant="secondary"
                  className="w-full sm:w-auto px-8 py-4 text-lg rounded-full hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                >
                  Explore Public Feed
                </Button>
              </Link>
            </div>
          </div>
        </div>

        {/* Background blobs */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 blur-3xl opacity-20 dark:opacity-10 pointer-events-none">
          <div className="w-[800px] h-[600px] bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full" />
        </div>
      </section>

      {/* Core Functionality - Visual Showcase */}
      <section className="py-20 bg-gray-50 dark:bg-gray-800/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">How it Works</h2>
            <p className="text-gray-600 dark:text-gray-400">From a simple description to a complex psychological profile.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Step 1: Persona Creation */}
            <div className="bg-white dark:bg-gray-800 p-8 rounded-3xl border border-gray-200 dark:border-gray-700 shadow-sm">
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-xl flex items-center justify-center mb-6">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">1. Build a Persona</h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4 text-sm">
                Enter a name and backstory. Our AI automatically infers their <strong>OCEAN</strong> personality traits and generates a unique profile picture.
              </p>
              <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-900/50 rounded-xl border border-dashed border-gray-300 dark:border-gray-600">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-8 h-8 rounded-full bg-purple-500" />
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-24" />
                </div>
                <div className="space-y-2">
                  <div className="h-2 bg-indigo-400 rounded-full w-[80%]" />
                  <div className="h-2 bg-blue-400 rounded-full w-[40%]" />
                  <div className="h-2 bg-amber-400 rounded-full w-[60%]" />
                </div>
              </div>
            </div>

            {/* Step 2: Focus Groups */}
            <div className="bg-white dark:bg-gray-800 p-8 rounded-3xl border border-gray-200 dark:border-gray-700 shadow-sm">
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-xl flex items-center justify-center mb-6">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">2. Run Focus Groups</h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4 text-sm">
                Choose multiple personas and give them a topic. Watch as they engage in a realistic, multi-perspective conversation based on their personalities.
              </p>
              <div className="mt-6 space-y-3">
                <div className="p-2 bg-gray-50 dark:bg-gray-900/50 rounded-lg text-[10px] text-gray-500 border border-gray-100 dark:border-gray-800">
                  &quot;I disagree, this proposal ignores economic realities...&quot;
                </div>
                <div className="p-2 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg text-[10px] text-indigo-600 dark:text-indigo-400 border border-indigo-100 dark:border-indigo-900/30 ml-4">
                  &quot;Actually, the social impact could be huge!&quot;
                </div>
              </div>
            </div>

            {/* Step 3: Challenge Mode */}
            <div className="bg-white dark:bg-gray-800 p-8 rounded-3xl border border-gray-200 dark:border-gray-700 shadow-sm">
              <div className="w-12 h-12 bg-red-100 dark:bg-red-900/30 rounded-xl flex items-center justify-center mb-6">
                <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">3. Challenge Mode</h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4 text-sm">
                Propose an idea and try to persuade disagreeable personas. See your <strong>persuasion score</strong> update in real-time as you refine your arguments.
              </p>
              <div className="mt-6 p-4 bg-red-50 dark:bg-red-900/20 rounded-xl border border-red-100 dark:border-red-900/30">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-[10px] font-bold text-red-600 dark:text-red-400 uppercase">Persuasion Score</span>
                  <span className="text-xs font-bold text-gray-900 dark:text-white">68%</span>
                </div>
                <div className="h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <div className="h-full bg-red-500 w-[68%]" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Key Concepts */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-12 text-center">Key Concepts</h2>

          <div className="space-y-12">
            <div className="flex flex-col md:flex-row gap-8 items-start">
              <div className="flex-1">
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">What is a Persona?</h3>
                <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                  A Persona is more than just a chatbot. It&apos;s a unique AI character with a consistent worldview, backstory, and personality profile based on the <strong>Big Five (OCEAN)</strong> model:
                </p>
                <ul className="mt-4 grid grid-cols-2 gap-2">
                  <li className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <span className="w-2 h-2 rounded-full bg-ocean-openness" /> Openness
                  </li>
                  <li className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <span className="w-2 h-2 rounded-full bg-ocean-conscientiousness" /> Conscientiousness
                  </li>
                  <li className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <span className="w-2 h-2 rounded-full bg-ocean-extraversion" /> Extraversion
                  </li>
                  <li className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <span className="w-2 h-2 rounded-full bg-ocean-agreeableness" /> Agreeableness
                  </li>
                  <li className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <span className="w-2 h-2 rounded-full bg-ocean-neuroticism" /> Neuroticism
                  </li>
                </ul>
              </div>
              <div className="w-full md:w-64 bg-gray-50 dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700">
                <div className="aspect-square bg-gray-200 dark:bg-gray-700 rounded-xl mb-4 animate-pulse" />
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2" />
                <div className="h-3 bg-gray-100 dark:bg-gray-800 rounded w-1/2" />
              </div>
            </div>

            <div className="flex flex-col md:flex-row-reverse gap-8 items-start">
              <div className="flex-1">
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Focus Groups & Challenge Mode</h3>
                <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                  Traditional AI chat is one-on-one. <strong>Focus Groups</strong> allow you to see how different personalities interact with each other.
                  <strong> Challenge Mode</strong> takes it a step further, pitting you against tough critics to test how persuasive your ideas really are.
                </p>
              </div>
              <div className="w-full md:w-64 flex flex-col gap-2">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="bg-gray-50 dark:bg-gray-800 p-3 rounded-xl border border-gray-200 dark:border-gray-700 flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-indigo-100 dark:bg-indigo-900/30" />
                    <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded" />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Footer */}
      <section className="py-20 bg-indigo-600 dark:bg-indigo-900">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-white mb-6">Ready to start simulating?</h2>
          <p className="text-indigo-100 mb-10 text-lg">
            Join PersonaComposer today and build your first focus group in seconds.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/login">
              <button className="w-full sm:w-auto px-10 py-4 bg-white text-indigo-600 hover:bg-indigo-50 font-bold text-lg rounded-full transition-colors shadow-lg">
                Create Account
              </button>
            </Link>
            <Link href="/feed">
              <button
                className="w-full sm:w-auto px-10 py-4 bg-transparent border-2 border-white text-white hover:bg-white/10 font-bold text-lg rounded-full transition-colors"
              >
                Explore First
              </button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
