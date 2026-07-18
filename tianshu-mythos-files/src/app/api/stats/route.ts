import { NextResponse } from "next/server";
import pool from "@/lib/db";

export async function GET() {
  try {
    const { rows } = await pool.query("SELECT COUNT(*)::int AS registry_count FROM subscribers");
    return NextResponse.json({ registryCount: rows[0]?.registry_count ?? 0 });
  } catch {
    return NextResponse.json({ registryCount: 0 });
  }
}
