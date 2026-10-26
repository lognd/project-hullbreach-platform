import { useSession } from "@/auth/session";
import { ButtonLink } from "@/components/Button";
import { HullReadout } from "@/components/HullReadout";
import { Panel, SectionHeading } from "@/components/Readout";

/** The four beats of a match, numbered down the landing page: what you do, in the order you do it. */
const LOOP = [
  ["01", "Build", "Assemble your ship block by block: hull, thrusters, weapons."],
  ["02", "Fly", "Real gravity, real momentum. Mass you add is mass you have to move."],
  ["03", "Breach", "Hits load the hull block by block. Overload one and it breaks open."],
  ["04", "Rank", "Every match moves your ELO and lands in your match history."],
] as const;

// frob:ticket 01M2H5T11EWXN4QEQ0QET8ZC6Y
// frob:doc docs/index.md#landing-and-policy-pages
/** The `/` route: premise, the four-beat match loop, and account and download calls to action; the signed-in view swaps register/login for profile links. */
export function Landing() {
  const session = useSession();
  return (
    <main className="flex w-full flex-1 flex-col bg-paper text-ink">
      <div className="mx-auto grid w-full max-w-[72rem] items-start gap-space-48 px-space-16 py-space-48 sm:px-space-24 lg:grid-cols-2 lg:py-space-64">
        <div className="flex flex-col gap-space-24">
          <div className="flex flex-col gap-space-12">
            <h1 className="font-display text-font-size-32 uppercase leading-none tracking-wider sm:text-font-size-48">
              Project Hullbreach
            </h1>
            <h2 className="font-display text-font-size-20 uppercase leading-tight tracking-wider text-accent sm:text-font-size-24">
              Build. Breach. Claim the void.
            </h2>
          </div>
          <p className="max-w-[32rem] text-font-size-20 text-muted">
            Build a spaceship one block at a time. Fly it under real gravity. Break the
            enemy&apos;s hull before it breaks yours.
          </p>
          <div className="flex flex-wrap gap-space-12">
            {session === null ? (
              <>
                <ButtonLink href="/register" variant="primary">
                  Create account
                </ButtonLink>
                <ButtonLink href="/login">Log in</ButtonLink>
              </>
            ) : (
              <>
                <ButtonLink href="/me" variant="primary">
                  Profile
                </ButtonLink>
                <ButtonLink href="/me/matches">Match history</ButtonLink>
              </>
            )}
          </div>
          <Panel label="Download">
            <div className="flex flex-col gap-space-8 px-space-16 py-space-16">
              <SectionHeading id="landing-download">Game build</SectionHeading>
              <p className="text-font-size-14 text-muted">
                The downloadable game is not published yet. An account made now works the
                day it ships, and your ELO and match history are kept with it.
              </p>
            </div>
          </Panel>
          <section aria-labelledby="landing-loop" className="flex flex-col gap-space-12">
            <SectionHeading id="landing-loop">How a match runs</SectionHeading>
            <ol className="m-space-0 grid list-none gap-space-8 p-space-0 sm:grid-cols-2">
              {LOOP.map(([step, name, line]) => (
                <li
                  key={step}
                  className="flex flex-col gap-space-4 border border-line bg-panel px-space-16 py-space-12"
                >
                  <span className="font-mono text-font-size-12 uppercase tracking-widest text-accent">
                    {step} {name}
                  </span>
                  <span className="text-font-size-14 text-muted">{line}</span>
                </li>
              ))}
            </ol>
          </section>
        </div>
        <HullReadout />
      </div>
    </main>
  );
}
