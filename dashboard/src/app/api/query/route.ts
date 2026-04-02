import { NextRequest, NextResponse } from "next/server";
import { exec } from "child_process";
import path from "path";

export async function POST(req: NextRequest) {
  const { question } = await req.json();
  if (!question?.trim()) {
    return NextResponse.json({ error: "No question provided" }, { status: 400 });
  }

  const root = path.join(process.cwd(), "..");
  const escaped = question.replace(/"/g, '\\"');

  return new Promise<NextResponse>((resolve) => {
    exec(
      `py -3.14 main.py query "${escaped}"`,
      { cwd: root, timeout: 30000 },
      (err, stdout, stderr) => {
        if (err) {
          resolve(
            NextResponse.json({ answer: stderr || err.message, error: true })
          );
        } else {
          resolve(NextResponse.json({ answer: stdout.trim() }));
        }
      }
    );
  });
}
