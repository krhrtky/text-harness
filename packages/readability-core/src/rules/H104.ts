import { createHeuristicFinding, type HeuristicFinding } from "../types/findings.ts";
import { sentencesFromSource } from "./shared/sentences.ts";

const PAIRS = Object.freeze([
  ["（", "）"], ["「", "」"], ["『", "』"], ["【", "】"], ["[", "]"],
] as const);
const CLOSE_BY_OPEN = new Map<string, string>(PAIRS);
const CLOSING: ReadonlySet<string> = new Set(PAIRS.map(([, close]) => close));

function balancedMaximumDepth(text: string): number | undefined {
  let stack: readonly string[] = [];
  let maximum = 0;
  for (const character of text) {
    const expectedClose = CLOSE_BY_OPEN.get(character);
    if (expectedClose !== undefined) {
      stack = [...stack, expectedClose];
      maximum = Math.max(maximum, stack.length);
    } else if (CLOSING.has(character)) {
      if (stack.at(-1) !== character) return undefined;
      stack = stack.slice(0, -1);
    }
  }
  return stack.length === 0 ? maximum : undefined;
}

export function analyzeH104(
  input: string,
  threshold: number,
  excludeCodeBlocks: boolean,
): readonly HeuristicFinding[] {
  return sentencesFromSource(input, excludeCodeBlocks).flatMap(({ text, range }) => {
    const actual = balancedMaximumDepth(text);
    return actual !== undefined && actual > threshold
      ? [createHeuristicFinding(input, {
          ruleId: "H104",
          range,
          actual,
          threshold,
          message: `括弧の最大ネスト深度が閾値${threshold}を超えています（${actual}）。`,
        })]
      : [];
  });
}
