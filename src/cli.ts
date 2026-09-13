import { runExactRefCli } from "./lib/exactref-cli";

const result = runExactRefCli(process.argv.slice(2));
if (result.stdout) process.stdout.write(result.stdout);
if (result.stderr) process.stderr.write(result.stderr);
process.exit(result.code);
