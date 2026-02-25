import { getServerSession } from "next-auth";
import { NextResponse } from "next/server";

import { authOptions } from "@/lib/auth";
import { getCourseById } from "@/lib/data/lms";
import { createCheckoutSession } from "@/lib/stripe";

export async function POST(request: Request) {
  const session = await getServerSession(authOptions);

  if (!session?.user?.id) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const body = (await request.json()) as { courseId?: string };

  if (!body.courseId) {
    return NextResponse.json({ error: "courseId is required" }, { status: 400 });
  }

  const course = await getCourseById(body.courseId);

  if (!course) {
    return NextResponse.json({ error: "Course not found" }, { status: 404 });
  }

  try {
    const checkoutSession = await createCheckoutSession(
      {
        id: course.id,
        title: course.title,
        price: course.price
      },
      {
        id: session.user.id
      }
    );

    if (!checkoutSession.url) {
      return NextResponse.json({ error: "Failed to create checkout session" }, { status: 500 });
    }

    return NextResponse.json({ url: checkoutSession.url });
  } catch (error) {
    return NextResponse.json({ error: (error as Error).message }, { status: 500 });
  }
}
