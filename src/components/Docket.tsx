import Link from "next/link";
import { Rail } from "@/components/Rail";
import { ReplayAll } from "@/components/ReplayAll";
import { CONTRIBUTIONS, type ExceptionRecord } from "@/lib/exceptions";
import { provenanceLabel, type Provenance } from "@/lib/provenance";

export type DocketWrite = {
  id: string;
  title: string;
  fieldLabel: string;
  provenance: Provenance;
  writable: boolean;
};

export function Docket({
  exception,
  exceptionWrites,
  otherWrites,
}: {
  exception: ExceptionRecord;
  exceptionWrites: DocketWrite[];
  otherWrites: DocketWrite[];
}) {
  return (
    <div className="shell">
      <Rail
        cases={[...exceptionWrites, ...otherWrites]}
        currentId="docket"
      />
      <main className="work">
        <p className="kicker">Package · fixture replay</p>
        <h1>{exception.id}</h1>
        <p className="reason">{exception.title}. {exception.purpose}</p>
        <ReplayAll />
        <ul className="facts">
          {exception.facts.map((fact) => (
            <li key={fact}>{fact}</li>
          ))}
        </ul>

        <h2>Writes from this exception</h2>
        <ul className="writes">
          {exceptionWrites.map((item) => (
            <li key={item.id}>
              <Link href={`/cases/${item.id}`}>
                <strong>
                  {item.id} · {item.fieldLabel}
                </strong>
                <span>
                  {provenanceLabel(item.provenance)} · writable {item.writable ? "yes" : "no"}
                </span>
              </Link>
            </li>
          ))}
        </ul>

        <h2>Other identifier classes</h2>
        <ul className="writes">
          {otherWrites.map((item) => (
            <li key={item.id}>
              <Link href={`/cases/${item.id}`}>
                <strong>
                  {item.id} · {item.fieldLabel}
                </strong>
                <span>
                  {provenanceLabel(item.provenance)} · writable {item.writable ? "yes" : "no"}
                </span>
              </Link>
            </li>
          ))}
        </ul>

        <h2>This package</h2>
        <dl className="pack">
          <div>
            <dt>Skill</dt>
            <dd>
              <code>skills/exact-ref/</code> classifies spoken identifiers. It does not place a
              call.
            </dd>
          </div>
          <div>
            <dt>CLI</dt>
            <dd>
              <code>npm run exactref -- classify|verify|compile</code>. Exit 0 only when writable.
            </dd>
          </div>
          <div>
            <dt>Board</dt>
            <dd>Character diff and the second-channel stamp. Live create is fail-closed.</dd>
          </div>
          <div>
            <dt>CALL-E</dt>
            <dd>
              {CONTRIBUTIONS.map((item, index) => (
                <span key={item.id}>
                  {index > 0 ? ", " : ""}
                  <a href={item.href} rel="noreferrer">
                    #{item.id}
                  </a>
                </span>
              ))}
            </dd>
          </div>
        </dl>
      </main>
    </div>
  );
}
