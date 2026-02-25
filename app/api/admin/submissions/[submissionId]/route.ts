import { Prisma } from "@prisma/client";
import { getServerSession } from "next-auth";
import { NextResponse } from "next/server";

import { authOptions } from "@/lib/auth";
import { getSubmissionById, reviewSubmission } from "@/lib/data/submissions";

type Params = {
  params: {
    submissionId: string;
  };
};

export async function GET(_request: Request, { params }: Params) {
  const session = await getServerSession(authOptions);

  if (session?.user?.role !== "ADMIN") {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  const submission = await getSubmissionById(params.submissionId);

  if (!submission) {
    return NextResponse.json({ error: "Submission not found" }, { status: 404 });
  }

  return NextResponse.json({ submission });
}

export async function PATCH(request: Request, { params }: Params) {
  const session = await getServerSession(authOptions);

  if (session?.user?.role !== "ADMIN") {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  const body = (await request.json()) as {
    teacherScore?: number;
    teacherFeedback?: string;
  };

  if (
    typeof body.teacherScore !== "number" ||
    Number.isNaN(body.teacherScore) ||
    body.teacherScore < 0 ||
    body.teacherScore > 7
  ) {
    return NextResponse.json({ error: "teacherScore must be between 0 and 7" }, { status: 400 });
  }

  try {
    const submission = await reviewSubmission({
      submissionId: params.submissionId,
      teacherScore: body.teacherScore,
      teacherFeedback: (body.teacherFeedback ?? "").trim()
    });

    return NextResponse.json({ submission });
  } catch (error) {
    if (
      error instanceof Prisma.PrismaClientKnownRequestError &&
      error.code === "P2025"
    ) {
      return NextResponse.json({ error: "Submission not found" }, { status: 404 });
    }

    throw error;
  }
}
