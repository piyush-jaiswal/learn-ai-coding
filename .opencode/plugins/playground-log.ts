import { Plugin } from "@opencode/plugin";
import { appendFile, mkdir } from "node:fs/promises";
import { join } from "node:path";

const PLAYGROUND_SERVER = "playground/server.py";
const LOG_ENTRY = "playground shell request\n";

export default Plugin.define({
  id: "applymaxxing.playground-log",
  setup: async (ctx) => {
    const projectRoot = ctx.location.directory;
    const logPath = join(projectRoot, "logs", "plugin-playground.log");

    await ctx.shell.hook("create.before", async (event) => {
      if (typeof event.command !== "string") {
        return;
      }

      if (!event.command.includes(PLAYGROUND_SERVER)) {
        return;
      }

      await mkdir(join(projectRoot, "logs"), { recursive: true });
      await appendFile(logPath, LOG_ENTRY);
    });
  },
});
