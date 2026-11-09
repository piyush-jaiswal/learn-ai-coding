import { Plugin } from "@opencode/plugin";
import { appendFile, mkdir } from "node:fs/promises";
import { join } from "node:path";

const LOGGED_TOOLS = new Set(["edit", "write", "patch", "apply_patch"]);
const LOG_DIRECTORY = "logs";
const LOG_FILE = "plugin-tools.log";

export default Plugin.define({
  id: "applymaxxing.edit-log",
  setup: async (ctx) => {
    const logDirectory = join(ctx.location.directory, LOG_DIRECTORY);
    const logPath = join(logDirectory, LOG_FILE);

    await ctx.tool.hook("execute.after", async (event) => {
      if (event.status !== "completed") {
        return;
      }

      if (!LOGGED_TOOLS.has(event.tool)) {
        return;
      }

      await mkdir(logDirectory, { recursive: true });
      await appendFile(logPath, `${JSON.stringify({ tool: event.tool, status: event.status })}\n`);
    });
  },
});
