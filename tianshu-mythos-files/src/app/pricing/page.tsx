import PageShell from "@/components/PageShell";
import CTASection from "@/components/CTASection";
import JsonLd from "@/components/JsonLd";
import Link from "next/link";
import { buildPageMetadata } from "@/lib/metadata";
import { SITE_URL } from "@/lib/site";

export const metadata = buildPageMetadata({
  title: "Pricing & Membership",
  description:
    "Compare Citizen, Founding Citizen, and Lore Patron membership tiers for TianShu MythOS. Join the free Genesis Registry today.",
  path: "/pricing",
});

const tiers = [
  {
    name: "Citizen",
    price: "Free",
    status: "Available now",
    features: [
      "Genesis Registry number",
      "Weekly Chronicle email",
      "Public Throne voting",
      "Full archive access",
    ],
    cta: "Join the Registry",
    href: "/join",
    highlight: false,
  },
  {
    name: "Founding Citizen",
    price: "$5 / mo",
    status: "Waitlist open",
    features: [
      "Everything in Citizen",
      "Early canon drops",
      "Private vote rounds",
      "Member badge",
      "Member-only recaps",
    ],
    cta: "Join waitlist",
    href: "/join?plan=founding",
    highlight: true,
  },
  {
    name: "Lore Patron",
    price: "$15 / mo",
    status: "Coming soon",
    features: [
      "Everything in Founding Citizen",
      "Character naming proposals",
      "Quarterly world event input",
      "Private archive notes",
    ],
    cta: "Join waitlist",
    href: "/join?plan=patron",
    highlight: false,
  },
];

export default function PricingPage() {
  return (
    <PageShell label="Pricing">
      <JsonLd
        data={{
          "@context": "https://schema.org",
          "@type": "WebPage",
          name: "Pricing & Membership",
          url: `${SITE_URL}/pricing`,
          description: "Membership tiers for TianShu MythOS.",
        }}
      />
      <section className="mx-auto max-w-[1120px] px-6 py-16 text-center md:py-24">
        <p className="font-serif text-xs uppercase tracking-[0.26em] text-[#8b7535]">Membership</p>
        <h1 className="mt-4 font-serif text-5xl text-[#c9a84c] md:text-6xl">
          Choose your place in the First Age.
        </h1>
        <p className="mx-auto mt-5 max-w-[760px] text-lg leading-8 text-[#b0ab9c]">
          Start free with the Genesis Registry. Paid tiers unlock when the community loop proves
          retention — join now to secure early access.
        </p>
      </section>
      <section className="mx-auto grid max-w-[1120px] gap-5 px-6 pb-16 md:grid-cols-3">
        {tiers.map((tier) => (
          <div
            key={tier.name}
            className={`border p-7 ${
              tier.highlight
                ? "border-[#c9a84c] bg-[#12121c] shadow-[0_0_60px_rgba(201,168,76,0.08)]"
                : "border-[rgba(201,168,76,0.13)] bg-[#0e0e16]"
            }`}
          >
            <p className="text-xs uppercase tracking-[0.16em] text-[#8b7535]">{tier.status}</p>
            <h2 className="mt-2 font-serif text-2xl text-[#e8d08f]">{tier.name}</h2>
            <p className="mt-3 font-serif text-3xl text-[#c9a84c]">{tier.price}</p>
            <ul className="mt-5 space-y-2 text-sm leading-6 text-[#8a8578]">
              {tier.features.map((f) => (
                <li key={f}>• {f}</li>
              ))}
            </ul>
            <Link
              href={tier.href}
              className={`mt-6 inline-block w-full px-5 py-3 text-center font-serif text-xs uppercase tracking-[0.14em] ${
                tier.highlight
                  ? "bg-[#c9a84c] text-[#08080c] hover:bg-[#e8d08f]"
                  : "border border-[rgba(201,168,76,0.35)] text-[#c9a84c] hover:border-[#c9a84c]"
              }`}
            >
              {tier.cta}
            </Link>
          </div>
        ))}
      </section>
      <section className="mx-auto max-w-[900px] px-6 pb-12 text-center">
        <p className="text-sm leading-7 text-[#8a8578]">
          Payment processing is not live yet. Founding Citizen and Lore Patron are waitlist tiers —
          join the free Registry first, then upgrade when billing opens.
        </p>
        <Link href="/faq" className="mt-4 inline-block text-sm text-[#c9a84c] hover:text-[#e8d08f]">
          Read membership FAQ →
        </Link>
      </section>
      <CTASection
        title="Enter the Registry before paid tiers open."
        body="Early citizens receive priority access to Founding Citizen when billing goes live."
      />
    </PageShell>
  );
}
