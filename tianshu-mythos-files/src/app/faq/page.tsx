import PageShell from "@/components/PageShell";
import CTASection from "@/components/CTASection";
import JsonLd from "@/components/JsonLd";
import Link from "next/link";
import { buildPageMetadata } from "@/lib/metadata";
import { SITE_URL } from "@/lib/site";

export const metadata = buildPageMetadata({
  title: "Frequently Asked Questions",
  description:
    "Answers about TianShu MythOS, the Genesis Registry, Throne voting, Chronicle newsletter, and Founding Citizen membership.",
  path: "/faq",
});

const faqs = [
  [
    "What is TianShu MythOS?",
    "TianShu MythOS (天枢神谱) is an AI-native living fantasy universe. Readers join the Genesis Registry, back one of the Twelve Thrones, and receive weekly canon events through the Chronicle.",
  ],
  [
    "Is it free to join?",
    "Yes. The Citizen tier is free. You get a Registry number, weekly Chronicle emails, and public Throne voting.",
  ],
  [
    "How does Throne voting work?",
    "Each citizen can pledge Aether to a Throne. Weekly rankings signal which cosmic pressure should rise in the next canon cycle. Voting guides narrative direction without replacing editorial judgment.",
  ],
  [
    "What is the Chronicle?",
    "The Chronicle is a weekly email dispatch covering new canon events, character movements, and world consequences. It is designed as a story update, not a promotional newsletter.",
  ],
  [
    "When will paid membership launch?",
    "Founding Citizen and Lore Patron tiers are on the roadmap. Payment opens after the email, community, and voting loops prove retention. Join the free Registry now to secure early access.",
  ],
  [
    "What do I get as a Founding Citizen?",
    "Early canon drops, private vote rounds, a member badge, and member-only recaps. See the pricing page for full details.",
  ],
  [
    "Is the content AI-generated?",
    "MythOS uses AI-assisted narrative generation with human editorial curation. Reader votes provide pressure signals; canon requires judgment to stay coherent.",
  ],
  [
    "Can I explore without registering?",
    "Yes. The World Bible, characters, events, and Thrones are publicly accessible. Registration unlocks voting and Chronicle delivery.",
  ],
  [
    "Is there a Chinese version?",
    "A Chinese homepage is available at /zh. More Chinese content is planned.",
  ],
  [
    "How do I contact the team?",
    "Use the Press Kit page for media inquiries. Community discussion will move to Discord as the community grows.",
  ],
];

export default function FaqPage() {
  return (
    <PageShell label="FAQ">
      <JsonLd
        data={{
          "@context": "https://schema.org",
          "@type": "FAQPage",
          mainEntity: faqs.map(([q, a]) => ({
            "@type": "Question",
            name: q,
            acceptedAnswer: { "@type": "Answer", text: a },
          })),
        }}
      />
      <section className="mx-auto max-w-[900px] px-6 py-16 md:py-24">
        <p className="font-serif text-xs uppercase tracking-[0.26em] text-[#8b7535]">Help</p>
        <h1 className="mt-4 font-serif text-5xl text-[#c9a84c]">Frequently asked questions</h1>
        <p className="mt-5 text-lg leading-8 text-[#b0ab9c]">
          Everything you need to know before entering the Genesis Registry.
        </p>
        <div className="mt-10 space-y-4">
          {faqs.map(([q, a]) => (
            <details
              key={q}
              className="border border-[rgba(201,168,76,0.12)] bg-[#0e0e16] p-5 open:border-[rgba(201,168,76,0.28)]"
            >
              <summary className="cursor-pointer font-serif text-lg text-[#e8d08f]">{q}</summary>
              <p className="mt-3 text-sm leading-7 text-[#8a8578]">{a}</p>
            </details>
          ))}
        </div>
        <p className="mt-8 text-sm text-[#8a8578]">
          Still have questions? Read{" "}
          <Link href="/how-it-works" className="text-[#c9a84c] hover:text-[#e8d08f]">
            How it works
          </Link>{" "}
          or view{" "}
          <Link href="/pricing" className="text-[#c9a84c] hover:text-[#e8d08f]">
            Pricing
          </Link>
          .
        </p>
      </section>
      <CTASection />
    </PageShell>
  );
}
