import { getServerSession } from "next-auth";
import { NextResponse } from "next/server";

import { authOptions } from "@/lib/auth";
import { uploadSubmissionFile } from "@/lib/s3";

const allowedTypes = new Set(["application/pdf", "image/jpeg", "image/png"]);

export async function POST(request: Request) {
  const session = await getServerSession(authOptions);

  if (!session?.user?.id) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const formData = await request.formData();
  const file = formData.get("file");

  if (!(file instanceof File)) {
    return NextResponse.json({ error: "File is required" }, { status: 400 });
  }

  if (!allowedTypes.has(file.type)) {
    return NextResponse.json({ error: "Only PDF, JPG, PNG are allowed" }, { status: 400 });
  }

  const arrayBuffer = await file.arrayBuffer();
  const buffer = Buffer.from(arrayBuffer);

  const { fileUrl } = await uploadSubmissionFile({
    userId: session.user.id,
    fileBuffer: buffer,
    contentType: file.type || "application/octet-stream"
  });

  return NextResponse.json({ fileUrl }, { status: 201 });
}
