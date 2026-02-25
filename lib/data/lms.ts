import { prisma } from "@/lib/prisma";

export async function getCoursesForUser(userId: string) {
  const enrollments = await prisma.enrollment.findMany({
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
    }
  });

  if (enrollments.length > 0) {
    return enrollments.map((enrollment) => enrollment.course);
  }

  return prisma.course.findMany({
    include: {
      modules: {
        include: { materials: true },
        orderBy: { order: "asc" }
      }
    },
    orderBy: { createdAt: "desc" }
  });
}

export async function getAllCourses() {
  return prisma.course.findMany({
    include: {
      modules: {
        include: { materials: true },
        orderBy: { order: "asc" }
      }
    },
    orderBy: { createdAt: "desc" }
  });
}

export async function getCourseById(courseId: string) {
  return prisma.course.findUnique({
    where: { id: courseId },
    include: {
      modules: {
        include: { materials: true },
        orderBy: { order: "asc" }
      }
    }
  });
}

export async function getModuleById(courseId: string, moduleId: string) {
  return prisma.module.findFirst({
    where: { id: moduleId, courseId },
    include: {
      course: true,
      materials: {
        orderBy: { order: "asc" }
      }
    }
  });
}

export async function getMaterialById(materialId: string) {
  return prisma.material.findUnique({
    where: { id: materialId },
    include: {
      module: {
        include: {
          course: true
        }
      }
    }
  });
}
