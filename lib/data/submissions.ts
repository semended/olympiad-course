import { SubmissionStatus } from "@prisma/client";

import { prisma } from "@/lib/prisma";

export async function createSubmission(input: {
  userId: string;
  materialId: string;
  fileUrl: string;
}) {
  return prisma.submission.create({
    data: {
      userId: input.userId,
      materialId: input.materialId,
      fileUrl: input.fileUrl,
      extractedText: null,
      status: SubmissionStatus.PENDING,
      aiScore: null,
      teacherScore: null,
      aiFeedback: null,
      teacherFeedback: null
    },
    include: {
      material: true
    }
  });
}

export async function getLatestUserSubmissionForMaterial(userId: string, materialId: string) {
  return prisma.submission.findFirst({
    where: { userId, materialId },
    orderBy: { createdAt: "desc" }
  });
}

export async function getUserSubmissions(userId: string) {
  return prisma.submission.findMany({
    where: { userId },
    include: {
      material: true
    },
    orderBy: { createdAt: "desc" }
  });
}

export async function getAllSubmissions() {
  return prisma.submission.findMany({
    include: {
      user: true,
      material: true
    },
    orderBy: { createdAt: "desc" }
  });
}

export async function getSubmissionById(submissionId: string) {
  return prisma.submission.findUnique({
    where: { id: submissionId },
    include: {
      user: true,
      material: true
    }
  });
}

export async function reviewSubmission(input: {
  submissionId: string;
  teacherScore: number;
  teacherFeedback: string;
}) {
  return prisma.submission.update({
    where: { id: input.submissionId },
    data: {
      status: SubmissionStatus.REVIEWED,
      teacherScore: input.teacherScore,
      teacherFeedback: input.teacherFeedback
    },
    include: {
      user: true,
      material: true
    }
  });
}

export async function getLatestSubmissionMapForUser(userId: string) {
  const submissions = await prisma.submission.findMany({
    where: { userId },
    orderBy: { createdAt: "desc" }
  });

  const map = new Map<string, (typeof submissions)[number]>();

  for (const submission of submissions) {
    if (!map.has(submission.materialId)) {
      map.set(submission.materialId, submission);
    }
  }

  return map;
}
