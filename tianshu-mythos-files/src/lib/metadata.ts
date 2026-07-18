import type { Metadata } from "next";
import { SITE_NAME, SITE_URL } from "./site";

export function buildPageMetadata({
  title,
  description,
  path,
  alternateLocale,
}: {
  title: string;
  description: string;
  path: string;
  alternateLocale?: { lang: string; path: string };
}): Metadata {
  const url = path === "/" ? SITE_URL : `${SITE_URL}${path}`;
  const languages: Record<string, string> = { en: url };
  if (alternateLocale) {
    languages[alternateLocale.lang] = `${SITE_URL}${alternateLocale.path}`;
  }
  const ogTitle =
    title.includes("TianShu") || title.includes("MythOS") ? title : `${title} | ${SITE_NAME}`;
  return {
    title,
    description,
    alternates: { canonical: url, languages },
    openGraph: {
      title: ogTitle,
      description,
      url,
      siteName: SITE_NAME,
      type: "website",
      locale: "en_US",
      images: [{ url: "/og-image.png", width: 1200, height: 630, alt: SITE_NAME }],
    },
    twitter: {
      card: "summary_large_image",
      title: ogTitle,
      description,
      images: ["/og-image.png"],
    },
  };
}
