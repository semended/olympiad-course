import { PutObjectCommand, S3Client } from "@aws-sdk/client-s3";

import { requireEnv } from "@/lib/env";

function getS3ClientConfig() {
  const region = requireEnv("AWS_REGION");
  const accessKeyId = requireEnv("AWS_ACCESS_KEY_ID");
  const secretAccessKey = requireEnv("AWS_SECRET_ACCESS_KEY");

  return {
    region,
    credentials: {
      accessKeyId,
      secretAccessKey
    }
  };
}

export function getS3Bucket() {
  return requireEnv("AWS_S3_BUCKET");
}

export async function uploadSubmissionFile(params: {
  userId: string;
  fileBuffer: Buffer;
  contentType: string;
}) {
  const bucket = getS3Bucket();
  const { region } = getS3ClientConfig();
  const client = new S3Client(getS3ClientConfig());

  const key = `submissions/${params.userId}/${Date.now()}.pdf`;

  await client.send(
    new PutObjectCommand({
      Bucket: bucket,
      Key: key,
      Body: params.fileBuffer,
      ContentType: params.contentType
    })
  );

  const fileUrl = `https://${bucket}.s3.${region}.amazonaws.com/${key}`;

  return {
    key,
    fileUrl
  };
}
