import bcrypt from "bcryptjs";
import { MaterialType, Role } from "@prisma/client";

import { prisma } from "../lib/prisma";

async function main() {
  const adminEmail = "admin@olympiad.local";
  const adminPassword = await bcrypt.hash("admin12345", 10);

  const admin = await prisma.user.upsert({
    where: { email: adminEmail },
    update: {
      name: "Admin",
      role: Role.ADMIN,
      password: adminPassword
    },
    create: {
      name: "Admin",
      email: adminEmail,
      role: Role.ADMIN,
      password: adminPassword
    }
  });

  await prisma.submission.deleteMany();
  await prisma.progress.deleteMany();
  await prisma.enrollment.deleteMany();
  await prisma.material.deleteMany();
  await prisma.module.deleteMany();
  await prisma.course.deleteMany();

  const course = await prisma.course.create({
    data: {
      title: "Math Olympiad Starter",
      description: "Тестовый курс для разработки LMS-потока.",
      price: 0,
      durationDays: 60,
      modules: {
        create: [
          {
            title: "Module 1: Algebra Basics",
            order: 1,
            materials: {
              create: [
                {
                  title: "Lesson: Equations Intro",
                  type: MaterialType.LESSON,
                  content: "Базовые подходы к решению уравнений.",
                  order: 1
                },
                {
                  title: "Homework: Solve Equation Set",
                  type: MaterialType.HOMEWORK,
                  content: "Решите набор уравнений и опишите ход решения.",
                  order: 2
                }
              ]
            }
          },
          {
            title: "Module 2: Geometry",
            order: 2,
            materials: {
              create: [
                {
                  title: "Lesson: Triangle Properties",
                  type: MaterialType.LESSON,
                  content: "Свойства треугольников и типовые методы доказательства.",
                  order: 1
                },
                {
                  title: "Exam: Geometry Proof",
                  type: MaterialType.EXAM,
                  content: "Подготовьте доказательство и объясните ключевые шаги.",
                  order: 2
                }
              ]
            }
          }
        ]
      }
    }
  });

  await prisma.enrollment.create({
    data: {
      userId: admin.id,
      courseId: course.id,
      expiresAt: new Date(new Date().setMonth(new Date().getMonth() + 6))
    }
  });

  // eslint-disable-next-line no-console
  console.log("Seed completed:", { adminEmail, adminPasswordHint: "admin12345", courseId: course.id });
}

main()
  .catch((error) => {
    // eslint-disable-next-line no-console
    console.error(error);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
