import Link from "next/link";

export type RailCase = {
  id: string;
  title: string;
};

export function Rail({
  cases,
  currentId,
}: {
  cases: RailCase[];
  currentId?: string;
}) {
  return (
    <nav className="list" aria-label="Package">
      <Link href="/" className="case-link" data-active={currentId === "docket"}>
        <strong>Docket</strong>
        <span>OH-01 and the package</span>
      </Link>
      <h2>Writes</h2>
      {cases.map((item) => (
        <Link
          key={item.id}
          href={`/cases/${item.id}`}
          className="case-link"
          data-active={item.id === currentId}
        >
          <strong>{item.id}</strong>
          <span>{item.title}</span>
        </Link>
      ))}
    </nav>
  );
}
