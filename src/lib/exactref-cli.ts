import { applyHumanVerification, classifyIdentifier, type IdentifierObservation } from "./provenance";
import { compileIdentifierTask } from "./task";

export type CliResult = {
  code: number;
  stdout: string;
  stderr: string;
};

function hasFlag(args: string[], name: string): boolean {
  return args.includes(name);
}

function flagValue(args: string[], name: string): string | undefined {
  const index = args.indexOf(name);
  if (index === -1) return undefined;
  const value = args[index + 1];
  if (!value || value.startsWith("--")) return undefined;
  return value;
}

function flagValues(args: string[], name: string): string[] {
  const values: string[] = [];
  for (let i = 0; i < args.length; i += 1) {
    if (args[i] === name && args[i + 1] && !args[i + 1].startsWith("--")) {
      values.push(args[i + 1]);
      i += 1;
    }
  }
  return values;
}

function observationFromArgs(args: string[]): IdentifierObservation {
  const json = flagValue(args, "--json");
  if (json) {
    return JSON.parse(json) as IdentifierObservation;
  }
  return {
    field: flagValue(args, "--field") ?? "identifier",
    intended: flagValue(args, "--intended") ?? null,
    extracted: flagValue(args, "--extracted") ?? null,
    readbackConfirmed: hasFlag(args, "--readback"),
    evidenceKind: flagValue(args, "--evidence-kind") === "verbatim_span" ? "verbatim_span" : "none",
    evidenceText: flagValue(args, "--evidence") ?? null,
    secondChannelMatch: hasFlag(args, "--matched"),
  };
}

function printJson(value: unknown): string {
  return `${JSON.stringify(value, null, 2)}\n`;
}

export function runExactRefCli(argv: string[]): CliResult {
  const [command, ...args] = argv;
  try {
    if (command === "classify") {
      const decision = classifyIdentifier(observationFromArgs(args));
      return { code: decision.writable ? 0 : 2, stdout: printJson(decision), stderr: "" };
    }
    if (command === "verify") {
      const typed = flagValue(args, "--typed") ?? "";
      const claimsSecondChannel = hasFlag(args, "--second-channel");
      const decision = applyHumanVerification({
        observation: observationFromArgs(args),
        typed,
        claimsSecondChannel,
      });
      return { code: decision.writable ? 0 : 2, stdout: printJson(decision), stderr: "" };
    }
    if (command === "compile") {
      const compiled = compileIdentifierTask({
        purpose: flagValue(args, "--purpose") ?? "Obtain the identifier.",
        fieldLabel: flagValue(args, "--field") ?? "identifier",
        destinationLabel: flagValue(args, "--destination") ?? "the destination",
        factsTheAgentMayState: flagValues(args, "--fact"),
        intended: flagValue(args, "--intended") ?? null,
      });
      return {
        code: compiled.leaksIntended ? 2 : 0,
        stdout: printJson(compiled),
        stderr: compiled.leaksIntended ? "Rejected: intended identifier leaked into the task.\n" : "",
      };
    }
  } catch (error) {
    return {
      code: 1,
      stdout: "",
      stderr: error instanceof Error ? `${error.message}\n` : "Command failed.\n",
    };
  }

  return {
    code: 2,
    stdout: "",
    stderr:
      "Usage: exactref classify|verify|compile [--intended] [--extracted] [--readback] [--typed] [--second-channel] [--json '{...}']\n",
  };
}
