import { prisma } from "@/lib/prisma";

export async function getUserEnrollments(userId: string) {
  return prisma.enrollment.findMany({
    where: { userId },
    include: {
      course: {
        include: {
          modules: {
            include: { materials: true },
            orderBy: { order: "asc" }
          }
        }
      }
    },
    orderBy: { expiresAt: "asc" }
  });
}

export async function getEnrollmentForCourse(userId: string, courseId: string) {
  return prisma.enrollment.findUnique({
    where: {
      userId_courseId: {
        userId,
        courseId
      }
    }
  });
}

export async function hasValidEnrollment(userId: string, courseId: string) {
  const enrollment = await getEnrollmentForCourse(userId, courseId);

  if (!enrollment) {
    return false;
  }

  return enrollment.expiresAt > new Date();
}

export async function upsertEnrollmentWithDurationDays(input: {
  userId: string;
  courseId: string;
  durationDays: number;
}) {
  const expiresAt = new Date();
  expiresAt.setDate(expiresAt.getDate() + input.durationDays);

  return prisma.enrollment.upsert({
    where: {
      userId_courseId: {
        userId: input.userId,
        courseId: input.courseId
      }
    },
    create: {
      userId: input.userId,
      courseId: input.courseId,
      expiresAt
    },
    update: {
      expiresAt
    }
  });
}
