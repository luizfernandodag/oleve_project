// src/types.ts
export interface Pin {
  image_url: string;
  title: string;
  pin_url: string;
  description: string;
  match_score: number;
  status: "approved" | "disqualified";
  ai_explanation?: string;
}