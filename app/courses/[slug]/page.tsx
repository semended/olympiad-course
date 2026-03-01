import { notFound } from "next/navigation";

import CoursePageTemplate from "@/components/CoursePageTemplate";

const courseSlugs = ["olmat-5-6", "olmat-6-7", "olmat-7-8"];

export function generateStaticParams() {
  return courseSlugs.map((slug) => ({ slug }));
}

export default function CoursePage({
  params
}: {
  params: { slug: string };
}) {
  if (!courseSlugs.includes(params.slug)) {
    notFound();
  }

  return <CoursePageTemplate slug={params.slug} />;
}
