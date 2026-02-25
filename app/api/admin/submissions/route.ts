import { getServerSession } from "next-auth";
import { NextResponse } from "next/server";

import { authOptions } from "@/lib/auth";
import { getAllSubmissions } from "@/lib/data/submissions";

export async function GET() {
  const session = await getServerSession(authOptions);

  if (session?.user?.role !== "ADMIN") {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  const submissions = await getAllSubmissions();

  return NextResponse.json({ submissions });
}
