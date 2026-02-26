import Stripe from "stripe";

import { requireEnv } from "@/lib/env";

export function getStripe() {
  const secretKey = requireEnv("STRIPE_SECRET_KEY");

  return new Stripe(secretKey, {
    apiVersion: "2025-02-24.acacia"
  });
}

export function getStripeWebhookSecret() {
  return requireEnv("STRIPE_WEBHOOK_SECRET");
}

export function getAppUrl() {
  return requireEnv("NEXT_PUBLIC_APP_URL");
}

export async function createCheckoutSession(course: {
  id: string;
  title: string;
  price: number;
}, user: { id: string }) {
  const stripe = getStripe();
  const appUrl = getAppUrl();

  return stripe.checkout.sessions.create({
    mode: "payment",
    line_items: [
      {
        quantity: 1,
        price_data: {
          currency: "usd",
          product_data: {
            name: course.title
          },
          unit_amount: course.price
        }
      }
    ],
    success_url: `${appUrl}/courses?success=true`,
    cancel_url: `${appUrl}/courses?canceled=true`,
    metadata: {
      userId: user.id,
      courseId: course.id
    }
  });
}
