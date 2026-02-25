import bcrypt from "bcryptjs";
import { NextResponse } from "next/server";

import { prisma } from "@/lib/prisma";

export async function POST(request: Request) {
  const body = (await request.json()) as {
    name?: string;
    email?: string;
    password?: string;
  };

  if (!body.email || !body.password || !body.name) {
    return NextResponse.json({ error: "Все поля обязательны" }, { status: 400 });
  }

  const existingUser = await prisma.user.findUnique({ where: { email: body.email } });

  if (existingUser) {
    return NextResponse.json({ error: "Пользователь уже существует" }, { status: 409 });
  }

  const hashedPassword = await bcrypt.hash(body.password, 10);

  await prisma.user.create({
    data: {
      name: body.name,
      email: body.email,
      password: hashedPassword,
      role: "USER"
    }
  });

  return NextResponse.json({ success: true }, { status: 201 });
}
