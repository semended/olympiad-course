"use client";

import { ChevronDown } from "lucide-react";
import { useState } from "react";

import type { CourseProgramSection } from "@/data/courses";

export function CourseAccordion({ sections }: { sections: CourseProgramSection[] }) {
  const [opened, setOpened] = useState<number | null>(0);

  return (
    <div className="space-y-3">
      {sections.map((section, index) => {
        const isOpen = opened === index;

        return (
          <div key={section.title} className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
            <button
              type="button"
              onClick={() => setOpened(isOpen ? null : index)}
              className="flex w-full items-center justify-between px-5 py-4 text-left"
            >
              <span className="text-base font-semibold text-slate-900">{section.title}</span>
              <ChevronDown
                className={`h-5 w-5 text-slate-500 transition-transform duration-300 ${isOpen ? "rotate-180" : ""}`}
              />
            </button>

            <div
              className={`grid transition-all duration-300 ease-in-out ${isOpen ? "grid-rows-[1fr]" : "grid-rows-[0fr]"}`}
            >
              <div className="overflow-hidden">
                <ul className="list-disc space-y-2 px-10 pb-5 text-sm text-slate-600">
                  {section.topics.map((topic) => (
                    <li key={topic}>{topic}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
