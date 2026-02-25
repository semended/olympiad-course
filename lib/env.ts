export function requireEnv(name: string) {
  const value = process.env[name];

  if (!value) {
    throw new Error(`Missing ENV: ${name}`);
  }

  return value;
}
