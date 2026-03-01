import { notFound } from "next/navigation";

import { CoursePageTemplate } from "@/components/course-page-template";
import { COURSES, getCourseBySlug } from "@/data/courses";

type CoursePageProps = {
  params: {
    slug: string;
  };
};

export function generateStaticParams() {
  return COURSES.map((course) => ({ slug: course.slug }));
}

export default function CourseDetailsPage({ params }: CoursePageProps) {
  const course = getCourseBySlug(params.slug);

  if (!course) {
    notFound();
  }

  return <CoursePageTemplate course={course} />;
}
