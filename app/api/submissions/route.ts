import { getServerSession } from "next-auth";
import { NextResponse } from "next/server";

import { authOptions } from "@/lib/auth";
import { createSubmission, getLatestUserSubmissionForMaterial, getUserSubmissions } from "@/lib/data/submissions";

export async function GET(request: Request) {
  const session = await getServerSession(authOptions);

  if (!session?.user?.id) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { searchParams } = new URL(request.url);
  const materialId = searchParams.get("materialId");

  if (materialId) {
    const submission = await getLatestUserSubmissionForMaterial(session.user.id, materialId);
    return NextResponse.json({ submission });
  }

  const submissions = await getUserSubmissions(session.user.id);
  return NextResponse.json({ submissions });
}

export async function POST(request: Request) {
  const session = await getServerSession(authOptions);

  if (!session?.user?.id) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const body = (await request.json()) as {
    materialId?: string;
    fileUrl?: string;
  };

  if (!body.materialId || !body.fileUrl) {
    return NextResponse.json({ error: "materialId and fileUrl are required" }, { status: 400 });
  }

  const submission = await createSubmission({
    userId: session.user.id,
    materialId: body.materialId,
    fileUrl: body.fileUrl
  });

  return NextResponse.json({ submission }, { status: 201 });
}
