// =============================================================================
// server.ts — MCP server setup com handlers para list_tools e call_tool
// =============================================================================

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { KBLoader } from "./kb-loader.js";
import { buildTools, type ToolHandler } from "./tools.js";

export interface ServerOptions {
  kbRoot: string;
  serverName?: string;
  serverVersion?: string;
}

export function createServer(options: ServerOptions): Server {
  const { kbRoot, serverName = "kb-mcp", serverVersion = "0.1.0" } = options;

  const kb = new KBLoader(kbRoot);
  const tools = buildTools(kb);
  const toolMap = new Map<string, ToolHandler>(tools.map((t) => [t.name, t]));

  const server = new Server(
    {
      name: serverName,
      version: serverVersion,
    },
    {
      capabilities: {
        tools: {},
      },
    }
  );

  // Handler: list tools
  server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
      tools: tools.map((t) => ({
        name: t.name,
        description: t.description,
        inputSchema: t.inputSchema,
      })),
    };
  });

  // Handler: call tool
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;
    const tool = toolMap.get(name);
    if (!tool) {
      return {
        isError: true,
        content: [
          {
            type: "text" as const,
            text: `Unknown tool: ${name}. Available: ${Array.from(toolMap.keys()).join(", ")}`,
          },
        ],
      };
    }

    try {
      const result = await tool.handler(args || {});
      return result;
    } catch (e) {
      return {
        isError: true,
        content: [
          {
            type: "text" as const,
            text: `Error executing ${name}: ${(e as Error).message}`,
          },
        ],
      };
    }
  });

  return server;
}
