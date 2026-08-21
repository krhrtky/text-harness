import { createDeterministicFinding, type DeterministicFinding } from "../types/findings.ts";
import { type Severity } from "../types/rules.ts";
import { sentencesFromSource, type SourceSentence } from "./shared/sentences.ts";

export type D001Style = "consistent" | "desu-masu" | "da-dearu";
type ClassifiedStyle = Exclude<D001Style, "consistent">;
type ClassifiedSentence = Readonly<SourceSentence & { style: ClassifiedStyle }>;

const QUOTED_CONTENT = /「[^」]*」|『[^』]*』|“[^”]*”|‘[^’]*’/gu;
const TERMINAL_PUNCTUATION = /[。！？!?]+$/u;
const DESU_MASU_ENDING = /(?:です|ます|でした|ました|ません|ませんでした|でしょう|ましょう)$/u;
const DA_DEARU_ENDING = /(?:である|であった|だ|だった)$/u;

function classifySentence(sentence: SourceSentence): ClassifiedSentence | undefined {
  const outerText = sentence.text
    .replace(QUOTED_CONTENT, "")
    .trim()
    .replace(TERMINAL_PUNCTUATION, "")
    .trimEnd();
  const style = DESU_MASU_ENDING.test(outerText)
    ? "desu-masu"
    : DA_DEARU_ENDING.test(outerText)
      ? "da-dearu"
      : undefined;
  return style === undefined ? undefined : Object.freeze({ ...sentence, style });
}

export function analyzeD001(
  input: string,
  style: D001Style,
  severity: Severity,
): readonly DeterministicFinding[] {
  const classified = sentencesFromSource(input, false)
    .map(classifySentence)
    .filter((sentence): sentence is ClassifiedSentence => sentence !== undefined);
  const expected = style === "consistent" ? classified[0]?.style : style;
  if (expected === undefined) return [];
  const candidates = style === "consistent" ? classified.slice(1) : classified;
  return candidates
    .filter((sentence) => sentence.style !== expected)
    .map((sentence) => createDeterministicFinding(input, {
      ruleId: "D001",
      range: sentence.range,
      severity,
      message: `文体が基準の${expected}と一致しません（${sentence.style}）。`,
    }));
}
