import { SubmissionStatus, type Material } from "@prisma/client";

import { getCourseById } from "@/lib/data/lms";
import { getLatestSubmissionMapForUser } from "@/lib/data/submissions";

type MaterialState = {
  material: Material;
  status: "NOT_SUBMITTED" | "PENDING" | "REVIEWED";
  teacherScore: number | null;
};

export type CourseProgress = {
  totalTasks: number;
  completedTasks: number;
  averageScore: number | null;
  percent: number;
  materialStates: MaterialState[];
};

export async function getCourseProgressForUser(courseId: string, userId: string): Promise<CourseProgress> {
  const course = await getCourseById(courseId);

  if (!course) {
    return {
      totalTasks: 0,
      completedTasks: 0,
      averageScore: null,
      percent: 0,
      materialStates: []
    };
  }

  const latestSubmissionMap = await getLatestSubmissionMapForUser(userId);
  const taskMaterials = course.modules
    .flatMap((module) => module.materials)
    .filter((material) => material.type === "HOMEWORK" || material.type === "EXAM");

  const materialStates = taskMaterials.map((material) => {
    const latest = latestSubmissionMap.get(material.id);

    if (!latest) {
      return { material, status: "NOT_SUBMITTED" as const, teacherScore: null };
    }

    if (latest.status === SubmissionStatus.REVIEWED) {
      return { material, status: "REVIEWED" as const, teacherScore: latest.teacherScore };
    }

    return { material, status: "PENDING" as const, teacherScore: null };
  });

  const totalTasks = taskMaterials.length;
  const reviewed = materialStates.filter((item) => item.status === "REVIEWED");
  const completedTasks = reviewed.length;
  const percent = totalTasks === 0 ? 0 : Math.round((completedTasks / totalTasks) * 100);
  const scores = reviewed
    .map((item) => item.teacherScore)
    .filter((score): score is number => typeof score === "number");

  const averageScore =
    scores.length === 0 ? null : Number((scores.reduce((sum, score) => sum + score, 0) / scores.length).toFixed(2));

  return {
    totalTasks,
    completedTasks,
    averageScore,
    percent,
    materialStates
  };
}
