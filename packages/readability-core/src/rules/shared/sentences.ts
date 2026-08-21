import { parse } from "@textlint/markdown-to-ast";
import { split } from "sentence-splitter";

import { type SourceRange } from "../../types/range.ts";

type RangedNode = Readonly<{
  type?: unknown;
  range?: unknown;
  children?: unknown;
}>;

type SourceInterval = Readonly<{ start: number; end: number }>;

export type SourceSentence = Readonly<{
  text: string;
  range: SourceRange;
}>;

function isRange(value: unknown): value is readonly [number, number] {
  return Array.isArray(value)
    && value.length === 2
    && Number.isInteger(value[0])
    && Number.isInteger(value[1]);
}

function codeBlockRanges(node: RangedNode): readonly SourceInterval[] {
  const own = node.type === "CodeBlock" && isRange(node.range)
    ? [{ start: node.range[0], end: node.range[1] }]
    : [];
  const children = Array.isArray(node.children)
    ? node.children.flatMap((child) => codeBlockRanges(child as RangedNode))
    : [];
  return [...own, ...children];
}

function sourceIntervals(input: string, excludeCodeBlocks: boolean): readonly SourceInterval[] {
  if (!excludeCodeBlocks) return [{ start: 0, end: input.length }];
  const excluded = [...codeBlockRanges(parse(input))].sort((left, right) => left.start - right.start);
  const state = excluded.reduce(
    (current, range) => ({
      cursor: Math.max(current.cursor, range.end),
      intervals: range.start > current.cursor
        ? [...current.intervals, { start: current.cursor, end: range.start }]
        : current.intervals,
    }),
    { cursor: 0, intervals: [] as readonly SourceInterval[] },
  );
  return state.cursor < input.length
    ? [...state.intervals, { start: state.cursor, end: input.length }]
    : state.intervals;
}

export function sentencesFromSource(input: string, excludeCodeBlocks: boolean): readonly SourceSentence[] {
  return sourceIntervals(input, excludeCodeBlocks).flatMap((interval) =>
    split(input.slice(interval.start, interval.end))
      .filter((node) => node.type === "Sentence")
      .flatMap((node) => {
        const text = node.raw.trim();
        if (text.length === 0) return [];
        const leadingWhitespace = node.raw.length - node.raw.trimStart().length;
        const trailingWhitespace = node.raw.length - node.raw.trimEnd().length;
        return [{
          text,
          range: Object.freeze({
            start: interval.start + node.range[0] + leadingWhitespace,
            end: interval.start + node.range[1] - trailingWhitespace,
          }),
        }];
      }));
}
