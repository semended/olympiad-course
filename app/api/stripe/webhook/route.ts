import Stripe from "stripe";
import { NextResponse } from "next/server";

import { upsertEnrollmentWithDurationDays } from "@/lib/data/enrollments";
import { getCourseById } from "@/lib/data/lms";
import { getStripe, getStripeWebhookSecret } from "@/lib/stripe";

export async function POST(request: Request) {
  const signature = request.headers.get("stripe-signature");

  if (!signature) {
    return NextResponse.json({ error: "Missing stripe-signature header" }, { status: 400 });
  }

  const body = await request.text();

  try {
    const stripe = getStripe();
    const webhookSecret = getStripeWebhookSecret();

    const event = stripe.webhooks.constructEvent(body, signature, webhookSecret);

    if (event.type === "checkout.session.completed") {
      const session = event.data.object as Stripe.Checkout.Session;
      const userId = session.metadata?.userId;
      const courseId = session.metadata?.courseId;

      if (userId && courseId) {
        const course = await getCourseById(courseId);

        if (course) {
          await upsertEnrollmentWithDurationDays({
            userId,
            courseId,
            durationDays: course.durationDays
          });
        }
      }
    }

    return NextResponse.json({ received: true });
  } catch (error) {
    // eslint-disable-next-line no-console
    console.error("Stripe webhook error:", error);
    return NextResponse.json({ error: (error as Error).message }, { status: 400 });
  }
}
